#!/usr/bin/env python3
"""preToolUse hook — bloqueia comandos de shell destrutivos e, em 'proposal', os que mutam o repositório.

Stdlib only — veja _common.py.

Payload (um dos dois formatos):
  Claude Code: {"tool_name": "Bash", "tool_input": {"command": "..."}, ...}
  Copilot:     {"toolName": "bash", "toolArgs": {"command": "..."}, ...}

Decisão no formato de cada host (veja _common.deny): Claude Code recebe código 2 e
o motivo em stderr; o Copilot recebe o JSON de decisão em stdout.

Config: "harness.config.json" na raiz do projeto (blocked_bash_patterns,
proposal_blocked_bash_patterns, phase_state_path). Sem configuração, ou com
configuração inválida, valem os bloqueios embutidos abaixo; só os checks que
dependem da configuração (fase 'proposal') são desligados.
"""

import json
import re
import sys
from pathlib import Path

from _common import allow, cfg_list, cfg_str, deny, load_config, project_root, read_payload, run

DEFAULT_PHASE_STATE_PATH = ".harness/change-phase.json"

# Posição de comando: início do texto, ou logo depois de ; & | quebra de linha ou $(, com '(' e 'sudo' opcionais.
# Assim 'git push' só bloqueia quando é um comando; citado em texto (echo, mensagem de commit, corpo de PR em
# Markdown com crases, grep) não. Limites conhecidos: formas como 'env X=1 git push', 'git -C dir push' ou
# substituição por crases não são detectadas — o harness é uma rede de segurança contra deslizes do agente,
# não um sandbox.
_CMD = r"(?:^|[;&|\n]|\$\()\s*\(?\s*(?:sudo\s+)?"

DEFAULT_BLOCKED = [
    {"pattern": _CMD + r"git\s+push\b", "reason": "git push requer confirmação explícita do usuário."},
    {"pattern": _CMD + r"git\s+reset\s+--hard\b", "reason": "git reset --hard é destrutivo — peça confirmação explícita."},
    {"pattern": _CMD + r"git\s+clean\s+-[a-z]*f", "reason": "git clean -f é destrutivo — peça confirmação explícita."},
    # (?-i:D): só o D maiúsculo; sem isso a busca sem diferenciar caixa bloquearia 'git branch -a' e '-vv'.
    {"pattern": _CMD + r"git\s+branch\s+-[a-zA-Z]*(?-i:D)", "reason": "deleção forçada de branch requer confirmação explícita."},
    {"pattern": _CMD + r"rm\s+-[a-z]*r[a-z]*f\b", "reason": "rm -rf é destrutivo — use deleções explícitas ou git rm."},
    {"pattern": r"(>+|tee)\s+\.env\b", "reason": "escrita em .env é bloqueada — credenciais não devem ser commitadas."},
]


def _entries(values: list) -> list:
    """Só as entradas utilizáveis: dicionários com 'pattern' de texto."""
    return [entry for entry in values if isinstance(entry, dict) and isinstance(entry.get("pattern"), str)]


def _matches(pattern: str, command: str) -> bool:
    try:
        return re.search(pattern, command, re.IGNORECASE) is not None
    except re.error:
        return False  # regex inválida na configuração nunca derruba o hook


def _extract_command(payload: dict) -> str:
    for container_key in ("toolArgs", "tool_input"):
        container = payload.get(container_key)
        if isinstance(container, dict):
            value = container.get("command")
            if isinstance(value, str) and value:
                return value
    return ""


def _read_phase(root: Path, phase_state_path: str) -> "str | None":
    try:
        with open(root / phase_state_path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    phase = data.get("phase")
    return phase if isinstance(phase, str) else None


def main() -> None:
    payload = read_payload()
    command = _extract_command(payload)
    if not command:
        allow(payload)

    root = project_root()
    config = load_config(root)

    for entry in _entries(cfg_list(config, "blocked_bash_patterns", DEFAULT_BLOCKED)):
        if _matches(entry["pattern"], command):
            reason = entry.get("reason")
            deny(payload, reason if isinstance(reason, str) and reason else f"Comando bloqueado pelo harness: {entry['pattern']}")

    phase_state_path = cfg_str(config, "phase_state_path", DEFAULT_PHASE_STATE_PATH)
    proposal_blocked = _entries(cfg_list(config, "proposal_blocked_bash_patterns", []))

    if proposal_blocked and _read_phase(root, phase_state_path) == "proposal":
        for entry in proposal_blocked:
            if _matches(entry["pattern"], command):
                label = entry.get("label") if isinstance(entry.get("label"), str) else entry["pattern"]
                deny(
                    payload,
                    f"{label} é bloqueado na fase 'proposal' — a proposta não muta o "
                    "repositório. Conclua o handoff e promova a change para 'apply'.",
                )

    allow(payload)


if __name__ == "__main__":
    run(main, "pre-tool-bash-guard")
