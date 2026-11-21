# Tasks

## 1. Testes primeiro (vermelhos)

- [x] 1.1 Criar `tests/specs/__init__.py` e `tests/specs/test_gherkin_blocks.py`: leitor dos requisitos efetivos (specs principais trocadas pelos `ADDED`/`MODIFIED` dos deltas ativos, menos os `REMOVED`), teste em tabela da regra do formato (bloco ```` ```gherkin ````, depois do parágrafo e antes do primeiro `#### Scenario:`, `Cenário:`, `Dado`, `Quando`, `Então` nessa ordem, título igual ao de um `#### Scenario:`) e amostras negativas (sem bloco, bloco depois do cenário, sem `Então`, título sem correspondência, `Entao` sem acento); verificar que falha antes de o leitor existir por completo e que cada amostra negativa é reprovada
- [x] 1.2 Acrescentar em `tests/agents/test_contract.py` os testes de que `sdlc-planner.agent.md` e `openspec-workflow/SKILL.md` citam o bloco `gherkin` com `Dado`, `Quando` e `Então`, e de que as cópias implantadas são idênticas à fonte; verificar com `python3 -m unittest tests.agents.test_contract -v` que falham com o texto atual

## 2. Instruções do planner e do skill

- [x] 2.1 Acrescentar ao `.apm/agents/sdlc-planner.agent.md` a seção "Cenários Gherkin nas specs" (um bloco por requisito, posição, formato, título igual ao `#### Scenario:`, os `WHEN`/`THEN` continuam) e o passo na ordem de trabalho; sem termos de stack; verificar que o teste do 1.2 do planner e os testes de neutralidade passam
- [x] 2.2 Acrescentar ao `.apm/skills/openspec-workflow/SKILL.md` a seção do formato exato e um exemplo; verificar que o teste do 1.2 do skill passa
- [x] 2.3 Acrescentar `rules.specs` em `openspec/config.yaml` com a exigência do bloco (fora do escopo de escrita do coder: feito pela sessão principal ou pelo humano) e verificar com `openspec instructions specs --change cenarios-gherkin-na-spec --json` que a regra aparece
- [x] 2.4 Citar o bloco Gherkin na etapa "Propor" do fluxo SDD do `CLAUDE.md` e verificar relendo o texto

## 3. Implantação

- [x] 3.1 Rodar `apm install --target claude,copilot` e verificar que `.claude/agents/sdlc-planner.md`, `.github/agents/sdlc-planner.agent.md` e as cópias de `openspec-workflow` em `.claude/skills` e `.agents/skills` são idênticas à fonte (`diff`), e que `claude plugin validate .claude/agents` passa
- [x] 3.2 Conferir que `.apm/skills/openspec-propose/SKILL.md` não mudou (`git diff --stat`)

## 4. Integração

- [x] 4.1 Rodar `python3 -m unittest discover -s tests -t . -v` e verificar que tudo passa, inclusive o teste de formato sobre os requisitos efetivos
- [x] 4.2 Rodar `openspec validate cenarios-gherkin-na-spec --strict` e `openspec validate versao-final-1-0-0 --strict` e verificar que passam
- [x] 4.3 Rodar `grep -rniE "cowboy|cobol|cobc|calculadora" .apm` e verificar que volta vazia
- [ ] 4.4 Confirmar que o planner, dado um pedido de teste, gera requisitos com o bloco (verificação manual, registrada no PR; a fiscalização automática é do F2)

## Workflow follow-up

- Abrir o PR com título `feat(agents): …`; push e mesclagem são do Elói.
- Arquivar `versao-final-1-0-0` antes desta change; depois `openspec archive cenarios-gherkin-na-spec` e trocar o `## Purpose` provisório de `spec-gherkin-scenarios` por uma frase real, e então `openspec validate --specs --strict`.
