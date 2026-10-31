"""The vault: secrets go in, proofs and signatures come out, values never do.

It holds the vehicle's attribute values with their commitment randomness and the agent's signing key. Its public
surface is: commitments, threshold proofs, and signatures. There is no getter for a value, and the representation
is redacted, so a language model given the agent's state, logs or tracebacks cannot read a secret from them.
"""
from __future__ import annotations

import secrets as _secrets

from eth_account import Account
from eth_account.messages import encode_defunct

from zkid import sigma
from zkid.ec import N


class Vault:
    def __init__(self, attributes: dict[str, int], agent_key: str | None = None, rng=None):
        self.__values = dict(attributes)
        self.__r = {k: (rng.randrange(1, N) if rng else _secrets.randbelow(N - 1) + 1) for k in attributes}
        self.__account = Account.from_key(agent_key) if agent_key else Account.create()

    def __repr__(self) -> str:
        return f"Vault(<{len(self.__values)} sealed attributes>, agent={self.address})"

    __str__ = __repr__

    @property
    def address(self) -> str:
        return self.__account.address

    def commitment(self, attribute: str):
        return sigma.pedersen_commit(self.__values[attribute], self.__r[attribute])

    def holds(self, attribute: str, predicate: str, t: int) -> bool:
        v = self.__values[attribute]
        return {"ge": v >= t, "le": v <= t, "eq": v == t}[predicate]

    def prove_ge(self, attribute: str, t: int, context: bytes, n: int = 6, rng=None):
        """A zero-knowledge proof that value >= t bound to `context`, or None when the predicate is false."""
        v = self.__values[attribute]
        if v < t or v - t >= (1 << n):
            return None
        C = self.commitment(attribute)
        return sigma.threshold_prove(v, self.__r[attribute], C, t, n, context, rng)

    def sign(self, text: str) -> str:
        return Account.sign_message(encode_defunct(text=text), self.__account.key).signature.hex()
