"""
main.py — entrypoint CLI per MiniSentinel.

Uso:
    python main.py                              # lista i documenti
    python main.py read nota.txt                # legge nota.txt
    python main.py read ../secrets.txt          # BLOCCATO: path traversal
    python main.py run delete_file              # BLOCCATO: tool non consentito
"""
from __future__ import annotations

import sys

from agent import DEFAULT_IDENTITY, AgentPolicy, check_permission, PolicyViolationError, AuditLogger
from tools import list_documents, read_document

TOOL_MAP = {
    "list_documents": list_documents,
    "read_document":  read_document,
}

_policy = AgentPolicy()
_audit  = AuditLogger()


def run(tool_name: str, **kwargs) -> None:
    print(f"\n── Esecuzione: '{tool_name}' ──")

    # Gate 1 — Identity
    if not DEFAULT_IDENTITY.can_use(tool_name):
        _audit.log("IDENTITY_DENIED", {"tool": tool_name})
        print(f"[BLOCCATO] '{tool_name}' non è nella whitelist dell'agente.")
        return

    # Gate 2 — Policy
    try:
        check_permission(_policy, tool_name)
    except PolicyViolationError as exc:
        _audit.log("POLICY_DENIED", {"tool": tool_name, "reason": str(exc)})
        print(f"[BLOCCATO] Policy: {exc}")
        return

    # Dispatch
    fn = TOOL_MAP[tool_name]
    _audit.log("TOOL_CALL", {"tool": tool_name, "args": kwargs})

    try:
        result = fn(**kwargs)
        _audit.log("TOOL_OK", {"tool": tool_name})
        print(f"\nRisultato:\n{result}")
    except (FileNotFoundError, PermissionError, ValueError) as exc:
        _audit.log("TOOL_ERROR", {"tool": tool_name, "error": str(exc)})
        print(f"[ERRORE] {exc}")


def main() -> None:
    args = sys.argv[1:]

    if not args or args[0] == "list":
        run("list_documents")

    elif args[0] == "read":
        if len(args) < 2:
            print("Uso: python main.py read <nomefile>")
            sys.exit(1)
        run("read_document", filename=args[1])

    elif args[0] == "run":
        # test esplicito: prova a chiamare un tool non consentito
        tool = args[1] if len(args) > 1 else "delete_file"
        run(tool)

    else:
        print("Comandi: list | read <file> | run <tool>")


if __name__ == "__main__":
    main()
