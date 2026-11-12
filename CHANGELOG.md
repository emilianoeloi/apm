# Changelog

## Preparação da 1.0.0 final (2026-11-12)

Change `versao-final-1-0-0`. A prova da calculadora em Go foi aprovada pelo Elói; esta change faz a configuração propor a `1.0.0`. Nada é publicado até o Elói mesclar este PR e, depois, o PR de release.

### O que muda

* `release-please-config.json`: `"prerelease"` passa de `true` para `false`. As chaves `"versioning": "prerelease"` e `"prerelease-type": "alpha.1"` **ficam** até a tag `v1.0.0` existir.
* O teste de configuração (`tests/release/`) passa a guardar a versão final e a armadilha da saída precoce da estratégia de pré-lançamento.
* README e `CLAUDE.md` descrevem o estado novo; a spec `release-versioning` troca os dois requisitos do período de pré-lançamento (cumpridos) pelo requisito da versão final.

### Verificação

* Simulação executando a biblioteca `release-please` nas versões `17.6.0` e `17.11.2` (12 de 12 cenários ok): de `1.0.0-alpha.1`, com commits só de documentação, com `feat` ou com mudança incompatível, a próxima versão é `1.0.0`; depois dela, `feat` resulta em `1.1.0`, `fix` em `1.0.1` e incompatível em `2.0.0`.
* Armadilha medida: se `versioning` fosse removido antes da tag final, o bot proporia `2.0.0-alpha.1` (incompatível) ou `1.1.0-alpha.1` (`feat`) a partir de `1.0.0-alpha.1`. Por isso a chave fica, e o teste falha se ela sair enquanto o manifesto tiver um sufixo de pré-lançamento.
* `python3 -m unittest discover -s tests -t .` e `openspec validate versao-final-1-0-0 --strict`: ok.
* **Não verificado (depende do GitHub):** o PR de release real propondo `1.0.0`, a linha `version:` do `apm.yml` sem sufixo e o GitHub Release publicado sem a marca de pré-lançamento. A conferência é depois do merge, antes de mesclar o PR de release.

### Depois do merge

1. Conferir que o bot atualizou o PR de release para `1.0.0` (título, `apm.yml`, manifesto e CHANGELOG): tags `v*` não se apagam nem se movem.
2. O Elói mescla o PR de release; nascem a tag `v1.0.0` e o GitHub Release.
3. Depois da tag: trocar o exemplo de consumo do README para `#v1.0.0`, apontar o `calculadora_go` para a `v1.0.0`, remover `versioning` e `prerelease-type` (com o teste ajustado) e arquivar a change.

### Retrospectiva de skills

* A simulação com a biblioteca (incluindo a armadilha da estratégia padrão) é o procedimento certo para qualquer mudança de versionamento do release-please; candidato a skill público de CI (Onda 3).
* Nenhum skill foi publicado sem o "ok" do Elói.

## Prova da calculadora em Go (2026-11-12)

