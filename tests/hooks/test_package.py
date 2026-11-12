"""Contrato do pacote: registro dos hooks, só biblioteca padrão, sem termos de stack, sem cópias que divergem."""

import ast
import importlib.util
import json
import re
import sys
import unittest

from tests.hooks._util import HOOK_SCRIPTS, PHASE_CLI, REPO

MANIFEST = REPO / ".apm" / "hooks" / "harness.json"
TEMPLATE_PROJECT = REPO / ".apm" / "templates" / "harness.config.json"
TEMPLATE_SKILL = REPO / ".apm" / "skills" / "install-dev-harness" / "templates" / "harness.config.json.template"
TERMOS_PROIBIDOS = re.compile(r"cowboy|cobol|cobc|calculadora", re.IGNORECASE)


class ManifestTest(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))["hooks"]

    def test_eventos_registrados(self):
        self.assertEqual(set(self.manifest), {"SessionStart", "PreToolUse", "Stop"})

    def test_pre_tool_use_tem_os_dois_matchers(self):
        matchers = sorted(entry["matcher"] for entry in self.manifest["PreToolUse"])
        self.assertEqual(matchers, ["Bash", "Write|Edit|NotebookEdit"])

    def test_cada_comando_aponta_para_um_script_que_existe(self):
        for event, entries in self.manifest.items():
            for entry in entries:
                with self.subTest(event=event, comando=entry["command"]):
                    self.assertEqual(entry["type"], "command")
                    found = re.search(r"\$\{PLUGIN_ROOT\}/\.apm/hooks/scripts/([\w.-]+\.py)", entry["command"])
                    self.assertIsNotNone(found, "o comando deve usar ${PLUGIN_ROOT}/.apm/hooks/scripts/")
                    self.assertTrue((HOOK_SCRIPTS / found.group(1)).exists())

    def test_timeout_do_stop_cobre_o_padrao_dos_sensores(self):
        stop = self.manifest["Stop"][0]["timeout"]
        self.assertGreater(stop, 50)


class ScriptsTest(unittest.TestCase):
    def scripts(self):
        return sorted(HOOK_SCRIPTS.glob("*.py"))

    def test_so_biblioteca_padrao_ou_o_helper(self):
        for script in self.scripts():
            tree = ast.parse(script.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [alias.name.split(".")[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    names = [node.module.split(".")[0]]
                for name in names:
                    with self.subTest(script=script.name, importa=name):
                        self.assertTrue(name in sys.stdlib_module_names or name == "_common")

    def test_sem_termos_de_stack_ou_do_projeto_de_origem(self):
        for path in sorted((REPO / ".apm" / "hooks").rglob("*")):
            if path.is_file():
                with self.subTest(arquivo=str(path.relative_to(REPO))):
                    self.assertIsNone(TERMOS_PROIBIDOS.search(path.read_text(encoding="utf-8")))

    def test_modulos_sao_sintaticamente_validos_e_tem_docstring(self):
        for script in self.scripts():
            with self.subTest(script=script.name):
                self.assertTrue(ast.get_docstring(ast.parse(script.read_text(encoding="utf-8"))))


class CopiasTest(unittest.TestCase):
    def test_phase_cli_tem_uma_unica_versao(self):
        fonte = PHASE_CLI.read_text(encoding="utf-8")
        for copia in (REPO / "scripts" / "harness" / "phase_cli.py",
                      REPO / ".apm" / "skills" / "install-dev-harness" / "templates" / "phase_cli.py"):
            with self.subTest(copia=str(copia.relative_to(REPO))):
                self.assertEqual(copia.read_text(encoding="utf-8"), fonte)


class ModelosDeConfiguracaoTest(unittest.TestCase):
    def load(self, path):
        text = path.read_text(encoding="utf-8")
        text = text.replace("{{RULEBOOK_FILE}}", "CLAUDE.md").replace("{{PLANNING_PREFIXES}}", "[]").replace("{{CODE_PREFIXES}}", "[]")
        return json.loads(text)

    def test_campos_de_sensor_nos_dois_modelos(self):
        for path in (TEMPLATE_PROJECT, TEMPLATE_SKILL):
            with self.subTest(modelo=path.name):
                config = self.load(path)
                self.assertEqual(config["sensors_command"], "")
                self.assertEqual(config["sensors_timeout_seconds"], 50)

    def test_raizes_extras_vazias_por_padrao_nos_modelos(self):
        for path in (TEMPLATE_PROJECT, TEMPLATE_SKILL):
            with self.subTest(modelo=path.name):
                self.assertEqual(self.load(path)["allowed_write_roots"], [])

    def test_padroes_dos_modelos_acompanham_os_embutidos_do_guarda(self):
        spec = importlib.util.spec_from_file_location("bashguard", HOOK_SCRIPTS / "pre-tool-bash-guard.py")
        sys.path.insert(0, str(HOOK_SCRIPTS))
        try:
            guard = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(guard)
        finally:
            sys.path.remove(str(HOOK_SCRIPTS))
        embutidos = [entry["pattern"] for entry in guard.DEFAULT_BLOCKED]
        for path in (TEMPLATE_PROJECT, TEMPLATE_SKILL, REPO / "harness.config.json"):
            with self.subTest(arquivo=str(path.relative_to(REPO))):
                self.assertEqual([e["pattern"] for e in self.load(path)["blocked_bash_patterns"]], embutidos)

    def test_nenhum_modelo_aponta_para_guia_de_pre_commit_inexistente(self):
        for path in (TEMPLATE_PROJECT, TEMPLATE_SKILL):
            with self.subTest(modelo=path.name):
                paths = [guide["path"] for guide in self.load(path).get("guide_files", [])]
                self.assertNotIn(".pre-commit-config.yaml", paths)

    def test_padrao_de_branch_so_bloqueia_delecao_forcada(self):
        for path in (TEMPLATE_PROJECT, TEMPLATE_SKILL):
            with self.subTest(modelo=path.name):
                patterns = [e["pattern"] for e in self.load(path)["blocked_bash_patterns"] if "branch" in e["pattern"]]
                self.assertEqual(len(patterns), 1)
                regex = re.compile(patterns[0], re.IGNORECASE)
                self.assertIsNotNone(regex.search("git branch -D velha"))
                self.assertIsNone(regex.search("git branch -vv"))
                self.assertIsNone(regex.search("git branch -a"))


if __name__ == "__main__":
    unittest.main()
