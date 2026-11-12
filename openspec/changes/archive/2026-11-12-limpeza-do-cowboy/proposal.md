# Proposal

## Why

O pacote APM `emilianoeloi/apm` nasceu do projeto `cowboy` (uma calculadora em COBOL) e ainda carrega esse projeto: cinco agentes, sete prompts, três skills, um hook de encerramento que exige `make fitness`, um pre-commit que compila COBOL e um modelo de quadrante que é, na verdade, a análise preenchida do cowboy. Quem instala o pacote em outra stack recebe esse peso, e o hook pode travar o agente ao encerrar. A visão do produto é um pacote genérico, para qualquer stack, e esta é a funcionalidade F1 da Onda 1 da spec APM_SETUP V1.2: sem ela, nenhuma outra funcionalidade da onda entrega um pacote genérico.

## What Changes

- **BREAKING**: remover os agentes `cobol-vibecoder`, `cobol-planner`, `cobol-coder`, `cobol-reviewer` e `readme-writer`.
- **BREAKING**: remover os prompts `criar-programa`, `implementar-soma`, `implementar-subtracao`, `implementar-log`, `testar-programa`, `atualizar-readme` e `manutencao-repositorio`.
- **BREAKING**: remover as skills `cobol-calculadora`, `vibe-coding-fundamentals` e `readme-manutencao`.
- **BREAKING**: remover `.apm/scripts/git-hooks/pre-commit` (compila `src/CALCULADORA.cbl` com `cobc`) e `.apm/_pending/instructions/cowboy.instructions.md`.
- Trocar os exemplos COBOL da skill `openspec-workflow` por exemplos sem stack.
- Transformar `.apm/templates/HARNESS_QUADRANTE.md` em modelo com campos a preencher.
- Tirar o cowboy e a palavra "privado" do `apm.yml` e do `README.md`, e acrescentar o aviso de migração para quem usava a 0.3.x.
- Reimplantar o pacote com `apm install --target claude,copilot` para que `.claude/`, `.agents/`, `.github/` e `apm.lock.yaml` deixem de carregar o conteúdo removido.
- Ignorar `.harness/` no git (estado de fase de cada desenvolvedor).

Ficam fora desta change, por serem de outras funcionalidades: o hook genérico que substitui o `cowboy.json` (F2), os agentes `sdlc-*` (F3), a configuração do release-please para pré-lançamento (versão `1.0.0-alpha.1`) e os agentes de harness (Onda 2).

## Capabilities

### New Capabilities
- `pacote-generico`: o conteúdo, os metadados e a implantação do pacote APM não carregam o projeto cowboy nem nenhuma linguagem ou stack específica.

### Modified Capabilities

Nenhuma. O repositório ainda não tem specs em `openspec/specs/`.

## Impact

- **Arquivos removidos**: 5 agentes, 7 prompts, 3 skills (com `SKILL.md`), 1 script de pre-commit e 1 guia de instruções em `.apm/`, além das cópias implantadas em `.claude/`, `.agents/` e `.github/`.
- **Arquivos alterados**: `.apm/skills/openspec-workflow/SKILL.md`, `.apm/templates/HARNESS_QUADRANTE.md`, `apm.yml`, `README.md`, `.gitignore`, `apm.lock.yaml` e, por efeito da reimplantação, os diretórios implantados.
- **Consumidores**: quem instala `emilianoeloi/apm#v0.3.x` não é afetado até trocar a tag. Quem trocar para a `1.0.0-alpha.1` perde tudo o que foi removido; o aviso de migração no README cobre esse caso.
- **Release**: a mensagem desta change é incompatível (`!`) e o release-please vai propor `1.0.0`. O PR de release não deve ser mesclado antes da configuração de pré-lançamento (change própria); mesclá-lo continua sendo ato humano.
- **Risco**: sem o pre-commit e sem o hook de Stop, o repositório fica sem sensor de encerramento até a F2. Aceito: o pacote ainda não tem versão publicada sem o cowboy.
