"""
Message freshness and replay protection for the V2X identity providers
(review 02, T-9).

Before review 02 the providers put a `timestamp` next to the signature but
signed only `message`, and no verifier looked at the timestamp. A captured
packet therefore verified forever, and its timestamp could be rewritten.

This module gives every provider the same three pieces:

1. `signed_bytes(message, timestamp)`: the exact bytes that are signed. The
   generation time is inside the signature, so altering it breaks the
   signature. Any `seq`/`msgCnt`/nonce field is part of `message` and is
   therefore signed as well.
2. A freshness window: the receiver rejects a message whose generation time
   is more than `max_age_s` in the past or more than `max_future_s` in the
   future of its own clock.
3. An optional bounded replay cache: within the window a message whose
   (signer, sha256(signed bytes)) was already accepted is rejected. The key is
   the digest of the signed bytes, not of the signature, so ECDSA signature
   malleability (r, n-s) does not produce a "new" message.

Default window (project choice, documented here and in docs/review02/PASS2_T.md)
-------------------------------------------------------------------------------
`docs/LATENCY_BUDGET.md` fixes the BSM interval at 100 ms (SAE J2945/1, 10 Hz)
and does not state a generation-time tolerance; this repository has no IEEE
1609.2 security-profile text to quote. The default is therefore a project
choice tied to that budget:

  * DEFAULT_MAX_AGE_S = 1.0 s   (ten BSM intervals: a BSM older than that is
                                 stale for any safety application and long
                                 past the identity budget of 50 ms)
  * DEFAULT_MAX_FUTURE_S = 0.1 s (one BSM interval of clock skew between
                                 sender and receiver; GNSS-disciplined OBU
                                 clocks are far tighter)

Both are constructor arguments; a deployment that follows a specific IEEE
1609.2 / ETSI profile sets its own values.

Replay cache bound
------------------
Entries live for max_age_s + max_future_s (after that the freshness check
alone rejects the packet). The cache holds at most `replay_cache_size`
entries; when it is full of still-live entries the oldest is evicted and
`evicted_live` is incremented. A replay of an evicted message inside the
window would then pass, so size the cache for the expected message rate x
window (default 65,536 entries: about 650 senders at 10 Hz for 1.1 s, with
a margin of ten).
"""

from __future__ import annotations

import hashlib
import json
import time
from collections import OrderedDict
from datetime import datetime, timezone
from typing import Callable, Optional, Tuple

DEFAULT_MAX_AGE_S = 1.0
DEFAULT_MAX_FUTURE_S = 0.1
DEFAULT_REPLAY_CACHE_SIZE = 65_536


def generation_timestamp() -> str:
    """Current UTC time as the providers have always written it (naive ISO 8601).

    Same format and length as the pre-review `datetime.utcnow().isoformat()`,
    so the wire size of a signed message does not change.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None).isoformat()


def signed_bytes(message, timestamp) -> bytes:
    """The bytes a provider signs: the message AND its generation time."""
    return json.dumps({'message': message, 'timestamp': timestamp},
                      sort_keys=True).encode()


def parse_timestamp(ts) -> float:
    """ISO 8601 (naive = UTC, or with an offset) or a number -> epoch seconds."""
    if isinstance(ts, bool):
        raise ValueError("timestamp must be a string or a number")
    if isinstance(ts, (int, float)):
        return float(ts)
    if not isinstance(ts, str):
        raise ValueError("timestamp must be a string or a number")
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


class FreshnessPolicy:
    """
    Freshness window plus optional bounded replay cache.

    Usage inside a verifier:

        reason = policy.check(timestamp, signer_id, payload_bytes)
        if reason: reject
        ... verify the signature over payload_bytes ...
        policy.accept(signer_id, payload_bytes, timestamp)

    `accept` is called only after the signature verified, so a forged packet
    cannot pre-poison the cache and block the genuine one.

    `enabled=False` turns the whole policy off (no window, no cache). It
    exists so a caller can measure the cost of the checks; nothing in the
    repository runs with it off.
    """

    def __init__(self, max_age_s: float = DEFAULT_MAX_AGE_S,
                 max_future_s: float = DEFAULT_MAX_FUTURE_S,
                 replay_cache: bool = True,
                 replay_cache_size: int = DEFAULT_REPLAY_CACHE_SIZE,
                 clock: Optional[Callable[[], float]] = None,
                 enabled: bool = True):
        if max_age_s <= 0 or max_future_s < 0:
            raise ValueError("max_age_s must be > 0 and max_future_s >= 0")
        if replay_cache and replay_cache_size < 1:
            raise ValueError("replay_cache_size must be >= 1")
        self.max_age_s = float(max_age_s)
        self.max_future_s = float(max_future_s)
        self.replay_cache = bool(replay_cache)
        self.replay_cache_size = int(replay_cache_size)
        self.clock = clock or time.time
        self.enabled = bool(enabled)
        self._seen: "OrderedDict[Tuple[str, bytes], float]" = OrderedDict()
        self.evicted_live = 0
        self.rejected_stale = 0
        self.rejected_future = 0
        self.rejected_replay = 0

    # -- configuration record (written into experiment outputs) -------------
    def describe(self) -> dict:
        return {
            'enabled': self.enabled,
            'max_age_s': self.max_age_s,
            'max_future_s': self.max_future_s,
            'replay_cache': self.replay_cache,
            'replay_cache_size': self.replay_cache_size if self.replay_cache else 0,
        }

    @staticmethod
    def _key(signer_id, payload: bytes):
        return (str(signer_id), hashlib.sha256(payload).digest())

    def check(self, timestamp, signer_id, payload: bytes,
              now: Optional[float] = None) -> Optional[str]:
        """None if the message may proceed to signature verification, else a reason."""
        if not self.enabled:
            return None
        if timestamp is None:
            return "missing timestamp"
        try:
            t = parse_timestamp(timestamp)
        except (ValueError, TypeError, OverflowError):
            return "unparseable timestamp"
        now = self.clock() if now is None else now
        if now - t > self.max_age_s:
            self.rejected_stale += 1
            return "stale (older than freshness window)"
        if t - now > self.max_future_s:
            self.rejected_future += 1
            return "timestamp in the future"
        if self.replay_cache and self._key(signer_id, payload) in self._seen:
            self.rejected_replay += 1
            return "replay (already accepted)"
        return None

    def accept(self, signer_id, payload: bytes, timestamp,
               now: Optional[float] = None) -> None:
        """Record a verified message in the replay cache."""
        if not (self.enabled and self.replay_cache):
            return
        now = self.clock() if now is None else now
        expiry = parse_timestamp(timestamp) + self.max_age_s + self.max_future_s
        # Drop expired entries from the front (insertion order ~ arrival order).
        while self._seen:
            k, exp = next(iter(self._seen.items()))
            if exp >= now:
                break
            self._seen.popitem(last=False)
        self._seen[self._key(signer_id, payload)] = expiry
        while len(self._seen) > self.replay_cache_size:
            _, exp = self._seen.popitem(last=False)
            if exp >= now:
                self.evicted_live += 1

    def __len__(self):
        return len(self._seen)
