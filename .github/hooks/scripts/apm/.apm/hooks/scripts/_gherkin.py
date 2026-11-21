"""Regra de formato do bloco Gherkin e leitura dos requisitos efetivos das specs do OpenSpec.

Só biblioteca padrão, de propósito: é importada pelo sensor `gherkin-sensor.py` e pelos testes.
Estática: só lê arquivos, nunca escreve. Arquivo ilegível vira um requisito com falha, nunca exceção.

Requisito efetivo: spec principal com os requisitos trocados pelos `ADDED`/`MODIFIED` dos deltas
de changes ativas (fora de `changes/archive/`), sem os `REMOVED` e com os `RENAMED` aplicados.
"""

import re
from dataclasses import dataclass
from pathlib import Path

REQ = re.compile(r"^### Requirement: (.+?)\s*$", re.MULTILINE)
SECTION = re.compile(r"^## (ADDED|MODIFIED|REMOVED|RENAMED) Requirements\s*$", re.MULTILINE)
SCENARIO = re.compile(r"^#### Scenario: (.+?)\s*$", re.MULTILINE)
FENCE_OPEN = re.compile(r"^```gherkin\s*$", re.MULTILINE)
KEYWORD = re.compile(r"^\s*(Cenário:|(?:Dado|Quando|Então|E|Mas)\b)\s*(.*)$")
WRONG = re.compile(r"^\s*(Cenario:|Scenario:|(?:Entao|Given|When|Then)\b)")
RENAME = re.compile(
    r"^\s*-\s*FROM:\s*`?###\s*Requirement:\s*(.+?)`?\s*$\s*^\s*-\s*TO:\s*`?###\s*Requirement:\s*(.+?)`?\s*$",
    re.MULTILINE,
)

PRINCIPAL = "principal"


@dataclass(frozen=True)
class Requisito:
    """Um requisito efetivo: capability, nome, corpo e origem (`principal` ou o nome da change)."""

    capability: str
    name: str
    body: str
    origin: str = PRINCIPAL
    error: str = ""  # preenchido só quando o arquivo da spec não pôde ser lido


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
    """Devolve {'ADDED', 'MODIFIED', 'REMOVED', 'RENAMED'} de um delta; RENAMED é {nome_antigo: nome_novo}."""
    parts = list(SECTION.finditer(text))
    out = {"ADDED": {}, "MODIFIED": {}, "REMOVED": {}, "RENAMED": {}}
    for index, match in enumerate(parts):
        end = parts[index + 1].start() if index + 1 < len(parts) else len(text)
        chunk = text[match.end():end]
        if match.group(1) == "RENAMED":
            out["RENAMED"].update({old: new for old, new in RENAME.findall(chunk)})
        else:
            out[match.group(1)].update(parse_requirements(chunk))
    return out


def _read(path: Path):
    """(texto, None) ou (None, motivo) quando o arquivo não pode ser lido como UTF-8."""
    try:
        return path.read_text(encoding="utf-8"), None
    except (OSError, UnicodeDecodeError) as error:
        return None, f"arquivo ilegível ({type(error).__name__})"


def effective_requirements(root: Path) -> list:
    """Lista de `Requisito` efetivos de `<root>/openspec`; vazia se a pasta não existir."""
    root = Path(root)
    specs = root / "openspec" / "specs"
    changes = root / "openspec" / "changes"
    result = []
    deltas = []
    for path in sorted(changes.glob("*/specs/*/spec.md")):
        if "archive" in path.relative_to(changes).parts:
            continue
        text, problem = _read(path)
        if text is None:
            result.append(Requisito(path.parent.name, f"({path.name})", "", path.relative_to(changes).parts[0], problem))
            continue
        deltas.append((path.parent.name, path.relative_to(changes).parts[0], parse_delta(text)))
    capabilities = set()
    for path in sorted(specs.glob("*/spec.md")):
        capability = path.parent.name
        capabilities.add(capability)
        text, problem = _read(path)
        if text is None:
            result.append(Requisito(capability, f"({path.name})", "", PRINCIPAL, problem))
            continue
        base = {name: (body, PRINCIPAL) for name, body in parse_requirements(text).items()}
        for dcap, change, delta in deltas:
            if dcap != capability:
                continue
            for old, new in delta["RENAMED"].items():
                if old in base:
                    base[new] = base.pop(old)
            for name in delta["REMOVED"]:
                base.pop(name, None)
            for name, body in {**delta["MODIFIED"], **delta["ADDED"]}.items():
                base[name] = (body, change)
        result.extend(Requisito(capability, name, body, origin) for name, (body, origin) in base.items())
    for dcap, change, delta in deltas:
        if dcap in capabilities:
            continue
        for name, body in {**delta["ADDED"], **delta["MODIFIED"]}.items():
            result.append(Requisito(dcap, name, body, change))
    return result


def parse_scenarios(body: str) -> list:
    """Lista de `(título, passos)` dos `Cenário:` do bloco gherkin, na ordem; `[]` sem bloco.

    `passos` são as linhas de passo (Dado/Quando/Então/E/Mas) já sem recuo, unidas por quebra de linha.
    Lê o bloco como `validate` (`FENCE_OPEN`, `KEYWORD`), mas não julga formato.
    """
    start = FENCE_OPEN.search(body)
    if not start:
        return []
    rest = body[start.end():]
    close = re.search(r"^```\s*$", rest, re.MULTILINE)
    inner = rest[: close.start()] if close else rest
    scenarios = []
    for line in inner.splitlines():
        match = KEYWORD.match(line)
        if not match or line.strip().startswith("#"):
            continue
        if match.group(1) == "Cenário:":
            scenarios.append((match.group(2).strip(), []))
        elif scenarios:
            scenarios[-1][1].append(line.strip())
    return [(title, "\n".join(steps)) for title, steps in scenarios]


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
