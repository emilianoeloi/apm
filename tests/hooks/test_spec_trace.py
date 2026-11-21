"""Contrato do spec-trace.py: confere o vínculo cenário-teste, chamado como processo em projetos temporários.

Cada teste de cenário traz a linha de ligação (`Spec:` + trinca) em comentário. Os exemplos montados aqui
usam a constante TAG para que fixtures não virem linhas órfãs na leitura deste próprio repositório.
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from tests.hooks._util import HOOK_SCRIPTS, ProjectCase

SCRIPT = HOOK_SCRIPTS / "spec-trace.py"
TAG = "Spec"
EXCLUDED_DIRS = (
    ".git", "openspec", "spdd", ".harness", ".claude", ".github", ".agents", ".apm", "apm_modules",
    "node_modules", "vendor", "target", "build", "dist", "__pycache__", ".venv", "venv",
)


def scenario_block(scenarios) -> str:
    """Corpo de requisito: parágrafo, bloco gherkin e um `#### Scenario:` por cenário. Item: título ou (título, então)."""
    pairs = [(s, "três") if isinstance(s, str) else s for s in scenarios]
    gherkin = "".join(f"Cenário: {t}\n  Dado um\n  Quando dois\n  Então {then}\n" for t, then in pairs)
    tail = "".join(f"#### Scenario: {t}\n- **WHEN** x\n- **THEN** y\n\n" for t, _ in pairs)
    return f"Texto SHALL valer.\n\n```gherkin\n{gherkin}```\n\n{tail}"


def requirement(name: str, scenarios) -> str:
    return f"### Requirement: {name}\n{scenario_block(scenarios)}\n"


def section(kind: str, *items: str) -> str:
    return f"## {kind} Requirements\n\n" + "\n".join(items)


def link(capability: str, name: str, title: str) -> str:
    return f"{TAG}: {capability} / {name} / {title}"


def snapshot(base: Path) -> dict:
    return {str(p.relative_to(base)): p.read_bytes() for p in sorted(base.rglob("*")) if p.is_file()}


class TraceCase(ProjectCase):
    def put(self, relative: str, content) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        return path

    def principal(self, capability: str, *reqs: str) -> None:
        self.put(f"openspec/specs/{capability}/spec.md", "## Requirements\n\n" + "\n".join(reqs))

    def delta(self, capability: str, *sections: str, change: str = "c1") -> None:
        self.put(f"openspec/changes/{change}/specs/{capability}/spec.md", "\n\n".join(sections))

    def trace(self, *args: str):
        self.assertTrue(SCRIPT.exists(), f"script ausente: {SCRIPT.relative_to(HOOK_SCRIPTS.parents[2])}")
        result = self.run_script(SCRIPT, "", args=["--root", str(self.root), *args])
        self.assertNoTraceback(result)
        self.assertNotIn("can't open file", result.stderr)
        return result

    def lines(self, result) -> list:
        return [line for line in result.stdout.splitlines() if line.startswith("spec-trace: ")]

    def state_line(self, result, state: str, needle: str) -> str:
        found = [line for line in self.lines(result) if f" {state} " in line and needle in line]
        self.assertEqual(len(found), 1, f"esperava 1 linha {state} com {needle!r}; saída:\n{result.stdout}{result.stderr}")
        return found[0]

    def assertNoState(self, result, state: str, needle: str = "") -> None:
        found = [line for line in self.lines(result) if f" {state} " in line and needle in line]
        self.assertEqual(found, [], f"não esperava {state}: {found}")


class VinculoTest(TraceCase):
    # Spec: spec-trace / Script confere o vínculo cenário-teste / Cenário exigido com e sem teste
    def test_cenario_exigido_com_e_sem_teste(self):
        self.delta("cap", section("ADDED", requirement("Req", ["Um", "Dois"])))
        self.put("tests/test_a.py", "# cabeçalho\n# " + link("cap", "Req", "Um") + "\n")
        result = self.trace()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("cap / Req / Um @ tests/test_a.py:2", self.state_line(result, "COBERTO", "/ Um"))
        self.state_line(result, "SEM_TESTE", "cap / Req / Dois")

    # Extra (#### Scenario: sem Cenário: no bloco, não exigido): spec-trace / Script confere o vínculo cenário-teste / Todos cobertos
    # Extra (#### Scenario: sem Cenário: no bloco, não exigido): spec-trace / Fim do título do marcador / Marcador sozinho na linha
    def test_todos_cobertos(self):
        self.delta("cap", section("ADDED", requirement("Req", ["Um", "Dois"])))
        self.put("tests/test_a.py", f"# {link('cap', 'Req', 'Um')}\n# {link('cap', 'Req', 'Dois')}\n")
        result = self.trace()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNoState(result, "SEM_TESTE")
        self.state_line(result, "COBERTO", "/ Um")
        self.state_line(result, "COBERTO", "/ Dois")

    # Extra (#### Scenario: sem Cenário: no bloco, não exigido): spec-trace / Script confere o vínculo cenário-teste / Prefixo mais longo
    def test_prefixo_mais_longo(self):
        self.delta("cap", section("ADDED", requirement("Req", ["Caso", "Caso feliz"])))
        self.put("tests/test_a.py", f"# {link('cap', 'Req', 'Caso feliz')}\n")
        result = self.trace()
        self.assertEqual(result.returncode, 2)
        self.state_line(result, "COBERTO", "/ Caso feliz")
        self.assertNotIn("Caso @", result.stdout)
        self.state_line(result, "SEM_TESTE", "cap / Req / Caso")

    # Spec: spec-trace / Fim do título do marcador / Fechamento conhecido depois do título
    def test_fechamento_de_comentario_depois_do_titulo(self):
        self.delta("cap", section("ADDED", requirement("Req", ["Um"])))
        closers = ("*/", "-->", "--]]", "--}}", "%}", "?>", '"', "'", "`", ")", "]", "}", "#", "//")
        spaces = ("", " ", "\t", "\u00a0")
        for closing in closers:
            for space in spaces:
                with self.subTest(fechamento=closing, espaco=space):
                    self.put("tests/test_a.txt", f"/* {link('cap', 'Req', 'Um')}{space}{closing}\n")
                    result = self.trace()
                    self.assertEqual(result.returncode, 0, result.stdout)
                    self.state_line(result, "COBERTO", "/ Um")
        for tail in ('") # x', "*/ -->", "*/-->", "\r"):
            with self.subTest(resto=tail):
                self.put("tests/test_a.txt", f"/* {link('cap', 'Req', 'Um')}{tail}\n")
                result = self.trace()
                self.assertEqual(result.returncode, 0, result.stdout)
                self.state_line(result, "COBERTO", "/ Um")

    # Spec: spec-trace / Fim do título do marcador / Sufixo que não é fechamento
    def test_sufixo_que_nao_e_fechamento_vira_orfao(self):
        self.delta("cap", section("ADDED", requirement("Req", ["Caso"])))
        typos = ("Caso extra digitado errado", "Casos", "Caso2", "Caso  além")
        typos += tuple("Caso" + suffix for suffix in (
            " - feliz", "_2", ".", " (extra)", ", feliz", "#2", "'2", '"abc', ")extra", "*/x", "-->x", "//x",
            ":", ";", ",", " é",
        ))
        for typo in typos:
            with self.subTest(linha=typo):
                self.put("tests/test_a.py", f"# {link('cap', 'Req', typo)}\n")
                result = self.trace()
                self.assertEqual(result.returncode, 2, result.stdout)
                self.state_line(result, "SEM_TESTE", "cap / Req / Caso")
                self.state_line(result, "ORFAO", typo)
                self.assertNoState(result, "COBERTO")


class EscopoTest(TraceCase):
    def principal_a(self, *titles) -> None:
        self.principal("cap", requirement("Req", list(titles) or ["A"]))

    # Spec: spec-trace / Só cenário novo ou alterado é exigido / Cenário herdado de requisito modificado
    def test_cenario_herdado_nao_pesa_e_o_novo_e_exigido(self):
        self.principal_a("A")
        self.delta("cap", section("MODIFIED", requirement("Req", ["A", "B"])))
        result = self.trace()
        self.assertEqual(result.returncode, 2, result.stdout)
        self.state_line(result, "HERDADO_SEM_TESTE", "cap / Req / A")
        self.state_line(result, "SEM_TESTE", "cap / Req / B")

    def test_so_herdado_sai_zero(self):
        self.principal_a("A")
        self.delta("cap", section("MODIFIED", requirement("Req", ["A"])))
        result = self.trace()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.state_line(result, "HERDADO_SEM_TESTE", "cap / Req / A")

    def test_herdado_com_teste_sai_coberto(self):
        self.principal_a("A")
        self.delta("cap", section("MODIFIED", requirement("Req", ["A"])))
        self.put("tests/test_a.py", f"# {link('cap', 'Req', 'A')}\n")
        result = self.trace()
        self.assertEqual(result.returncode, 0)
        self.state_line(result, "COBERTO", "cap / Req / A")

    # Extra (#### Scenario: sem Cenário: no bloco, não exigido): spec-trace / Só cenário novo ou alterado é exigido / Passos alterados
    def test_passos_alterados_sao_exigidos(self):
        self.principal("cap", requirement("Req", [("A", "três")]))
        self.delta("cap", section("MODIFIED", requirement("Req", [("A", "quatro")])))
        result = self.trace()
        self.assertEqual(result.returncode, 2, result.stdout)
        self.state_line(result, "SEM_TESTE", "cap / Req / A")
        self.assertNoState(result, "HERDADO_SEM_TESTE")

    def test_renamed_segue_a_base_para_achar_o_herdado(self):
        self.principal("cap", requirement("Velho", ["A"]))
        renamed = section("RENAMED", "- FROM: `### Requirement: Velho`\n- TO: `### Requirement: Novo`\n")
        self.delta("cap", renamed, section("MODIFIED", requirement("Novo", ["A", "B"])))
        result = self.trace()
        self.assertEqual(result.returncode, 2, result.stdout)
        self.state_line(result, "HERDADO_SEM_TESTE", "cap / Novo / A")
        self.state_line(result, "SEM_TESTE", "cap / Novo / B")

    def test_modified_sem_base_exige_tudo(self):
        self.delta("cap", section("MODIFIED", requirement("Req", ["A"])))
        result = self.trace()
        self.assertEqual(result.returncode, 2)
        self.state_line(result, "SEM_TESTE", "cap / Req / A")

    def test_removed_nada_exige(self):
        self.principal_a("A")
        self.delta("cap", section("REMOVED", "### Requirement: Req\n"))
        result = self.trace()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNoState(result, "SEM_TESTE")

    # Extra (#### Scenario: sem Cenário: no bloco, não exigido): spec-trace / Só cenário novo ou alterado é exigido / Filtro por change
    def test_filtro_por_change(self):
        self.delta("cap", section("ADDED", requirement("Req", ["Um"])), change="c1")
        self.delta("outra", section("ADDED", requirement("Req", ["Dois"])), change="c2")
        result = self.trace("--change", "c1")
        self.state_line(result, "SEM_TESTE", "cap / Req / Um")
        self.assertNotIn("Dois", result.stdout)
        both = self.trace()
        self.state_line(both, "SEM_TESTE", "outra / Req / Dois")

    def test_change_inexistente_sai_dois(self):
        self.delta("cap", section("ADDED", requirement("Req", ["Um"])))
        result = self.trace("--change", "nao-existe")
        self.assertEqual(result.returncode, 2)
        self.assertIn("nao-existe", result.stderr)


class OrfaoEAmbiguoTest(TraceCase):
    # Spec: spec-trace / Marcador órfão e marcador ambíguo são apontados / Título digitado errado
    def test_titulo_errado_sai_orfao(self):
        self.delta("cap", section("ADDED", requirement("Req", ["Um"])))
        self.put("tests/test_a.py", f"x = 1\n# {link('cap', 'Req', 'Titulo errado')}\n")
        result = self.trace()
        self.assertEqual(result.returncode, 2)
        self.assertIn("tests/test_a.py:2", self.state_line(result, "ORFAO", "Titulo errado"))

    def test_cenario_removido_vira_orfao(self):
        self.principal("cap", requirement("Req", ["Um"]))
        self.delta("cap", section("REMOVED", "### Requirement: Req\n"))
        self.put("tests/test_a.py", f"# {link('cap', 'Req', 'Um')}\n")
        result = self.trace()
        self.assertEqual(result.returncode, 2)
        self.state_line(result, "ORFAO", "cap / Req / Um")

    # Extra (#### Scenario: sem Cenário: no bloco, não exigido): spec-trace / Marcador órfão e marcador ambíguo são apontados / Literal em colisão
    def test_literal_em_colisao_sai_ambiguo(self):
        self.delta(
            "cap",
            section("ADDED", requirement("A / B", ["C"]), requirement("A", ["B / C"])),
        )
        result = self.trace()
        self.assertEqual(result.returncode, 2, result.stdout)
        ambiguous = [line for line in self.lines(result) if " AMBIGUO " in line]
        self.assertEqual(ambiguous, ["spec-trace: AMBIGUO cap / A / B / C"] * 2)

    # Extra (#### Scenario: sem Cenário: no bloco, não exigido): spec-trace / Marcador órfão e marcador ambíguo são apontados / Prosa com Spec:
    def test_prosa_com_marcador_e_ignorada(self):
        self.delta("cap", section("ADDED", requirement("Req", ["Um"])))
        self.put(
            "tests/test_a.py",
            f"# {TAG}: alguma coisa\n# {TAG}: a / b\n# {link('cap', 'Req', 'Um')}\n",
        )
        result = self.trace()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNoState(result, "ORFAO")


class BuscaTest(TraceCase):
    def setUp(self):
        super().setUp()
        self.delta("cap", section("ADDED", requirement("Req", ["Um", "Dois"])))
        self.um = f"# {link('cap', 'Req', 'Um')}\n"
        self.dois = f"# {link('cap', 'Req', 'Dois')}\n"

    # Spec: spec-trace / Busca em arquivos de teste com exclusões / Marcador só em documentação
    def test_marcador_so_em_markdown_e_em_pasta_excluida(self):
        self.put("docs/guia.md", self.um)
        result = self.trace()
        self.state_line(result, "SEM_TESTE", "cap / Req / Um")
        for folder in EXCLUDED_DIRS:
            with self.subTest(pasta=folder):
                self.put(f"{folder}/t/test_x.py", self.um)
                self.state_line(self.trace(), "SEM_TESTE", "cap / Req / Um")

    # Extra (#### Scenario: sem Cenário: no bloco, não exigido): spec-trace / Busca em arquivos de teste com exclusões / Busca restrita
    def test_tests_restringe_a_busca(self):
        self.put("tests_a/test_a.py", self.um)
        self.put("tests_b/test_b.py", self.dois)
        result = self.trace("--tests", "tests_a")
        self.state_line(result, "COBERTO", "cap / Req / Um")
        self.state_line(result, "SEM_TESTE", "cap / Req / Dois")
        both = self.trace("--tests", "tests_a", "--tests", "tests_b")
        self.assertNoState(both, "SEM_TESTE")

    def test_tests_em_pasta_excluida_vale(self):
        self.put("build/test_a.py", self.um)
        self.state_line(self.trace(), "SEM_TESTE", "cap / Req / Um")
        self.state_line(self.trace("--tests", "build"), "COBERTO", "cap / Req / Um")

    # Extra (#### Scenario: sem Cenário: no bloco, não exigido): spec-trace / Busca em arquivos de teste com exclusões / Arquivo que não é texto
    def test_binario_ilegivel_e_grande_sao_ignorados(self):
        self.put("tests/binario.bin", b"\x00\x01" + self.um.encode())
        self.put("tests/ilegivel.txt", b"\xff\xfe\xfa " + self.um.encode())
        self.put("tests/grande.txt", self.um.encode() + b"x" * (1024 * 1024 + 1))
        result = self.trace()
        self.assertEqual(result.returncode, 2)
        self.state_line(result, "SEM_TESTE", "cap / Req / Um")
        self.state_line(result, "SEM_TESTE", "cap / Req / Dois")


class RastroERobustezTest(TraceCase):
    # Spec: spec-trace / Script só lê e não deixa rastro / Execução sem rastro
    def test_execucao_sem_rastro(self):
        self.delta("cap", section("ADDED", requirement("Req", ["Um"])))
        self.put("tests/test_a.py", f"# {link('cap', 'Req', 'Um')}\n")
        before_root, before_scripts = snapshot(self.root), snapshot(HOOK_SCRIPTS)
        result = self.trace()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(snapshot(self.root), before_root)
        self.assertEqual(snapshot(HOOK_SCRIPTS), before_scripts)

    def run_with_deadline(self, *args: str):
        try:
            return self.trace_with_timeout(*args)
        except subprocess.TimeoutExpired:
            self.fail("o script travou lendo arquivo que não é regular")

    def trace_with_timeout(self, *args: str):
        self.assertTrue(SCRIPT.exists(), "script ausente")
        return self.run_script(SCRIPT, "", args=["--root", str(self.root), *args], timeout=10)

    # Spec: spec-trace / Busca em arquivos de teste com exclusões / Arquivo trocado por FIFO depois da listagem
    def test_arquivo_trocado_por_fifo_depois_da_listagem(self):
        target = self.put("tests_race.py", "x = 1\n")
        child = (
            "import importlib.util, json, os, sys\n"
            "from pathlib import Path\n"
            "spec = importlib.util.spec_from_file_location('spec_trace', sys.argv[1])\n"
            "mod = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(mod)\n"
            "target, flags, real = sys.argv[2], [], os.open\n"
            "def wrapper(path, flag, *args, **kwargs):\n"
            "    flags.append(flag)\n"
            "    os.unlink(target)\n"
            "    os.mkfifo(target)\n"
            "    return real(path, flag, *args, **kwargs)\n"
            "os.open = wrapper\n"
            "result = mod.read_text(Path(target))\n"
            "print(json.dumps({'flags': flags, 'result': result}))\n"
        )
        try:
            result = subprocess.run(
                [sys.executable, "-B", "-I", "-c", child, str(SCRIPT), str(target)],
                capture_output=True, text=True, timeout=10,
            )
        except subprocess.TimeoutExpired:
            self.fail("o script travou ao abrir o arquivo trocado por FIFO")
        self.assertNoTraceback(result)
        self.assertEqual(result.returncode, 0, result.stderr)
        seen = json.loads(result.stdout.strip().splitlines()[-1])
        self.assertTrue(seen["flags"], "a abertura não passou por os.open: sem O_NONBLOCK e O_NOFOLLOW")
        for name in ("O_NONBLOCK", "O_NOFOLLOW"):
            with self.subTest(flag=name):
                self.assertTrue(seen["flags"][0] & getattr(os, name), f"{name} ausente nas flags {seen['flags'][0]}")
        self.assertIsNone(seen["result"])

    # Extra (#### Scenario: sem Cenário: no bloco, não exigido): spec-trace / Busca em arquivos de teste com exclusões / Link, FIFO e dispositivo
    def test_fifo_nao_trava_o_script(self):
        self.delta("cap", section("ADDED", requirement("Req", ["Um"])))
        os.mkfifo(self.root / "tests_fifo.py")
        result = self.run_with_deadline()
        self.assertNoTraceback(result)
        self.state_line(result, "SEM_TESTE", "cap / Req / Um")

    # Extra (#### Scenario: sem Cenário: no bloco, não exigido): spec-trace / Busca em arquivos de teste com exclusões / Link, FIFO e dispositivo
    def test_link_simbolico_para_dispositivo_nao_trava_o_script(self):
        self.delta("cap", section("ADDED", requirement("Req", ["Um"])))
        (self.root / "zero.py").symlink_to("/dev/zero")
        result = self.run_with_deadline()
        self.assertNoTraceback(result)
        self.state_line(result, "SEM_TESTE", "cap / Req / Um")

    def test_link_simbolico_para_arquivo_comum_e_ignorado(self):
        self.delta("cap", section("ADDED", requirement("Req", ["Um"])))
        real = self.put("fora/real.txt", f"# {link('cap', 'Req', 'Um')}\n")
        (self.root / "tests_link.py").symlink_to(real)
        result = self.trace("--tests", "tests_link.py")
        self.state_line(result, "SEM_TESTE", "cap / Req / Um")

    def test_ajuda_diz_que_orfao_e_ambiguo_saem_dois_sem_ser_o_veredito(self):
        self.assertTrue(SCRIPT.exists(), "script ausente")
        text = SCRIPT.read_text(encoding="utf-8")
        for needle in ("ORFAO", "AMBIGUO", "severidade média", "não é o veredito"):
            with self.subTest(trecho=needle):
                self.assertIn(needle, text)
        helped = subprocess.run([sys.executable, "-B", str(SCRIPT), "--help"], capture_output=True, text=True, timeout=10)
        self.assertEqual(helped.returncode, 0)
        self.assertIn("não é o veredito", helped.stdout)

    # Spec: spec-trace / Saída e robustez / Projeto sem openspec
    def test_sem_openspec_avisa_e_sai_zero(self):
        self.put("tests/test_a.py", f"# {link('cap', 'Req', 'Um')}\n")
        result = self.trace()
        self.assertEqual(result.returncode, 0)
        self.assertIn("openspec", result.stderr)

    def test_sem_change_ativa_avisa_e_sai_zero(self):
        self.principal("cap", requirement("Req", ["Um"]))
        self.put("openspec/changes/archive/velha/specs/cap/spec.md", section("ADDED", requirement("X", ["Y"])))
        result = self.trace()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertRegex(result.stderr, r"(?i)change")

    # Extra (#### Scenario: sem Cenário: no bloco, não exigido): spec-trace / Saída e robustez / Resumo
    def test_resumo_traz_contagens_e_extras(self):
        extra = scenario_block(["Um"]) + "#### Scenario: Extra\n- **WHEN** x\n- **THEN** y\n"
        self.delta("cap", section("ADDED", f"### Requirement: Req\n{extra}\n"))
        result = self.trace()
        last = result.stdout.strip().splitlines()[-1]
        self.assertTrue(last.startswith("spec-trace: "), last)
        self.assertRegex(last, r"extras: 1\b")
        self.assertRegex(last, r"sem_teste 1\b")
        self.assertEqual(result.returncode, 2)

    def test_resumo_extras_zero(self):
        self.delta("cap", section("ADDED", requirement("Req", ["Um"])))
        self.assertRegex(self.trace().stdout.strip().splitlines()[-1], r"extras: 0\b")

    def test_saidas_somente_zero_ou_dois(self):
        self.delta("cap", section("ADDED", requirement("Req", ["Um"])))
        for args in ([], ["--change", "x"], ["--tests", "nao-existe"], ["--tests"], ["--change"]):
            with self.subTest(args=args):
                self.assertIn(self.trace(*args).returncode, (0, 2))


class BibliotecaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.dont_write_bytecode = True
        sys.path.insert(0, str(HOOK_SCRIPTS))
        import _gherkin

        cls.lib = _gherkin

    # Extra (#### Scenario: sem Cenário: no bloco, não exigido): spec-trace / Script só lê e não deixa rastro / Leitura dos cenários do bloco
    def test_parse_scenarios_devolve_titulo_e_passos_na_ordem(self):
        body = scenario_block(["Segundo", "Primeiro", ("Terceiro", "fim")])
        found = self.lib.parse_scenarios(body)
        self.assertEqual([title for title, _ in found], ["Segundo", "Primeiro", "Terceiro"])
        steps = found[2][1]
        self.assertIn("Dado um", steps)
        self.assertIn("Então fim", steps)

    def test_parse_scenarios_sem_bloco_devolve_vazio(self):
        self.assertEqual(self.lib.parse_scenarios("Texto SHALL valer.\n\n#### Scenario: A\n- **WHEN** x\n"), [])

    def test_validate_e_o_requisito_efetivo_nao_mudam(self):
        self.assertEqual(self.lib.validate(scenario_block(["A", "B"])), [])
        self.assertTrue(self.lib.validate("Texto SHALL valer.\n"))


if __name__ == "__main__":
    unittest.main()
