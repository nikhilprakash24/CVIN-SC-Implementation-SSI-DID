"""The owner's disclosure policy: what may be proved, to whom, how coarsely, and how much may leak in total.

A policy is data, not code. It is canonicalised, hashed and signed by the owner's key; the kernel runs only signed
policies. A policy proposed by a language model is accepted only if it is *no wider* than the owner's signed one
(`is_narrower_or_equal`); widening needs the owner's signature again. That rule is the boundary between what the
model may suggest and what the owner decides (Plan 1, P4).
"""
from __future__ import annotations

import copy
import fnmatch
import hashlib
import json
from dataclasses import dataclass, field

from eth_account import Account
from eth_account.messages import encode_defunct

PREDICATES = ("ge", "le", "eq", "member")
# Attributes the Steward knows. Ordered attributes carry a domain; leakage is accounted on them.
ATTRIBUTES = {
    "model_year": {"ordered": True, "domain": [1995, 2026]},
    "region": {"ordered": False},
    "manufacturer": {"ordered": False},
    "odometer_band": {"ordered": True, "domain": [0, 40]},
    "vin": {"ordered": False},
}
SECRET_ATTRIBUTES = ("vin", "salt", "private_key")

# JSON Schema of a policy (strict: no unknown fields anywhere). The language-model backend is constrained to it.
RULE_SCHEMA = {
    "type": "object",
    "properties": {
        "verifiers": {"type": "string", "description": "verifier DID or class pattern, e.g. insurer:*, rsu:*, *"},
        "attribute": {"type": "string", "enum": list(ATTRIBUTES)},
        "predicates": {"type": "array", "items": {"type": "string", "enum": list(PREDICATES)}},
        "consent": {"type": "boolean"},
        "expires": {"type": ["string", "null"], "description": "YYYY-MM-DD or null"},
    },
    "required": ["verifiers", "attribute", "predicates", "consent", "expires"],
    "additionalProperties": False,
}
LIMIT_SCHEMA = {
    "type": "object",
    "properties": {
        "attribute": {"type": "string", "enum": [a for a, s in ATTRIBUTES.items() if s["ordered"]]},
        "granularity": {"type": "integer"},
        "global_budget_bits": {"type": "number"},
        "per_verifier_budget_bits": {"type": ["number", "null"]},
    },
    "required": ["attribute", "granularity", "global_budget_bits", "per_verifier_budget_bits"],
    "additionalProperties": False,
}
POLICY_SCHEMA = {
    "type": "object",
    "properties": {
        "never_reveal": {"type": "array", "items": {"type": "string"}},
        "blocked_verifiers": {"type": "array", "items": {"type": "string"}},
        "rules": {"type": "array", "items": RULE_SCHEMA},
        "limits": {"type": "array", "items": LIMIT_SCHEMA},
    },
    "required": ["never_reveal", "blocked_verifiers", "rules", "limits"],
    "additionalProperties": False,
}


class PolicyError(ValueError):
    pass


def validate(doc: dict) -> dict:
    """Structural validation against POLICY_SCHEMA without a schema library (the kernel must not trust input)."""
    def check_obj(obj, schema, where):
        if not isinstance(obj, dict):
            raise PolicyError(f"{where}: expected an object")
        extra = set(obj) - set(schema["properties"])
        if extra:
            raise PolicyError(f"{where}: unknown field(s) {sorted(extra)}")
        missing = set(schema["required"]) - set(obj)
        if missing:
            raise PolicyError(f"{where}: missing field(s) {sorted(missing)}")
        for k, s in schema["properties"].items():
            v = obj[k]
            types = s["type"] if isinstance(s["type"], list) else [s["type"]]
            ok = any((t == "string" and isinstance(v, str)) or (t == "boolean" and isinstance(v, bool))
                     or (t == "integer" and isinstance(v, int) and not isinstance(v, bool))
                     or (t == "number" and isinstance(v, (int, float)) and not isinstance(v, bool))
                     or (t == "null" and v is None) or (t == "array" and isinstance(v, list)) for t in types)
            if not ok:
                raise PolicyError(f"{where}.{k}: wrong type")
            if "enum" in s and v not in s["enum"]:
                raise PolicyError(f"{where}.{k}: {v!r} not allowed")
            if s.get("type") == "array" and "items" in s:
                for i, item in enumerate(v):
                    if s["items"].get("type") == "object":
                        check_obj(item, s["items"], f"{where}.{k}[{i}]")
                    elif "enum" in s["items"] and item not in s["items"]["enum"]:
                        raise PolicyError(f"{where}.{k}[{i}]: {item!r} not allowed")
                    elif not isinstance(item, str):
                        raise PolicyError(f"{where}.{k}[{i}]: expected a string")
    check_obj(doc, POLICY_SCHEMA, "policy")
    for lim in doc["limits"]:
        if lim["granularity"] < 1 or lim["global_budget_bits"] < 0:
            raise PolicyError("limits: granularity >= 1 and budgets >= 0")
    for secret in SECRET_ATTRIBUTES:
        if any(r["attribute"] == secret for r in doc["rules"]):
            raise PolicyError(f"no rule may disclose {secret}")
    return doc