Projeto de prova: [`emilianoeloi/calculadora_go`](https://github.com/emilianoeloi/calculadora_go), criado do zero sobre o pré-lançamento `v1.0.0-alpha.1` (o código da calculadora nunca entra neste repositório). Resultados por passo em [docs/roteiro-de-teste.md](docs/roteiro-de-teste.md).

### Resultado

* **Onda 0 do projeto:** o skill `install-dev-harness` instalou o harness a partir da tag publicada, sem ajuste manual no pacote; a verificação passou inteira.
* **Funcionalidade 1 (`calculadora-basica`):** `sdlc-planner` (proposta, specs, design, tasks, análise e canvas), `sdlc-coder` (código em `cmd/` e `internal/`) e `sdlc-reviewer` (relatório com veredito e achados com arquivo, linha e Operation) rodaram de verdade. Quatro operadores, divisão por zero devolve erro sem pânico. Publicada direto em `main`, sem pull request.
* **Funcionalidade 2 (`numeros-especiais-e-formato`):** feita em branch e fechada no PR [calculadora_go#1](https://github.com/emilianoeloi/calculadora_go/pull/1), mesclado: entradas `nan`, `inf`, hexadecimais e sublinhados rejeitadas (saída 2), overflow vira erro (saída 1) e o zero negativo sai como `0`.
* **Conferência independente, na `main` publicada (`3c06a5d`):** `go vet` e `go test -count=1 ./...` passam, com 100% de cobertura em `internal/calculo` e `internal/cli`; todos os cenários do roteiro batem; nenhum commit nem a descrição do PR cita o assistente.

### Achados (para a Onda 2)

* Hook de Stop sem `go.mod`: com `sensors_command` igual a `go test ./...`, o Stop bloqueia qualquer encerramento até o módulo existir. Falta um modo "sensor ainda não aplicável".
* `go.mod` sem dono: nenhum agente cobre o arquivo de módulo (o coder só escreve em `code_prefixes`); a sessão principal teve de criá-lo.
* Harness acoplado à pasta da sessão: uma sessão aberta em outro projeto não consegue disparar agentes para escrever na pasta da calculadora (o guarda de escrita bloqueia, corretamente); funciona abrindo a sessão no projeto.
* Nada impede publicar direto em `main`: a 1ª funcionalidade saiu sem PR e não há correção retroativa sem reescrever o histórico. Proteção de branch ou o `sdlc-orchestrator` (F4) devem impor "uma funcionalidade, uma branch, um PR".
* Os skills de SPDD geram nomes com `GGQPA-XXX` quando o projeto não tem ticket; vale um prefixo configurável.

### Não verificado

* O comportamento do `sdlc-planner` quando se pede de propósito um arquivo `.go` em `proposal` (o gate foi provado pelos hooks, e o planner real ficou dentro de `openspec/` e `spdd/`).
* O formato dos agentes e dos hooks num Copilot real.
* A aprovação da prova pelo Elói, que libera a `1.0.0` final.

### Retrospectiva de skills (fecha a Onda 1)

* **Funcionaram sem ajuste:** `install-dev-harness`, `sdlc-planner`, `sdlc-coder` e `sdlc-reviewer` no projeto de prova.
* **A atualizar (público):** `openspec-workflow` (divergência do schema em todas as changes), orientação de adaptar o canvas a mudanças que não são de backend, e o `install-dev-harness` (pré-requisitos do projeto, como o `go.mod`, e a ordem de configurar o `sensors_command`).
* **Procedimentos reutilizáveis:** teste de fumaça de agente no host, conferência independente numa cópia limpa da `main` e verificação do pré-lançamento executando a biblioteca do release-please.
* Nada foi publicado sem o "ok" do Elói.

## Onda 1 — fechamento (2026-11-12)

A Onda 1 (MVP: F1, F2 e F3) foi publicada como o pré-lançamento `1.0.0-alpha.1`. Roteiro de teste em [docs/roteiro-de-teste.md](docs/roteiro-de-teste.md).

### Publicado

* Tag `v1.0.0-alpha.1` (commit `8c3f94a`), com o GitHub Release marcado como **Pre-release**; a `v0.3.1` segue como a última versão estável (`Latest`). O manifesto e a linha `version:` do `apm.yml` estão em `1.0.0-alpha.1`.
* A seção `1.0.0-alpha.1` gerada pelo release-please lista a remoção do cowboy como mudança incompatível, como a spec pede.
* Fecha o que estava "não verificado" na change do pré-lançamento: o bot atualizou o PR #12 para `1.0.0-alpha.1`, o `apm.yml` aceitou a versão com sufixo e o Release saiu como pré-lançamento.

### Verificação (roteiro de teste)

* Instalação real da tag num repositório vazio (`apm install --target claude,copilot` com `emilianoeloi/apm#v1.0.0-alpha.1`): 6 prompts, 8 agentes (4 por host), 6 comandos, 18 skills e os hooks nos dois hosts, sem nenhum termo do cowboy. Os scripts de hook implantados passaram nas 8 verificações (Stop sem configuração sai 0, Stop com sensor que falha sai 2 com a saída, `git push` e `.env` bloqueados, configuração corrompida não trava, Copilot devolve JSON `deny`).
* Gate de fase no projeto instalado: em `proposal`, a escrita de um arquivo `.go` é bloqueada; artefatos de planejamento passam; em `apply` o mesmo arquivo passa.
* O `apm install` não exigiu `apm approve` (o APM informa "Executable-trust gate disabled" quando o `apm.yml` não declara `executables:`).
* Resultado por passo: itens 1 a 5 passaram, o gate do item 7 passou, o item 9 ficou parcial (o reviewer já rodou no Claude Code, falta sobre a calculadora) e os itens 6, 8 e 10 dependem do projeto `calculadora_go`.

### Retrospectiva de skills da Onda 1

* **Usados:** `openspec-explore`, `openspec-propose`, `openspec-apply-change`, `openspec-archive-change`, `openspec-workflow`, `spdd-analysis`, `spdd-reasons-canvas`, `spdd-generate`, `install-dev-harness` e, só de leitura, `skill-retrospective`. Nenhum skill do repositório privado serviu.
* **Desatualizado ou incompleto:**
  * `openspec-workflow` divergiu do schema nas quatro changes (criação manual do `.openspec.yaml`, fases das tasks, canvas pensado para backend). É a atualização de maior prioridade (público).
  * `spdd-reasons-canvas` e `spdd-generate` (vendorizados) exigiram adaptação à mão para mudanças que não são de backend; a orientação deve morar no `openspec-workflow`, nunca nos arquivos vendorizados.
  * `install-dev-harness` foi atualizado na Onda 0, na F2 e na F3 (hooks e agentes pelo APM, `sensors_command`, `allowed_write_roots`); falta publicar uma versão do skill.
* **Procedimentos que serviriam a outros projetos (públicos):**
  * teste de fumaça de agente no host (`claude -p --agent <nome>` com permissões só de leitura, comparando o `git status`), para `dev-harness-architect` e `harness-quadrant-process`;
  * checagem do hook disparando de verdade no host, e não só os testes de saída;
  * como configurar e verificar o pré-lançamento do release-please executando a biblioteca, para o skill de CI da Onda 3.
* **Skill novo:** o `sdlc-orchestrator` já está previsto para a Onda 2 (F4). Nada foi publicado sem o "ok" do Elói.

### Pendências e próximos passos

* Prova com a calculadora em Go (`emilianoeloi/calculadora_go`) sobre a `1.0.0-alpha.1`; só depois, `"prerelease": false` para a `1.0.0`.
* Onda 2 (F4, F5 e F8), incluindo a imposição mecânica de somente leitura para os agentes de leitura.
* Lacunas dos guardas de hook apontadas na F3 (`.env.local`, escrita por Bash, ferramentas de MCP, `.gitignore` sem regra de credenciais).
* O guarda de escrita barra caminhos fora do repositório; quem quiser salvar arquivos fora dele (por exemplo, a pasta de memória do assistente) precisa listá-los em `allowed_write_roots`.

## Onda 1 — Pré-lançamento 1.0.0-alpha.1 (2026-11-12)

Change `prelancamento-alpha`. Última peça do MVP da Onda 1 (F1, F2 e F3). Ainda sem tag e sem push; a tag `v1.0.0-alpha.1` só nasce quando o Elói mesclar o PR de release.

### Novidades

* `release-please-config.json` passa a usar a estratégia de pré-lançamento (`versioning: "prerelease"`, `prerelease: true`, `prerelease-type: "alpha.1"`). O PR de release #12, que propunha `1.0.0`, passa a propor `1.0.0-alpha.1`; a tag será `v1.0.0-alpha.1` (sem componente) e o GitHub Release sai marcado como pré-lançamento.
* Os pré-lançamentos seguintes numeram sozinhos (`alpha.2`, `alpha.3`, …), sem `release-as` para lembrar de remover.
* A `1.0.0` final fica a uma mudança de configuração (`"prerelease": false`), depois da prova da calculadora em Go.
* Teste de configuração em `tests/release/` (nenhum `release-as`, chaves do pré-lançamento, tag sem componente, `apm.yml` e manifesto em sincronia, workflow sem mesclagem automática); a suíte passa a ter 110 testes.
* README: seção de pré-lançamento (última estável `v0.3.1`, como consumir a tag, como a final sai) e correção da frase sobre o marcador, que não existe no `apm.yml`.

### Verificação

* A pesquisa fecha o "não informado" da spec: o tipo `alpha` sem número daria `1.0.0-alpha`; `alpha.1` dá `1.0.0-alpha.1` e depois o último número sobe. Confirmado lendo o código da estratégia e **executando a biblioteca** `release-please` nas versões `17.6.0` (piso da ação) e `17.11.2`: 16 de 16 cenários ok (primeira publicação, `alpha.2` a `alpha.5` com `feat`, `fix`, `chore`/`ci` e incompatível, e `1.0.0` com `prerelease` falso).
* A configuração valida contra o schema oficial (`schemas/config.json`) com `jsonschema`.
* `python3 -m unittest discover -s tests -t .`: todos ok; busca por "cowboy", "cobol", "cobc" e "calculadora" em `.apm/`, `.claude/`, `.agents/` e `.github/`: vazia.
* **Não verificado (depende do GitHub):** o efeito no PR #12 real, a linha `version:` do `apm.yml` com sufixo de pré-lançamento no diff do PR de release e a criação do GitHub Release como pré-lançamento. A conferência é depois do merge, antes de mesclar o PR de release.

### Depois do merge

1. O bot atualiza o PR #12 sozinho (push na `main`). Conferir título, `apm.yml`, manifesto e CHANGELOG: tags `v*` não se apagam nem se movem.
2. O Elói mescla o PR de release; a tag `v1.0.0-alpha.1` e o GitHub Release de pré-lançamento nascem.
3. Fechar a Onda 1: README com o consumo da tag nova, CHANGELOG, roteiro de teste manual e retrospectiva.
4. Prova da calculadora em Go sobre a `1.0.0-alpha.1`; só depois, `"prerelease": false` para a `1.0.0`.

### Retrospectiva de skills

* O "não informado" da spec virou procedimento reutilizável (ler a estratégia de versionamento do release-please e executá-la fora do repositório). Candidato a skill público ou a um passo do `install-dev-harness` quando a F6 (CI em camadas) chegar.
* `install-dev-harness`: sem mudança nesta change.
* `openspec-workflow`: continua pendente de atualização (ver as retrospectivas anteriores).

## Onda 1 — F3: agentes de SDLC (2026-11-12)

Change `agentes-sdlc`. Ainda sem tag e sem push; só falta a change de pré-lançamento (`1.0.0-alpha.1`) para fechar o MVP da Onda 1.

### Novidades

* Quatro agentes de papel único e fonte única em `.apm/agents/`, entregues pelo `apm install` para `.claude/agents/` e `.github/agents/`:
  * `sdlc-planner` (fase `proposal`): proposta OpenSpec validada, análise e REASONS Canvas; escreve só nas pastas de planejamento.
  * `sdlc-coder` (fase `apply`): código pelas Operations do canvas, tasks marcadas e sensores antes de entregar; escreve só em `code_prefixes` e nos checkboxes do `tasks.md`; para sem canvas.
  * `sdlc-reviewer` (somente leitura): confere código, Operations e tasks, roda a validação e os sensores e entrega relatório com veredito e achados (arquivo, linha e Operation).
  * `sdlc-auditor` (somente leitura, opcional): responde e audita com evidências de arquivo e linha.
* Formato único para os dois hosts: `name`, `description` e `tools` com nomes do Claude Code (o Copilot os aceita como alias), sem `model` e sem `handoffs`. Resolve o risco 2 da spec: os agentes antigos usavam `tools: ['read', 'search', 'execute']`, que o Claude Code não reconhece, e o APM copia o arquivo sem converter.
* Os agentes não se chamam entre si: a sessão principal dispara cada um (`Agent` e `Task` fora de `tools`).
* Testes de contrato em `tests/agents/` (formato, ferramentas por papel, neutralidade de stack, skills citadas existem, implantação idêntica à fonte); a suíte inteira tem 100 testes.
* README com a lista de agentes, a ordem de disparo e os limites; modelo de `CLAUDE.md` e skill `install-dev-harness` com o fluxo por agentes.

### Verificação

* `python3 -m unittest discover -s tests -t .`: 100 testes ok. Busca por "cowboy", "cobol", "cobc" e "calculadora" em `.apm/`, `.claude/`, `.agents/` e `.github/`: vazia.
* `claude plugin validate .claude/agents`: passou.
* **Teste de fumaça no Claude Code** (`claude -p --agent … --permission-mode dontAsk`, permissões restritas a leitura e verificação): o `sdlc-reviewer` revisou esta própria change e devolveu o relatório com veredito, achados com arquivo, linha e Operation, e o resultado da validação e dos sensores; o `sdlc-auditor` respondeu a uma pergunta de segurança com evidências. Nos dois, o `git status --porcelain` ficou idêntico antes e depois.
* **Não verificado:** o comportamento do `sdlc-planner` e do `sdlc-coder` (escrevem) fora de um projeto real, que é o que a prova com a calculadora em Go vai exercitar, e o carregamento dos quatro agentes num Copilot real.

### Observações

* O somente leitura do reviewer e do auditor vem de ferramentas mínimas e de texto; o `Bash` deles ainda poderia escrever. A imposição mecânica (uma fase de revisão no gate) fica para a Onda 2. O escopo do coder em `apply` não tem bloqueio mecânico e é conferido pelo reviewer.
* O CLI headless do Claude Code não funcionou com o modelo padrão das settings locais do desenvolvedor (modelo local sem resposta); o teste de fumaça passou `--model sonnet`.
* Lacunas dos guardas de hook que o auditor apontou, a tratar numa change própria: `.env.local` e `.env.production` não são bloqueados (só o nome exato `.env`); a escrita por Bash só é checada para `.env`; ferramentas de escrita de MCP não passam pelo guarda; o `.gitignore` do repositório não tem regra para credenciais.

### Retrospectiva de skills

* `openspec-workflow`: terceira change seguida em que o roteiro dele diverge do que o schema pede (criação manual do `.openspec.yaml`, fases das tasks, canvas pensado para backend). Prioridade para atualizar (público).
* `spdd-reasons-canvas` e `spdd-generate` (vendorizados): de novo adaptados à mão para uma mudança que não é de backend; a orientação deve ir no `openspec-workflow`.
* `dev-harness-architect` e `harness-quadrant-process`: devem recomendar o teste de fumaça de um agente no host (`claude -p --agent <nome> --allowedTools …`), que aqui provou o somente leitura e o formato, além de `claude plugin validate`. Proposta de atualização, skill público.
* `install-dev-harness`: atualizado para o fluxo por agentes. Skill novo: o `sdlc-orchestrator` já está previsto para a Onda 2 (F4); nada além disso.

## Onda 1 — F2: hooks genéricos (2026-11-12)

Change `hooks-genericos`. Ainda sem tag e sem push; a F3 e o pré-lançamento `1.0.0-alpha.1` vêm depois.

### Novidades

* Hook de Stop `stop-sensors`: roda o `sensors_command` do `harness.config.json` (vazio por padrão). Sem comando, sem arquivo ou sem Makefile, o encerramento é permitido; sensor que falha ou estoura `sensors_timeout_seconds` bloqueia com código 2 e mostra a saída. Estouro de tempo mata o grupo de processos, sem sensor órfão.
* Entrega pelo APM: hooks e scripts em `.apm/hooks/`; `apm install --target claude,copilot` registra `SessionStart`, `PreToolUse` e `Stop` em `.claude/settings.json` e `.github/hooks/` e implanta os scripts, sem cópia manual. O risco 1 da spec está resolvido.
* Pre-commit genérico em `.apm/scripts/git-hooks/pre-commit`, que roda o mesmo `sensors_command`.
* `allowed_write_roots` (opt-in, vazio por padrão) para escrita fora do projeto, como `/tmp`.
* Primeira bateria de testes do pacote (`tests/`, `unittest`, 81 testes), usada como `sensors_command` do próprio repositório.

### Correções

* Hooks não quebram mais com configuração ou payload ausente, corrompido ou de tipo errado; as defesas embutidas seguem valendo sem configuração.
* Contenção de caminho exata (`/tmp/proj-outro` deixou de passar como se fosse `/tmp/proj`), nos guardas e no `phase_cli.py`; `phase_cli.py show` aguenta estado corrompido.
* Bloqueio no formato de cada host: código 2 e motivo em stderr no Claude Code; JSON `deny` no Copilot. Antes só existia o JSON, que o Claude Code não usa para bloquear.
* Padrões de comando ancorados na posição de comando: `git push` citado em texto (mensagem de commit, corpo de PR) não bloqueia mais.
* Padrão de `git branch` só bloqueia `-D`; `git branch -a` e `-vv` passam.
* O skill `install-dev-harness` deixou de copiar scripts e de mesclar `settings.json`; o modelo de `harness.config.json` perdeu a entrada de pre-commit inexistente.

### Mudanças de quem usa o pacote

* Projetos que copiaram `scripts/hooks/` (0.3.x) devem apagar a cópia e deixar o `apm install` registrar os hooks, para não duplicar. Os padrões de comando nos `harness.config.json` existentes não mudam sozinhos: copie os novos do modelo.
* O `.claude/hooks/<pacote>/` e `.github/hooks/scripts/<pacote>/` passam a existir no projeto; o caminho usa o nome do pacote (`apm`).

### Verificação

* `python3 -m unittest discover -s tests -t .`: 81 testes ok. Busca por "cowboy", "cobol", "cobc" e "calculadora" em `.apm/`, `.claude/`, `.agents/`, `.github/` e `apm.lock.yaml`: vazia.
* Projeto consumidor temporário que depende do pacote: instalação ok e 8/8 verificações dos scripts implantados (Stop sem configuração sai 0; Stop com sensor que falha sai 2 com a saída; Bash bloqueado; escrita em `.env` bloqueada; configuração corrompida não trava; Copilot devolve JSON `deny`).
* **Claude Code real:** com os hooks entregues pelo APM ativos na sessão, o guarda de Bash e o de escrita bloquearam comandos reais (código 2, motivo em stderr). Foi assim que apareceram a menção em texto e a pasta temporária fora do projeto.
* **Não verificado:** o formato do Copilot (`.github/hooks/`) e a decisão `agentStop` dele num Copilot real; só há testes de saída. O comportamento de `apm approve` para pacotes remotos também não foi exercitado (a dependência local foi aceita sem aprovação).

### Observações

* O aviso do APM "Skill 'harness' replaced overlapping files" segue aparecendo a partir da segunda rodada do `apm install` (registrado na F1).
* Meus testes numa cópia temporária deixaram recibos em `~/.apm/deployment-receipts` (sem efeito neste repositório; não removidos).
* Sem hooks ativos no repositório, `git push` e demais comandos destrutivos passam a ser bloqueados nas sessões do Claude Code: o push precisa ser feito pelo desenvolvedor.

### Retrospectiva de skills

* `install-dev-harness`: atualizado nesta change (hooks pelo APM, `sensors_command`, pre-commit opcional, `allowed_write_roots`); os furos da Onda 0 foram fechados. Falta publicar o skill; nada foi publicado sem o "ok".
* `dev-harness-architect` e `harness-quadrant-process`: devem pedir um teste de fumaça de que o hook dispara no host (aqui o formato errado passou despercebido porque o bloqueio nunca era exercitado). Proposta de atualização, skill público.
* `openspec-workflow`: continua com os pontos da F1 (criação manual do `.openspec.yaml`, fases das tasks); candidato a receber também a orientação de adaptar o canvas a mudanças que não são de backend.
* Skill novo: nenhum necessário.

## Onda 1 — F1: limpeza do cowboy (2026-11-12)

Change `limpeza-do-cowboy`. Ainda sem tag e sem push; a F2, a F3 e o pré-lançamento `1.0.0-alpha.1` vêm depois.

### ⚠ BREAKING

* Removidos os agentes `cobol-vibecoder`, `cobol-planner`, `cobol-coder`, `cobol-reviewer` e `readme-writer`.
* Removidos os prompts `criar-programa`, `implementar-soma`, `implementar-subtracao`, `implementar-log`, `testar-programa`, `atualizar-readme` e `manutencao-repositorio`.
* Removidas as skills `cobol-calculadora`, `vibe-coding-fundamentals` e `readme-manutencao`.
* Removidos o pre-commit que compilava COBOL e o guia `cowboy.instructions.md`. O hook `cowboy.json` já saíra na Onda 0.
* Quem depende da 0.3.x deve manter a tag `v0.3.1` (aviso de migração no README).

### Mudanças

* `openspec-workflow` sem exemplos COBOL; `HARNESS_QUADRANTE.md` virou modelo com campos a preencher.
* `apm.yml`: nome `apm` e descrição genérica (a versão segue com o release-please). README público, sem "extraído do cowboy", com aviso de migração.
* `.harness/` no `.gitignore`.
* Pacote reimplantado com `apm install --target claude,copilot`: 36 arquivos antigos limpos de `.claude/`, `.agents/` e `.github/`.

### Verificação

* Busca por "cowboy", "cobol", "cobc" e "calculadora" em `.apm/`, `.claude/`, `.agents/`, `.github/agents`, `.github/prompts` e `apm.lock.yaml`: vazia.
* `session-start.py`, `openspec list`, `phase_cli.py show` e `openspec validate limpeza-do-cowboy --strict`: ok.
* `.apm/agents/` ficou sem arquivos e a pasta deixou de existir no git (o APM avisa sobre `.gitkeep` em pasta de agentes); a F3 a recria com os agentes `sdlc-*`.

### Observações

* O `apm install` (0.35.0) mostra, a partir da segunda rodada, o aviso "Skill 'harness' replaced overlapping files from another package". Os arquivos implantados estão corretos e o lockfile só lista o pacote local; causa não identificada, vale reportar ao projeto do APM se persistir.
* Testes numa cópia temporária deixaram 6 recibos de implantação em `~/.apm/deployment-receipts` (arquivos sem efeito neste repositório); não foram removidos.

### Retrospectiva de skills

* `openspec-workflow` (autoral): manda criar `.openspec.yaml` e as pastas à mão, mas o `openspec new change` já faz isso; e a lista de fases das tasks (Propose, Analysis, Canvas, Generate, Review) não bate com os grupos que o schema `spec-driven` pede (cada grupo com seus testes e documentação). Proposta: atualizar o skill (público). Nada publicado.
* `spdd-reasons-canvas` e `spdd-generate` (vendorizados): os modelos são de backend Java (controller, service, anotações) e servem mal a mudanças de empacotamento ou documentação; adaptei as seções à mão. Como são vendorizados, a orientação para esses casos deve ir no `openspec-workflow` (público), não nos arquivos do vendor.
* `install-dev-harness`: os furos da Onda 0 seguem abertos (guia de pre-commit no template, fonte local no passo 3, chave `_comment` do `settings.hooks.json`). Skill novo: nenhum necessário.

## Onda 0 — preparo do repositório (2026-11-12)

Spec: APM_SETUP V1.2. Nenhuma tag e nenhum push; a Onda 1 (1.0.0-alpha.1) ainda não começou.

### Feito

* Removido `.apm/hooks/cowboy.json` (hook de Stop do cowboy que exigia `make fitness`).
* Harness instalado no próprio repositório pela **fonte local** (`apm install --target claude,copilot`, sem instalar a tag v0.3.1): `apm.lock.yaml`, `.claude/`, `.agents/`, `.github/agents/` e `.github/prompts/`.
* Estado do OpenSpec criado com `openspec init --tools none --language português` (`openspec/`); pastas `spdd/analysis/` e `spdd/prompt/`.
* Gate de fase: `harness.config.json` (planejamento em `openspec/`, `spdd/`, `.harness/`; código em `.apm/`, `scripts/`, `tests/`), `scripts/hooks/*.py`, `scripts/harness/phase_cli.py`, `.claude/settings.json` e `CLAUDE.md` (quality gates: não informado).

### Verificação

* `session-start.py` imprime JSON com `additionalContext`: ok.
* `openspec list` roda sem erro: ok.
* `phase_cli.py show` mostra a fase (não declarada): ok.
* `spdd-*/SKILL.md` e `opsx-*.prompt.md` existem em `.claude/skills/` e `.github/prompts/`: ok.
* `.apm/hooks/cowboy.json` não existe mais: ok.

### Observações

* O APM aceitou a fonte local do próprio repositório (risco 3 da spec não se confirmou).
* `apm install` ainda implanta agentes, prompts e skills COBOL em `.claude/`, `.agents/` e `.github/`, e avisa de frontmatter não suportado nos prompts do cowboy. Saem na Onda 1 (F1).
* Os hooks de segurança ainda não são entregues pelo APM (`.apm/_pending/hooks/harness.json`); por isso os scripts foram copiados para `scripts/` e registrados em `.claude/settings.json`.

### Retrospectiva de skills

* `install-dev-harness`: o template `harness.config.json.template` lista `.pre-commit-config.yaml` em `guide_files` mesmo sem o arquivo existir, gerando um "MISSING" falso (removido à mão aqui). O passo 3 só cobre `apm install <repo>#<tag>`, não a fonte local. `settings.hooks.json` traz uma chave `_comment` que precisou ser tirada ao criar `.claude/settings.json`. Proposta: atualizar o skill (público, serve a qualquer projeto). Nada publicado.
* Skill novo: nenhum necessário nesta onda.

## [1.0.0-alpha.1](https://github.com/emilianoeloi/apm/compare/v0.3.1...v1.0.0-alpha.1) (2026-11-12)


### ⚠ BREAKING CHANGES

* agentes, prompts e skills do cowboy deixam de existir; quem depende deles deve manter a tag v0.3.1.

### Features

* agentes de SDLC genéricos sdlc-planner, coder, reviewer e auditor (F3) ([#14](https://github.com/emilianoeloi/apm/issues/14)) ([ff3afa6](https://github.com/emilianoeloi/apm/commit/ff3afa62fd13d61f98868b6722f8e7938791356a))
* hooks genéricos com sensores configuráveis e entrega pelo APM (F2) ([#13](https://github.com/emilianoeloi/apm/issues/13)) ([db5389e](https://github.com/emilianoeloi/apm/commit/db5389efa36b29f3808c578638d75781d91b7cf0))
* remove o conteúdo do cowboy e neutraliza o pacote (F1) ([#11](https://github.com/emilianoeloi/apm/issues/11)) ([021fc8c](https://github.com/emilianoeloi/apm/commit/021fc8c123a121023a7da923cbf8b92777b0a43d))

## [0.3.1](https://github.com/emilianoeloi/apm/compare/v0.3.0...v0.3.1) (2026-11-11)


### Bug Fixes

* **release:** tag sem o nome do componente (vX.Y.Z) ([#8](https://github.com/emilianoeloi/apm/issues/8)) ([70812ed](https://github.com/emilianoeloi/apm/commit/70812ed29b8774245a9354753228c4cd4124fb6a))

## [0.3.0](https://github.com/emilianoeloi/apm/compare/harness-v0.2.0...harness-v0.3.0) (2026-11-11)


### Features

* pacote APM com o harness extraido do cowboy ([789c49e](https://github.com/emilianoeloi/apm/commit/789c49e155b64916185a57fe86315feca5293ad7))
* **skills:** install-dev-harness com fluxo APM + OpenSpec + OpenSPDD ([#3](https://github.com/emilianoeloi/apm/issues/3)) ([76f66a7](https://github.com/emilianoeloi/apm/commit/76f66a78e0c8a7b7dc4372ab6655844754dd097c))
* **skills:** skill-retrospective e passo de retrospectiva no fluxo ([#5](https://github.com/emilianoeloi/apm/issues/5)) ([368a0e8](https://github.com/emilianoeloi/apm/commit/368a0e8c56969231e75ef1618341cf43c50491fa))
* vendoriza OpenSpec e OpenSPDD (original) no pacote APM ([#4](https://github.com/emilianoeloi/apm/issues/4)) ([c29d3a7](https://github.com/emilianoeloi/apm/commit/c29d3a7d1a9819fe1802076cb8427858d973f231))


### Bug Fixes

* **hooks:** regex de bloqueio so casa no inicio do comando ([#2](https://github.com/emilianoeloi/apm/issues/2)) ([335a22e](https://github.com/emilianoeloi/apm/commit/335a22e9d7c6fda64f1c1adba302a4491c8bdb92))
