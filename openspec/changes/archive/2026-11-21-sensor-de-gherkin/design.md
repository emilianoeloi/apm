# Design

## Context

A F1 deixou o formato do bloco em `spec-gherkin-scenarios` e a lógica de leitura/validação em `tests/specs/test_gherkin_blocks.py` (`parse_requirements`, `parse_delta`, `effective_requirements`, `validate`), que só enxerga este repositório (constantes `SPECS` e `CHANGES`). Os hooks do pacote ficam em `.apm/hooks/scripts/` (só stdlib, helper `_common.py`, saída 0 ou 2, fail-open via `_common.run`) e são registrados em `.apm/hooks/harness.json` com `${PLUGIN_ROOT}`. O `apm install` os implanta sob um caminho que **varia por host** (`.claude/hooks/apm/.apm/hooks/scripts/` no Claude Code). Por isso um `sensors_command` de projeto-alvo não consegue apontar para o script por um caminho estável, e um hook registrado pelo manifesto consegue.

Não li a especificação APM_SETUP_V2.0 no Drive; uso os critérios e restrições do pedido.

## Goals / Non-Goals

**Goals:**
- Sensor stdlib, ao lado dos hooks, que falha citando capability + requisito e passa quando tudo está conforme.
- Rodar junto do `openspec validate --strict` em qualquer projeto que instale o pacote.
- Uma só implementação da regra de formato.

**Non-Goals:**
- `acceptance-from-spec` (F3), executor de Gherkin, perfis de SDLC.
- Julgar o sentido dos passos; o sensor confere forma.
- Reescrever `openspec validate`, ou invocá-lo por dentro do sensor.

## Decisions

1. **Biblioteca + CLI.** `_gherkin.py` (sem `if __name__`, docstring, só stdlib) leva a lógica movida do teste, parametrizada por `root: Path` em vez de constantes: `effective_requirements(root) -> list[Requisito]`, `validate(body) -> list[str]`. `Requisito` traz `capability`, `name`, `body` e `origin` (`"principal"` ou o nome da change). `gherkin-sensor.py` é a fina camada de CLI. O arquivo com hífen não é importável, por isso a lógica fica na biblioteca com nome de módulo, como `_common.py`. O teste da F1 passa a importar de `_gherkin` (carregando `HOOK_SCRIPTS` no `sys.path`, como `test_package.py` já faz) e mantém só os testes, as amostras e a verificação do repo.
2. **Onde roda "junto" do validate.** Hook `PostToolUse` com matcher `Bash`, registrado em `harness.json`, chamando `gherkin-sensor.py --on-validate`. Nesse modo lê o payload na entrada padrão, extrai o comando (`tool_input.command` no Claude Code; `toolArgs` no Copilot, JSON em texto) e só age se casar `\bopenspec\s+validate\b`; senão sai 0 em silêncio. Código 2 e stderr voltam ao agente como retorno da ferramenta. Funciona em qualquer projeto, em qualquer fase, sem editar `sensors_command`. O modo é decidido por flag, não por adivinhação do payload.
3. **Stop e pre-commit.** `sensors_command` continua do projeto. Neste repositório vira `python3 -m unittest discover -s tests -t . && python3 .apm/hooks/scripts/gherkin-sensor.py`. Em projetos-alvo continua vazio por padrão (os modelos não mudam); o README ensina a compor `openspec validate --all --strict && python3 <caminho-implantado>/gherkin-sensor.py`. O pre-commit genérico já roda o `sensors_command`, então herda o sensor sem mudança.
4. **Raiz e `openspec/`.** `--root` > `CLAUDE_PROJECT_DIR` > pasta com `.git` acima do cwd (reaproveita `_common.project_root`, estendido só com o parâmetro). Procura `<raiz>/openspec/`; sem ele, sai 0 e avisa em stderr (projeto sem OpenSpec não deve ser bloqueado). Não busca `openspec/` em subpastas (monorepo é Q5).
5. **Requisitos efetivos.** Mesma ideia da F1: principais trocadas pelos `ADDED`/`MODIFIED` dos deltas ativos, sem `REMOVED`, ignorando `changes/archive/`. Acrescenta `RENAMED` (pares `FROM`/`TO` em linhas de lista): o nome antigo é trocado pelo novo, para um requisito renomeado não ser citado duas vezes. Delta de capability que ainda não existe nas principais entra como está (F1 já fazia).
6. **Saída.** Uma linha por violação em stderr: `gherkin: <capability> / Requirement: <nome> [change <nome>]: <motivo>`, mais um total no final. Todas as violações de uma vez (não para na primeira). Só os códigos 0 e 2. No modo CLI, erro inesperado vira código 2 com a mensagem (sensor que não consegue rodar não deve declarar aprovação; Q3); no modo hook, `_common.run` mantém o fail-open como nos demais hooks. Arquivo ilegível ou malformado vira violação citada.
7. **Teste de contrato.** `test_package.py` passa a aceitar o helper `_gherkin` e o evento `PostToolUse`. A neutralidade já varre `.apm/hooks/`.
8. **Agentes.** Nenhum agente é editado: o coder e o reviewer já rodam o `sensors_command` e `openspec validate`, e o hook do item 2 pega o `validate` deles. Só adição.

