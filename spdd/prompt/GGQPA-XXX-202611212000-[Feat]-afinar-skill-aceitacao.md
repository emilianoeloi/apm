# Afinar o skill acceptance-from-spec (F5, follow-up das provas)

## Requirements

Afinar, só por adição e esclarecimento, o skill `acceptance-from-spec` e os agentes `sdlc-coder` e `sdlc-planner` com seis convenções vindas das provas: (1) o vermelho vem da asserção do `Então`, erro do ambiente não conta e teste que passa sem o programa é falso verde (reforçar afirmando o conteúdo); (2) o `#### Scenario:` extra que ganhar teste leva `Extra: <capability> / <requisito> / <título>`, nunca `Spec:`; (3) a linha `Spec:` de fixture é montada por constante; (4) o cenário de comportamento do modelo vira pendente de prova humana (`SEM_TESTE` conhecido, com a decisão do humano), sem teste fingido; (5) um teste por `Cenário:` do bloco, nas tasks do planner também; (6) o herdado em `MODIFIED` não exige teste novo. Fora: mudar `spec-trace.py`, reviewer, hooks, `harness.config.json`; ferramenta de teste nomeada; subir o teto de 150 linhas.

## Entities

```mermaid
classDiagram
direction TB

class SkillAceitacao {
    +version 1.1
    +passo 1: herdado, Extra
    +passo 4: fixture por constante
    +passo 5: vermelho pela asserção
    +passo 8: prova humana, listas
    +teto 150 linhas
}

class Coder {
    +Entregável aponta as convenções
}

class Planner {
    +Tasks de teste: um por Cenário
    +Cenários só de prova humana
}

class SpecTrace {
    +ignora Extra:
    +herdado informativo
    +somente leitura (não muda)
}

class Reviewer {
    +SEM_TESTE = alta (não muda)
}

class Convencoes {
    Spec: trinca
    Extra: trinca
    prova humana pendente
}

Coder --> SkillAceitacao : usa
Planner ..> SkillAceitacao : coerente com
SkillAceitacao --> Convencoes : define
SpecTrace ..> Convencoes : lê Spec:
Reviewer --> SpecTrace : Bash
```

Conservador: só adições; a fonte do texto é o skill; `spec-trace.py`, reviewer, hooks e `harness.config.json` não mudam.

## Approach

1. Testes vermelhos em `tests/agents/test_acceptance_skill.py` e `test_contract.py` (trechos em tabela, linha `Spec:` por cenário, `Extra:` nos extras, dois testes de caracterização com o `spec-trace` real).
2. Editar o skill (versão 1.1, passos 1, 4, 5 e 8).
3. Editar o coder (parágrafo) e o planner (seção "Tasks de teste").
4. Sessão principal: README, CHANGELOG, `apm install`, cópias.
5. Integração e prova humana (6.4).

## Structure

### Inheritance Relationships
1. Sem herança.

### Dependencies
1. Os testes dependem de `tests.agents.test_contract` (`AGENTS`, `STACK_TERMS`, `split_agent`, `tool_set`) e de `tests.hooks._util.ProjectCase` e do `spec-trace.py`.
2. O README e as cópias implantadas dependem da sessão principal.
3. Agentes e skill dependem do `STACK_TERMS` (neutralidade) e dos limites de tamanho.

### Layered Architecture
1. Texto normativo: skill.
2. Apontadores: coder e planner.
3. Prova: `tests/agents/`.
4. Documentação e implantação: README, CHANGELOG, `apm install` (sessão principal).

## Operations

### Create Tests - tests/agents/test_acceptance_skill.py (primeiro, vermelho)
1. Responsibility: `AfinacaoDoSkillTest` (um método por cenário com `Spec:` em comentário; tabela de trechos: `falso verde`, `conteúdo`, `código de saída`, `erro do ambiente`, `Extra:`, `por constante`, `ORFAO`, `prova humana`, `decisão do humano`, `SEM_TESTE`, `herdado`, `informativo`, `version: "1.1"`); `REQUIRED` antigo e `MAX_LINES` preservados; `Extra:` no teste de cópias; caracterização com o `spec-trace` real (`Extra:` não sai `ORFAO`, saída 0) e lint do fonte (sem linha `Spec:` com três campos fora de comentário); `ReadmeTest`. Registrar comando e contagem de falhas. Estimativa: ~120 linhas.

