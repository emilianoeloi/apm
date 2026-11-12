"""phase_cli.py: declara e lê a fase sem quebrar com estado ou configuração inválidos."""

import json

from tests.hooks._util import PHASE_CLI, ProjectCase


class PhaseCliTest(ProjectCase):
    def cli(self, *args):
        return self.run_script(PHASE_CLI, "", args=list(args))

    def test_show_sem_estado(self):
        result = self.cli("show")
        self.assertEqual(result.returncode, 0)
        self.assertIn("não declarada", result.stdout)

    def test_set_e_show(self):
        self.assertEqual(self.cli("set", "proposal", "minha-change").returncode, 0)
        state = json.loads((self.root / ".harness" / "change-phase.json").read_text(encoding="utf-8"))
        self.assertEqual(state, {"phase": "proposal", "change_name": "minha-change"})
        result = self.cli("show")
        self.assertIn("proposal (change: minha-change)", result.stdout)

    def test_show_com_estado_corrompido_nao_quebra(self):
        (self.root / ".harness").mkdir()
        (self.root / ".harness" / "change-phase.json").write_text("{ nope", encoding="utf-8")
        result = self.cli("show")
        self.assertEqual(result.returncode, 0)
        self.assertNoTraceback(result)
        self.assertIn("estado inválido", result.stdout)

    def test_show_com_estado_que_nao_e_objeto(self):
        (self.root / ".harness").mkdir()
        (self.root / ".harness" / "change-phase.json").write_text("[1, 2]", encoding="utf-8")
        result = self.cli("show")
        self.assertEqual(result.returncode, 0)
        self.assertNoTraceback(result)

    def test_configuracao_corrompida_usa_o_caminho_padrao(self):
        self.write_config("{ nope")
        self.assertEqual(self.cli("set", "apply", "x").returncode, 0)
        self.assertTrue((self.root / ".harness" / "change-phase.json").exists())

    def test_caminho_de_estado_em_pasta_irma_e_recusado(self):
        outro = self.parent / "proj-outro"
        outro.mkdir()
        self.write_config({"phase_state_path": "../proj-outro/estado.json"})
        result = self.cli("set", "proposal", "x")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("escapa da raiz", result.stderr)
        self.assertFalse((outro / "estado.json").exists())

    def test_caminho_de_estado_com_tipo_errado_usa_o_padrao(self):
        self.write_config({"phase_state_path": 42})
        self.assertEqual(self.cli("set", "apply", "x").returncode, 0)
        self.assertTrue((self.root / ".harness" / "change-phase.json").exists())

    def test_comando_desconhecido(self):
        self.assertEqual(self.cli("voar").returncode, 2)


if __name__ == "__main__":
    import unittest

    unittest.main()
