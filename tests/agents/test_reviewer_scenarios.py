"""Proteção estática da conferência de cenários no sdlc-reviewer: texto, ferramentas, neutralidade e cópias.

Prova o texto do agente e a implantação, não o comportamento do modelo (isso se prova no projeto de prova).
"""

import json
import re
import unittest
from pathlib import Path

from tests.agents.test_contract import AGENTS, CLAUDE_DEPLOY, COPILOT_DEPLOY, STACK_TERMS, split_agent, tool_set

REPO = Path(__file__).resolve().parents[2]
SOURCE = AGENTS / "sdlc-reviewer.agent.md"
SCRIPTS = REPO / ".apm" / "hooks" / "scripts"
SCRIPT_DEPLOYS = (
    REPO / ".claude" / "hooks" / "apm" / ".apm" / "hooks" / "scripts",
    REPO / ".github" / "hooks" / "scripts" / "apm" / ".apm" / "hooks" / "scripts",
)
ORIGIN_TERMS = re.compile(r"cowboy|cobol|cobc|calculadora", re.IGNORECASE)

REQUIRED = (
    "spec-trace.py", "Glob", "Spec:", "grep -F", "HERDADO", "Cenários x testes", "REPROVADO",
    "falso verde", "fonte", "vermelho não verificado",
)


def reviewer() -> str:
    return SOURCE.read_text(encoding="utf-8")


class TextoDoReviewerTest(unittest.TestCase):
    def test_trechos_obrigatorios(self):
        text = reviewer()
        for needle in REQUIRED:
            with self.subTest(trecho=needle):
                self.assertIn(needle, text)

    def test_cita_orfao(self):
        text = reviewer()
        self.assertTrue("órfã" in text or "ORFAO" in text)

    # Extra (#### Scenario: sem Cenário: no bloco, não exigido): sdlc-agent-roles / Reviewer confere cada cenário contra um teste / Ferramentas inalteradas
    def test_ferramentas_continuam_somente_leitura(self):
        front, _ = split_agent(SOURCE)
        self.assertEqual(front["tools"], "Read, Grep, Glob, Bash")
        self.assertEqual(tool_set(front), {"Read", "Grep", "Glob", "Bash"})

    def test_passo_novo_vem_antes_do_relatorio(self):
        text = reviewer()
        step = text.find("spec-trace.py")
        report = text.find("## Relatório")
        self.assertGreaterEqual(step, 0)
        self.assertGreaterEqual(report, 0)
        self.assertLess(step, report)
        self.assertGreater(text.find("Cenários x testes", report), report, "a seção deve estar em Relatório")

    def test_neutralidade(self):
        text = reviewer()
        for label, regex in (("stack", STACK_TERMS), ("origem", ORIGIN_TERMS)):
            with self.subTest(termos=label):
                self.assertIsNone(regex.search(text), regex.search(text))


    def test_saida_dois_do_script_nao_e_o_veredito(self):
        text = reviewer()
        for needle in ("saída 2", "não é o veredito", "ORFAO", "AMBIGUO"):
            with self.subTest(trecho=needle):
                self.assertIn(needle, text)


class ReadmeTest(unittest.TestCase):
    # Spec: pacote-generico / Aviso de migração para a conferência de cenários / Leitor de projeto na versão anterior
    # Prova o texto do README, não o comportamento do reviewer (o script ignora `.md`, então o vínculo é este teste).
    def test_readme_traz_a_secao_e_o_aviso_de_migracao(self):
        text = (REPO / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Conferência de cenários na revisão", text)
        for needle in ("reprova", "Cenários antigos não são exigidos", "ORFAO", "não a qualidade do teste"):
            with self.subTest(trecho=needle):
                self.assertIn(needle, text)


class CopiasImplantadasTest(unittest.TestCase):
    def test_copias_do_agente_identicas_a_fonte(self):
        for deployed in (CLAUDE_DEPLOY / "sdlc-reviewer.md", COPILOT_DEPLOY / "sdlc-reviewer.agent.md"):
            with self.subTest(copia=str(deployed.relative_to(REPO))):
                self.assertTrue(deployed.exists(), "não implantado")
                self.assertEqual(deployed.read_text(encoding="utf-8"), reviewer())

    # Spec: spec-trace / Implantação junto dos scripts do pacote / Script implantado
    def test_copias_do_script_e_da_biblioteca_identicas_a_fonte(self):
        for folder in SCRIPT_DEPLOYS:
            for name in ("spec-trace.py", "_gherkin.py"):
                with self.subTest(copia=str((folder / name).relative_to(REPO))):
                    self.assertTrue((folder / name).exists(), "não implantado")
                    self.assertEqual((folder / name).read_bytes(), (SCRIPTS / name).read_bytes())

    # Extra (#### Scenario: sem Cenário: no bloco, não exigido): spec-trace / Implantação junto dos scripts do pacote / Fora do hook e do sensor
    def test_fora_do_hook_e_do_sensor(self):
        self.assertNotIn("spec-trace", (REPO / ".apm" / "hooks" / "harness.json").read_text(encoding="utf-8"))
        config = json.loads((REPO / "harness.config.json").read_text(encoding="utf-8"))
        self.assertNotIn("spec-trace", config["sensors_command"])


if __name__ == "__main__":
    unittest.main()