### Create Tests - tests/agents/test_contract.py (vermelho)
1. Responsibility: tabelas de trechos do coder (`asserção` ou `falso verde`, `Extra:`, `herdado`, `prova humana`) e do planner (um teste por `Cenário:`, `Extra:`, `Cenários só de prova humana`), `tools` inalteradas, sem `STACK_TERMS`, corpo dentro de 300 linhas; linhas `Spec:` dos dois cenários de texto. Estimativa: ~30 linhas.

### Update Skill - .apm/skills/acceptance-from-spec/SKILL.md
1. Responsibility: `version: "1.1"`; passo 1 (herdado informativo; `Extra:` nunca `Spec:`); passo 4 (fixture por constante); passo 5 (vermelho pela asserção; erro do ambiente; falso verde; símbolo ausente em linguagem compilada); passo 8 (prova humana; listas de extras, herdados e provas humanas). Só adições, sem termo de stack. Estimativa: ~19 linhas (116 no total).

### Update Agent - .apm/agents/sdlc-coder.agent.md
1. Responsibility: parágrafo no Entregável apontando as convenções do skill por cenário, sem copiar. Estimativa: ~4 linhas.

### Update Agent - .apm/agents/sdlc-planner.agent.md
1. Responsibility: seção "Tasks de teste" (um teste por `Cenário:`; extras só se distintos e com `Extra:`; "Cenários só de prova humana" em `design.md` com a task de prova). Estimativa: ~8 linhas.

### Update Docs (sessão principal)
1. `README.md` (seção "Testes de aceitação": convenções e aviso de migração), `CHANGELOG.md` (Onda 2, F5), `docs/roteiro-de-teste.md` (prova 6.4).

### Deploy (sessão principal)
1. `apm install --target claude,copilot`; `diff` das cópias; `claude plugin validate .claude/agents`.

### Verify
1. `python3 -B -m unittest discover -s tests -t .`; `openspec validate afinar-skill-aceitacao --strict`; `python3 -B .apm/hooks/scripts/gherkin-sensor.py`; `grep -rniE "cowboy|cobol|cobc|calculadora" .apm` vazia; `spec-trace` (9 cobertos, 2 `SEM_TESTE` conhecidos, 0 órfãos, 4 extras); prova de comportamento 6.4.

## Norms

1. Artefatos em português; cabeçalhos do OpenSpec e SHALL/MUST em inglês.
2. Skill e agentes sem nome de ferramenta de teste nem termo de stack (`pip`, `make`, `node`, `python`).
3. Teste primeiro: cada task só vira `[x]` depois da verificação; relatar o vermelho com comando, contagem e motivo; dizer quando um teste é de caracterização.
4. Conventional Commits (`feat(agents):`), sem atribuição ao Claude.
5. Testes em `unittest`, em tabela (`subTest`); linha `Spec:` em comentário; fixtures com `Spec:` montadas por constante.
6. Só adições no skill e nos agentes.

## Safeguards

1. Functional Constraints: `openspec validate --strict` e o sensor de Gherkin passam; o `REQUIRED` antigo do skill continua verde.
2. Scope Constraints: sem mudança em `spec-trace.py`, reviewer, hooks, `harness.config.json`; coder e planner mantêm `tools` e limites de escrita.
3. Size Constraints: skill até 150 linhas (projetado ~116); corpo de cada agente até 300.
4. Neutrality Constraints: `grep` de neutralidade vazia; `STACK_TERMS` não casa no skill nem nos agentes.
5. Honesty Constraints: os 2 cenários de comportamento do modelo ficam `SEM_TESTE` conhecidos; teste de caracterização declarado como tal; comportamento do modelo "não verificado" até a 6.4.
6. Release Constraints: sem push, tag ou merge sem o "ok" do Elói; PR `feat(agents):` empilhado sobre a F4 (#38).
