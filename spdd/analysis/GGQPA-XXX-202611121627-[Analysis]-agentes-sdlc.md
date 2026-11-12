# SPDD Analysis: Agentes de SDLC do pacote APM

## Original Business Requirement

Fonte: `APM_SETUP_V1.2.md` (Google Drive), funcionalidade F3 da Onda 1, mais a change `openspec/changes/agentes-sdlc/`. Trechos da spec, sem alteração:

> F3. Agentes de SDLC. Esforço M, valor $$$, confiança verde.
>
> H3. Como Elói, quero planejar por um sub-agente, para ter proposta, análise e canvas sem tocar em código.
> Dado um pedido de funcionalidade, quando disparo o sdlc-planner, então ele entrega a proposta OpenSpec, a análise e o REASONS Canvas.
> Dado o sdlc-planner em ação, quando ele tenta escrever fora de openspec/ e spdd/, então o gate de fase bloqueia.
> Dado o planejamento pronto, quando rodo openspec validate --strict, então a validação passa.
>
> H4. Como Elói, quero implementar por um sub-agente, para o código seguir o canvas.
> Dado um canvas aprovado e a fase "apply", quando disparo o sdlc-coder, então ele gera o código pelas Operations do canvas.
> Dado o código gerado, quando o sdlc-coder termina, então os sensores do projeto passam e as tasks estão marcadas.
> Dado um canvas ausente, quando disparo o sdlc-coder, então ele avisa e para.
>
> H5. Como Elói, quero uma revisão pronta para ler, para decidir o merge request com segurança.
> Dado o código implementado, quando disparo o sdlc-reviewer, então ele entrega um relatório com achados e veredito.
> Dado o sdlc-reviewer em ação, quando ele roda, então ele não altera nenhum arquivo.
> Dado o relatório, quando leio, então cada achado cita arquivo, linha e a Operation do canvas.
>
> H6. Como Elói, quero uma auditoria sob demanda, para tirar dúvidas sem mexer no código.
> Dado uma dúvida ou um pedido de auditoria, quando disparo o sdlc-auditor, então ele responde com evidências do repositório.
> Dado o sdlc-auditor em ação, quando ele roda, então ele não altera nenhum arquivo.
>
> Contrato dos agentes de SDLC: Fonte única: .apm/agents/sdlc-*.agent.md, entregue pelo APM para claude e copilot. Nenhum agente cita linguagem, pasta ou comando de um projeto. O que é do projeto vem do arquivo raiz do agente e do harness.config.json. Os agentes não se chamam entre si: a sessão principal dispara cada um. Cada agente tem escopo exclusivo de escrita, como pede a Ficha 166.
> sdlc-planner: fase "proposal". Usa openspec-explore, openspec-propose, spdd-analysis e spdd-reasons-canvas. Escreve só em openspec/ e spdd/. Nunca escreve código.
> sdlc-coder: fase "apply". Usa spdd-generate e openspec-apply-change. Escreve só nas pastas de código e de testes do harness.config.json. Roda o comando de sensores do projeto antes de entregar.
> sdlc-reviewer: só leitura. Confere o código contra as Operations do canvas e as tasks. Roda openspec validate --strict e os sensores. Entrega relatório para o humano decidir.
> sdlc-auditor: só leitura e opcional. Responde dúvidas e audita conformidade, arquitetura e segurança.
>
> Riscos: 2. Formato dos agentes: os atuais usam o formato do Copilot; a conversão para .claude/agents está não informada.
>
> Roteiro de teste manual: 2. Listar .apm/agents. Esperado: só sdlc-planner, sdlc-coder, sdlc-reviewer e sdlc-auditor. 7. Em fase "proposal", pedir ao sdlc-planner um arquivo .go. Esperado: bloqueio pelo gate. 8. Disparar o sdlc-coder com canvas aprovado. Esperado: código gerado e go test ./... verde. 9. Disparar o sdlc-reviewer. Esperado: relatório entregue e git status sem mudanças dele.
>
> Documentação: README do apm: o que é o pacote, como consumir a versão nova, os três blocos do fluxo e a lista de agentes.

