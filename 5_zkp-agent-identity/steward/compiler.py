"""Plain English to policy.

Two compilers, one output type (a policy dict valid under `policy.POLICY_SCHEMA`):

* `GrammarCompiler`  offline and deterministic: a controlled-English grammar of ten sentence forms. It refuses a
                     sentence it does not understand rather than guessing.
* `ClaudePolicyCompiler`  optional: sends the owner's text to a language model constrained by the policy JSON
                     schema (structured outputs). Its output is validated like any untrusted input, and the Steward
                     accepts it only if it is no wider than the owner's signed policy, or after the owner signs it.

The language model never decides a disclosure; it only drafts a policy that the owner can read and sign.
"""
from __future__ import annotations

import json
import os
import re

from .policy import ATTRIBUTES, POLICY_SCHEMA, PolicyError, empty_policy, validate

ROLES = {
    "insurers": "insurer:*", "insurer": "insurer:*", "toll operators": "toll:*", "tolls": "toll:*",
    "rsus": "rsu:*", "roadside units": "rsu:*", "dealers": "dealer:*", "anyone": "*", "everyone": "*",
    "regulators": "regulator:*", "other agents": "agent:*",
}
ATTR_WORDS = {
    "model year": "model_year", "model-year": "model_year", "year": "model_year", "region": "region",
    "registration region": "region", "manufacturer": "manufacturer", "make": "manufacturer", "vin": "vin",
    "odometer": "odometer_band", "mileage": "odometer_band", "odometer band": "odometer_band",
}
PRED_WORDS = {"at least": "ge", "at most": "le", "equals": "eq", "equal to": "eq", "is": "eq",
              "authorised": "member", "authorized": "member"}


class CompileError(PolicyError):
    def __init__(self, unknown: list[str]):
        super().__init__("could not understand: " + " | ".join(unknown))
        self.unknown = unknown


def _attr(words: str) -> str:
    w = words.strip().lower().removeprefix("my ").strip()
    if w in ATTR_WORDS:
        return ATTR_WORDS[w]
    if w.replace(" ", "_") in ATTRIBUTES:
        return w.replace(" ", "_")
    raise KeyError(w)


def _limit(doc: dict, attribute: str) -> dict:
    for lim in doc["limits"]:
        if lim["attribute"] == attribute:
            return lim
    lim = {"attribute": attribute, "granularity": 1, "global_budget_bits": 64.0, "per_verifier_budget_bits": None}
    doc["limits"].append(lim)
    return lim


_VERIFIER = r"(insurers?|toll operators|tolls|rsus|roadside units|dealers|anyone|everyone|regulators|other agents|verifier [\w:.\-]+)"
_FORMS = [
    ("never", re.compile(r"^never (?:reveal|share|disclose|give out) my ([\w \-]+)$")),
    ("allow", re.compile(r"^" + _VERIFIER + r" (?:may|can) (?:check|verify|confirm|learn) (?:that )?my ([\w \-]+?) "
                         r"(?:is )?(at least|at most|equals|equal to|authori[sz]ed)(?: a threshold| some value| [\d]+)?$")),
    ("allow_member", re.compile(r"^" + _VERIFIER + r" (?:may|can) (?:check|verify|confirm) (?:that )?my ([\w \-]+?) "
                                r"is (?:an )?(authori[sz]ed)(?: one| manufacturer)?$")),
    ("allow_eq", re.compile(r"^" + _VERIFIER + r" (?:may|can) (?:check|verify|confirm) my ([\w \-]+)$")),
    ("round", re.compile(r"^round (?:my )?([\w \-]+?) (?:answers |proofs )?to (\d+)[- ](?:year|unit)s?(?: buckets?)?$")),
    ("budget", re.compile(r"^(?:do not|don't|never) (?:leak|reveal) more than ([\d.]+) bits? (?:in total )?about my ([\w \-]+?)(?: in total)?$")),
    ("per_verifier", re.compile(r"^no single verifier (?:may|can|should) learn more than ([\d.]+) bits? about my ([\w \-]+)$")),
    ("consent", re.compile(r"^ask me (?:first )?before (?:sharing|proving) (?:anything about )?my ([\w \-]+?)$")),
    ("block", re.compile(r"^(?:block|never answer|ignore) (?:verifier )?([\w:.\-]+)$")),
    ("expires", re.compile(r"^(?:these rules|this policy|the rules) expires? on (\d{4}-\d{2}-\d{2})$")),
]


