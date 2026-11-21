# Roteiro de teste manual

Roteiro de aceite do pacote `apm` (spec APM_SETUP V1.2). Cada passo diz o que rodar, o esperado e o resultado da última execução. Atualize a tabela de resultados a cada onda.

Última execução: Onda 1 completa, sobre a tag `v1.0.0-alpha.1` (commit `8c3f94a`) e sobre a `main` do projeto de prova `emilianoeloi/calculadora_go` (commit `3c06a5d`, com os PRs publicados), em 2026-11-12.

## Passos

1. **Busca de termos.** `grep -rniE "cowboy|cobol|cobc|calculadora" .apm`. Esperado: nenhum resultado, nem em hooks.
2. **Agentes.** `ls .apm/agents`. Esperado: só `sdlc-planner`, `sdlc-coder`, `sdlc-reviewer` e `sdlc-auditor`.
3. **Stop sem Makefile.** Rodar o hook de Stop numa pasta sem Makefile e sem `sensors_command`. Esperado: saída 0.
4. **Stop com sensor falhando.** Rodar o hook de Stop com `sensors_command` que falha. Esperado: saída 2 e a mensagem do sensor em stderr.
5. **Instalar a tag num repositório vazio.** `apm install --target claude,copilot` com a dependência `emilianoeloi/apm#v1.0.0-alpha.1`. Esperado: skills, agentes, prompts e hooks nos dois hosts.
6. **install-dev-harness na calculadora.** No projeto `calculadora_go`, rodar o skill `install-dev-harness`. Esperado: a verificação do harness passa inteira.
7. **Gate de fase.** Em fase `proposal`, pedir ao `sdlc-planner` um arquivo `.go`. Esperado: bloqueio pelo gate.
8. **Coder com canvas aprovado.** Disparar o `sdlc-coder`. Esperado: código gerado e `go test ./...` verde.
9. **Reviewer.** Disparar o `sdlc-reviewer`. Esperado: relatório entregue e `git status` sem mudanças feitas por ele.
10. **Divisão por zero.** Rodar a calculadora dividindo por zero. Esperado: mensagem de erro, sem pânico.

## Resultados

| # | Resultado | Evidência |
|---|---|---|
| 1 | Passou | busca vazia em `.apm/` e nos diretórios implantados |
| 2 | Passou | quatro arquivos `sdlc-*.agent.md`, nenhum outro |
| 3 | Passou | scripts implantados da tag, projeto sem configuração: saída 0 |
| 4 | Passou | `sensors_command` com `exit 7`: saída 2 e a mensagem do sensor em stderr |
| 5 | Passou | instalação real da tag (`@8c3f94ad`): 6 prompts, 8 agentes (4 por host), 6 comandos, 18 skills e os hooks em `.claude/settings.json` e `.github/hooks/`; nenhum termo do cowboy no instalado |
| 6 | Passou | Onda 0 da `calculadora_go` com a tag `v1.0.0-alpha.1`: `session-start.py` imprime `additionalContext`, `openspec list` sem erro, `phase_cli.py show` ok, 5 skills `spdd-*` e 6 comandos `opsx-*` nos dois hosts, cada evento de hook uma vez em `.claude/settings.json`, Stop com `sensors_command` vazio sai 0, `git push` e escrita fora da raiz bloqueados, nenhum arquivo legado |
| 7 | Passou (gate) e parcial (agente) | o gate bloqueia a escrita de um `.go` em `proposal` (saída 2) e libera em `apply`, testado com os hooks implantados. O `sdlc-planner` real rodou duas vezes no projeto de prova (`calculadora-basica` e `numeros-especiais-e-formato`), gravou só em `openspec/` e `spdd/`, deixou a fase em `proposal` e não escreveu código. **Não exercitado:** pedir de propósito um arquivo `.go` ao planner real |
| 8 | Passou | o `sdlc-coder` real gerou o código pelo canvas nas duas funcionalidades; `go vet ./...` e `go test -count=1 ./...` passam na `main` publicada, com cobertura de 100% em `internal/calculo` e `internal/cli` |
| 9 | Passou | o `sdlc-reviewer` real rodou duas vezes sobre a calculadora e entregou relatório com veredito (`APROVADO COM RESSALVAS`) e achados com arquivo, linha e Operation; a árvore de trabalho ficou idêntica. Também rodou sobre o próprio `apm` (F3) com o mesmo resultado |
| 10 | Passou | `divisao 6 0`, `divisao 0 0` e `divisao 6 -0` imprimem `erro: divisão por zero` em `stderr`, `stdout` vazio, saída 1, sem pânico; nenhum `panic` nem `recover` no código; entradas inválidas também não causam pânico |

