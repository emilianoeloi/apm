# Design

## Context

O pacote entrega skills (`openspec-*`, `spdd-*`), prompts (`/opsx-*`), hooks (gate de fase, guardas, Stop com sensores) e o `phase_cli.py`. `.apm/agents/` não existe desde a F1. O `harness.config.json` do projeto já informa as pastas de planejamento (`planning_write_prefixes`), as pastas de código (`code_prefixes`) e o comando de sensores (`sensors_command`), e o gate de fase bloqueia escrita fora do planejamento enquanto a fase é `proposal`.

Pesquisa feita para esta change (docs do APM, do Claude Code e do GitHub Copilot, e o Claude Code 2.1.316 instalado aqui):
- O APM copia `.apm/agents/<nome>.agent.md` **sem converter** para `.claude/agents/<nome>.md` e `.github/agents/<nome>.agent.md`. `model` e `tools` chegam verbatim; as docs recomendam omitir `model` num agente compartilhado, porque os identificadores de modelo são de cada fornecedor.
- Claude Code: `name` e `description` são obrigatórios; `tools` é texto separado por vírgula ou lista de nomes de ferramenta do Claude (`Read, Grep, Glob, Edit, Write, Bash, Skill`); se nenhuma entrada resolve, o subagente falha ao iniciar; campo desconhecido é ignorado sem aviso; `name` não pode começar com `-` nem ter `:`. `claude plugin validate <pasta>` checa o frontmatter de uma pasta de agentes (v2.1.233 em diante).
- Copilot: só `description` é obrigatório; `tools` aceita texto separado por vírgula ou lista; os nomes do Claude valem como alias (`Bash` para `execute`, `Read` para `read`, `Edit` e `Write` para `edit`, `Grep` e `Glob` para `search`, sem diferenciar caixa) e nomes desconhecidos são ignorados; `handoffs` é do VS Code e não vale para o agente de nuvem.
- Consequência: os agentes antigos (`tools: ['read', 'search', 'execute']`, `name: COBOL Reviewer`) provavelmente não carregavam no Claude Code. É o risco 2 da spec, que um formato único resolve.

## Goals / Non-Goals

**Goals:**
- Quatro agentes que carregam nos dois hosts a partir de um arquivo só, sem conversão.
- Escopo de escrita por papel, com o que dá para impor de forma mecânica e o resto declarado e verificável pelo reviewer.
- Contrato dos agentes coberto por testes, sem depender de rodar um modelo.

**Non-Goals:**
- Orquestração automática (skill `sdlc-orchestrator`, F4) e agentes `harness-*` (F5).
- Imposição mecânica de somente leitura para Bash (fase de revisão no gate): fica para a Onda 2.
- `/spdd-sync` por agente: a reconciliação código para canvas continua passo da sessão principal.
- Verificação num Copilot real e prova completa do fluxo (calculadora em Go).

## Decisions

1. **Um arquivo por papel, nomes `sdlc-<papel>`**, em `.apm/agents/`. O `name` do frontmatter é igual ao do arquivo, em minúsculas com hífen.
2. **Frontmatter mínimo e portátil:** `name`, `description`, `tools`. Sem `model` (recomendação das docs do APM), sem `handoffs` (é do VS Code e contraria a regra de não encadear), sem `skills:` (é do Claude e não existe no Copilot) e sem `color`. Os skills são citados pelo nome no corpo, com o caminho do `SKILL.md` como alternativa se a ferramenta `Skill` não estiver disponível.
3. **Ferramentas mínimas por papel, com nomes do Claude:**
   - `sdlc-planner`: `Read, Grep, Glob, Write, Edit, Bash, Skill`.
   - `sdlc-coder`: `Read, Grep, Glob, Write, Edit, Bash, Skill`.
   - `sdlc-reviewer` e `sdlc-auditor`: `Read, Grep, Glob, Bash` (sem `Write` e sem `Edit`).
   - Nenhum tem `Agent` nem `Task`. Alternativa descartada: `disallowedTools`, que o Copilot não conhece.
4. **Escopo de escrita:**
   - Planner: o gate de fase já bloqueia fora de `planning_write_prefixes` enquanto a fase é `proposal`; o planner só declara `proposal` se não houver fase ou se for `done`, e para se a fase for `apply`.
   - Coder: escreve só em `code_prefixes` (código e testes) e nos checkboxes do `tasks.md`; exige a fase `apply` e um canvas, e não promove a fase sozinho (quem promove é a sessão principal, depois do "ok" do humano). Não há bloqueio mecânico em `apply`, então o reviewer confere o escopo pelo diff e registra um achado se houver arquivo fora dele.
   - Reviewer e auditor: sem ferramentas de escrita; o texto proíbe comandos que alteram arquivos e exige conferir `git status --porcelain` no fim.
