# CLAUDE.md

Harness local do Claude Code para este repositório.

## Fonte de verdade do projeto

1. `CLAUDE.md` (raiz do repo)
2. Specs / contratos de domínio, se houver

Se houver conflito, siga a ordem acima.

## Regras operacionais

- Toda escrita em filesystem deve respeitar os limites do projeto.
- Não fazer `git push` sem confirmação explícita do usuário.
- Não capturar exceções de forma ampla sem justificativa.
- Não expor secrets em logs, eventos ou artefatos.

## Fase da change

Este projeto usa gate de fase (planejamento vs. implementação). Antes de
implementar, declare a fase:

```bash
python3 scripts/harness/phase_cli.py set proposal <nome-da-mudanca>
# ... planejamento (specs, design, tasks) ...
python3 scripts/harness/phase_cli.py set apply <nome-da-mudanca>
# ... agora escrita em código é liberada ...
```

Enquanto a fase for `proposal`, o hook `pre-tool-write-guard.py` bloqueia
escrita em `.apm/`, `scripts/` e `tests/` e o hook `pre-tool-bash-guard.py`
bloqueia `git commit`/`add`/`merge`/`rebase`. Consulte a fase atual com
`python3 scripts/harness/phase_cli.py show`.

## Fluxo SDD (OpenSpec + OpenSPDD)

| Etapa | Comando | Fase |
|---|---|---|
| Propor (cada requisito com bloco ```` ```gherkin ````: `Dado`/`Quando`/`Então`) | `/opsx-propose` | `proposal` |
| Validar | `openspec validate <change> --strict` | `proposal` |
| Analisar | `/spdd-analysis openspec/changes/<change>` | `proposal` |
| Canvas | `/spdd-reasons-canvas spdd/analysis/<arquivo>` | `proposal` |
| Gerar | `/spdd-generate spdd/prompt/<canvas>` | `apply` |
| Fechar tasks | `/opsx-apply` + `openspec validate <change> --strict` | `apply` |
| Arquivar | `openspec archive <change>` | `set done <change>` |
| Retrospectiva de skills | `skill-retrospective` (depois do merge) | `done` |

## Quality gates mínimos

- Testes do pacote e dos hooks: `python3 -m unittest discover -s tests -t .`. O `sensors_command` do `harness.config.json` roda esses testes e depois o sensor de Gherkin (`python3 .apm/hooks/scripts/gherkin-sensor.py`, sai 2 citando o requisito sem bloco); o hook de Stop o roda sozinho ao encerrar a sessão.
- Contrato dos agentes de SDLC: `python3 -m unittest tests.agents.test_contract` (já incluído no comando acima) e `claude plugin validate .claude/agents` depois de `apm install`.
- Validação da change: `openspec validate <change> --strict`.
- Testes de aceitação: na fase `apply`, o `sdlc-coder` usa o skill `acceptance-from-spec` e escreve primeiro o teste de cada `Cenário:`, com a linha `Spec: <capability> / <requisito> / <cenário>`.
- Neutralidade: `grep -rniE "cowboy|cobol|cobc|calculadora" .apm` deve voltar vazia.

## Cuidados de release

- Não reintroduza `release-as` no `release-please-config.json` (o teste em `tests/release/` falha se voltar) e não mescle o PR de release sem conferir a versão proposta: tags `v*` não se apagam nem se movem.
- O pré-lançamento `1.0.0-alpha.1` foi publicado e a prova em projeto real foi aprovada; a configuração já está na versão final (`"prerelease": false`). Mantenha `"versioning": "prerelease"` até a tag `v1.0.0` existir (sem ela, o bot propõe `2.0.0-alpha.1` a partir do alpha); depois da tag, remova `versioning` e `prerelease-type` e ajuste o teste.
- O PR de release só abre com um commit liberável (`feat`, `fix` ou incompatível) desde a última tag; `docs`, `chore` e `ci` ficam escondidos do CHANGELOG e não o provocam. Para forçar uma versão, use `fix` com o rodapé `Release-As: <versão>` na mensagem do commit de squash (nunca `release-as` na configuração).
- Publicar (mesclar o PR de release) e dar push são atos do desenvolvedor.

## Status no Drive

Ao fim de toda interação que mudar algo (código, fase, branch, commit, PR, merge, decisão ou bloqueio), salve um novo arquivo APM_STATUS_V<n>.md no Google Drive, em PROJECT_INSTRUCTIONS/PROJETOS/APM.
Leia o status mais novo antes e continue a numeração. Nunca edite um status antigo.
Confira a pasta de novo logo antes de salvar. Se o número já existir, use o próximo.
Comece o arquivo pelo título e pelo cabeçalho fixo, uma linha por campo, no formato "- Campo: valor".
Campos do cabeçalho: Agente (CLAUDE-CODE, ANTIGRAVITY, HUMANO ou outro nome), Modelo, Estado (ANDAMENTO, BLOQUEADO, PARADO ou LANÇADO), Data e hora (America/Sao_Paulo), Onda, Fase do harness, Branch, Commits (hash curto), PR, Substitui.
Agente e Modelo dizem quem fez esta interação. Dado ausente vira "não informado".
Depois do cabeçalho, use as seções: Feito (até 5 linhas), Testado e Não testado, Próximo passo, Bloqueios.
Interação só de leitura não gera status.
Se o Drive falhar, salve em docs/STATUS.md e avise no fim da resposta.

Numeração: continue o padrão do status mais novo da pasta.
Dois agentes no projeto: cada um na sua branch, cada STATUS diz quem o escreveu, o segundo a salvar usa o número seguinte, e quem assume o trabalho do outro lê o STATUS dele antes de mexer.

## Escopo

Este arquivo é um guia básico para o Claude Code. Detalhes de arquitetura,
segurança e convenções estão em `CLAUDE.md`.
