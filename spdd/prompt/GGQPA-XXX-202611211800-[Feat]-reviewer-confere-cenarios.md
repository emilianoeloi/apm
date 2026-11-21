# Reviewer confere cenário contra teste (F4 da V2.0)

## Requirements

Fazer o `sdlc-reviewer` conferir, na revisão, que cada `Cenário:` novo ou alterado pela change tem um teste ligado pela linha `Spec: <capability> / <requisito> / <cenário>`: um script só-leitura `spec-trace.py` (achado por `Glob`, reserva em `grep -F`) lista os cenários exigidos, compara com a spec principal (herdado é informativo) e casa a trinca com linhas de teste; o agente lê cada teste ligado para confirmar que afirma o `Então`, classifica os achados (sem teste e falso verde = alta = `REPROVADO`; órfão, ambíguo e cobertura sem marcador = média) e entrega a seção "Cenários x testes". Inclui `_gherkin.parse_scenarios`, a edição do reviewer e os testes. Fora: revisão cruzada entre modelos, perfis, executar Gherkin, modo `--all`, ligar ao `sensors_command`/hook, mutação de código, ferramenta de teste nomeada.

## Entities

```mermaid
classDiagram
direction TB

class Cenario {
    +String capability
    +String requisito
    +String titulo
    +String passos
    +estado: NOVO | ALTERADO | HERDADO
}

class LinhaSpec {
    +"Spec: capability / requisito / titulo"
    +arquivo:linha
}

class EstadoDoVinculo {
    COBERTO
    SEM_TESTE
    HERDADO_SEM_TESTE
    ORFAO
    AMBIGUO
}

class SpecTrace {
    +--root --change --tests
    +classificar(cenarios)
    +casar(prefixo mais longo)
    +saida 0 ou 2
    +somente leitura, sem bytecode
}

class GherkinLib {
    +parse_delta()
    +effective_requirements()
    +parse_scenarios() novo
}

class SdlcReviewer {
    +acha o script por Glob
    +le cada teste ligado
    +classifica achados
    +secao Cenarios x testes
}

class Veredito {
    APROVADO
    APROVADO COM RESSALVAS
    REPROVADO
}

SpecTrace --> GherkinLib : reutiliza
SpecTrace ..> LinhaSpec : procura
LinhaSpec ..> Cenario : Spec:
SpecTrace --> EstadoDoVinculo : emite
SdlcReviewer --> SpecTrace : Bash
SdlcReviewer --> Veredito : decide
SdlcReviewer ..> LinhaSpec : le o teste
```

Conservador: só adições; `harness.json`, `sensors_command`, `validate` e `effective_requirements` não mudam.

## Approach

1. Testes vermelhos: `tests/hooks/test_spec_trace.py` e `tests/agents/test_reviewer_scenarios.py`.
2. `_gherkin.parse_scenarios`, depois `spec-trace.py` (dont_write_bytecode antes do import; classificação novo/alterado/herdado; prefixo mais longo; ORFAO/AMBIGUO; resumo; saídas 0/2).
3. Editar o reviewer: passo novo, regras de severidade e de veredito, seção "Cenários x testes", reserva em prosa, conferência no fonte.
4. Sessão principal: README (seção e aviso), `apm install`, cópias, `CLAUDE.md` opcional.
5. Prova de comportamento num projeto de prova (humano).

## Structure

### Inheritance Relationships
1. Sem herança.

### Dependencies
1. `spec-trace.py` depende de `_gherkin.py` e `_common.py` (mesma pasta) e da biblioteca padrão.
2. O reviewer depende do nome `spec-trace.py` (achado por `Glob`) e da convenção `Spec:` do skill da F3.
3. Os testes dependem de `tests/hooks/_util.py` (`ProjectCase`, `run_script`).
4. As cópias implantadas dependem de `apm install`.

### Layered Architecture
1. Biblioteca: `_gherkin.py`.
2. Ferramenta: `spec-trace.py`.
3. Agente: `sdlc-reviewer.agent.md`.
4. Prova: `tests/hooks/`, `tests/agents/`.
5. Documentação e implantação: README, `apm install` (sessão principal).

## Operations

