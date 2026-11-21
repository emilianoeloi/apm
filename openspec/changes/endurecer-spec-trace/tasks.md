# Tasks

## 1. Testes primeiro (vermelhos pela asserção)

- [x] 1.1 Em `tests/hooks/test_spec_trace.py`, teste de aceitação do cenário "Arquivo trocado por FIFO depois da listagem", com a linha `# Spec: spec-trace / Busca em arquivos de teste com exclusões / Arquivo trocado por FIFO depois da listagem`: subprocesso `python3 -B -I -c` que carrega `spec-trace.py` por `importlib`, troca `os.open` por invólucro que registra as flags, troca o arquivo por FIFO e delega; afirma `O_NONBLOCK` e `O_NOFOLLOW` nas flags e `read_text` devolvendo `None` em até 10 s. Vermelho esperado: asserção das flags (o invólucro nunca é chamado). Registrar comando, contagem e mensagem
- [x] 1.2 Em `tests/hooks/test_spec_trace.py`, estender `test_fechamento_de_comentario_depois_do_titulo` com a linha `# Spec: spec-trace / Fim do título do marcador / Fechamento conhecido depois do título` e uma tabela de fechamentos de `CLOSERS` (`*/`, `-->`, `--]]`, `--}}`, `%}`, `?>`, `"`, `'`, `` ` ``, `)`, `]`, `}`, `#`, `//`) x espaço (`""`, `" "`, `"\t"`, `" "`), cada um com `subTest`; esperar `COBERTO`. **Verde de nascença** (caracterização): provar que morde com a mutação manual `lstrip()` por `lstrip(" ")` em `ends_title`, ver falhar o caso de tab e NBSP e reverter; registrar isso no relatório
- [x] 1.3 Em `tests/hooks/test_spec_trace.py`, estender `test_sufixo_alfanumerico_depois_do_titulo_vira_orfao` (renomear para `test_sufixo_que_nao_e_fechamento_vira_orfao`) com a linha `# Spec: spec-trace / Fim do título do marcador / Sufixo que não é fechamento` e os sufixos `" - feliz"`, `"_2"`, `"."`, `" (extra)"`, `", feliz"`, além dos alfanuméricos atuais; esperar `ORFAO`, `SEM_TESTE` do cenário e saída 2. Vermelho esperado: asserção (hoje saem `COBERTO`)
- [x] 1.4 Em `tests/hooks/test_spec_trace.py`, comentários `# Extra (#### Scenario: sem Cenário: no bloco, não exigido): <trinca>` nos testes que já provam os extras novos (`Marcador sozinho na linha` no teste do fim de linha, `Link, FIFO e dispositivo` nos dois testes de FIFO e de link); sem mudar o comportamento
- [x] 1.5 Em `tests/agents/test_reviewer_scenarios.py`, teste do cenário "Cópia certa do script" com `# Spec: sdlc-agent-roles / Reviewer confere cada cenário contra um teste / Cópia certa do script`: o texto do reviewer contém `apm_modules`, `find`, `.claude/hooks/apm/.apm/hooks/scripts/spec-trace.py` e `.github/hooks/scripts/apm/.apm/hooks/scripts/spec-trace.py`. Vermelho esperado: `assertIn` falha
- [x] 1.6 Em `tests/agents/test_reviewer_scenarios.py`, estender `ReadmeTest` com a regra do fim do título (por exemplo `fechamento de comentário` e `ORFAO`); a linha `Spec:` de `pacote-generico` já existe. Vermelho esperado: asserção, até o README ser editado (4.1)
- [x] 1.7 Rodar `python3 -B -m unittest discover -s tests -t .`, registrar comando e contagem de falhas de 1.1, 1.3, 1.5 e 1.6 e o motivo de cada vermelho (asserção, não erro de ambiente)

## 2. Script

- [x] 2.1 `.apm/hooks/scripts/spec-trace.py`: reescrever `read_text` (decisão 1): `os.open` com `O_RDONLY | O_NONBLOCK | O_NOFOLLOW` via `getattr(os, ..., 0)`, `os.fstat` no descritor, leitura do descritor até `MAX_BYTES + 1`, `finally` fechando; `OSError` e `UnicodeDecodeError` devolvem `None`
- [x] 2.2 `.apm/hooks/scripts/spec-trace.py`: constante `CLOSERS` e `ends_title` por `startswith(CLOSERS)` (decisão 2); atualizar o docstring do módulo e do `--help` com a regra do fim do título, mantendo "não é o veredito", `ORFAO`, `AMBIGUO` e "severidade média"
- [x] 2.3 Verificar que 1.1 a 1.4 passam e que `python3 -B .apm/hooks/scripts/spec-trace.py --root .` roda neste repositório sem criar arquivo (`git status --porcelain` igual)

## 3. Reviewer

- [x] 3.1 `.apm/agents/sdlc-reviewer.agent.md`: em "Cenários x testes → Como conferir", dizer que a cópia certa é a implantada do host (os dois caminhos) e nunca a de `apm_modules/`, e que sem `Glob` o plano B é `find . -name spec-trace.py -not -path "*/apm_modules/*"`; sem termos de stack, `tools` intacto
- [x] 3.2 Verificar `python3 -B -m unittest tests.agents.test_contract tests.agents.test_reviewer_scenarios` (1.5 passa; 1.6 depende de 4.1)

## 4. Documentação (sessão principal, fora de `code_prefixes`)

- [x] 4.1 `README.md`, seção "Conferência de cenários na revisão": a regra do fim do título (só fim da linha ou fechamento de comentário conhecido; senão `ORFAO` e `SEM_TESTE`), a lista de fechamentos e o aviso de migração (`fechamento de comentário`, `ORFAO`); a cópia do host e o `find` como plano B
- [x] 4.2 `CHANGELOG.md`: entrada da F6 com o impacto em projetos que já usam o spec-trace (Q2)
- [x] 4.3 (opcional) `CLAUDE.md`: nada a mudar, salvo se citar o `spec-trace`

## 5. Implantação (sessão principal)

- [x] 5.1 `apm install --target claude,copilot`; `diff` das cópias do agente, de `spec-trace.py` e de `_gherkin.py` nos dois hosts
- [x] 5.2 `claude plugin validate .claude/agents`

## 6. Integração

- [x] 6.1 `python3 -B -m unittest discover -s tests -t . -v`: tudo verde
- [x] 6.2 `openspec validate endurecer-spec-trace --strict` e `python3 -B .apm/hooks/scripts/gherkin-sensor.py` (sai 0)
- [x] 6.3 `grep -rniE "cowboy|cobol|cobc|calculadora" .apm` volta vazia
- [ ] 6.4 Prova de comportamento (humano): reviewer sem `Glob`, com cópias em `apm_modules/`; registrar a cópia usada; o que não for executado, "não verificado"

## Workflow follow-up

- PR `fix(agents): …` ou `fix(hooks): …`; push e merge são do Elói.
- Depois do merge: `openspec archive endurecer-spec-trace`, `openspec validate --specs --strict` e a retrospectiva de skills.
