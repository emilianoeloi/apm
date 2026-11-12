# Tasks

## 1. Contrato testável dos agentes

- [x] 1.1 Escrever `tests/agents/test_contract.py` (`unittest`) cobrindo os cenários de `sdlc-agent-contract` e as ferramentas por papel de `sdlc-agent-roles`, e verificar com `python3 -m unittest tests.agents.test_contract -v` que os testes falham enquanto os agentes não existem
- [x] 1.2 Acrescentar ao teste a checagem de implantação idêntica à fonte (`.claude/agents/sdlc-*.md` e `.github/agents/sdlc-*.agent.md`) e a de skills citadas existentes, e verificar que ela falha antes da reimplantação

## 2. Os quatro agentes

- [x] 2.1 Criar `.apm/agents/sdlc-planner.agent.md` (fase `proposal`, skills `openspec-explore`, `openspec-propose`, `spdd-analysis`, `spdd-reasons-canvas`, escrita só em pastas de planejamento) e verificar com os testes de contrato do planner
- [x] 2.2 Criar `.apm/agents/sdlc-coder.agent.md` (fase `apply`, skills `spdd-generate` e `openspec-apply-change`, escrita só em pastas de código e testes mais checkboxes do `tasks.md`, sensores antes de entregar, para sem canvas) e verificar com os testes de contrato do coder
- [x] 2.3 Criar `.apm/agents/sdlc-reviewer.agent.md` (somente leitura, confere Operations e tasks, `openspec validate --strict`, sensores, relatório com veredito e achados com arquivo, linha e Operation, achado de escopo) e verificar com os testes de contrato do reviewer
- [x] 2.4 Criar `.apm/agents/sdlc-auditor.agent.md` (somente leitura, opcional, evidências de arquivo e linha) e verificar com `python3 -m unittest tests.agents.test_contract -v`, que deve passar inteiro, exceto a implantação

## 3. Implantação e validação nos hosts

- [x] 3.1 Rodar `apm install --target claude,copilot` e verificar que `.claude/agents/sdlc-*.md` e `.github/agents/sdlc-*.agent.md` existem e que o teste de implantação passa
- [x] 3.2 Rodar `claude plugin validate .claude/agents` e verificar que nenhum agente é reportado com frontmatter inválido; se o comando não existir, registrar "não verificado"
- [x] 3.3 Rodar o teste de fumaça de somente leitura (`sdlc-reviewer` e `sdlc-auditor` sobre este repositório, sem permissão de escrita) e verificar que `git status --porcelain` fica idêntico antes e depois; se não for possível rodar, registrar "não verificado"

## 4. Documentação e skill

- [x] 4.1 Atualizar o `README.md` com a lista dos quatro agentes, a ordem de disparo pela sessão principal, os limites (escopo de escrita, Bash dos agentes de leitura, Copilot não verificado) e o aviso para quem usava os agentes da 0.3.x, e verificar relendo que cobre os cenários da spec
- [x] 4.2 Atualizar o modelo `CLAUDE.md.template` e o skill `install-dev-harness` com o fluxo por agentes (planner, aprovação, `phase_cli.py set apply`, coder, reviewer, auditor opcional) e verificar com `grep -n "sdlc-" .apm/skills/install-dev-harness/templates/CLAUDE.md.template .apm/skills/install-dev-harness/SKILL.md`
- [x] 4.3 Atualizar o `CLAUDE.md` do repositório com o quality gate dos agentes e verificar que o `python3 -m unittest discover -s tests -t .` cobre `tests/agents`

## 5. Integração

- [x] 5.1 Rodar `grep -rniE "cowboy|cobol|cobc|calculadora" .apm .claude .agents .github` e verificar que volta vazia
- [x] 5.2 Rodar `python3 -m unittest discover -s tests -t . -v` e `openspec validate agentes-sdlc --strict` e verificar que passam
- [x] 5.3 Registrar a F3 na seção da Onda 1 do `CHANGELOG.md` (resultado, itens não verificados e retrospectiva de skills) e verificar que o texto lista o que foi entregue

## Workflow follow-up

- Abrir o PR com título `feat: …` e esperar o "ok" do Elói para o push e a mesclagem.
- Não mesclar o PR de release do release-please antes da change de pré-lançamento.
- Reconciliar o código com o canvas (`/spdd-sync`), arquivar a change depois do merge e fazer a retrospectiva de skills.
