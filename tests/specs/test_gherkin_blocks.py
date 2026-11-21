"""Formato do bloco Gherkin em todo requisito efetivo das specs do OpenSpec.

Requisito efetivo: spec principal com os requisitos trocados pelos `ADDED`/`MODIFIED` dos deltas ativos
(fora de `archive/`) e sem os `REMOVED`. Estático: só lê arquivos.
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SPECS = REPO / "openspec" / "specs"
CHANGES = REPO / "openspec" / "changes"

REQ = re.compile(r"^### Requirement: (.+?)\s*$", re.MULTILINE)
SECTION = re.compile(r"^## (ADDED|MODIFIED|REMOVED|RENAMED) Requirements\s*$", re.MULTILINE)
SCENARIO = re.compile(r"^#### Scenario: (.+?)\s*$", re.MULTILINE)
FENCE_OPEN = re.compile(r"^```gherkin\s*$", re.MULTILINE)
KEYWORD = re.compile(r"^\s*(Cenário:|(?:Dado|Quando|Então|E|Mas)\b)\s*(.*)$")
WRONG = re.compile(r"^\s*(Cenario:|Scenario:|(?:Entao|Given|When|Then)\b)")


def parse_requirements(text: str) -> dict:
    """Devolve {nome: corpo} dos `### Requirement:` do texto, na ordem."""
    matches = list(REQ.finditer(text))
    out = {}
    for index, match in enumerate(matches):
        end = len(text)
        if index + 1 < len(matches):
            end = matches[index + 1].start()
        body = text[match.end():end]
        nxt = re.search(r"^## ", body, re.MULTILINE)
        out[match.group(1)] = body[: nxt.start()] if nxt else body
    return out


def parse_delta(text: str) -> dict:
    """Devolve {'ADDED': {...}, 'MODIFIED': {...}, 'REMOVED': {...}} de um delta."""
    parts = list(SECTION.finditer(text))
    out = {"ADDED": {}, "MODIFIED": {}, "REMOVED": {}, "RENAMED": {}}
    for index, match in enumerate(parts):
        end = parts[index + 1].start() if index + 1 < len(parts) else len(text)
        out[match.group(1)].update(parse_requirements(text[match.end():end]))
    return out


def effective_requirements() -> list:
    """Lista de (origem, nome, corpo) dos requisitos efetivos."""
    result = []
    deltas = []
    for path in sorted(CHANGES.glob("*/specs/*/spec.md")):
        if "archive" in path.relative_to(CHANGES).parts:
            continue
        deltas.append((path, parse_delta(path.read_text(encoding="utf-8"))))
    for path in sorted(SPECS.glob("*/spec.md")):
        capability = path.parent.name
        base = parse_requirements(path.read_text(encoding="utf-8"))
        for dpath, delta in deltas:
            if dpath.parent.name != capability:
                continue
            for name in delta["REMOVED"]:
                base.pop(name, None)
            for name, body in delta["MODIFIED"].items():
                base[name] = body
            for name, body in delta["ADDED"].items():
                base[name] = body
        for name, body in base.items():
            result.append((capability, name, body))
    known = {p.parent.name for p in SPECS.glob("*/spec.md")}
    for dpath, delta in deltas:
        if dpath.parent.name in known:
            continue
        for name, body in {**delta["ADDED"], **delta["MODIFIED"]}.items():
            result.append((dpath.parent.name, name, body))
    return result


def validate(body: str) -> list:
    """Lista de erros do bloco Gherkin de um requisito (vazia = conforme)."""
    errors = []
    opens = list(FENCE_OPEN.finditer(body))
    if len(opens) != 1:
        return [f"esperado exatamente 1 bloco gherkin, achei {len(opens)}"]
    start = opens[0]
    close = re.search(r"^```\s*$", body[start.end():], re.MULTILINE)
    if not close:
        return ["bloco gherkin sem fechamento"]
    inner = body[start.end(): start.end() + close.start()]
    first_scenario = SCENARIO.search(body)
    if not first_scenario:
        errors.append("requisito sem #### Scenario:")
    elif start.start() > first_scenario.start():
        errors.append("bloco gherkin depois do primeiro #### Scenario:")
    if not body[: start.start()].strip().split("\n", 1)[-1].strip():
        errors.append("bloco gherkin sem parágrafo normativo antes")
    titles = set(SCENARIO.findall(body))
    scenarios = []
    for line in inner.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if WRONG.match(line):
            errors.append(f"palavra-chave fora do padrão: {line.strip()}")
            continue
        match = KEYWORD.match(line)
        if not match:
            errors.append(f"linha fora do formato: {line.strip()}")
            continue
        word, rest = match.groups()
        if word == "Cenário:":
            scenarios.append({"title": rest.strip(), "steps": []})
        elif not scenarios:
            errors.append(f"passo antes de Cenário: {line.strip()}")
        else:
            scenarios[-1]["steps"].append(word)
    if not scenarios:
        errors.append("nenhum Cenário:")
    for scenario in scenarios:
        steps = [s for s in scenario["steps"] if s in ("Dado", "Quando", "Então")]
        order = []
        for step in steps:
            if not order or order[-1] != step:
                order.append(step)
        if order != ["Dado", "Quando", "Então"]:
            errors.append(f"passos fora de ordem ou faltando em '{scenario['title']}': {order}")
        if scenario["title"] not in titles:
            errors.append(f"título sem #### Scenario: correspondente: '{scenario['title']}'")
    return errors


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

    def test_leitor_acha_requisitos_efetivos(self):
        found = effective_requirements()
        self.assertGreaterEqual(len(found), 31)
        names = {name for _, name, _ in found}
        self.assertNotIn("Primeira publicação do 1.0.0 é um pré-lançamento", names)
        self.assertIn("Bloco Gherkin cercado sob cada requisito", names)

    def test_todo_requisito_efetivo_tem_o_bloco(self):
        for capability, name, body in effective_requirements():
            with self.subTest(spec=capability, requisito=name):
                self.assertEqual(validate(body), [])


if __name__ == "__main__":
    unittest.main()
