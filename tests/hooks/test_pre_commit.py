"""Pre-commit genérico: roda o sensors_command do projeto e nunca trava sem ele."""

import subprocess

from tests.hooks._util import REPO, ProjectCase

PRE_COMMIT = REPO / ".apm" / "scripts" / "git-hooks" / "pre-commit"


class PreCommitTest(ProjectCase):
    def setUp(self):
        super().setUp()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)

    def commit_hook(self, cwd=None):
        return subprocess.run(
            ["sh", str(PRE_COMMIT)],
            capture_output=True,
            text=True,
            env=self.env(),
            cwd=str(cwd or self.root),
            timeout=30,
        )

    def test_sem_configuracao_passa(self):
        result = self.commit_hook()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_comando_vazio_passa(self):
        self.write_config({"sensors_command": ""})
        self.assertEqual(self.commit_hook().returncode, 0)

    def test_comando_so_com_espacos_passa(self):
        self.write_config({"sensors_command": "   "})
        self.assertEqual(self.commit_hook().returncode, 0)

    def test_configuracao_corrompida_ou_que_nao_e_objeto_passa(self):
        for text in ("{ nope", "[1, 2]", "null", '{"sensors_command": 5}'):
            with self.subTest(text=text):
                self.write_config(text)
                self.assertEqual(self.commit_hook().returncode, 0)

    def test_sensor_que_passa_deixa_commitar(self):
        self.write_config({"sensors_command": "exit 0"})
        self.assertEqual(self.commit_hook().returncode, 0)

    def test_sensor_que_falha_aborta_o_commit_e_mostra_a_saida(self):
        self.write_config({"sensors_command": "echo sensor-quebrou; exit 4"})
        result = self.commit_hook()
        self.assertEqual(result.returncode, 1)
        self.assertIn("sensor-quebrou", result.stdout + result.stderr)
        self.assertIn("4", result.stderr)

    def test_sensor_roda_na_raiz_mesmo_de_um_subdiretorio(self):
        self.write_config({"sensors_command": "pwd > cwd.txt"})
        sub = self.root / "a" / "b"
        sub.mkdir(parents=True)
        self.assertEqual(self.commit_hook(cwd=sub).returncode, 0)
        self.assertEqual((self.root / "cwd.txt").read_text().strip(), str(self.root))


if __name__ == "__main__":
    import unittest

    unittest.main()
