# Roteiro de teste manual

Roteiro de aceite do pacote `apm` (spec APM_SETUP V1.2). Cada passo diz o que rodar, o esperado e o resultado da última execução. Atualize a tabela de resultados a cada onda.

Última execução: Onda 1, sobre a tag `v1.0.0-alpha.1` (commit `8c3f94a`), em 2026-11-12.

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
| 6 | Pendente | depende do repositório `calculadora_go` |
| 7 | Passou (gate) | em `proposal`, escrita de `cmd/calculadora/main.go` bloqueada (saída 2); artefato de planejamento passa; em `apply` o mesmo arquivo passa. O `sdlc-planner` real ainda não foi rodado contra o gate |
| 8 | Pendente | depende do `calculadora_go` |
| 9 | Parcial | o `sdlc-reviewer` rodou de verdade no Claude Code (Onda 1, F3) e o `git status --porcelain` ficou idêntico; falta rodá-lo sobre a calculadora |
| 10 | Pendente | depende do `calculadora_go` |

## Itens conhecidos fora do roteiro

- O formato dos agentes e dos hooks no Copilot não foi verificado num Copilot real.
- O comportamento do `sdlc-planner` e do `sdlc-coder` (que escrevem) só se prova no fluxo completo da calculadora.
- Lacunas dos guardas de hook (`.env.local` e `.env.production` não são bloqueados, escrita por Bash só é checada para `.env`, ferramentas de escrita de MCP não passam pelo guarda): ver o CHANGELOG da F3.
