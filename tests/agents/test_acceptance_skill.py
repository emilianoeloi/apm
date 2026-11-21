"""Proteção estática do skill acceptance-from-spec: frontmatter, trechos obrigatórios, neutralidade e cópias.

Prova o texto, não o comportamento do modelo (isso se prova no projeto de prova).
"""

import re
import unittest
from pathlib import Path

from tests.agents.test_contract import AGENTS, STACK_TERMS
from tests.hooks._util import HOOK_SCRIPTS, ProjectCase

REPO = Path(__file__).resolve().parents[2]
NAME = "acceptance-from-spec"
SOURCE = REPO / ".apm" / "skills" / NAME / "SKILL.md"
COPIES = (
    REPO / ".claude" / "skills" / NAME / "SKILL.md",
    REPO / ".agents" / "skills" / NAME / "SKILL.md",
)
ORIGIN_TERMS = re.compile(r"cowboy|cobol|cobc|calculadora", re.IGNORECASE)
TAG = "Spec"
EXTRA_TAG = "Extra"
README = REPO / "README.md"
TRACE = HOOK_SCRIPTS / "spec-trace.py"
MARKER = re.compile(rf"^{TAG}: .+ / .+ / .+$", re.MULTILINE)
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
            f"{TAG}: cap / req",
            f"{TAG}: cap",
            f"{TAG}:  /  / ",
            f"{TAG}: cap /  / titulo",
            f"{TAG}:  / req / titulo",
            f"{TAG}: cap / req / ",
        ):
            with self.subTest(linha=line):
                self.assertIsNone(MARKER.search(line))

    def test_marcador_casa_com_tres_campos(self):
        self.assertIsNotNone(MARKER.search(f"{TAG}: cap / req / titulo"))

    def test_descricao_sem_acento_errado(self):
        self.assertNotIn("pára", read_skill())


class CopiasImplantadasTest(unittest.TestCase):
    # Extra: acceptance-from-spec / Afinação só por adição e dentro do teto / Cópias do skill idênticas à fonte
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


class AfinacaoDoSkillTest(unittest.TestCase):
    """Afinação 1.1 do skill: o texto novo existe (vermelho natural: os trechos ainda não estavam lá)."""

    def assert_trechos(self, text: str, needles) -> None:
        for needle in needles:
            with self.subTest(trecho=needle):
                self.assertIn(needle, text)

    # Spec: acceptance-from-spec / Vermelho vem da asserção do cenário / Teste que passa sem o programa
    def test_falso_verde_reforcado_pelo_conteudo(self):
        self.assert_trechos(read_skill(), ("falso verde", "conteúdo", "código de saída"))

    # Extra: acceptance-from-spec / Vermelho vem da asserção do cenário / Vermelho por erro do ambiente
    def test_erro_do_ambiente_nao_e_vermelho(self):
        self.assert_trechos(read_skill(), ("erro do ambiente", "símbolo de produção"))

    # Spec: acceptance-from-spec / Cenário extra anotado sem virar órfão / Extra com comportamento distinto
    def test_extra_leva_extra_e_nunca_spec(self):
        self.assert_trechos(read_skill(), (f"{EXTRA_TAG}:", f"nunca `{TAG}:`"))

    # Spec: acceptance-from-spec / Fixture com linha Spec montada por constante / Fixture montada por constante
    def test_fixture_montada_por_constante(self):
        self.assert_trechos(read_skill(), ("por constante", "ORFAO"))

    # Spec: acceptance-from-spec / Cenário de comportamento do modelo é prova humana / Cenário que só a prova humana cobre
    def test_prova_humana_pendente_com_decisao_do_humano(self):
        self.assert_trechos(read_skill(), ("prova humana", "decisão do humano", "SEM_TESTE"))

    # Extra: acceptance-from-spec / Cenário de comportamento do modelo é prova humana / Teste que não prova o comportamento
    def test_teste_que_nao_prova_nao_liga_ao_cenario(self):
        self.assert_trechos(read_skill(), ("finja cobri-lo", f"nem o ligue por `{TAG}:`"))

    # Spec: acceptance-from-spec / Cenário herdado em requisito modificado / Herdado não exige teste novo
    def test_herdado_nao_exige_teste_novo(self):
        self.assert_trechos(read_skill(), ("herdado", "informativo", "não precisa de teste novo"))

    # Spec: acceptance-from-spec / Afinação só por adição e dentro do teto / Skill afinado cabe no teto
    def test_skill_afinado_cabe_no_teto(self):
        text = read_skill()
        self.assertIn('version: "1.1"', text)
        self.assert_trechos(text, REQUIRED)  # o REQUIRED antigo continua presente
        self.assertLessEqual(len(text.splitlines()), MAX_LINES)
        for regex in (STACK_TERMS, ORIGIN_TERMS):
            self.assertIsNone(regex.search(text), regex.search(text))


class CaracterizacaoSpecTraceTest(ProjectCase):
    """Caracterização com o spec-trace real: o script já ignora `Extra:` antes da edição (sem vermelho natural)."""

    def write(self, relative: str, content: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def trace_with(self, label: str):
        self.write(
            "openspec/changes/c1/specs/cap/spec.md",
            "## ADDED Requirements\n\n### Requirement: Req\nTexto SHALL valer.\n\n```gherkin\n"
            "Cenário: Um\n  Dado um\n  Quando dois\n  Então três\n```\n\n"
            "#### Scenario: Um\n- **WHEN** x\n- **THEN** y\n\n#### Scenario: Dois\n- **WHEN** x\n- **THEN** y\n",
        )
        self.write("tests/test_a.py", f"# {TAG}: cap / Req / Um\n# {label}: cap / Req / Dois\n")
        return self.run_script(TRACE, "", args=["--root", str(self.root), "--change", "c1"])

    # Extra: acceptance-from-spec / Cenário extra anotado sem virar órfão / Extra anotado não vira órfão
    def test_extra_anotado_nao_vira_orfao(self):
        result = self.trace_with(EXTRA_TAG)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("ORFAO", result.stdout)
        self.assertIn("COBERTO cap / Req / Um", result.stdout)
        self.assertIn("extras: 1", result.stdout)

    def test_mesma_linha_com_spec_vira_orfao(self):
        result = self.trace_with(TAG)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("ORFAO", result.stdout)

    def test_fonte_sem_linha_spec_literal_fora_de_comentario(self):
        pattern = re.compile(rf"{TAG}: .+ / .+ / .+")
        lines = Path(__file__).read_text(encoding="utf-8").splitlines()
        literal = [n for n, line in enumerate(lines, 1) if not line.lstrip().startswith("#") and pattern.search(line)]
        self.assertEqual(literal, [], f"linha com três campos fora de comentário: {literal}")


class ReadmeTest(unittest.TestCase):
    # Spec: pacote-generico / Aviso de migração para o skill afinado / Leitor de projeto na versão anterior
    def test_secao_de_aceitacao_traz_o_aviso_de_migracao(self):
        text = README.read_text(encoding="utf-8")
        start = text.index("## Testes de aceitação")
        end = text.find("\n## ", start + 1)
        section = text[start:end if end > 0 else len(text)]
        for needle in ("falso verde", f"{EXTRA_TAG}:", "por constante", "prova humana"):
            with self.subTest(trecho=needle):
                self.assertIn(needle, section)


if __name__ == "__main__":
    unittest.main()
