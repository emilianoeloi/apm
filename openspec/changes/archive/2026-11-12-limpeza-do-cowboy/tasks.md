# Tasks

## 1. Remover o conteúdo do cowboy da fonte

- [x] 1.1 Apagar os cinco agentes (`cobol-vibecoder`, `cobol-planner`, `cobol-coder`, `cobol-reviewer`, `readme-writer`) e verificar que `ls .apm/agents` não lista nenhum arquivo `cobol-*` nem `readme-writer`
- [x] 1.2 Apagar os sete prompts do cowboy (`criar-programa`, `implementar-soma`, `implementar-subtracao`, `implementar-log`, `testar-programa`, `atualizar-readme`, `manutencao-repositorio`) e verificar que `ls .apm/prompts` lista só os seis `opsx-*`
- [x] 1.3 Apagar as skills `cobol-calculadora`, `vibe-coding-fundamentals` e `readme-manutencao` e verificar que `ls .apm/skills` não as lista
- [x] 1.4 Apagar `.apm/scripts/git-hooks/` (pre-commit com `cobc`) e `.apm/_pending/instructions/cowboy.instructions.md` e verificar que os dois caminhos não existem mais

## 2. Neutralizar o que fica

- [x] 2.1 Reescrever as linhas 69, 76, 95 e 96 da skill `openspec-workflow` com exemplos sem stack (decisão 4 do design) e verificar com `grep -niE "cobol|cobc|calculadora|make fitness"` no arquivo, que deve voltar vazio
- [x] 2.2 Substituir o conteúdo de `.apm/templates/HARNESS_QUADRANTE.md` pelo modelo de `harness-quadrant-process/references/quadrant-doc-template.md` e verificar que o arquivo tem campos `<...>` para preencher e nenhum dos quatro termos
- [x] 2.3 Atualizar `apm.yml` (nome `apm`, descrição genérica, versão intocada) e verificar com `apm install --dry-run --target claude,copilot` que o manifesto continua válido
- [x] 2.4 Reescrever a introdução e a linha de layout do `README.md` (público, sem "extraído do cowboy", sem `pre-commit` e sem `.apm/hooks`, tag de exemplo atual) e acrescentar o aviso de migração da 0.3.x com a lista do que foi removido e a tag `v0.3.1`; verificar relendo que o texto cobre os cenários da spec
- [x] 2.5 Acrescentar `.harness/` ao `.gitignore` e verificar com `git check-ignore -v .harness/change-phase.json`

## 3. Reimplantar e conferir a implantação

- [x] 3.1 Rodar `apm install --target claude,copilot` e verificar que o comando termina sem erro e sem os avisos de frontmatter dos prompts do cowboy
- [x] 3.2 Conferir que `.claude/`, `.agents/`, `.github/agents` e `.github/prompts` não têm mais o conteúdo removido; se sobrar órfão, usar `apm prune` e, só se necessário, apagar os arquivos listados no lockfile; verificar com a busca pelos quatro termos, que deve voltar vazia
- [x] 3.3 Conferir que `apm.lock.yaml` não lista mais arquivos do cowboy, com `grep -iE "cobol|cowboy|readme-writer" apm.lock.yaml` vazio

## 4. Integração

- [x] 4.1 Rodar a busca `grep -rniE "cowboy|cobol|cobc|calculadora" .apm` e verificar que não retorna nada (roteiro de teste, item 1)
- [x] 4.2 Rodar `echo '{"source":"new"}' | python3 scripts/hooks/session-start.py`, `openspec list` e `python3 scripts/harness/phase_cli.py show` e verificar que continuam funcionando
- [x] 4.3 Rodar `openspec validate limpeza-do-cowboy --strict` e verificar que passa
- [x] 4.4 Registrar a remoção como incompatível na seção da Onda 1 do `CHANGELOG.md`, com o resultado das verificações, e verificar que o texto lista os itens removidos

## Workflow follow-up

- Abrir o PR com título `feat!: …` (Conventional Commits) e esperar o "ok" do Elói para o push e a mesclagem.
- Não mesclar o PR de release do release-please antes da change de pré-lançamento.
- Reconciliar o código com o canvas (`/spdd-sync`), arquivar a change e fazer a retrospectiva de skills.
