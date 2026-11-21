"""Contrato do sensor de Gherkin: CLI e modo hook, chamados como processo, em projetos temporários."""

import json
import re
import unittest
from pathlib import Path

from tests.hooks._util import HOOK_SCRIPTS, ProjectCase

SENSOR = HOOK_SCRIPTS / "gherkin-sensor.py"

GOOD_BODY = (
    "Texto SHALL valer.\n\n"
    "```gherkin\nCenário: A\n  Dado um\n  Quando dois\n  Então três\n```\n\n"
    "#### Scenario: A\n- **WHEN** x\n- **THEN** y\n"
)
NO_BLOCK_BODY = "Texto SHALL valer.\n\n#### Scenario: A\n- **WHEN** x\n- **THEN** y\n"
NO_THEN_BODY = (
    "Texto SHALL valer.\n\n"
    "```gherkin\nCenário: A\n  Dado um\n  Quando dois\n```\n\n"
    "#### Scenario: A\n- **WHEN** x\n- **THEN** y\n"
)
WRONG_TITLE_BODY = (
    "Texto SHALL valer.\n\n"
    "```gherkin\nCenário: Outro\n  Dado um\n  Quando dois\n  Então três\n```\n\n"
    "#### Scenario: A\n- **WHEN** x\n- **THEN** y\n"
)


def requirement(name: str, body: str) -> str:
    return f"### Requirement: {name}\n{body}\n"


def spec(*reqs: str) -> str:
    return "## Requirements\n\n" + "\n".join(reqs)


def delta(section: str, *reqs: str) -> str:
    return f"## {section} Requirements\n\n" + "\n".join(reqs)


class SensorCase(ProjectCase):
    def put(self, relative: str, content) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        return path

    def sensor(self, args=None, stdin: str = ""):
        return self.run_script(SENSOR, stdin, args=args)


class CliTest(SensorCase):
    def test_requisito_sem_bloco_reprova_citando_tudo(self):
        self.put("openspec/specs/alfa/spec.md", spec(requirement("Sem bloco", NO_BLOCK_BODY)))
        result = self.sensor()
        self.assertEqual(result.returncode, 2)
        self.assertIn("alfa", result.stderr)
        self.assertIn("Requirement: Sem bloco", result.stderr)
        self.assertRegex(result.stderr, r"gherkin: alfa / Requirement: Sem bloco: .+")
        self.assertNoTraceback(result)

    def test_todas_as_violacoes_sao_listadas(self):
        self.put(
            "openspec/specs/alfa/spec.md",
            spec(requirement("Sem Então", NO_THEN_BODY), requirement("Título errado", WRONG_TITLE_BODY)),
        )
        result = self.sensor()
        self.assertEqual(result.returncode, 2)
        self.assertIn("Requirement: Sem Então", result.stderr)
        self.assertIn("Requirement: Título errado", result.stderr)
        self.assertIn("passos fora de ordem", result.stderr)
        self.assertIn("título sem #### Scenario: correspondente", result.stderr)

    def test_projeto_conforme_sai_0_sem_stderr(self):
        self.put("openspec/specs/alfa/spec.md", spec(requirement("Bom", GOOD_BODY)))
        result = self.sensor()
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")

    def test_delta_added_sem_bloco_cita_a_change(self):
        self.put("openspec/specs/alfa/spec.md", spec(requirement("Bom", GOOD_BODY)))
        self.put("openspec/changes/minha-change/specs/alfa/spec.md", delta("ADDED", requirement("Novo", NO_BLOCK_BODY)))
        result = self.sensor()
        self.assertEqual(result.returncode, 2)
        self.assertIn("alfa / Requirement: Novo [change minha-change]", result.stderr)

    def test_delta_de_capability_nova_e_verificado(self):
        self.put("openspec/specs/alfa/spec.md", spec(requirement("Bom", GOOD_BODY)))
        self.put("openspec/changes/c1/specs/beta/spec.md", delta("ADDED", requirement("Novo", NO_BLOCK_BODY)))
        result = self.sensor()
        self.assertEqual(result.returncode, 2)
        self.assertIn("beta / Requirement: Novo [change c1]", result.stderr)

    def test_removed_nao_conta(self):
        self.put("openspec/specs/alfa/spec.md", spec(requirement("Velho", NO_BLOCK_BODY), requirement("Bom", GOOD_BODY)))
        self.put("openspec/changes/c1/specs/alfa/spec.md", delta("REMOVED", requirement("Velho", "Removido.\n")))
        result = self.sensor()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_modified_conforme_substitui_o_principal_ruim(self):
        self.put("openspec/specs/alfa/spec.md", spec(requirement("Velho", NO_BLOCK_BODY)))
        self.put("openspec/changes/c1/specs/alfa/spec.md", delta("MODIFIED", requirement("Velho", GOOD_BODY)))
        result = self.sensor()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_renamed_nao_duplica_a_citacao(self):
        self.put("openspec/specs/alfa/spec.md", spec(requirement("Nome antigo", NO_BLOCK_BODY)))
        renamed = "## RENAMED Requirements\n\n- FROM: `### Requirement: Nome antigo`\n- TO: `### Requirement: Nome novo`\n"
        self.put("openspec/changes/c1/specs/alfa/spec.md", renamed)
        result = self.sensor()
        self.assertEqual(result.returncode, 2)
        self.assertIn("Requirement: Nome novo", result.stderr)
        self.assertNotIn("Requirement: Nome antigo", result.stderr)
        self.assertEqual(len(re.findall(r"^gherkin: .* / Requirement: ", result.stderr, re.MULTILINE)), 1)

    def test_renamed_seguido_de_modified_com_o_nome_novo(self):
        self.put("openspec/specs/alfa/spec.md", spec(requirement("Nome antigo", NO_BLOCK_BODY)))
        content = (
            "## RENAMED Requirements\n\n- FROM: `### Requirement: Nome antigo`\n- TO: `### Requirement: Nome novo`\n\n"
            + delta("MODIFIED", requirement("Nome novo", GOOD_BODY))
        )
        self.put("openspec/changes/c1/specs/alfa/spec.md", content)
        result = self.sensor()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_archive_e_ignorado(self):
        self.put("openspec/specs/alfa/spec.md", spec(requirement("Bom", GOOD_BODY)))
        self.put(
            "openspec/changes/archive/2026-01-01-velha/specs/alfa/spec.md",
            delta("ADDED", requirement("Arquivado", NO_BLOCK_BODY)),
        )
        result = self.sensor()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Arquivado", result.stderr)

    def test_sem_openspec_sai_0_com_aviso(self):
        result = self.sensor()
        self.assertEqual(result.returncode, 0)
        self.assertIn("openspec", result.stderr)
        self.assertNoTraceback(result)

    def test_root_por_parametro_ignora_o_diretorio_atual(self):
        other = self.parent / "outro"
        (other / "openspec" / "specs" / "zeta").mkdir(parents=True)
        (other / "openspec" / "specs" / "zeta" / "spec.md").write_text(
            spec(requirement("Sem bloco", NO_BLOCK_BODY)), encoding="utf-8"
        )
        result = self.sensor(args=["--root", str(other)])
        self.assertEqual(result.returncode, 2)
        self.assertIn("zeta / Requirement: Sem bloco", result.stderr)

    def test_claude_project_dir_define_a_raiz(self):
        self.put("openspec/specs/alfa/spec.md", spec(requirement("Sem bloco", NO_BLOCK_BODY)))
        result = self.sensor()  # env() já traz CLAUDE_PROJECT_DIR
        self.assertEqual(result.returncode, 2)
        self.assertIn("alfa / Requirement: Sem bloco", result.stderr)

    def test_utf8_invalido_sai_2_sem_traceback(self):
        self.put("openspec/specs/alfa/spec.md", b"### Requirement: X\n\xff\xfe\xfa invalido\n")
        result = self.sensor()
        self.assertEqual(result.returncode, 2)
        self.assertIn("alfa", result.stderr)
        self.assertNoTraceback(result)

    def test_nao_altera_arquivos(self):
        path = self.put("openspec/specs/alfa/spec.md", spec(requirement("Sem bloco", NO_BLOCK_BODY)))
        before = path.read_bytes()
        self.sensor()
        self.assertEqual(path.read_bytes(), before)


