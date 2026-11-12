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
- Validação da change: `openspec validate <change> --strict`.
- Neutralidade: `grep -rniE "cowboy|cobol|cobc|calculadora" .apm` deve voltar vazia.

## Escopo

Este arquivo é um guia básico para o Claude Code. Detalhes de arquitetura,
segurança e convenções estão em `CLAUDE.md`.
