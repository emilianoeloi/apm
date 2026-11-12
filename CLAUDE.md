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
| Propor | `/opsx-propose` | `proposal` |
| Validar | `openspec validate <change> --strict` | `proposal` |
| Analisar | `/spdd-analysis openspec/changes/<change>` | `proposal` |
| Canvas | `/spdd-reasons-canvas spdd/analysis/<arquivo>` | `proposal` |
| Gerar | `/spdd-generate spdd/prompt/<canvas>` | `apply` |
| Fechar tasks | `/opsx-apply` + `openspec validate <change> --strict` | `apply` |
| Arquivar | `openspec archive <change>` | `set done <change>` |
| Retrospectiva de skills | `skill-retrospective` (depois do merge) | `done` |

## Quality gates mínimos

- Testes do pacote e dos hooks: `python3 -m unittest discover -s tests -t .` (é também o `sensors_command` do `harness.config.json`: o hook de Stop o roda sozinho ao encerrar a sessão).
- Contrato dos agentes de SDLC: `python3 -m unittest tests.agents.test_contract` (já incluído no comando acima) e `claude plugin validate .claude/agents` depois de `apm install`.
- Validação da change: `openspec validate <change> --strict`.
- Neutralidade: `grep -rniE "cowboy|cobol|cobc|calculadora" .apm` deve voltar vazia.

## Cuidados de release

- Não reintroduza `release-as` no `release-please-config.json` (o teste em `tests/release/` falha se voltar) e não mescle o PR de release sem conferir a versão proposta: tags `v*` não se apagam nem se movem.
- O pré-lançamento `1.0.0-alpha.1` foi publicado e a prova em projeto real foi aprovada; a configuração já está na versão final (`"prerelease": false`). Mantenha `"versioning": "prerelease"` até a tag `v1.0.0` existir (sem ela, o bot propõe `2.0.0-alpha.1` a partir do alpha); depois da tag, remova `versioning` e `prerelease-type` e ajuste o teste.
- O PR de release só abre com um commit liberável (`feat`, `fix` ou incompatível) desde a última tag; `docs`, `chore` e `ci` ficam escondidos do CHANGELOG e não o provocam. Para forçar uma versão, use `fix` com o rodapé `Release-As: <versão>` na mensagem do commit de squash (nunca `release-as` na configuração).
- Publicar (mesclar o PR de release) e dar push são atos do desenvolvedor.

## Escopo

Este arquivo é um guia básico para o Claude Code. Detalhes de arquitetura,
segurança e convenções estão em `CLAUDE.md`.