class HookModeTest(SensorCase):
    def setUp(self):
        super().setUp()
        self.put("openspec/specs/alfa/spec.md", spec(requirement("Sem bloco", NO_BLOCK_BODY)))

    def hook(self, stdin):
        return self.sensor(args=["--on-validate"], stdin=stdin)

    def test_openspec_validate_dispara_o_sensor(self):
        result = self.hook({"tool_name": "Bash", "tool_input": {"command": "openspec validate minha --strict"}})
        self.assertEqual(result.returncode, 2)
        self.assertIn("alfa / Requirement: Sem bloco", result.stderr)

    def test_outro_comando_sai_0_mudo(self):
        result = self.hook({"tool_name": "Bash", "tool_input": {"command": "git status"}})
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))

    def test_payload_invalido_sai_0(self):
        for text in ("não é json", "", "[1, 2]"):
            with self.subTest(payload=text):
                result = self.hook(text)
                self.assertEqual(result.returncode, 0)
                self.assertNoTraceback(result)

    def test_formato_copilot_dispara(self):
        payload = {"toolName": "bash", "toolArgs": json.dumps({"command": "openspec validate --all --strict"})}
        result = self.hook(payload)
        self.assertEqual(result.returncode, 2)
        self.assertIn("alfa / Requirement: Sem bloco", result.stderr)

    def test_formato_copilot_com_outro_comando_sai_0(self):
        payload = {"toolName": "bash", "toolArgs": json.dumps({"command": "ls"})}
        result = self.hook(payload)
        self.assertEqual(result.returncode, 0)

    def test_tool_input_de_tipo_errado_sai_0(self):
        result = self.hook({"tool_name": "Bash", "tool_input": "openspec validate"})
        self.assertEqual(result.returncode, 0)
        self.assertNoTraceback(result)

    def test_validate_com_projeto_conforme_sai_0(self):
        self.put("openspec/specs/alfa/spec.md", spec(requirement("Bom", GOOD_BODY)))
        result = self.hook({"tool_name": "Bash", "tool_input": {"command": "openspec validate --strict"}})
        self.assertEqual((result.returncode, result.stderr), (0, ""))


if __name__ == "__main__":
    unittest.main()