## Domain Concept Identification

### Existing Concepts (from codebase)
- **Skills do fluxo SDLC**: `openspec-explore`, `openspec-propose`, `openspec-apply-change`, `spdd-analysis`, `spdd-reasons-canvas`, `spdd-generate` (vendorizados) e `openspec-workflow` (autoral), mais o prompt `/opsx-*`. Já entregues; os agentes os usam, não os substituem.
- **Gate de fase**: `phase_cli.py` e os hooks. Em `proposal`, só passa escrita em `planning_write_prefixes`; em `apply`, nada é bloqueado por fase.
- **Configuração do projeto (`harness.config.json`)**: pastas de planejamento e de código, `sensors_command`, `phase_state_path`. É a fonte do que é do projeto.
- **Entrega de agentes pelo APM**: `.apm/agents/<n>.agent.md` é copiado verbatim para `.claude/agents/<n>.md` e `.github/agents/<n>.agent.md`. `.apm/agents/` não existe desde a F1.
- **Contrato de testes**: a bateria `tests/hooks/` e o padrão de testes de pacote; `claude plugin validate` valida uma pasta de agentes no Claude Code.

### New Concepts Required
- **Agente de SDLC**: persona de papel único, de fonte única, disparada pela sessão principal, com ferramentas mínimas e escopo de escrita declarado.
- **Escopo exclusivo de escrita**: planejamento, código e testes, ou nada; verificável pelo gate (planner) ou pelo diff (coder).
- **Relatório de revisão**: veredito mais achados rastreados a arquivo, linha e Operation, entregue na mensagem e não em arquivo.
- **Formato portátil de agente**: o subconjunto de frontmatter que carrega nos dois hosts.

### Key Business Rules
- **Sem cadeia**: nenhum agente chama outro; a sessão principal orquestra (Mediator).
- **Neutralidade de stack**: nada de linguagem, pasta ou comando de projeto; o que é do projeto vem do arquivo raiz e da configuração.
- **Escopo exclusivo de escrita** por papel (Ficha 166).
- **Somente leitura** para reviewer e auditor.
- **Sem código antes da proposta aprovada**; o coder só atua com canvas aprovado e fase `apply`.
- **Sem push e sem publicação sem o "ok" do Elói**; o humano decide o merge.

## Strategic Approach

### Solution Direction
Escrever quatro arquivos de agente num formato único que os dois hosts carregam, com ferramentas mínimas por papel, e cobrir o contrato com testes estáticos, sem depender de rodar um modelo. Fluxo: pedido do humano → sessão principal declara a fase → dispara o planner (propose, analysis, canvas) → humano aprova → sessão principal declara `apply` → dispara o coder → dispara o reviewer → humano decide; o auditor entra sob demanda.

### Key Design Decisions
- **Frontmatter portátil com nomes de ferramenta do Claude**: o Claude Code falha ao iniciar se nenhuma ferramenta resolve, e o Copilot aceita esses nomes como alias → adotar, em vez de manter `read/search/execute`.
- **Sem `model`, `handoffs`, `skills:` e `color`**: modelos são de cada fornecedor, `handoffs` é do VS Code e contraria a regra de não encadear, `skills:` não existe no Copilot → omitir, citar skills pelo nome no corpo.
- **Escopo do coder verificado pelo reviewer**: não há bloqueio mecânico em `apply` → o reviewer confere o diff e registra achado de escopo.
- **Somente leitura por ferramentas mínimas**: Bash continua disponível para validar e rodar sensores; a imposição mecânica fica para a Onda 2.
- **Relatório na mensagem**: escrever arquivo violaria o somente leitura.
- **Testes de contrato estáticos**: dão confiança no formato e na neutralidade; o comportamento se prova na calculadora em Go.

