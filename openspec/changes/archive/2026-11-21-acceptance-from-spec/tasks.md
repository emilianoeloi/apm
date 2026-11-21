# Tasks

## 1. Testes primeiro (vermelhos)

- [x] 1.1 Criar `tests/agents/test_acceptance_skill.py` (em tabela): skill existe com frontmatter (`name` igual à pasta, `description`, `license`); trechos obrigatórios presentes (`Spec:`, `Cenário:`, `vermelho`, `verde`, `contagem de falhas`, `sensors_command`, `harness.config.json`, `Pare`, `aprovação`, `não instal`, `code_prefixes`); sem `STACK_TERMS` nem os quatro termos de neutralidade; até 150 linhas; exemplo de marcador do skill casa com o regex canônico `Spec: .+ / .+ / .+`; cópias em `.claude/skills/` e `.agents/skills/` idênticas à fonte; verificar que falha porque o skill não existe
- [x] 1.2 Ajustar `tests/agents/test_contract.py`: `SKILLS_BY_ROLE["sdlc-coder"]` inclui `acceptance-from-spec`; o regex de "skills citadas existem" cobre o nome; teste de que o coder cita o skill antes do item que executa as Operations; verificar que falha
- [x] 1.3 Registrar a contagem de falhas de 1.1 e 1.2 (comando e número) para o relatório

## 2. Skill

- [x] 2.1 Criar `.apm/skills/acceptance-from-spec/SKILL.md` com frontmatter e os passos: listar cenários da change, descobrir o framework (arquivo raiz do agente, `sensors_command`, testes existentes), escrever o teste ligado (`Spec: <capability> / <requisito> / <cenário>`), vermelho com comando e contagem de falhas (sem stubs), código, verde pelo `sensors_command` e conferência de que ele roda a aceitação, relatório por cenário
- [x] 2.2 Escrever no skill o ramo "sem framework": propor 1 a 3 opções (motivo, custo, pasta, comando, composição no `sensors_command`), parar sem escrever nem instalar, devolver à sessão principal para a aprovação do Emiliano; edições de `CLAUDE.md`/`harness.config.json` ficam como pendência (fora de `code_prefixes`)
- [x] 2.3 Verificar que os testes de 1.1 passam e que `grep -rniE "cowboy|cobol|cobc|calculadora" .apm` volta vazia

## 3. Coder

- [x] 3.1 Editar `.apm/agents/sdlc-coder.agent.md`: item em "O que você faz" mandando usar `acceptance-from-spec` antes de implementar a Operation que realiza requisito com cenário; linha em "Entregável" exigindo, por cenário, teste, vermelho e verde; sem ferramenta nova, sem termos de stack
- [x] 3.2 Verificar que 1.2 e todo `tests/agents` passam (`python3 -B -m unittest tests.agents.test_contract tests.agents.test_acceptance_skill`)

## 4. Documentação (sessão principal, fora de `code_prefixes`)

- [x] 4.1 README: seção "Testes de aceitação" (o que o skill faz, a convenção `Spec:`, vermelho e verde, "sem framework: propõe e espera", como compor o `sensors_command`) e linha na tabela de agentes/skills
- [x] 4.2 README: aviso de migração para projetos na versão anterior (o coder passa a exigir o teste antes do código; proposta de ferramenta na primeira `apply` sem framework; `sensors_command` precisa rodar a aceitação)
- [x] 4.3 (opcional, Q7) `CLAUDE.md` deste repo: citar o skill nos quality gates

## 5. Implantação (sessão principal)

- [x] 5.1 Rodar `apm install --target claude,copilot`; conferir com `diff` que `.claude/skills/acceptance-from-spec/`, `.agents/skills/acceptance-from-spec/`, `.claude/agents/sdlc-coder.md` e `.github/agents/sdlc-coder.agent.md` são idênticos à fonte
- [x] 5.2 Rodar `claude plugin validate .claude/agents`

## 6. Integração

- [x] 6.1 Rodar `python3 -B -m unittest discover -s tests -t . -v` e verificar que tudo passa
- [x] 6.2 Rodar `openspec validate acceptance-from-spec --strict` e `python3 -B .apm/hooks/scripts/gherkin-sensor.py` (deve sair 0)
- [x] 6.3 Rodar `grep -rniE "cowboy|cobol|cobc|calculadora" .apm` e verificar que volta vazia
- [ ] 6.4 Prova de comportamento (humano, projeto de prova): disparar o coder com um cenário e verificar que o relatório mostra o teste ligado, o vermelho com contagem e o verde; num projeto sem framework, verificar que ele para e propõe sem escrever nada. Registrar no PR; o que não for executado, registrar como "não verificado"

## Workflow follow-up

- Abrir o PR com título `feat(agents): …`; push e mesclagem são do Elói.
- Depois do merge, `openspec archive acceptance-from-spec`, trocar o `## Purpose` provisório de `acceptance-from-spec` por uma frase real, rodar `openspec validate --specs --strict` e a retrospectiva de skills.
- F4 (fora daqui): o reviewer confere cada `Cenário:` contra a linha `Spec:` do teste.
