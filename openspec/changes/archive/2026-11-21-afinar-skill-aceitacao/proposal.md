# Proposal

## Why

As provas da F3 (projeto de prova `calculadora_go` e ramo sem framework) e a revisão da F4 mostraram seis atritos no skill `acceptance-from-spec` e nas tasks do planner. O skill hoje prova o ciclo (cenário, teste ligado por `Spec:`, vermelho, verde), mas deixa margem em pontos que o coder e o reviewer tiveram de resolver na hora:

1. **Falso verde.** Na prova sem framework o teste de "Sem argumento" passou sem o programa existir (o interpretador sai com 2 e escreve em stderr quando o arquivo falta); na F4, `python3 script-ausente.py` também sai 2. O vermelho veio do ambiente, não da asserção.
2. **`#### Scenario:` extras** (sem `Cenário:` no bloco): o skill diz que só viram teste se distintos, mas não diz como anotá-los sem criar `ORFAO` no `spec-trace`; o coder da F4 improvisou `# Extra (...): <trinca>`.
3. **Fixtures com linha `Spec:` em string** aparecem como `ORFAO`.
4. **Cenário de comportamento do modelo**, que só prova humana cobre: o skill não diz o que fazer.
5. **Skill x tasks do planner** divergiam: o skill manda um teste por `Cenário:` do bloco; as tasks mandavam cobrir todos os `#### Scenario:`.
6. **Cenário herdado em requisito `MODIFIED`**: o `spec-trace` já o trata como informativo; o skill ainda não diz isso.

Origem: follow-up das provas, fora da spec V2.0 (decisão do Emiliano). Não li a V2.0 no Drive; este pedido não depende dela.

## What Changes

Só adições e esclarecimentos; nenhum passo existente é removido nem muda de sentido; stack-agnóstico (nenhuma ferramenta de teste nomeada).

- **Skill `acceptance-from-spec`** (`.apm/skills/acceptance-from-spec/SKILL.md`, versão `1.0` para `1.1`):
  - Passo 1: cenário herdado (`MODIFIED`, idêntico à spec principal) não exige teste novo; o extra recebe a anotação `Extra: <capability> / <requisito> / <título do #### Scenario>` (nunca `Spec:`).
  - Passo 4: a linha `Spec:` dentro de fixture ou exemplo de teste é montada por constante, para não aparecer como `ORFAO`.
  - Passo 5: o vermelho vem da asserção do cenário; erro do ambiente (arquivo, módulo ou comando ausente, código de saída genérico) não é vermelho; teste que passa sem o programa é falso verde e se reforça afirmando o conteúdo; em linguagem compilada, símbolo de produção ausente declarado vale.
  - Passo 8: cenário que só a prova humana cobre vira pendente "prova humana" (`SEM_TESTE` conhecido, com a decisão do humano), sem teste que finja cobri-lo; o relatório lista extras, herdados e prova humana.
- **`sdlc-coder`**: um parágrafo curto no Entregável apontando as convenções do skill (sem duplicar o texto).
- **`sdlc-planner`**: uma seção curta "Tasks de teste": um teste por `Cenário:` do bloco, extras só se distintos (anotados `Extra:`), e a seção "Cenários só de prova humana" em `design.md`.
- **Testes**: extensão de `tests/agents/test_acceptance_skill.py` e `tests/agents/test_contract.py`, em tabela, com a linha `Spec:` dos cenários desta change.
- **README (sessão principal)**: um parágrafo na seção "Testes de aceitação" e aviso de migração.

**Rotina de quem opera:** depois de atualizar o pacote, o coder passa a relatar um teste que passa sem o programa como falso verde e a reforçá-lo; a prova humana de um cenário vira pendente explícito em vez de teste fingido; o planner passa a gerar tasks de teste por `Cenário:` e uma seção "Cenários só de prova humana". O reviewer não muda: um cenário de prova humana continua `SEM_TESTE` para ele, e a decisão do humano precisa ir no brief da revisão. Isso vai para o README e o CHANGELOG, não só para o design.

Fora desta change: mudar o `spec-trace.py` (por exemplo, reconhecer `Extra:` ou ignorar fixtures), mudar o reviewer, mudar a V2.0, perfis de SDLC, revisão cruzada, retrofit de cenários herdados sem teste, criar arquivos auxiliares do skill (pasta `references/`).

## Capabilities

### New Capabilities
Nenhuma.

### Modified Capabilities
- `acceptance-from-spec`: seis requisitos acrescentados (vermelho pela asserção, extra anotado, fixture por constante, prova humana, herdado, afinação só por adição e dentro do teto).
- `sdlc-agent-roles`: dois requisitos acrescentados (convenções no coder; regra das tasks no planner).
- `pacote-generico`: um requisito acrescentado (aviso de migração no README).

## Impact

- **Arquivos (apply, dentro de `code_prefixes`)**: `.apm/skills/acceptance-from-spec/SKILL.md`, `.apm/agents/sdlc-coder.agent.md`, `.apm/agents/sdlc-planner.agent.md`, `tests/agents/test_acceptance_skill.py`, `tests/agents/test_contract.py`.
- **Fora de `code_prefixes` (sessão principal)**: `README.md` (parágrafo e aviso), `CHANGELOG.md` (entrada manual, como na F4), `docs/roteiro-de-teste.md` (registro da prova), cópias implantadas por `apm install --target claude,copilot` (`.claude/skills/`, `.agents/skills/`, `.claude/agents/`, `.github/agents/`) e `apm.lock.yaml`, `CLAUDE.md` deste repo (opcional). `harness.config.json` não muda.
- **Release**: `feat(agents):` (minor), recomendação; push, PR e mesclagem são do Elói. Branch empilhada sobre `feat/f4-reviewer-confere-cenarios`; o PR #38 consolidado ainda está aberto.
- **Risco principal**: o comportamento do coder e do planner só se prova num projeto real; os testes provam o texto e a implantação. Dois cenários da change ficam `SEM_TESTE` conhecidos (prova humana).
