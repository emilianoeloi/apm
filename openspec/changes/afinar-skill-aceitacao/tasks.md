# Tasks

Cada teste novo traz, em comentário, a linha `Spec:` do seu cenário (montada por constante só dentro de fixtures). Os `#### Scenario:` extras (sem `Cenário:`) com teste levam `Extra:`: "Vermelho por erro do ambiente", "Extra anotado não vira órfão", "Teste que não prova o comportamento" e "Cópias do skill idênticas à fonte".

## 1. Testes primeiro (vermelhos)

- [x] 1.1 Em `tests/agents/test_acceptance_skill.py`, classe `AfinacaoDoSkillTest` (um método curto por cenário, trechos em tabela com `subTest`), cada método com a sua linha `Spec: acceptance-from-spec / <requisito> / <cenário>`: vermelho pela asserção (`falso verde`, `conteúdo`, `código de saída`, `erro do ambiente`); extra (`Extra:`, "nunca"); fixture (`por constante`, `ORFAO`); prova humana (`prova humana`, `decisão do humano`, `SEM_TESTE`); herdado (`herdado`, `informativo`); versão `1.1`; o `REQUIRED` antigo continua presente e o skill não passa de `MAX_LINES`; a linha `Extra: acceptance-from-spec / Afinação só por adição e dentro do teto / Cópias do skill idênticas à fonte` entra no teste de cópias idênticas que já existe (`CopiasImplantadasTest`). Verificar que falha porque os trechos ainda não existem
- [x] 1.2 Em `tests/agents/test_acceptance_skill.py`, caracterização com o `spec-trace.py` real (processo, projeto temporário via `tests.hooks._util.ProjectCase`, linha `Spec:` montada por constante): uma linha `Extra:` com a trinca de um extra não sai `ORFAO` e a saída é 0 (`Extra: ... / Extra anotado não vira órfão`); e o fonte de `test_acceptance_skill.py` não tem linha `Spec:` com três campos fora de comentário (`Spec: ... / Fixture montada por constante`). Relatar que a parte do script já passa antes da edição (sem vermelho natural) e que a parte de texto fica vermelha
- [x] 1.3 Em `tests/agents/test_acceptance_skill.py`, `ReadmeTest`: a seção "Testes de aceitação" do `README.md` cita `falso verde`, `Extra:`, `por constante` e `prova humana` (`pacote-generico / Aviso de migração para o skill afinado / Leitor de projeto na versão anterior`); prova o texto, não o comportamento. Ficará vermelho até a task 4.1 (sessão principal)
- [x] 1.4 Em `tests/agents/test_contract.py`, tabelas de trechos: o coder cita `falso verde` ou `asserção`, `Extra:`, `herdado`, `prova humana` e mantém `tools`; o planner cita "um teste por `Cenário:`", `Extra:` e `Cenários só de prova humana` e mantém `tools`; sem `STACK_TERMS`; corpo de cada agente continua dentro do teto de 300 linhas. Linhas `Spec:` de `sdlc-agent-roles / Coder aplica as convenções afinadas do skill / Texto do coder cita as convenções` e `... / Planner gera tasks coerentes com o skill / Texto do planner cita a regra das tasks`. Verificar que falha
- [x] 1.5 Registrar o comando e a contagem de falhas de 1.1 a 1.4 (`python3 -B -m unittest tests.agents.test_acceptance_skill tests.agents.test_contract`) para o relatório, com o motivo de cada vermelho (asserção de trecho ausente, não erro de importação)

## 2. Skill

- [x] 2.1 Editar `.apm/skills/acceptance-from-spec/SKILL.md` (só adições): `version: "1.1"`; passo 1 (herdado e `Extra:`); passo 4 (fixture por constante); passo 5 (vermelho pela asserção, falso verde, erro do ambiente, símbolo ausente em linguagem compilada); passo 8 (prova humana e listas à parte no relatório). Nenhum trecho antigo some; sem termo de stack nem de origem; até ~120 linhas
- [x] 2.2 Verificar que 1.1 e 1.2 passam (as cópias idênticas só depois da task 5.1)

## 3. Agentes

- [x] 3.1 Editar `.apm/agents/sdlc-coder.agent.md`: no Entregável, um parágrafo que aponta as convenções do skill (vermelho pela asserção e falso verde, `Extra:`, herdado informativo, prova humana pendente) por cenário, sem copiar o texto; `tools` e limites de escrita inalterados
- [x] 3.2 Editar `.apm/agents/sdlc-planner.agent.md`: seção "Tasks de teste" (um teste por `Cenário:` do bloco, extras só se distintos e com `Extra:`, "Cenários só de prova humana" em `design.md` com a task de prova); nada de termo de stack
- [x] 3.3 Verificar que 1.4 passa e `python3 -B -m unittest tests.agents.test_contract` fica verde (cópias dos agentes só depois da task 5.1)

## 4. Documentação (sessão principal, fora de `code_prefixes`; antes da integração)

- [x] 4.1 README, seção "Testes de aceitação": parágrafo das convenções e aviso de migração (falso verde, `Extra:`, fixture por constante, prova humana; o reviewer continua tratando esse cenário como `SEM_TESTE` e a decisão do humano vai no brief da revisão)
- [x] 4.2 `CHANGELOG.md`: entrada "Onda 2, F5" com a rotina que muda e a decisão do Elói sobre os 2 cenários de prova humana
- [x] 4.3 (opcional) `CLAUDE.md` deste repo: nada a acrescentar sem decisão

## 5. Implantação (sessão principal)

- [x] 5.1 Rodar `apm install --target claude,copilot`; conferir com `diff` as cópias do skill (`.claude/skills/`, `.agents/skills/`) e dos agentes (`.claude/agents/`, `.github/agents/`)
- [x] 5.2 Rodar `claude plugin validate .claude/agents`

## 6. Integração

- [x] 6.1 Rodar `python3 -B -m unittest discover -s tests -t . -v` e verificar que tudo passa (comando e contagem; separar da execução vermelha de 1.5)
- [x] 6.2 Rodar `openspec validate afinar-skill-aceitacao --strict` e `python3 -B .apm/hooks/scripts/gherkin-sensor.py` (deve sair 0)
- [x] 6.3 Rodar `grep -rniE "cowboy|cobol|cobc|calculadora" .apm` (deve voltar vazia) e `python3 -B .apm/hooks/scripts/spec-trace.py --root . --change afinar-skill-aceitacao`: esperado 9 cobertos, 2 `SEM_TESTE` conhecidos (prova humana), 0 órfãos, 4 extras
- [ ] 6.4 Prova de comportamento (humano, projeto de prova): disparar o coder real sobre uma change com um cenário só de prova humana e um extra com comportamento distinto, e o planner real sobre um pedido com um cenário e um extra; verificar o vermelho pela asserção, a linha `Extra:`, o pendente de prova humana e as tasks por `Cenário:`. Registrar em `docs/roteiro-de-teste.md`; o que não for executado, "não verificado"

## Workflow follow-up

- Abrir o PR com título `feat(agents): …` empilhado sobre a F4 (PR #38 aberto); push e mesclagem são do Elói.
- Depois do merge, `openspec archive afinar-skill-aceitacao`, trocar o `## Purpose` se vier provisório, rodar `openspec validate --specs --strict` e a retrospectiva de skills.
- Fora daqui: `spec-trace` reconhecer `Extra:`, reviewer aceitar a decisão de prova humana, retrofit de cenários herdados sem teste.
