"""Proteção estática do skill acceptance-from-spec: frontmatter, trechos obrigatórios, neutralidade e cópias.

Prova o texto, não o comportamento do modelo (isso se prova no projeto de prova).
"""

import re
import unittest
from pathlib import Path

from tests.agents.test_contract import AGENTS, STACK_TERMS

REPO = Path(__file__).resolve().parents[2]
NAME = "acceptance-from-spec"
SOURCE = REPO / ".apm" / "skills" / NAME / "SKILL.md"
COPIES = (
    REPO / ".claude" / "skills" / NAME / "SKILL.md",
    REPO / ".agents" / "skills" / NAME / "SKILL.md",
)
ORIGIN_TERMS = re.compile(r"cowboy|cobol|cobc|calculadora", re.IGNORECASE)
MARKER = re.compile(r"^Spec: .+ / .+ / .+$", re.MULTILINE)
MAX_LINES = 150

REQUIRED = (
    "Spec:", "Cenário:", "vermelho", "verde", "contagem de falhas", "sensors_command",
    "harness.config.json", "Pare", "aprovação", "não instal", "code_prefixes",
    "BLOQUEADO", "pendente", "pulou", "sem stubs",
    "não se aplica",  # ressalva 2: change sem Cenário
    "seguem normalmente",  # ressalva 1: Operations sem cenário
    "nada escrito",  # ressalva 1: formato do bloqueio
)
CODER_REQUIRED = (
    "BLOQUEADO", "nada escrito", "aguardando ferramenta", "seguem normalmente",
    "pendente", "sensors_command",
)


def read_skill() -> str:
    return SOURCE.read_text(encoding="utf-8")


def frontmatter(text: str) -> dict:
    assert text.startswith("---\n"), "o frontmatter deve abrir na primeira linha"
    head = text[4:].partition("\n---\n")[0]
    front = {}
    for line in head.splitlines():
        if line.strip() and not line.startswith((" ", "#")):
            key, _, value = line.partition(":")
            front[key.strip()] = value.strip()
    return front


class SkillFonteTest(unittest.TestCase):
    def test_skill_existe(self):
        self.assertTrue(SOURCE.exists(), f"skill ausente: {SOURCE.relative_to(REPO)}")

    def test_frontmatter(self):
        front = frontmatter(read_skill())
        self.assertEqual(front.get("name"), SOURCE.parent.name)
        self.assertEqual(front.get("name"), NAME)
        self.assertTrue(front.get("description"), "description obrigatória")
        self.assertTrue(front.get("license"), "license obrigatória")

    def test_trechos_obrigatorios(self):
        text = read_skill()
        for needle in REQUIRED:
            with self.subTest(trecho=needle):
                self.assertIn(needle, text)

    def test_neutralidade(self):
        text = read_skill()
        for label, regex in (("stack", STACK_TERMS), ("origem", ORIGIN_TERMS)):
            with self.subTest(termos=label):
                self.assertIsNone(regex.search(text), regex.search(text))

    def test_tamanho(self):
        self.assertLessEqual(len(read_skill().splitlines()), MAX_LINES)

    def test_exemplo_do_marcador_casa_com_o_regex_canonico(self):
        self.assertRegex(read_skill(), MARKER)

    def test_marcador_nao_casa_sem_os_tres_campos_ou_com_campo_vazio(self):
        for line in (
            "Spec: cap / req",
            "Spec: cap",
            "Spec:  /  / ",
            "Spec: cap /  / titulo",
            "Spec:  / req / titulo",
            "Spec: cap / req / ",
        ):
            with self.subTest(linha=line):
                self.assertIsNone(MARKER.search(line))

    def test_marcador_casa_com_tres_campos(self):
        self.assertIsNotNone(MARKER.search("Spec: cap / req / titulo"))

    def test_descricao_sem_acento_errado(self):
        self.assertNotIn("pára", read_skill())


class CopiasImplantadasTest(unittest.TestCase):
    def test_copias_identicas_a_fonte(self):
        for deployed in COPIES:
            with self.subTest(copia=str(deployed.relative_to(REPO))):
                self.assertTrue(deployed.exists(), "não implantado")
                self.assertEqual(deployed.read_text(encoding="utf-8"), read_skill())


class CoderCitaOSkillTest(unittest.TestCase):
    def test_coder_cita_o_skill_antes_do_item_das_operations(self):
        body = (AGENTS / "sdlc-coder.agent.md").read_text(encoding="utf-8")
        cited = body.find(f"`{NAME}`")
        operations = body.find("`spdd-generate`")
        self.assertGreaterEqual(cited, 0, "coder não cita o skill")
        self.assertLess(cited, operations)

    def test_coder_traz_formato_bloqueado_e_operations_sem_cenario(self):
        body = (AGENTS / "sdlc-coder.agent.md").read_text(encoding="utf-8")
        for needle in CODER_REQUIRED:
            with self.subTest(trecho=needle):
                self.assertIn(needle, body)


if __name__ == "__main__":
    unittest.main()
