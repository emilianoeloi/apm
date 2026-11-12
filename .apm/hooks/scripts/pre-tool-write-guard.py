#!/usr/bin/env python3
"""preToolUse hook — bloqueia escrita em arquivos sensíveis, fora do repositório ou fora da fase.

Stdlib only, de propósito: roda como processo externo, sob o próprio interpretador,
e nunca importa código do projeto — por isso funciona igual para qualquer stack.
O único código compartilhado é o _common.py, que vem no mesmo diretório.

Payload (um dos dois formatos):
  Claude Code: {"tool_name": "Write"|"Edit", "tool_input": {"file_path": "..."}, ...}
  Copilot:     {"toolName": "create"|"edit", "toolArgs": {"path": "..."}, ...}

Decisão no formato de cada host (veja _common.deny).

Config: "harness.config.json" na raiz do projeto (veja o modelo em
install-dev-harness/templates). Configuração ausente, corrompida ou de tipo errado
nunca bloqueia: só desliga a checagem por fase. Credenciais e contenção de caminho
usam padrões embutidos e valem mesmo sem configuração.
"""

import json
import os
from pathlib import Path

from _common import allow, cfg_list, cfg_str, deny, is_inside, load_config, project_root, read_payload, run, str_items

DEFAULT_PHASE_STATE_PATH = ".harness/change-phase.json"
DEFAULT_BLOCKED_FILENAMES = [".env", "service_account.json", "id_rsa", "id_ed25519"]
DEFAULT_BLOCKED_SUFFIXES = [".pem", ".p12", ".keystore", ".jks"]


def _read_phase(root: Path, phase_state_path: str) -> "tuple[str, str] | None":
    """Lê (fase, change) do estado compartilhado; ausência ou estado inválido nunca bloqueia."""
    try:
        with open(root / phase_state_path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    phase = data.get("phase")
    if not isinstance(phase, str):
        return None
    change = data.get("change_name")
    return phase, change if isinstance(change, str) else ""


def _extra_roots(config: dict) -> list:
    """Raízes extras de escrita: só caminhos absolutos (depois de expandir ~ e variáveis); o resto é ignorado."""
    roots = []
    for item in str_items(cfg_list(config, "allowed_write_roots", [])):
        expanded = Path(os.path.expandvars(os.path.expanduser(item)))
        if item and expanded.is_absolute():
            roots.append(expanded)
    return roots


def _extract_path(payload: dict) -> str:
    for container_key in ("toolArgs", "tool_input"):
        container = payload.get(container_key)
        if not isinstance(container, dict):
            continue
        for path_key in ("path", "file_path", "notebook_path"):
            value = container.get(path_key)
            if isinstance(value, str) and value:
                return value
    return ""


def main() -> None:
    payload = read_payload()
    raw_path = _extract_path(payload)
    if not raw_path:
        allow(payload)

    root = project_root()
    config = load_config(root)

    file_path = Path(raw_path)
    filename = file_path.name

    blocked_filenames = set(str_items(cfg_list(config, "blocked_filenames", DEFAULT_BLOCKED_FILENAMES)))
    blocked_suffixes = tuple(str_items(cfg_list(config, "blocked_filename_suffixes", DEFAULT_BLOCKED_SUFFIXES)))

    if filename in blocked_filenames or (blocked_suffixes and filename.endswith(blocked_suffixes)):
        deny(
            payload,
            f"Escrita em '{filename}' é bloqueada — credenciais não devem ser armazenadas no repositório.",
        )

    try:
        resolved = (root / file_path).resolve()
    except (OSError, RuntimeError):
        resolved = None  # não resolveu: deixa a ferramenta do projeto lidar com isso

    if resolved is not None and not is_inside(resolved, root):
        # Fora da raiz só passa por opt-in: 'allowed_write_roots' (diretórios absolutos, ex.: pastas temporárias).
        # Não vale para credenciais (já bloqueadas acima) e não sujeita o caminho à fase 'proposal'.
        if any(is_inside(resolved, extra) for extra in _extra_roots(config)):
            allow(payload)
        deny(
            payload,
            f"O caminho '{raw_path}' escapa da raiz do repositório — path traversal bloqueado pelo harness de segurança.",
        )

    # Fase 'proposal': só artefatos de planejamento podem ser escritos.
    planning_prefixes = tuple(str_items(cfg_list(config, "planning_write_prefixes", [])))
    code_prefixes = tuple(str_items(cfg_list(config, "code_prefixes", [])))
    phase_state_path = cfg_str(config, "phase_state_path", DEFAULT_PHASE_STATE_PATH)

    if planning_prefixes:
        state = _read_phase(root, phase_state_path)
        if state is not None and state[0] == "proposal":
            _phase, change_name = state
            if resolved is not None:
                relative = resolved.relative_to(root.resolve()).as_posix()
            else:
                relative = file_path.as_posix()

            if not relative.startswith(planning_prefixes):
                scope = "código" if code_prefixes and relative.startswith(code_prefixes) else "fora do escopo de planejamento"
                allowed = ", ".join(planning_prefixes)
                deny(
                    payload,
                    f"Escrita em '{relative}' bloqueada: a change '{change_name}' está na fase "
                    f"'proposal' e o caminho é {scope}. Na proposta só é permitido escrever "
                    f"artefatos de planejamento ({allowed}). Conclua o handoff e promova a "
                    "change para 'apply' antes de alterar código.",
                )

    allow(payload)


if __name__ == "__main__":
    run(main, "pre-tool-write-guard")
