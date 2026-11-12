"""Helper comum dos hooks do harness.

Só biblioteca padrão, de propósito: os hooks rodam como processo externo, sob o
próprio interpretador, e funcionam igual para qualquer stack do projeto.

Regra de ouro: nenhuma função daqui levanta exceção por causa de entrada
inválida (configuração ou payload ausente, corrompido ou de tipo errado). Quem
chama recebe um valor padrão seguro e decide o que fazer.
"""

import json
import os
import sys
from pathlib import Path


def project_root() -> Path:
    """Raiz do projeto, independente do diretório da sessão."""
    explicit = os.environ.get("CLAUDE_PROJECT_DIR")
    if explicit:
        return Path(explicit).resolve()
    current = Path.cwd().resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current


def load_config(root: Path) -> dict:
    """Lê o harness.config.json; devolve {} se faltar, estiver corrompido ou não for um objeto."""
    config_path = Path(os.environ.get("HARNESS_CONFIG_PATH") or (root / "harness.config.json"))
    try:
        with open(config_path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError, RecursionError):
        return {}
    return data if isinstance(data, dict) else {}


def read_payload() -> dict:
    """Lê o payload do host na entrada padrão; devolve {} se vazio, inválido ou não for um objeto."""
    try:
        data = json.load(sys.stdin)
    except (OSError, ValueError, RecursionError):
        return {}
    return data if isinstance(data, dict) else {}


def cfg_list(config: dict, key: str, default: list) -> list:
    value = config.get(key)
    return value if isinstance(value, list) else default


def cfg_str(config: dict, key: str, default: str) -> str:
    value = config.get(key)
    return value if isinstance(value, str) else default


def cfg_int(config: dict, key: str, default: int, minimum: int, maximum: int) -> int:
    """Inteiro dentro de [minimum, maximum]; qualquer outra coisa vira o padrão."""
    value = config.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        return default
    return value if minimum <= value <= maximum else default


def str_items(values: list) -> list:
    """Só os itens de texto de uma lista (ignora o resto)."""
    return [item for item in values if isinstance(item, str)]


def is_inside(path: Path, root: Path) -> bool:
    """True só se path está dentro de root como diretório (nunca por prefixo de texto)."""
    try:
        Path(path).resolve().relative_to(Path(root).resolve())
    except (ValueError, OSError, RuntimeError):
        return False
    return True


def host_of(payload: dict) -> str:
    """Identifica o host pelo formato do payload: 'claude', 'copilot' ou 'desconhecido'."""
    if "tool_name" in payload or "tool_input" in payload:
        return "claude"
    if "toolName" in payload or "toolArgs" in payload:
        return "copilot"
    return "desconhecido"


def allow(payload: dict) -> None:
    """Permite a ação. O Copilot espera o JSON de decisão; o Claude Code, só código 0."""
    if host_of(payload) == "copilot":
        print(json.dumps({"permissionDecision": "allow"}))
    sys.exit(0)


def deny(payload: dict, reason: str) -> None:
    """Bloqueia no formato do host. Host desconhecido: permite (nunca trava sem saber quem pergunta)."""
    host = host_of(payload)
    if host == "claude":
        sys.stderr.write(reason + "\n")
        sys.exit(2)
    if host == "copilot":
        print(json.dumps({"permissionDecision": "deny", "permissionDecisionReason": reason}, ensure_ascii=False))
        sys.exit(0)
    sys.exit(0)


def run(main, name: str) -> None:
    """Executa o hook; qualquer erro inesperado vira 'permitir' com um aviso em stderr."""
    try:
        main()
    except Exception as error:  # noqa: BLE001 - fail-open de propósito
        sys.stderr.write(f"hook {name}: erro inesperado ({type(error).__name__}: {error}); permitindo.\n")
        sys.exit(0)