## Critérios da história H7 (calculadora em Go)

| Critério | Resultado |
|---|---|
| `install-dev-harness` instala sem ajuste manual no pacote | Passou, com a ressalva do `go.mod` (abaixo) |
| Planner, coder e reviewer entregam a funcionalidade num merge request | Passou na 2ª funcionalidade: PR [calculadora_go#1](https://github.com/emilianoeloi/calculadora_go/pull/1), mesclado. A 1ª funcionalidade foi publicada direto em `main`, sem PR, e isso não tem correção retroativa |
| `go test ./...` passa | Passou |
| Prova aprovada pelo Elói, então a 1.0.0 final pode sair | **Pendente** da aprovação explícita do Elói |

## Achados da prova (para a Onda 2)

- **Hook de Stop sem `go.mod`:** com `sensors_command` igual a `go test ./...` e ainda sem `go.mod`, o Stop bloqueia qualquer encerramento. O comportamento está correto (o sensor falha de verdade), mas falta um modo "sensor ainda não aplicável" ou a regra de só configurar o comando depois de o código existir.
- **`go.mod` sem dono:** nenhum agente cobre o arquivo de módulo (o coder só escreve em `code_prefixes`); a sessão principal criou o `go.mod` e atualizou o README. O `install-dev-harness` ou o orquestrador (F4) deveria prever esse pré-requisito.
- **Harness acoplado à pasta da sessão:** os hooks usam `CLAUDE_PROJECT_DIR`; uma sessão aberta num projeto não consegue disparar agentes para escrever num projeto vizinho (o guarda de escrita bloqueia, corretamente). Funciona abrindo a sessão na pasta do projeto.
- **Funcionalidade fora do fluxo:** nada no harness impede publicar direto em `main`; a proteção de branch no repositório ou o `sdlc-orchestrator` (F4) deveriam impor "uma funcionalidade, uma branch, um PR".
- **Formato de saída decimal:** o formato escolhido (`strconv.FormatFloat` com `'g'`) imprime `1e+06` para um milhão e `1.23456789e+08` para 123456789; é decisão de produto da calculadora, registrada como característica conhecida, e não falha do harness.
- **Nomes `GGQPA-XXX`:** os skills de SPDD geram arquivos com um número de ticket que o projeto não tem; vale a pena aceitar um prefixo configurável.

## Prova da Onda 1 da rodada V2.0 (cenário, teste de aceitação e sensor)

Projeto de prova: `emilianoeloi/calculadora_go`, clone descartável no scratchpad, apm instalado da **fonte local** (sem push nem tag) na branch `feat/f3-acceptance-from-spec`. Mudança de prova: a operação `resto`.

| Passo | Resultado |
|---|---|
| Instalar o apm novo no projeto | `go test ./...` segue verde; skill, sensor, hook `PostToolUse` e agentes instalados |
| Rodar o sensor nas specs existentes | **Falha com 14 violações** (nenhum requisito tinha bloco): projetos antigos precisam de retrofit |
| Retrofit dos 14 requisitos (change própria) | Sensor sai 0 com a change ativa e depois de arquivada; texto e cenários WHEN/THEN idênticos |
| Planner gera `operacao-de-resto` | Requisitos com bloco gherkin e `#### Scenario:`; `openspec validate --strict` e sensor ok |
| Coder escreve o teste antes do código | Vermelho: build falhou com 3 `undefined: Resto`; na CLI, 2 testes de topo e 7 subtestes falharam. Verde: `go test ./...` com 17 subtestes `Spec:` |
| Reviewer confere | Aprovado com ressalvas; mutações pensadas (módulo estilo Python, `math.Remainder`, sem `b==0`, sem `verificarFinito`) seriam pegas |
| `git push` | Bloqueio coberto pelos testes do hook; não tentado de novo |

**Ramo "sem framework" (segunda prova).** Num projeto mínimo sem teste, manifesto nem linguagem (change `saudacao`, dois cenários), o coder real parou com `BLOQUEADO: ferramenta de teste não definida (nada escrito, aguardando ferramenta)`: `src/` ficou vazia, as tasks desmarcadas, os dois cenários pendentes, e propôs três opções sem instalar nada. Com a ferramenta aprovada (Python `unittest`, registrada pela sessão principal no `CLAUDE.md` e no `sensors_command`), ele retomou: vermelho (2 testes, 1 falha; depois do reforço, 2 falhas), verde (`discover` executou os 2 testes `Spec:`), sensor de Gherkin 0. Achado: o teste de "Sem argumento" passou sem o programa existir, porque o interpretador sai com código 2 e escreve em stderr quando o arquivo falta; o coder o reforçou (stdout vazio e mensagem do programa). Vale uma linha no skill: o vermelho precisa vir da asserção do cenário, não de erro do ambiente.

**Limites da prova.** O disparo ao vivo do hook `PostToolUse` não foi observado numa sessão real; só o payload simulado. O vermelho vem do relatório do coder e da estrutura dos testes; o git não registra a ordem das escritas. Nenhum cenário de `resto` ficou sem teste, mas 3 cenários herdados de um requisito modificado ficaram sem linha `Spec:`.

**Achados para o pacote**
- **Retrofit é parte da migração:** adotar o sensor num projeto com specs antigas falha até o bloco ser acrescentado; o README agora avisa.
- **Skill e tasks divergem:** o skill manda um teste por `Cenário:` do bloco; o planner mandou cobrir também todos os `#### Scenario:`. Alinhar.
- **Cenário herdado em requisito modificado:** não está dito se precisa de teste `Spec:`; a F4 precisa decidir.
- **Sensor não lê testes:** sai 0 sem nenhuma linha `Spec:`; o vínculo só será conferido pela F4.
- **Nome de subteste (Go):** espaços viram `_` e ` / ` vira hierarquia; o `grep` no fonte é o mais seguro.
- **Teste defensivo sem cenário:** o skill não diz como marcá-lo.
- **Instalação suja o `git status`:** os arquivos do apm se misturam à change; vale commitar a instalação à parte.
- **Hooks e outra pasta:** desta vez a escrita no projeto de prova passou porque ele estava em `/private/tmp`, liberado em `allowed_write_roots`; a limitação de `CLAUDE_PROJECT_DIR` da prova anterior continua valendo para outras pastas.

## Prova do reviewer (F4, task 6.4)

Projeto mínimo `semfw` (Python `unittest`), apm da F4 instalado da fonte local, change de prova `saudacao-composta` montada com defeitos conhecidos, sem dizer ao reviewer o que esperar: um cenário novo sem teste, um requisito novo sem teste, um marcador `Spec:` com título errado (`Nome compostos`), um teste vazio (`assertTrue(True)`) e tasks marcadas sem código.

| Defeito plantado | O reviewer real |
|---|---|
| cenário novo sem teste (`Nome composto`) | `SEM_TESTE`, severidade alta |
| requisito novo sem teste (`Saudação formal`) | `SEM_TESTE`, severidade alta |
| marcador com título errado | `ORFAO`, severidade média |
| teste que não afirma o `Então` | apontado como falso verde (alta), com leitura do teste |
| tasks marcadas sem código | apontado: `saudacao.py` não implementa nada novo |
| cenário já existente e com teste | `COBERTO` (lido: afirma `Olá, Ana!` e código 0) |

Veredito: **REPROVADO**. Ele também achou um defeito que eu não tinha plantado de propósito: a classe de teste nova estava depois do `if __name__ == "__main__"` e nunca rodava; foi um erro meu ao montar a fixture.

**Atritos**
- O reviewer, nessa execução, não tinha a ferramenta `Glob` (só `Bash` e `Read`) e usou `find . -name spec-trace.py`. Achou 4 cópias, 3 delas em `apm_modules/`. Usou a implantada em `.claude/hooks/apm/...`. Vale o agente dizer que a cópia certa é a do host, fora de `apm_modules/`, e que `find` é o plano B.
- Sem o relatório do coder, o vermelho aparece como "não verificado", como o agente manda.
- Ele não usou a reserva `grep -F`.

**Limites.** É uma prova com um modelo e uma fixture. Ela mostra o comportamento de uma revisão, não a taxa de acerto; os dois cenários `SEM_TESTE` conhecidos de `sdlc-agent-roles` seguem sem teste automático.

## Prova das convenções do skill e da cópia do reviewer (F5 e F6, tasks 6.4)

Projeto mínimo `semfw` (Python `unittest`), com o apm do `main` já com a F5 e a F6 (skill 1.1 e `spec-trace.py` endurecido), instalado da fonte local. Change de prova `despedida`: programa que imprime `Tchau, <nome>!`, erro com código 2 sem argumento e `--formal` com `Até logo, <nome>.`. Planner, coder e reviewer reais, sem dizer o que esperar; a sessão principal aprovou as decisões baixas da fixture (Q1 a Q3) como recomendadas.

| Passo | Resultado |
|---|---|
| Planner real (F5, "Tasks de teste") | um teste por `Cenário:` do bloco, cada um com a linha `Spec:`; o `#### Scenario:` extra ("Formal sem nome") ligado por `Extra:`, nunca `Spec:`; o teste de erro afirma o conteúdo (stdout vazio, stderr com "Erro:" e "nome"), não só o código 2; reconheceu o `unittest` já aprovado no `CLAUDE.md`, sem parar para propor ferramenta |
| Coder real (F5, vermelho pela asserção) | vermelho por cenário: `'' != 'Tchau, Ana!'`, `1 != 2` e `'Tchau, Ana!' != 'Até logo, Ana.'`; verde com os 6 testes pelo `sensors_command`; `Extra:` no extra; nenhum arquivo `*-E` |
| Reviewer real (F6, cópia do host) | sem `Glob` nesta execução, usou `find`, achou 4 cópias do `spec-trace.py` (3 em `apm_modules/`) e usou a implantada no host; 3 `COBERTO`, 0 órfãos, 1 extra; leu cada teste; veredito aprovado |

**Limites.** O falso verde de "Sem argumento" não foi exercido: o coder implementou o passo 1 antes de rodar o teste de erro, e este falhou com código 1 (`IndexError`), não com 2; o que a prova mostra é que o planner e o coder escreveram o teste de erro afirmando o conteúdo. O planner não invocou os skills `spdd-analysis` e `spdd-reasons-canvas` (escreveu a análise e o canvas à mão e declarou), e Q2 e Q3 (argumento depois do nome, argumentos extras) ficam sem cenário nem teste. É uma prova com um modelo e uma fixture, sem taxa de acerto.

## Itens conhecidos fora do roteiro

- O formato dos agentes e dos hooks no Copilot não foi verificado num Copilot real.
- Lacunas dos guardas de hook (`.env.local` e `.env.production` não são bloqueados, escrita por Bash só é checada para `.env`, ferramentas de escrita de MCP não passam pelo guarda): ver o CHANGELOG da F3.
