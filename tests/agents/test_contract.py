"""Contrato dos agentes de SDLC: formato, ferramentas por papel, neutralidade de stack, skills e implantação.

Estático de propósito: prova o contrato sem rodar um modelo. O comportamento de cada agente se prova no fluxo
completo (projeto de prova), não aqui.
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AGENTS = REPO / ".apm" / "agents"
SKILLS = REPO / ".apm" / "skills"
CLAUDE_DEPLOY = REPO / ".claude" / "agents"
COPILOT_DEPLOY = REPO / ".github" / "agents"

ROLES = ("planner", "coder", "reviewer", "auditor")
NAMES = tuple(f"sdlc-{role}" for role in ROLES)

# Ferramentas por papel (nomes do Claude Code; o Copilot os aceita como alias).
TOOLS = {
    "sdlc-planner": {"Read", "Grep", "Glob", "Write", "Edit", "Bash", "Skill"},
    "sdlc-coder": {"Read", "Grep", "Glob", "Write", "Edit", "Bash", "Skill"},
    "sdlc-reviewer": {"Read", "Grep", "Glob", "Bash"},
    "sdlc-auditor": {"Read", "Grep", "Glob", "Bash"},
}
ALLOWED_TOOLS = {"Read", "Grep", "Glob", "Write", "Edit", "Bash", "Skill"}
FORBIDDEN_KEYS = {"model", "handoffs", "skills", "color"}

# Skills que cada papel deve citar.
SKILLS_BY_ROLE = {
    "sdlc-planner": {"openspec-explore", "openspec-propose", "spdd-analysis", "spdd-reasons-canvas"},
    "sdlc-coder": {"spdd-generate", "openspec-apply-change"},
}

STACK_TERMS = re.compile(
    r"cowboy|cobol|cobc|calculadora|makefile|\bsrc/|\bpytest\b|\bnpm\b|\byarn\b|\bcargo\b|\bgradle\b|\bmaven\b"
    r"|\bxcodebuild\b|\bpip\b|\bpython\b|\bjava\b|\bswift\b|\bkotlin\b|\brust\b|\bgolang\b|\bjavascript\b"
    r"|\btypescript\b|\bnode\b|\bgo test\b|\bmake\b",
    re.IGNORECASE,
)


def split_agent(path: Path) -> tuple:
    """Devolve (frontmatter como dict de texto, corpo). Leitor mínimo: chave: valor, uma por linha."""
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path.name}: o frontmatter deve abrir na primeira linha"
    head, _, body = text[4:].partition("\n---\n")
    front = {}
    for line in head.splitlines():
        if line.strip() and not line.startswith((" ", "#")):
            key, _, value = line.partition(":")
            front[key.strip()] = value.strip()
    return front, body


def tool_set(front: dict) -> set:
    return {item.strip() for item in front.get("tools", "").split(",") if item.strip()}


class FonteDosAgentesTest(unittest.TestCase):
    def test_exatamente_os_quatro_agentes(self):
        found = sorted(path.name for path in AGENTS.glob("*")) if AGENTS.exists() else []
        self.assertEqual(found, sorted(f"{name}.agent.md" for name in NAMES))

    def test_frontmatter_obrigatorio_e_nome_igual_ao_arquivo(self):
        for name in NAMES:
            with self.subTest(agente=name):
                front, _ = split_agent(AGENTS / f"{name}.agent.md")
                self.assertEqual(front.get("name"), name)
                self.assertRegex(name, r"^[a-z][a-z0-9-]*$")
                self.assertTrue(front.get("description"), "description obrigatória")
                self.assertTrue(front.get("tools"), "tools obrigatório")

    def test_sem_campos_que_so_um_host_conhece(self):
        for name in NAMES:
            with self.subTest(agente=name):
                front, _ = split_agent(AGENTS / f"{name}.agent.md")
                self.assertFalse(FORBIDDEN_KEYS & set(front), f"campos proibidos: {FORBIDDEN_KEYS & set(front)}")

    def test_ferramentas_por_papel(self):
        for name in NAMES:
            with self.subTest(agente=name):
                front, _ = split_agent(AGENTS / f"{name}.agent.md")
                tools = tool_set(front)
                self.assertTrue(tools <= ALLOWED_TOOLS, f"ferramenta fora da lista: {tools - ALLOWED_TOOLS}")
                self.assertEqual(tools, TOOLS[name])

    def test_leitura_nao_escreve_e_ninguem_chama_agente(self):
        for name in NAMES:
            with self.subTest(agente=name):
                tools = tool_set(split_agent(AGENTS / f"{name}.agent.md")[0])
                self.assertFalse({"Agent", "Task"} & tools)
                if name in ("sdlc-reviewer", "sdlc-auditor"):
                    self.assertFalse({"Write", "Edit", "NotebookEdit"} & tools)

    def test_descricao_do_coder_exige_canvas_e_fase_apply(self):
        description = split_agent(AGENTS / "sdlc-coder.agent.md")[0]["description"].lower()
        self.assertIn("canvas", description)
        self.assertIn("apply", description)


class CorpoDosAgentesTest(unittest.TestCase):
    def body(self, name: str) -> str:
        return split_agent(AGENTS / f"{name}.agent.md")[1]

    def test_neutralidade_de_stack(self):
        for name in NAMES:
            with self.subTest(agente=name):
                text = (AGENTS / f"{name}.agent.md").read_text(encoding="utf-8")
                self.assertIsNone(STACK_TERMS.search(text), STACK_TERMS.search(text))

    def test_informacoes_do_projeto_vem_da_configuracao(self):
        for name in NAMES:
            with self.subTest(agente=name):
                body = self.body(name)
                self.assertIn("harness.config.json", body)
                self.assertTrue("CLAUDE.md" in body or "AGENTS.md" in body)

    def test_a_sessao_principal_dispara_e_ninguem_encadeia(self):
        for name in NAMES:
            with self.subTest(agente=name):
                body = self.body(name)
                self.assertIn("sessão principal", body)
                self.assertNotIn("handoff", body.lower())

    def test_tamanho_do_corpo(self):
        for name in NAMES:
            with self.subTest(agente=name):
                self.assertLessEqual(len(self.body(name).splitlines()), 300)

    def test_skills_citados_existem(self):
        pattern = re.compile(r"`((?:openspec|spdd)-[a-z-]+)`")
        for name in NAMES:
            with self.subTest(agente=name):
                for skill in set(pattern.findall(self.body(name))):
                    self.assertTrue((SKILLS / skill / "SKILL.md").exists(), f"skill inexistente: {skill}")

    def test_cada_papel_cita_os_seus_skills(self):
        for name, skills in SKILLS_BY_ROLE.items():
            with self.subTest(agente=name):
                body = self.body(name)
                for skill in skills:
                    self.assertIn(f"`{skill}`", body)

    def test_planner(self):
        body = self.body("sdlc-planner")
        for needle in ("phase_cli.py", "openspec validate", "--strict", "planning_write_prefixes", "proposal"):
            self.assertIn(needle, body)

    def test_coder(self):
        body = self.body("sdlc-coder")
        for needle in ("code_prefixes", "sensors_command", "canvas", "apply", "tasks.md", "Operations"):
            self.assertIn(needle, body)
        self.assertRegex(body, r"(?i)sem canvas|canvas (ausente|n[ãa]o existe)|n[ãa]o (houver|existir) canvas")

    def test_reviewer(self):
        body = self.body("sdlc-reviewer")
        for needle in ("openspec validate", "--strict", "git status --porcelain", "APROVADO", "REPROVADO", "Operation", "escopo"):
            self.assertIn(needle, body)

    def test_leitura_declara_que_nao_altera_nada(self):
        for name in ("sdlc-reviewer", "sdlc-auditor"):
            with self.subTest(agente=name):
                body = self.body(name)
                self.assertIn("só lê", body)
                self.assertRegex(body, r"(?i)n[ãa]o altera")
                self.assertRegex(body, r"(?i)git status --porcelain.*igual|igual ao inicial")

    def test_auditor(self):
        body = self.body("sdlc-auditor")
        for needle in ("git status --porcelain", "evidência", "arquivo"):
            self.assertIn(needle, body)


class ImplantacaoTest(unittest.TestCase):
    def test_copias_implantadas_identicas_a_fonte(self):
        for name in NAMES:
            source = (AGENTS / f"{name}.agent.md").read_text(encoding="utf-8") if (AGENTS / f"{name}.agent.md").exists() else None
            with self.subTest(agente=name):
                self.assertIsNotNone(source, "fonte ausente")
                for deployed in (CLAUDE_DEPLOY / f"{name}.md", COPILOT_DEPLOY / f"{name}.agent.md"):
                    self.assertTrue(deployed.exists(), f"não implantado: {deployed.relative_to(REPO)}")
                    self.assertEqual(deployed.read_text(encoding="utf-8"), source)

    def test_nada_alem_dos_quatro_nas_pastas_implantadas(self):
        self.assertEqual(sorted(p.name for p in CLAUDE_DEPLOY.glob("*.md")) if CLAUDE_DEPLOY.exists() else [],
                         sorted(f"{n}.md" for n in NAMES))
        self.assertEqual(sorted(p.name for p in COPILOT_DEPLOY.glob("*.md")) if COPILOT_DEPLOY.exists() else [],
                         sorted(f"{n}.agent.md" for n in NAMES))


if __name__ == "__main__":
    unittest.main()
