from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class SecretRef:
    name: str
    present: bool


class EnvSecretManager:
    """Minimal secret lookup layer.

    Secrets must not be committed to git. This class only reads environment
    variables and reports whether a required secret exists.
    """

    def has_secret(self, name: str) -> SecretRef:
        return SecretRef(name=name, present=bool(os.getenv(name)))

    def require(self, name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise RuntimeError(f"missing required secret: {name}")
        return value
