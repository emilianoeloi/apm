"""Utilitários dos testes de hooks: chama os scripts como processo, como os hosts fazem."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK_SCRIPTS = REPO / ".apm" / "hooks" / "scripts"
PHASE_CLI = REPO / ".apm" / "scripts" / "harness" / "phase_cli.py"


class ProjectCase(unittest.TestCase):
    """Cada teste ganha uma pasta de projeto temporária (e uma pasta-mãe, para casos de pasta irmã)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.parent = Path(self._tmp.name).resolve()
        self.root = self.parent / "proj"
        self.root.mkdir()
        self.extra_env = {}

    def write_config(self, content) -> None:
        text = content if isinstance(content, str) else json.dumps(content)
        (self.root / "harness.config.json").write_text(text, encoding="utf-8")

    def set_phase(self, phase: str, change: str = "teste") -> None:
        state = self.root / ".harness"
        state.mkdir(exist_ok=True)
        (state / "change-phase.json").write_text(json.dumps({"phase": phase, "change_name": change}), encoding="utf-8")

    def env(self) -> dict:
        env = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_PROJECT_DIR", "HARNESS_CONFIG_PATH")}
        env["CLAUDE_PROJECT_DIR"] = str(self.root)
        env.update(self.extra_env)
        return env

    def run_script(self, script: Path, stdin, args=None, timeout: int = 30) -> subprocess.CompletedProcess:
        text = stdin if isinstance(stdin, str) else json.dumps(stdin)
        return subprocess.run(
            [sys.executable, str(script), *(args or [])],
            input=text,
            capture_output=True,
            text=True,
            env=self.env(),
            cwd=str(self.root),
            timeout=timeout,
        )

    def run_hook(self, name: str, stdin, timeout: int = 30) -> subprocess.CompletedProcess:
        return self.run_script(HOOK_SCRIPTS / name, stdin, timeout=timeout)

    def assertNoTraceback(self, result: subprocess.CompletedProcess) -> None:
        self.assertNotIn("Traceback", result.stderr)
