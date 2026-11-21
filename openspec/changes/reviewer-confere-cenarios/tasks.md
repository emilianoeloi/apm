# Tasks

## 1. Testes primeiro (vermelhos)

- [x] 1.1 Criar `tests/hooks/test_spec_trace.py` (em tabela, script chamado como processo em projeto temporário, como `test_gherkin_sensor.py`): cenário `ADDED` coberto (`COBERTO` com arquivo:linha) e sem teste (`SEM_TESTE`, saída 2); `MODIFIED` com cenário herdado (`HERDADO_SEM_TESTE`, saída 0) e alterado (exigido); `RENAMED` seguido para achar a base; prefixo mais longo ("Caso" contra "Caso feliz"); fechamento de comentário depois do título; `ORFAO` (título errado, cenário removido); `AMBIGUO` (nomes com ` / ` que colidem); `--change` filtra os deltas; `--tests` restringe a busca; exclusões de pasta e `.md` ignorado; arquivo binário, ilegível e maior que 1 MiB ignorados; sem `openspec/` sai 0 avisando; sem change ativa sai 0; resumo com `extras: N`; árvore e pasta dos scripts intactas depois da execução (nenhum `__pycache__` novo). Verificar que falha porque o script não existe
- [x] 1.2 Em `tests/hooks/test_spec_trace.py`, caso da biblioteca: `_gherkin.parse_scenarios` devolve `(título, passos)` por `Cenário:`, preserva a ordem, devolve `[]` sem bloco e não altera `validate`; verificar que falha
- [x] 1.3 Criar `tests/agents/test_reviewer_scenarios.py` (em tabela): o reviewer cita `spec-trace.py`, `Glob`, `Spec:`, `grep -F`, `HERDADO`, `Cenários x testes`, `REPROVADO`, `falso verde`, `órfã` (ou `ORFAO`), `fonte`; `tools` continua `Read, Grep, Glob, Bash`; o passo novo vem antes de "Relatório"; sem `STACK_TERMS` e sem os quatro termos de neutralidade; cópias do agente (`.claude/agents/`, `.github/agents/`) e do script e de `_gherkin.py` (`.claude/hooks/apm/.apm/hooks/scripts/`, `.github/hooks/scripts/apm/.apm/hooks/scripts/`) idênticas à fonte; `harness.json` não cita `spec-trace`; verificar que falha
- [x] 1.4 Registrar comando e contagem de falhas de 1.1 a 1.3 para o relatório

## 2. Biblioteca e script

- [x] 2.1 Acrescentar `parse_scenarios(body)` a `.apm/hooks/scripts/_gherkin.py` (só acréscimo)
- [x] 2.2 Criar `.apm/hooks/scripts/spec-trace.py`: `sys.dont_write_bytecode = True` antes dos imports locais; opções `--root`, `--change`, `--tests`; classificação novo/alterado/herdado contra a spec principal; casamento por prefixo mais longo; `COBERTO`, `SEM_TESTE`, `HERDADO_SEM_TESTE`, `ORFAO`, `AMBIGUO`; resumo; saídas 0 e 2; só biblioteca padrão e `_gherkin`/`_common`; nunca escreve
- [x] 2.3 Verificar que 1.1 e 1.2 passam e que `python3 -B .apm/hooks/scripts/spec-trace.py --root .` roda neste repositório sem criar arquivo (`git status --porcelain` igual)

## 3. Reviewer

- [x] 3.1 Editar `.apm/agents/sdlc-reviewer.agent.md`: passo novo em "O que você faz" (conferir cenário contra teste: achar o script por `Glob`, rodar `python3 -B <caminho> --root . --change <nome>`, reserva com `grep -rnF`; ler cada teste ligado e checar que afirma o `Então`); regras de escopo (herdado informativo), de severidade e de veredito; seção "Cenários x testes" em "Relatório"; nota de que o literal é conferido no fonte, não na saída verbosa do executor; nada de ferramenta nova, nada de termos de stack
- [x] 3.2 Verificar que 1.3 e todo `tests/agents` passam (`python3 -B -m unittest tests.agents.test_contract tests.agents.test_reviewer_scenarios`)

## 4. Documentação (sessão principal, fora de `code_prefixes`)

- [x] 4.1 README: seção "Conferência de cenários na revisão" (o que o reviewer confere, a convenção `Spec:`, novo/alterado vs herdado, severidades, como rodar o script à mão, limite: prova o vínculo e não a qualidade do teste)
- [x] 4.2 README: aviso de migração (o reviewer passa a reprovar cenário novo/alterado sem teste; cenários antigos não são exigidos; fixtures com `Spec:` aparecem como órfãos)
- [x] 4.3 (opcional) `CLAUDE.md` deste repo: citar `spec-trace.py` nos quality gates

## 5. Implantação (sessão principal)

- [x] 5.1 Rodar `apm install --target claude,copilot`; conferir com `diff` as cópias do agente, de `spec-trace.py` e de `_gherkin.py` nos dois hosts
- [x] 5.2 Rodar `claude plugin validate .claude/agents`

## 6. Integração

- [x] 6.1 Rodar `python3 -B -m unittest discover -s tests -t . -v` e verificar que tudo passa
- [x] 6.2 Rodar `openspec validate reviewer-confere-cenarios --strict` e `python3 -B .apm/hooks/scripts/gherkin-sensor.py` (deve sair 0)
- [x] 6.3 Rodar `grep -rniE "cowboy|cobol|cobc|calculadora" .apm` e verificar que volta vazia
- [ ] 6.4 Prova de comportamento (humano, projeto de prova): disparar o reviewer sobre uma change com um cenário sem teste, um `Spec:` com título errado e um cenário herdado; verificar a seção "Cenários x testes", o veredito `REPROVADO`, o herdado só informativo e o `git status --porcelain` igual. Registrar no PR; o que não for executado, registrar como "não verificado"

## Workflow follow-up

- Abrir o PR com título `feat(agents): …` depois dos PRs da F3; push e mesclagem são do Elói.
- Depois do merge, `openspec archive reviewer-confere-cenarios`, trocar o `## Purpose` provisório de `spec-trace` por uma frase real, rodar `openspec validate --specs --strict` e a retrospectiva de skills.
- Fora daqui: linha no skill `acceptance-from-spec` sobre vermelho vindo da asserção (Q8) e retrofit de cenários herdados sem teste.
