"""
agent.py — identity, policy e audit in un unico file.
Nessuna dipendenza esterna.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, UTC
from pathlib import Path
from typing import Any


# ── Identity ─────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AgentIdentity:
    name: str
    allowed_tools: tuple[str, ...] = field(default_factory=tuple)

    def can_use(self, tool: str) -> bool:
        return tool in self.allowed_tools


DEFAULT_IDENTITY = AgentIdentity(
    name="MiniSentinel",
    allowed_tools=("list_documents", "read_document"),
)


# ── Policy ────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AgentPolicy:
    can_read_docs: bool = False
    can_write: bool = False                 # disabilitato: nessuna scrittura


POLICY_FLAGS: dict[str, str] = {
    "list_documents": "can_read_docs",
    "read_document":  "can_read_docs",
}


class PolicyViolationError(PermissionError):
    pass


def check_permission(policy: AgentPolicy, tool: str) -> None:
    flag = POLICY_FLAGS.get(tool)
    if flag is None:
        raise PolicyViolationError(f"Tool sconosciuto: '{tool}'")
    if not getattr(policy, flag):
        raise PolicyViolationError(f"Policy nega l'accesso a: '{tool}'")


# ── Audit ─────────────────────────────────────────────────────────────────────

class AuditLogger:
    def __init__(self, log_path: str = "audit.jsonl") -> None:
        self.log_path = Path(log_path)

    def log(self, event: str, payload: dict[str, Any]) -> None:
        record = {
            "ts": datetime.now(UTC).isoformat(),
            "event": event,
            **payload,
        }
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        # stampa anche a schermo per vedere cosa succede in VS Code
        print(f"  [AUDIT] {event} — {payload}")
