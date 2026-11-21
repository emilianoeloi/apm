#!/usr/bin/env python3
"""Sensor de Gherkin: confere o bloco Gherkin de todo requisito efetivo das specs do OpenSpec.

Uso:
  gherkin-sensor.py [--root DIR]      CLI: 0 se tudo conforme, 2 com uma linha por violação em stderr.
  gherkin-sensor.py --on-validate     Hook PostToolUse: lê o payload do host na entrada padrão e só
                                      roda o sensor se o comando contém `openspec validate`.

Raiz do projeto: --root, depois CLAUDE_PROJECT_DIR, depois a pasta com `.git` acima do diretório
atual. Sem `openspec/` na raiz, sai 0 avisando em stderr. Só lê arquivos; nunca escreve.
Saída: somente os códigos 0 e 2. No modo CLI, erro inesperado vira 2; no modo hook, fail-open.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _common  # noqa: E402
import _gherkin  # noqa: E402

VALIDATE = re.compile(r"\bopenspec\s+validate\b")


def violations(root: Path) -> list:
    """Linhas de violação (`gherkin: <capability> / Requirement: <nome> [change X]: <motivo>`)."""
    lines = []
    for item in _gherkin.effective_requirements(root):
        reasons = [item.error] if item.error else _gherkin.validate(item.body)
        where = "" if item.origin == _gherkin.PRINCIPAL else f" [change {item.origin}]"
        for reason in reasons:
            lines.append(f"gherkin: {item.capability} / Requirement: {item.name}{where}: {reason}")
    return lines


def check(root: Path) -> int:
    """Roda o sensor na raiz; imprime as violações e devolve 0 ou 2."""
    if not (root / "openspec").is_dir():
        sys.stderr.write(f"gherkin: sem openspec/ em {root}; não há specs para verificar.\n")
        return 0
    found = violations(root)
    if not found:
        return 0
    sys.stderr.write("\n".join(found) + f"\ngherkin: {len(found)} violação(ões) de formato do bloco Gherkin.\n")
    return 2


def command_of(payload: dict) -> str:
    """Comando do Bash no payload do Claude (`tool_input.command`) ou do Copilot (`toolArgs`)."""
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict) and isinstance(tool_input.get("command"), str):
        return tool_input["command"]
    args = payload.get("toolArgs")
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except (ValueError, RecursionError):
            return ""
    if isinstance(args, dict) and isinstance(args.get("command"), str):
        return args["command"]
    return ""


def hook_main() -> None:
    payload = _common.read_payload()
    if VALIDATE.search(command_of(payload)):
        sys.exit(check(_common.project_root()))
    sys.exit(0)


def cli_main(argv: list) -> int:
    root = None
    if "--root" in argv:
        index = argv.index("--root")
        if index + 1 < len(argv):
            root = Path(argv[index + 1]).resolve()
    try:
        return check(root or _common.project_root())
    except Exception as error:  # noqa: BLE001 - sensor que não roda não pode declarar aprovação
        sys.stderr.write(f"gherkin: erro inesperado ({type(error).__name__}: {error}).\n")
        return 2


if __name__ == "__main__":
    if "--on-validate" in sys.argv[1:]:
        _common.run(hook_main, "gherkin-sensor")
    else:
        sys.exit(cli_main(sys.argv[1:]))
