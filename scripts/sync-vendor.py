#!/usr/bin/env python3
"""Regenera as skills/prompts vendorizadas de OpenSpec e OpenSPDD em .apm/.

Roda `openspec init` e `openspdd generate` num repositório temporário e copia
o resultado para a estrutura do APM:

    openspec  -> .apm/skills/openspec-*/SKILL.md  e  .apm/prompts/opsx-*.prompt.md
    openspdd  -> .apm/prompts/spdd-*.prompt.md

Uso: python3 scripts/sync-vendor.py
Registra as versões usadas em vendor.json. Revise o diff antes de commitar.
"""

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".apm" / "skills"
PROMPTS = ROOT / ".apm" / "prompts"
# Skill autoral do repo que casa com o glob openspec-* mas não é vendorizada.
LOCAL_SKILLS = {"openspec-workflow"}


def run(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"falhou: {' '.join(cmd)}\n{result.stdout}{result.stderr}")
    return result.stdout.strip()


def normalize_commands(path: Path) -> None:
    # Via APM os comandos dos dois hosts são /opsx-<nome> (sem o ":" do OpenSpec/Claude).
    path.write_text(path.read_text(encoding="utf-8").replace("/opsx:", "/opsx-"), encoding="utf-8")


def spdd_to_prompt(source: Path) -> str:
    text = source.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n(.*)", text, re.DOTALL)
    if not match:
        sys.exit(f"frontmatter inesperado em {source.name}")
    meta = dict(
        line.split(": ", 1) for line in match.group(1).splitlines() if ": " in line
    )
    return (
        f"---\nname: {source.stem}\n"
        f"description: {meta['description']}\nmode: agent\n---\n{match.group(2)}"
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)
        run(["git", "init", "-q"], tmp)
        run(
            ["openspec", "init", "--tools", "claude,github-copilot",
             "--no-animation", "--no-copilot-cloud"],
            tmp,
        )
        run(["openspdd", "generate", "--all", "-f", "-t", "claude-code"], tmp)

        for old in SKILLS.glob("openspec-*/"):
            if old.name not in LOCAL_SKILLS:
                shutil.rmtree(old)
        for skill in sorted((tmp / ".claude" / "skills").glob("openspec-*")):
            shutil.copytree(skill, SKILLS / skill.name)
            normalize_commands(SKILLS / skill.name / "SKILL.md")

        for old in [*PROMPTS.glob("opsx-*.prompt.md"), *PROMPTS.glob("spdd-*.prompt.md")]:
            old.unlink()
        for prompt in sorted((tmp / ".github" / "prompts").glob("opsx-*.prompt.md")):
            shutil.copy(prompt, PROMPTS / prompt.name)
            normalize_commands(PROMPTS / prompt.name)
        for command in sorted((tmp / ".claude" / "commands").glob("spdd-*.md")):
            (PROMPTS / f"{command.stem}.prompt.md").write_text(
                spdd_to_prompt(command), encoding="utf-8"
            )

        versions = {
            "openspec": run(["openspec", "--version"], tmp),
            "openspdd": run(["openspdd", "--version"], tmp).split()[-1],
        }
    (ROOT / "vendor.json").write_text(json.dumps(versions, indent=2) + "\n", encoding="utf-8")
    print(f"Vendor sincronizado: {versions}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
