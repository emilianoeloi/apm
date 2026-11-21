# Proposal

## Why

A F1 pôs um bloco Gherkin em cada requisito, a F2 confere o formato do bloco e a F3 faz o `sdlc-coder` escrever, antes do código, um teste ligado a cada cenário pela linha `Spec: <capability> / <requisito> / <cenário>`. Falta fechar o ciclo: nada confere, na revisão, que cada cenário aprovado ficou com teste. O sensor da F2 sai 0 mesmo sem nenhuma linha `Spec:` nos testes (ele não lê testes). Na prova da F3 três cenários herdados de um requisito modificado ficaram sem `Spec:` e ninguém avisou, e um teste do ramo sem framework passou sem o programa existir (falso verde).

Fonte V2.0 (trecho recebido da sessão principal; **não li o arquivo no Drive**, se o texto original diferir vale o original): "Dado o sdlc-reviewer, quando revisa, então confere que cada cenário tem teste" e, na jornada, passo 5: "O sdlc-reviewer confere que cada cenário tem teste". Restrições: só adições; sem perfis de SDLC; sem revisão cruzada entre modelos; stack-agnóstico (nenhuma ferramenta de teste nomeada); o reviewer continua **somente leitura** (`tools`: Read, Grep, Glob, Bash).

## What Changes

- **Script só-leitura `spec-trace.py`** (`.apm/hooks/scripts/spec-trace.py`, implantado junto dos demais scripts): lê as specs com `_gherkin`, lista os cenários que a change em revisão acrescentou ou alterou, procura em arquivos de teste a linha literal `Spec: <capability> / <requisito> / <cenário>` e imprime uma linha por cenário (`COBERTO`, `SEM_TESTE`, `HERDADO_SEM_TESTE`) mais as linhas `Spec:` órfãs (`ORFAO`) e ambíguas (`AMBIGUO`). Saída 0 ou 2. Não escreve nada, nem bytecode. Não é hook e não entra no `sensors_command`.
- **`_gherkin.py`**: uma função nova, `parse_scenarios(body)`, que devolve `(título, passos)` de cada `Cenário:` do bloco. Só acréscimo; `validate` e `effective_requirements` não mudam.
- **Edição do `sdlc-reviewer`** (`.apm/agents/sdlc-reviewer.agent.md`): um passo novo em "O que você faz" (conferir cenário contra teste, com o script quando o achar por `Glob` e, sem ele, com `grep -F` por cenário), regras de achado e de veredito, e a seção "Cenários x testes" no relatório. Ferramentas e limite de escrita não mudam.
- **Regra de escopo**: exige teste só para cenário **novo ou alterado** pela change; cenário herdado (mesmo título e mesmos passos do requisito `MODIFIED` na spec principal) sem `Spec:` vira informativo e não muda o veredito.
- **Severidades**: cenário novo/alterado sem teste = alta (veredito `REPROVADO`); teste que não afirma o `Então` do cenário (falso verde) = alta; `Spec:` órfã, marcador ambíguo e cobertura sem marcador = média; herdado sem teste = informativo.
- **Testes**: `tests/hooks/test_spec_trace.py` (script, em tabela) e `tests/agents/test_reviewer_scenarios.py` (texto do reviewer e cópias implantadas).
- **README (sessão principal)**: seção sobre a conferência e aviso de migração.

Só adições; nenhum hook, spec ou agente existente é removido; sem perfis, sem revisão cruzada entre modelos, sem ferramenta de teste nomeada. O fluxo SDLC continua único.

**Rotina de quem opera**: depois de atualizar o pacote, o reviewer passa a **reprovar** uma change cujo cenário novo ou alterado não tenha teste ligado por `Spec:`. Em projetos que adotaram o pacote antes da F3 isso só vale para cenários da change em revisão; cenários antigos não são exigidos. O Emiliano passa a ver a seção "Cenários x testes" em todo relatório do reviewer. Isso vai para o README e o aviso de migração.

Fora desta change: revisão cruzada entre modelos, perfis de SDLC, executar Gherkin, exigir teste de cenários antigos (modo `--all`), ligar o script ao `sensors_command` ou a um hook, mutação de código para provar teste fraco (o reviewer não escreve), orquestrador (`sdlc-orchestrator`).

## Capabilities

### New Capabilities
- `spec-trace`: o script que confere o vínculo cenário-teste, o escopo (novo/alterado vs herdado), a saída, a robustez, a regra só-leitura e a implantação.

### Modified Capabilities
- `sdlc-agent-roles`: o reviewer passa a conferir cenário contra teste e a classificar os achados (dois requisitos acrescentados).
- `pacote-generico`: o README passa a trazer a seção e o aviso de migração desta versão (requisito acrescentado).

## Impact

- **Arquivos (apply, dentro de `code_prefixes`)**: `.apm/hooks/scripts/spec-trace.py` (novo), `.apm/hooks/scripts/_gherkin.py` (+`parse_scenarios`), `.apm/agents/sdlc-reviewer.agent.md`, `tests/hooks/test_spec_trace.py` (novo), `tests/agents/test_reviewer_scenarios.py` (novo).
- **Fora de `code_prefixes` (sessão principal)**: `README.md` (seção e aviso), cópias implantadas por `apm install` (`.claude/hooks/apm/`, `.github/hooks/scripts/apm/`, `.claude/agents/`, `.github/agents/`) e `apm.lock.yaml`, `CLAUDE.md` deste repo (opcional: citar o script nos quality gates). `harness.config.json` **não** muda.
- **Release**: `feat(agents):` (minor). Push, PR e mesclagem são do Elói. A branch está empilhada sobre `feat/f3-acceptance-from-spec` (PRs #33 a #36 abertos): o PR da F4 só faz sentido depois da F3.
- **Risco principal**: o comportamento do reviewer só se prova num projeto real; o teste do repositório prova o script (comportamento determinístico) e o texto do agente.