### Alternatives Considered
- **Manter o formato do Copilot e converter por script para o Claude**: o APM não converte e o script seria outra peça a manter → rejeitado.
- **Um agente por host**: duplica fonte e contraria "fonte única" → rejeitado.
- **`disallowedTools` para os agentes de leitura**: o Copilot não o conhece → rejeitado em favor da lista mínima de `tools`.
- **Fase de revisão no gate nesta change**: ampliaria o escopo para hooks já fechados na F2 → adiada para a Onda 2.

## Risk & Gap Analysis

### Requirement Ambiguities
- **"Escreve só nas pastas de código e de testes" vs. marcar as tasks**: o coder precisa marcar checkboxes em `openspec/changes/<change>/tasks.md`; tratado como a única exceção, escrita no contrato e conferida pelo reviewer.
- **Quem declara a fase**: a spec não diz. Decisão desta change: a sessão principal declara `apply` (depois da aprovação humana); o planner só declara `proposal` se não houver fase ou se for `done`.
- **Quem faz `/spdd-sync`**: fora do contrato dos quatro agentes; fica com a sessão principal.
- **Como o reviewer "roda os sensores" sem poder alterar arquivos**: o comando vem da configuração e pode gerar artefatos (relatórios de teste); o reviewer confere `git status` no fim e relata qualquer mudança.

### Edge Cases
- **Sem `harness.config.json` ou com campos vazios**: os agentes dizem "não informado" e não supõem pastas nem comando.
- **Sem `sensors_command`**: coder e reviewer relatam "sensores não configurados" em vez de afirmar que passaram.
- **Ferramenta `Skill` indisponível ao subagente**: o corpo manda ler o `SKILL.md`.
- **Fase `proposal` e o coder disparado por engano**: o coder para ao ver que a fase não é `apply`.
- **Canvas existente porém não aprovado**: o coder só age com canvas que o humano aprovou; a sessão principal garante isso ao declarar `apply`.

### Technical Risks
- **Bash em agentes de leitura pode escrever**: mitigado por ferramentas mínimas, texto e conferência do estado do git; fica como risco residual declarado.
- **Alias de ferramentas do Copilot só nas docs**: não verificado num Copilot real.
- **Comportamento do modelo**: nenhum teste estático prova que o planner gera um canvas bom; a prova é a calculadora em Go.
- **Descrição que dispara o agente sozinho**: especialmente o coder; mitigado pela descrição.

### Acceptance Criteria Coverage
| AC# | Description | Addressable? | Gaps/Notes |
|-----|-------------|--------------|------------|
| 1 | `.apm/agents` lista só os quatro `sdlc-*` | Yes | Teste de contrato |
| 2 | Planner entrega proposta, análise e canvas; `validate --strict` passa | Partial | Estático (skills e saídas descritos); prova real na calculadora |
| 3 | Planner fora de `openspec/` e `spdd/`: o gate bloqueia | Yes | Gate já testado na F2; o agente só declara `proposal` |
| 4 | Coder gera pelas Operations, sensores passam, tasks marcadas | Partial | Contrato e instruções; prova real na calculadora |
| 5 | Coder sem canvas avisa e para | Yes | Instrução e teste de texto |
| 6 | Reviewer entrega relatório com arquivo, linha e Operation; não altera arquivo | Partial | Sem `Write`/`Edit`; fumaça de somente leitura; Bash residual |
| 7 | Auditor responde com evidências; não altera arquivo | Partial | Idem |
| 8 | Nenhum agente cita linguagem, pasta ou comando de projeto | Yes | Teste de neutralidade |
| 9 | Agentes não se chamam entre si | Yes | Sem `Agent`/`Task`; texto |
| 10 | Risco 2 (formato) resolvido | Yes | Formato portátil, `claude plugin validate`; Copilot não verificado |