## Decisões em aberto (do humano)

- **Q1. Como o sensor roda "junto" do validate: hook `PostToolUse` (recomendado), wrapper ou só `sensors_command`?** Recomendação: o hook, mais o `sensors_command` neste repo. Custo: um evento novo no `harness.json` e ~40 linhas no sensor. Risco: o evento `PostToolUse` no Copilot não foi verificado (como o `deny` já não era); mitigado porque nada depende só dele (Stop e pre-commit cobrem). Alternativas: wrapper `openspec-validate.py` (obriga todos a mudar o comando; o agente esquece) ou só `sensors_command` (caminho implantado varia por host, e o sensor não roda quando o `validate` roda).
- **Q2. Verificar o `PostToolUse` num Copilot real?** Recomendação: documentar como não verificado no README, igual ao `deny`. Custo: nenhum agora. Risco: no Copilot o disparo junto do validate pode não ocorrer; o Stop continua cobrindo.
- **Q3. Erro inesperado no modo CLI: código 2 (recomendado) ou fail-open?** Custo: um bug do sensor pode bloquear o Stop do usuário. Risco: o inverso é um sensor que "passa" sem rodar. O modo hook mantém fail-open, para nunca travar o `validate` em si.
- **Q4. `sensors_command` do repo: acrescentar o sensor ou confiar no teste da F1?** Recomendação: acrescentar. Custo: <1 s. Risco: duplicidade (o teste já cobre o repo); em troca, o caminho que os projetos-alvo usam fica exercitado aqui. Edição de `harness.config.json` é da sessão principal.
- **Q5. Monorepo/vários `openspec/`?** Recomendação: fora do escopo; só `<raiz>/openspec/` ou `--root`. Custo de incluir: busca recursiva e mais testes. Risco de não incluir: projeto com `openspec/` em subpasta passa sem verificação (com o aviso de stderr).
- **Q6. Vincular o sensor ao `openspec/config.yaml` (`rules.specs` citar o sensor)?** Recomendação: não por ora; a regra já exige o bloco. Se quiser, é edição da sessão principal.
- **Q7. Mensagem de falha com o texto da spec ou só com o nome?** Recomendação: só capability, nome, change e motivo (curto, sem eco do corpo).

A seção "Decisões do humano" fica vazia até a aprovação.

### Ações do humano fora do código
- Em cada projeto-alvo que queira o sensor também no Stop: editar o `sensors_command` do `harness.config.json` (o pacote não o preenche).
- Depois do `apm install`, conferir se o host registrou `PostToolUse`; no Copilot, observar um `openspec validate` real.
- Push, PR e mesclagem; arquivar `sensor-de-gherkin` depois do merge.

## Risks / Trade-offs

- [Falso positivo em requisito ainda em rascunho, durante o `proposal`] → o sensor só roda no `validate` e no Stop; o planner já gera o bloco; mensagem aponta o motivo exato.
- [`PostToolUse` não disparar em algum host] → Stop e pre-commit continuam; README diz o que foi verificado.
- [Divergência entre teste e sensor] → uma só implementação (`_gherkin.py`), teste importa dela.
- [Parser próprio divergir do CLI do OpenSpec] → `--strict` do CLI segue como juiz da estrutura; o sensor só confere o bloco. Casos de `RENAMED` cobertos por teste.
- [Hook mais lento no `validate`] → leitura de poucos arquivos de texto; meta abaixo de 1 s.

## Migration Plan

1. Testes vermelhos (sensor, contrato do pacote, teste da F1 importando a lib).
2. `_gherkin.py` (lógica movida), CLI, modo hook, `harness.json`.
3. `apm install --target claude,copilot`; conferir `PostToolUse` em `.claude/apm-hooks.json` e `.github/hooks/`.
4. Sessão principal: `harness.config.json`, README, `CLAUDE.md`.
5. Rollback: reverter o commit; nada é publicado antes do PR de release.

## Estimativa de tamanho

- Código: `_gherkin.py` ~110 linhas (movidas do teste, mais `root`, `origin`, `RENAMED`: ~25 novas), `gherkin-sensor.py` ~90, `harness.json` +8: ~230 linhas, das quais ~120 novas e ~110 movidas.
- Testes (tabela de casos sobre pastas temporárias, ~1,4 vez o código novo): `test_gherkin_sensor.py` ~190 linhas, ajustes em `test_package.py` ~15 e em `test_gherkin_blocks.py` (−110 movidas, +15): ~220 linhas de teste, estimadas à parte.
- Documentação: README ~35 linhas, `install-dev-harness` ~8, `CLAUDE.md` ~2 (fora do coder).
- Limite de PR: não informado; código novo + teste ~340 linhas. Se o limite for ~200, dividir em duas Operations (biblioteca + teste da F1; depois CLI + hook).
