"""Formato do bloco Gherkin em todo requisito efetivo das specs do OpenSpec.

Requisito efetivo: spec principal com os requisitos trocados pelos `ADDED`/`MODIFIED` dos deltas ativos
(fora de `archive/`) e sem os `REMOVED`. Estático: só lê arquivos.
"""

import ast
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK_SCRIPTS = REPO / ".apm" / "hooks" / "scripts"
sys.path.insert(0, str(HOOK_SCRIPTS))

from _gherkin import effective_requirements, validate  # noqa: E402


def efetivos() -> list:
    """Lista de (capability, nome, corpo) dos requisitos efetivos deste repositório."""
    return [(r.capability, r.name, r.body) for r in effective_requirements(REPO)]


PARAGRAPH = "Texto SHALL valer.\n\n"
TAIL = "\n#### Scenario: A\n- **WHEN** x\n- **THEN** y\n"


def sample(block: str, tail: str = TAIL) -> str:
    return PARAGRAPH + block + tail


GOOD = "```gherkin\nCenário: A\n  Dado um\n  Quando dois\n  Então três\n```\n"
NEGATIVE = {
    "sem bloco": PARAGRAPH + TAIL,
    "bloco depois do cenário": PARAGRAPH + TAIL + "\n" + GOOD,
    "sem Então": sample("```gherkin\nCenário: A\n  Dado um\n  Quando dois\n```\n"),
    "Entao sem acento": sample("```gherkin\nCenário: A\n  Dado um\n  Quando dois\n  Entao três\n```\n"),
    "passos fora de ordem": sample("```gherkin\nCenário: A\n  Quando dois\n  Dado um\n  Então três\n```\n"),
    "título sem correspondência": sample("```gherkin\nCenário: Outro\n  Dado um\n  Quando dois\n  Então três\n```\n"),
    "dois blocos": sample(GOOD + "\n" + GOOD),
}


class FormatoDoBlocoTest(unittest.TestCase):
    def test_amostras_negativas_reprovam(self):
        for name, body in NEGATIVE.items():
            with self.subTest(amostra=name):
                self.assertTrue(validate(body), f"amostra aprovada indevidamente: {name}")

    def test_amostra_positiva_simples(self):
        self.assertEqual(validate(sample(GOOD)), [])

    def test_amostra_positiva_com_E_e_dois_cenarios(self):
        block = (
            "```gherkin\n# comentário\nCenário: A\n  Dado um\n  E outro\n  Quando dois\n  Então três\n  E quatro\n\n"
            "Cenário: B\n  Dado um\n  Quando dois\n  Então três\n```\n"
        )
        tail = TAIL + "\n#### Scenario: B\n- **WHEN** x\n- **THEN** y\n"
        self.assertEqual(validate(sample(block, tail)), [])

    def test_logica_vive_so_na_biblioteca(self):
        tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
        defined = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
        self.assertFalse(defined & {"validate", "effective_requirements", "parse_requirements", "parse_delta"})

    def test_leitor_acha_requisitos_efetivos(self):
        found = efetivos()
        self.assertGreaterEqual(len(found), 31)
        names = {name for _, name, _ in found}
        self.assertNotIn("Primeira publicação do 1.0.0 é um pré-lançamento", names)
        self.assertIn("Bloco Gherkin cercado sob cada requisito", names)

    def test_todo_requisito_efetivo_tem_o_bloco(self):
        for capability, name, body in efetivos():
            with self.subTest(spec=capability, requisito=name):
                self.assertEqual(validate(body), [])


if __name__ == "__main__":
    unittest.main()