5. **Todo agente começa lendo o contexto do projeto:** o arquivo raiz do agente (`CLAUDE.md` ou `AGENTS.md`) e o `harness.config.json` (pastas de planejamento e de código, `sensors_command`, `phase_state_path`). Sem o `harness.config.json`, ou com campo vazio, o agente diz "não informado" em vez de supor; sem `sensors_command`, o coder e o reviewer relatam "sensores não configurados" e não afirmam que passaram.
6. **Saída do reviewer e do auditor na mensagem final, não em arquivo** (escrever o relatório violaria o somente leitura). Reviewer: veredito (`APROVADO`, `APROVADO COM RESSALVAS` ou `REPROVADO`), validação OpenSpec, sensores, progresso das tasks, escopo da implementação e tabela de achados com severidade, arquivo e linha, Operation do canvas, descrição e sugestão.
7. **Corpo curto e em português:** papel e escopo em duas frases, o que faz e o que não faz, entradas esperadas e saída, no máximo 300 linhas (recomendação das docs do APM).
8. **Testes de contrato em `tests/agents/`** (só `unittest`): quatro arquivos e nenhum outro, frontmatter e nomes de ferramenta válidos, ferramentas por papel, ausência de `model`, `handoffs`, `Agent` e `Task`, neutralidade de stack (termos do cowboy e de linguagens e ferramentas de build, `Makefile`, `src/`), skills citadas existem em `.apm/skills/` (antecipa o sensor anti-fantasma da Onda 2), tamanho do corpo e implantação idêntica à fonte.
9. **Verificação além dos testes:** `claude plugin validate .claude/agents` e um teste de fumaça de somente leitura (reviewer e auditor sobre este repositório, conferindo que o estado do git não muda). Se algum não puder rodar aqui, fica declarado como não verificado.
   - **Resultado no apply:** `claude plugin validate` passou. O reviewer e o auditor rodaram de verdade no Claude Code (`claude -p --agent <nome> --permission-mode dontAsk` com `--allowedTools` restrito a leitura e comandos de verificação) e o `git status --porcelain` ficou idêntico antes e depois nos dois. O reviewer leu a configuração, rodou a validação OpenSpec e os sensores, conferiu escopo e devolveu o relatório com veredito e achados com arquivo, linha e Operation. O auditor respondeu com arquivo e linha e separou fato de inferência. Planner e coder, que escrevem, não foram rodados fora de um projeto real. O CLI headless usou o modelo `sonnet`, passado por `--model`, porque o modelo padrão das settings do desenvolvedor não respondeu.

## Risks / Trade-offs

- [O comportamento de cada agente só se prova rodando um modelo] → testes de contrato, `claude plugin validate` e o teste de fumaça nesta change; a prova completa é a calculadora em Go.
- [Bash dos agentes somente leitura ainda consegue escrever arquivos] → ferramentas mínimas, texto que proíbe, conferência de `git status` e o reviewer registra escopo; a imposição mecânica (fase de revisão no gate) fica para a Onda 2.
- [O alias de ferramentas do Copilot vem só das docs] → declarado como não verificado num Copilot real; nomes desconhecidos são ignorados, então o pior caso é o agente ter mais ferramentas que o previsto.
- [A ferramenta `Skill` pode não estar disponível a um subagente] → o corpo manda ler o `SKILL.md` do skill (em `.claude/skills/` ou `.agents/skills/`) quando não puder invocá-lo.
- [Descrição vaga leva o host a disparar o agente sozinho, em especial o coder] → a descrição do coder diz que ele só deve ser usado com canvas aprovado e fase `apply`.
- [O formato dos agentes pode mudar nos hosts] → o teste de contrato e o `claude plugin validate` pegam a deriva na próxima atualização do pacote.
- [Aviso conhecido do APM sobre o skill `harness`] → sem relação com os agentes; segue registrado.

## Migration Plan

1. Escrever os testes de contrato (falhando), depois os quatro agentes até os testes passarem.
2. Reimplantar com `apm install --target claude,copilot`; conferir `.claude/agents/` e `.github/agents/` e rodar `claude plugin validate`.
3. Atualizar README, modelo de `CLAUDE.md`, skill `install-dev-harness` e CHANGELOG; rodar o teste de fumaça.
4. Abrir o PR `feat:`; mesclar e o PR de release seguem como atos do Elói.
5. Rollback: reverter o PR ou manter a dependência na tag da F2.
