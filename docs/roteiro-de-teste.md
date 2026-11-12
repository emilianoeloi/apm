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

## Itens conhecidos fora do roteiro

- O formato dos agentes e dos hooks no Copilot não foi verificado num Copilot real.
- Lacunas dos guardas de hook (`.env.local` e `.env.production` não são bloqueados, escrita por Bash só é checada para `.env`, ferramentas de escrita de MCP não passam pelo guarda): ver o CHANGELOG da F3.
