#!/usr/bin/env python3
"""sessionStart hook — injeta o contexto do harness em toda sessão nova.

Stdlib only — veja _common.py.

Recebe o payload da sessão na entrada padrão (JSON):
  {"sessionId": "...", "cwd": "...", "source": "startup"|"resume"|"new", ...}

Escreve {"additionalContext": "..."} em stdout para prefixar o contexto da sessão.
Nunca falha por causa de configuração ou payload inválidos.
"""

import json
import subprocess
from pathlib import Path

from _common import cfg_list, cfg_str, load_config, project_root, read_payload, run

DEFAULT_PHASE_STATE_PATH = ".harness/change-phase.json"


def _phase_line(root: Path, phase_state_path: str) -> str:
    undeclared = "Fase da change: não declarada — use 'scripts/harness/phase_cli.py set' antes de implementar"
    try:
        with open(root / phase_state_path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return undeclared
    if not isinstance(data, dict):
        return "Fase da change: estado inválido — use 'scripts/harness/phase_cli.py set' antes de implementar"
    phase = data.get("phase")
    change = data.get("change_name", "")
    if not isinstance(phase, str):
        return "Fase da change: estado inválido — use 'scripts/harness/phase_cli.py set' antes de implementar"
    return f"Fase da change: {phase} ({change if isinstance(change, str) else ''})"


def _git_branch(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=3,
        )
        return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def _guide_lines(root: Path, guide_files: list) -> list:
    lines = []
    for entry in guide_files:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            continue
        label = entry.get("label") if isinstance(entry.get("label"), str) else entry["path"]
        status = "✓" if (root / entry["path"]).exists() else "✗ MISSING"
        lines.append(f"  {status}  {label}")
    return lines


def main() -> None:
    payload = read_payload()

    if payload.get("source") == "resume":
        print(json.dumps({}))
        return

    root = project_root()
    config = load_config(root)
    phase_state_path = cfg_str(config, "phase_state_path", DEFAULT_PHASE_STATE_PATH)
    guides = _guide_lines(root, cfg_list(config, "guide_files", []))

    context = f"""
=== Harness de Segurança ===

Branch atual: {_git_branch(root)}
{_phase_line(root, phase_state_path)}

Guias verificados:
{chr(10).join(guides) if guides else "  (nenhum configurado em harness.config.json)"}

Regras críticas (não negociáveis):
• Fase 'proposal' → escrita em código BLOQUEADA por hook (só artefatos de planejamento)
• git push → BLOQUEADO por hook — peça confirmação explícita ao usuário primeiro
• git reset --hard / rm -rf → BLOQUEADOS — peça confirmação explícita
• Credenciais → nunca como literal de string; use variáveis de ambiente
• Encerrar a sessão roda o comando de sensores do projeto (sensors_command), se houver

Consulte o arquivo raiz do agente para todas as regras antes de implementar código.
""".strip()

    print(json.dumps({"additionalContext": context}))


if __name__ == "__main__":
    run(main, "session-start")