def canonical(doc: dict) -> bytes:
    return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()


def policy_hash(doc: dict) -> str:
    return hashlib.sha256(canonical(doc)).hexdigest()


@dataclass
class SignedPolicy:
    doc: dict
    signer: str  # Ethereum address of the owner
    signature: str

    @classmethod
    def sign(cls, doc: dict, owner_key: str) -> "SignedPolicy":
        validate(doc)
        msg = encode_defunct(text="CVIN Steward policy " + policy_hash(doc))
        sig = Account.sign_message(msg, owner_key)
        return cls(copy.deepcopy(doc), Account.from_key(owner_key).address, sig.signature.hex())

    def verify(self, owner_address: str) -> bool:
        try:
            validate(self.doc)
            msg = encode_defunct(text="CVIN Steward policy " + policy_hash(self.doc))
            return Account.recover_message(msg, signature=bytes.fromhex(self.signature.removeprefix("0x"))) \
                == owner_address == self.signer
        except Exception:
            return False


def pattern_covers(outer: str, inner: str) -> bool:
    """True if every verifier matched by `inner` is matched by `outer` (patterns are 'x', 'class:*' or '*')."""
    if outer == "*" or outer == inner:
        return True
    if outer.endswith(":*"):
        return inner.startswith(outer[:-1]) and inner != outer[:-1]
    return False


def verifier_matches(pattern: str, verifier: str) -> bool:
    return fnmatch.fnmatchcase(verifier, pattern)


def is_narrower_or_equal(candidate: dict, base: dict) -> tuple[bool, list[str]]:
    """Can `candidate` replace `base` without the owner's signature? Only if it allows nothing `base` forbids."""
    why = []
    if not set(base["never_reveal"]) <= set(candidate["never_reveal"]):
        why.append("drops a never-reveal attribute")
    if not set(base["blocked_verifiers"]) <= set(candidate["blocked_verifiers"]):
        why.append("unblocks a verifier")
    for r in candidate["rules"]:
        covered = any(pattern_covers(b["verifiers"], r["verifiers"]) and b["attribute"] == r["attribute"]
                      and set(r["predicates"]) <= set(b["predicates"]) and (r["consent"] or not b["consent"])
                      and (b["expires"] is None or (r["expires"] is not None and r["expires"] <= b["expires"]))
                      for b in base["rules"])
        if not covered:
            why.append(f"rule {r['verifiers']}/{r['attribute']}/{r['predicates']} is wider than the signed policy")
    base_lim = {l["attribute"]: l for l in base["limits"]}
    for a, bl in base_lim.items():
        cl = next((l for l in candidate["limits"] if l["attribute"] == a), None)
        if cl is None:
            why.append(f"removes the limit on {a}")
            continue
        if cl["global_budget_bits"] > bl["global_budget_bits"]:
            why.append(f"raises the global budget on {a}")
        if cl["granularity"] < bl["granularity"]:
            why.append(f"refines the granularity on {a}")
        if bl["per_verifier_budget_bits"] is not None and (cl["per_verifier_budget_bits"] is None
                                                           or cl["per_verifier_budget_bits"] > bl["per_verifier_budget_bits"]):
            why.append(f"raises the per-verifier budget on {a}")
    return (not why, why)


def empty_policy() -> dict:
    return {"never_reveal": list(SECRET_ATTRIBUTES), "blocked_verifiers": [], "rules": [], "limits": []}
