# Contribuindo

Obrigado por querer contribuir com o apm. Este guia resume como mudar o pacote sem quebrar o fluxo.

## Antes de começar

- O fonte do pacote fica em `.apm/` (skills, agentes, prompts, hooks, scripts e templates). As pastas `.claude/`, `.agents/` e `.github/` são **cópias geradas** pelo `apm install`: não as edite à mão.
- As regras do repositório estão no [CLAUDE.md](CLAUDE.md); a visão geral, no [README](README.md).

## Fluxo de mudança

Mudanças de comportamento seguem o fluxo de especificação do próprio pacote (OpenSpec e OpenSPDD):

1. Proponha a change (`/opsx-propose`) e valide: `openspec validate <change> --strict`. Todo requisito traz um bloco `gherkin` e cada cenário novo ou alterado tem um teste com a linha `Spec:`.
2. Só depois implemente, com o teste escrito antes do código.
3. Rode os testes e os sensores antes de abrir o PR:

```bash
python3 -B -m unittest discover -s tests -t .
openspec validate --specs --strict
python3 -B .apm/hooks/scripts/gherkin-sensor.py
```

4. Depois de mudar algo em `.apm/`, rode `apm install --target claude,copilot --force` e commite as cópias e o `apm.lock.yaml`.
5. A neutralidade do pacote é conferida por teste: o conteúdo de `.apm/` não cita linguagem, pasta ou comando de um projeto específico.

Mudanças só de documentação (README, CHANGELOG e `docs/`) não precisam de change.

## Commits e PRs

- O **título do PR** segue [Conventional Commits](https://www.conventionalcommits.org/pt-br/) (`feat:`, `fix:`, `docs:`, `chore:`...), porque ele vira a mensagem do commit de squash e define a versão (`feat` gera MINOR, `fix` gera PATCH, `!` gera MAJOR). O workflow `pr-title` confere.
- Descreva no PR o que mudou, o que foi verificado e o **que não foi verificado**.
- Não faça `git push` sem a confirmação do mantenedor, e não edite o `CHANGELOG.md` nem a versão do `apm.yml` à mão: o release-please os gera (veja [docs/releases.md](docs/releases.md)).

## Segurança

Hooks são código executável. Não introduza hooks que executem comandos construídos a partir de dados não confiáveis, e não registre segredos em logs, eventos ou artefatos.