### Create Tests - tests/hooks/test_spec_trace.py (primeiro, vermelho)
1. Responsibility: proteger o comportamento do script como processo, em projetos temporários, em tabela: coberto, sem teste, herdado vs alterado, `RENAMED`, prefixo mais longo, fechamento de comentário, órfão, ambíguo, `--change`, `--tests`, exclusões e `.md`, binário/ilegível/grande, sem `openspec/`, sem change ativa, resumo com `extras`, árvore e pasta dos scripts intactas; e `parse_scenarios`.
2. Registrar comando e contagem de falhas (script inexistente). Estimativa: ~230 linhas.

### Create Tests - tests/agents/test_reviewer_scenarios.py (vermelho)
1. Responsibility: texto do reviewer (`spec-trace.py`, `Glob`, `Spec:`, `grep -F`, `HERDADO`, `Cenários x testes`, `REPROVADO`, `falso verde`, `ORFAO`, `fonte`), `tools` inalteradas, passo antes de "Relatório", neutralidade (`STACK_TERMS` e os quatro termos), cópias idênticas (agente, script, `_gherkin.py` nos dois hosts), `harness.json` sem `spec-trace`. Estimativa: ~60 linhas.

### Update Library - .apm/hooks/scripts/_gherkin.py
1. Responsibility: `parse_scenarios(body) -> [(título, passos)]`, mesma leitura do bloco que `validate` (`FENCE_OPEN`, `KEYWORD`). Só acréscimo. Estimativa: ~15 linhas.

### Create Script - .apm/hooks/scripts/spec-trace.py
1. Responsibility: ver Approach 2. Sem `git`, sem escrita, só stdlib + `_gherkin` + `_common`.
2. Algoritmo: (a) ler deltas ativos e spec principal; (b) montar cenários exigidos (ADDED todos; MODIFIED comparando com a base, seguindo RENAMED) e o conjunto de alvos válidos (todos os efetivos); (c) varrer arquivos pelas regras de exclusão, linha com `Spec:`; (d) prefixo mais longo por linha; (e) emitir uma linha por exigido/herdado e por órfão/ambíguo, o resumo e a saída. Estimativa: ~150 linhas.

### Update Agent - .apm/agents/sdlc-reviewer.agent.md
1. Responsibility: passo "Confira cenário contra teste" (script por `Glob`, `python3 -B <caminho> --root . --change <nome>`, reserva `grep -rnF`, ler cada teste ligado), regras de escopo/severidade/veredito, seção "Cenários x testes", "vermelho não verificado", conferência no fonte. Ferramentas e limites inalterados. Estimativa: ~25 linhas.

### Update Docs (sessão principal, fora do reviewer/coder)
1. `README.md`: seção "Conferência de cenários na revisão" e aviso de migração; `CLAUDE.md` opcional.

### Deploy (sessão principal)
1. `apm install --target claude,copilot`; `diff` das cópias (agente, script, `_gherkin.py`); `claude plugin validate .claude/agents`.

### Verify
1. `python3 -B -m unittest discover -s tests -t .`; `openspec validate reviewer-confere-cenarios --strict`; `python3 -B .apm/hooks/scripts/gherkin-sensor.py`; `grep -rniE "cowboy|cobol|cobc|calculadora" .apm` vazia; prova de comportamento em projeto de prova.

## Norms

1. Artefatos em português; cabeçalhos do OpenSpec e SHALL/MUST em inglês.
2. Reviewer e script sem nome de ferramenta de teste; o vínculo é texto.
3. Teste primeiro: cada task só vira `[x]` depois da verificação; relatar o vermelho com comando e contagem.
4. Conventional Commits (`feat(agents):`), sem atribuição ao Claude.
5. Testes em `unittest`, em tabela (`subTest`).
6. Só biblioteca padrão nos scripts, como os demais.

## Safeguards

1. Functional Constraints: `openspec validate --strict` e o sensor de Gherkin passam; o script sai só com 0 ou 2.
2. Read-only Constraints: reviewer com `tools` `Read, Grep, Glob, Bash`; script sem escrita, sem `git` e sem `__pycache__`; `git status --porcelain` igual.
3. Scope Constraints: sem revisão cruzada, perfis, executor de Gherkin, `--all`, hook ou `sensors_command`; só adições.
4. Neutrality Constraints: `grep` de neutralidade vazia; `STACK_TERMS` não casa no reviewer.
5. Honesty Constraints: o script nunca declara "aceitação provada" (prova o vínculo); sem relatório do coder, "vermelho não verificado"; comportamento do modelo "não verificado" até a prova real.
6. Release Constraints: sem push, tag ou merge sem o "ok" do Elói; PR `feat(agents):` depois dos PRs da F3.