class GrammarCompiler:
    """Controlled English. One sentence per line or per full stop. Unknown sentences raise CompileError."""

    def compile(self, text: str, base: dict | None = None) -> dict:
        doc = json.loads(json.dumps(base)) if base else empty_policy()
        unknown = []
        sentences = [s.strip().rstrip(".").lower() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]
        pending_expiry = None
        for s in sentences:
            if not self._apply(doc, s):
                m = _FORMS[-1][1].match(s)
                if m:
                    pending_expiry = m.group(1)
                else:
                    unknown.append(s)
        if unknown:
            raise CompileError(unknown)
        if pending_expiry:
            for r in doc["rules"]:
                r["expires"] = pending_expiry
        return validate(doc)

    def _apply(self, doc: dict, s: str) -> bool:
        for name, rx in _FORMS[:-1]:
            m = rx.match(s)
            if not m:
                continue
            try:
                if name == "never":
                    a = _attr(m.group(1))
                    if a not in doc["never_reveal"]:
                        doc["never_reveal"].append(a)
                    doc["rules"] = [r for r in doc["rules"] if r["attribute"] != a]
                elif name in ("allow", "allow_member", "allow_eq"):
                    who = m.group(1)
                    verifiers = who.split(" ", 1)[1] if who.startswith("verifier ") else ROLES[who]
                    a = _attr(m.group(2))
                    if a in doc["never_reveal"]:
                        return False
                    pred = "eq" if name == "allow_eq" else PRED_WORDS[m.group(3)]
                    for r in doc["rules"]:
                        if r["verifiers"] == verifiers and r["attribute"] == a:
                            if pred not in r["predicates"]:
                                r["predicates"].append(pred)
                            break
                    else:
                        doc["rules"].append({"verifiers": verifiers, "attribute": a, "predicates": [pred],
                                             "consent": False, "expires": None})
                elif name == "round":
                    _limit(doc, _attr(m.group(1)))["granularity"] = int(m.group(2))
                elif name == "budget":
                    _limit(doc, _attr(m.group(2)))["global_budget_bits"] = float(m.group(1))
                elif name == "per_verifier":
                    _limit(doc, _attr(m.group(2)))["per_verifier_budget_bits"] = float(m.group(1))
                elif name == "consent":
                    a = _attr(m.group(1))
                    for r in doc["rules"]:
                        if r["attribute"] == a:
                            r["consent"] = True
                elif name == "block":
                    if m.group(1) not in doc["blocked_verifiers"]:
                        doc["blocked_verifiers"].append(m.group(1))
                return True
            except KeyError:
                return False
        return False


class ClaudePolicyCompiler:
    """Optional language-model backend (needs the `anthropic` package and credentials). Never on the decision path."""

    SYSTEM = ("You translate a vehicle owner's plain-English data-sharing wishes into a disclosure policy for their "
              "identity agent. Output only the policy. Be conservative: when a wish is ambiguous, choose the reading "
              "that discloses less. Never create a rule that discloses vin, salt or private_key. Verifier patterns are "
              "'class:*' (insurer, toll, rsu, dealer, regulator, agent), an exact verifier id, or '*'.")

    def __init__(self, client=None, model: str = "claude-opus-5-5"):
        self.model = model
        self._client = client

    def _get_client(self):
        if self._client is None:
            import anthropic  # optional dependency
            self._client = anthropic.Anthropic()
        return self._client

    def compile(self, text: str, base: dict | None = None) -> dict:
        client = self._get_client()
        content = text if base is None else f"Current policy:\n{json.dumps(base)}\n\nOwner's new wishes:\n{text}"
        resp = client.beta.messages.create(
            model=self.model,
            max_tokens=16000,
            system=self.SYSTEM,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            output_config={"effort": "medium", "format": {"type": "json_schema", "schema": POLICY_SCHEMA}},
            messages=[{"role": "user", "content": content}],
        )
        if resp.stop_reason == "refusal":
            raise PolicyError("the model declined to draft a policy")
        if resp.stop_reason == "max_tokens":
            raise PolicyError("the policy draft was cut off")
        texts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
        if not texts:
            raise PolicyError("no policy in the model's response")
        try:
            doc = json.loads(texts[-1])
        except json.JSONDecodeError as e:
            raise PolicyError(f"the model's policy is not JSON: {e}") from e
        return validate(doc)


def default_compiler():
    """The grammar compiler unless CVIN_STEWARD_LLM=1 is set (then the language-model backend)."""
    return ClaudePolicyCompiler() if os.environ.get("CVIN_STEWARD_LLM") == "1" else GrammarCompiler()
