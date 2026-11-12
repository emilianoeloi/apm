"""Guarda da configuração de release: pré-lançamento ativo, nenhuma versão fixa pendente, publicação humana."""

import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CONFIG = REPO / "release-please-config.json"
MANIFEST = REPO / ".release-please-manifest.json"
WORKFLOW = REPO / ".github" / "workflows" / "release-please.yml"
APM_YML = REPO / "apm.yml"


def package() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))["packages"]["."]


class PreLancamentoTest(unittest.TestCase):
    def test_estrategia_de_pre_lancamento(self):
        pkg = package()
        self.assertEqual(pkg.get("versioning"), "prerelease")
        self.assertIs(pkg.get("prerelease"), True)

    def test_tipo_gera_exatamente_alpha_1_na_primeira_vez(self):
        # O tipo vira o primeiro sufixo: 0.3.1 + mudança incompatível = 1.0.0-alpha.1; depois o número sobe sozinho.
        self.assertEqual(package().get("prerelease-type"), "alpha.1")

    def test_nenhuma_versao_fixa_pendente(self):
        # release-as esquecido repetiria a mesma versão em toda proposta seguinte.
        self.assertNotIn("release-as", package())
        self.assertNotIn("release-as", json.loads(CONFIG.read_text(encoding="utf-8")))


class TagEArquivosTest(unittest.TestCase):
    def test_tag_com_v_e_sem_componente(self):
        pkg = package()
        self.assertIs(pkg.get("include-v-in-tag"), True)
        self.assertIs(pkg.get("include-component-in-tag"), False)

    def test_apm_yml_acompanha_a_versao(self):
        self.assertIn("apm.yml", package().get("extra-files", []))

    def test_manifesto_tem_a_chave_do_pacote(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertIn(".", manifest)
        self.assertRegex(manifest["."], r"^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?$")

    def test_versao_do_apm_yml_igual_a_do_manifesto(self):
        found = re.search(r"^version:\s*(\S+)\s*$", APM_YML.read_text(encoding="utf-8"), re.MULTILINE)
        self.assertIsNotNone(found)
        self.assertEqual(found.group(1), json.loads(MANIFEST.read_text(encoding="utf-8"))["."])

    def test_configuracao_continua_sendo_json_valido_com_schema(self):
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertIn("release-please", config["$schema"])
        self.assertIn(".", config["packages"])


class PublicarEAtoHumanoTest(unittest.TestCase):
    def setUp(self):
        self.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_roda_o_release_please_em_push_na_main(self):
        self.assertIn("googleapis/release-please-action", self.workflow)
        self.assertRegex(self.workflow, r"push:\s*\n\s*branches:\s*\[main\]")

    def test_nenhuma_mesclagem_automatica(self):
        for forbidden in ("auto-merge", "automerge", "gh pr merge", "--auto", "enablePullRequestAutoMerge"):
            with self.subTest(termo=forbidden):
                self.assertNotIn(forbidden, self.workflow)


if __name__ == "__main__":
    unittest.main()
