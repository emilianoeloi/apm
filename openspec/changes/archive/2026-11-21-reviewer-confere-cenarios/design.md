# Design

## Context

O `sdlc-reviewer` (`.apm/agents/sdlc-reviewer.agent.md`) tem as ferramentas `Read`, `Grep`, `Glob`, `Bash` e **não escreve**; entrega o relatório na mensagem final e confere `git status --porcelain` igual ao inicial. A F1 fixou o bloco Gherkin por requisito, a F2 trouxe `_gherkin.py` (`effective_requirements`, `parse_delta`, `validate`) e o sensor (que só confere o formato do bloco e **não lê testes**), e a F3 fixou a convenção de ligação: a linha literal `Spec: <capability> / <nome do requisito> / <título do cenário>` em comentário, nome ou rótulo do teste. Os scripts de `.apm/hooks/scripts/` são implantados por host em caminhos diferentes (`.claude/hooks/apm/.apm/hooks/scripts/` no Claude, `.github/hooks/scripts/apm/.apm/hooks/scripts/` no Copilot; na fonte, `.apm/hooks/scripts/`), então o agente não pode embutir um caminho.

Achados das provas (`docs/roteiro-de-teste.md`) que moldam o desenho: cenários herdados de requisito `MODIFIED` ficaram sem `Spec:`; o skill manda um teste por `Cenário:` do bloco, mas o planner mandou cobrir também todos os `#### Scenario:`; o nome de subteste de Go troca espaço por `_`; um teste passou de primeira porque o ambiente falhou (falso verde); o sensor sai 0 sem nenhuma linha `Spec:`; Python grava `__pycache__` ao importar, o que sujaria o `git status` que o reviewer promete deixar igual.

Não li a V2.0 no Drive; uso o trecho do pedido.

## Goals / Non-Goals

**Goals:**
- A revisão confere, por cenário novo ou alterado da change, que existe teste ligado por `Spec:`, com evidência (arquivo e linha) e sem escrever nada.
- Resultado reproduzível (mesma entrada, mesma saída) para a parte mecânica; julgamento humano-like só para o que exige leitura (o teste afirma o `Então`?).
- Stack-agnóstico: nenhum nome de ferramenta de teste; o vínculo é texto.

**Non-Goals:**
- Provar que o teste é bom por mutação (o reviewer não escreve nem altera código).
- Exigir teste de cenário antigo sem relação com a change; executar Gherkin; perfis; revisão cruzada entre modelos; orquestrador.
- Ligar a conferência ao `sensors_command` ou a um hook.

## Decisions

1. **Script `spec-trace.py` + prosa de reserva (Q1).** O script lista e confere o mecânico; o agente julga o resto. `Glob` por `**/spec-trace.py` acha o script em qualquer host; `Bash` roda `python3 -B <caminho> --root . [--change <nome>]`. Sem o script (ou sem `python3`), o agente faz o mesmo à mão: lê os deltas da change, lista os `Cenário:` dos requisitos `ADDED`/`MODIFIED` e roda `grep -rnF "Spec: <capability> / <requisito> / <cenário>"` nos testes. A prosa descreve o procedimento em ambos os casos; o script é só o atalho determinístico.
2. **O script é só-leitura de verdade.** Abre arquivos em modo leitura, define `sys.dont_write_bytecode = True` **antes** de importar `_gherkin` (nenhum `__pycache__` novo; o teste confere), não cria arquivo, não chama `git`. O agente o roda com `-B` também. Saída só em stdout (uma linha por cenário e um resumo); saída 0 ou 2.
3. **Reuso de `_gherkin` (uma única implementação da regra).** O script importa `_gherkin` (`parse_delta`, `parse_requirements`, `effective_requirements`) e ganha dele `parse_scenarios(body) -> [(título, passos)]`, que lê o bloco `gherkin` com o mesmo `FENCE_OPEN`/`KEYWORD` do `validate`. Só acréscimo em `_gherkin.py`. O `test_package` já aceita `_gherkin` como import local.
4. **Escopo: novo ou alterado é exigido; herdado é informativo (Q2).** Para cada requisito `ADDED` de delta de change ativa: todo `Cenário:` do bloco é exigido. Para `MODIFIED`: compara com o mesmo requisito na spec principal (seguindo `RENAMED` ao contrário); `Cenário:` de **mesmo título e mesmos passos** (espaços colapsados) é *herdado*; título novo ou passos diferentes é *alterado*, exigido. Sem requisito-base na principal, tudo é exigido. `REMOVED` nada exige. Com `--change <nome>` só os deltas dessa change são exigidos; sem a opção, os de todas as changes ativas. Cenários de requisitos não tocados pela change não são listados, mas contam como alvo válido de `Spec:` (para o teste de órfãos).
5. **Chave de ligação e casamento.** A chave é a trinca literal. Para cada linha de arquivo de teste que contém `Spec:`, o texto depois do primeiro `Spec:` (sem espaço à esquerda) é comparado por **prefixo** com `<capability> / <requisito> / <cenário>` de todos os cenários efetivos; vale o prefixo **mais longo** (resolve "Caso" contra "Caso feliz" e deixa passar fechamento de comentário, aspas ou parêntese depois do título). Duas trincas distintas com o mesmo literal (nomes com ` / ` que colidem) viram `AMBIGUO`. Linha com `Spec:` e ao menos dois ` / ` sem nenhum casamento vira `ORFAO` (título digitado errado, cenário renomeado ou removido). Linha com `Spec:` e menos separadores é ignorada (prosa).
6. **Quais arquivos (Q7).** Por padrão, todo arquivo de texto da raiz, exceto as pastas `.git`, `openspec`, `spdd`, `.harness`, `.claude`, `.github`, `.agents`, `.apm`, `apm_modules`, `node_modules`, `vendor`, `target`, `build`, `dist`, `__pycache__`, `.venv`, `venv`, e exceto arquivos `.md` (documentação nunca é teste e o skill de aceitação traz exemplos de `Spec:`). Ignora arquivo maior que 1 MiB ou com byte NUL. `--tests <caminho>` (repetível) restringe a busca a pastas ou arquivos (então as exclusões de pasta não valem). O script não sabe o que é teste; a ligação por linha é a evidência, e o agente confirma lendo o arquivo.
7. **Cenário do bloco vs `#### Scenario:` (Q3).** Vale o do skill da F3: **um teste por `Cenário:` do bloco**. Como a F1 exige que o título do bloco seja igual ao de um `#### Scenario:`, os dois nomes apontam para o mesmo comportamento, e o script usa os títulos do bloco. `#### Scenario:` sem `Cenário:` correspondente (extras WHEN/THEN) **não** são exigidos: o script só os conta no resumo (`extras: N`) e o agente, ao ler a spec, anota como baixa os que descrevem comportamento observável distinto sem teste. Isso resolve a divergência da prova (o planner mandou cobrir todos).
8. **Severidades e veredito (Q4).** O agente transforma a saída em achados:
   - `SEM_TESTE`: **alta**, veredito `REPROVADO`. Se um teste existente comprovadamente cobre o cenário mas sem a linha `Spec:` (o agente o acha por leitura), baixa para **média** (cobertura sem marcador) e cita o arquivo.
   - **Falso verde**: o agente lê cada teste ligado e confere que ele afirma o `Então` do cenário e que falharia com o código de produção ausente ou errado. Teste que só verifica que o ambiente executou (código de saída genérico, arquivo existente, mensagem do interpretador) é **alta**; afirmação parcial é **média**. Se o relatório do coder veio no pedido, compara o motivo do vermelho; se não veio, diz "vermelho não verificado" (o reviewer não executa mutação).
   - `ORFAO`: **média** (o vínculo silenciosamente não vale; costuma vir com um `SEM_TESTE`).
   - `AMBIGUO`: **média**.
   - `HERDADO_SEM_TESTE`: **informativo** (não entra em Achados nem muda o veredito; vai na seção "Cenários x testes").
   - Título repetido em duas capabilities **não é achado**: a chave inclui a capability e o requisito. Só a colisão de literal (item 5) é achado.
   `APROVADO COM RESSALVAS` continua cobrindo achados médios e baixos; `REPROVADO` passa a cobrir também alta de cenário.
9. **Subteste com espaço trocado (Q5).** O script e o `grep` de reserva leem o **fonte**, onde o literal está intacto. O agente não deve usar a saída verbosa do executor de testes (onde, por exemplo, o espaço vira `_` e ` / ` vira hierarquia).
10. **Relatório.** Seção nova "Cenários x testes": uma tabela `capability / requisito / cenário / estado / arquivo:linha / observação` mais a linha de resumo do script. Cada achado de cenário cita a Operation do canvas que realiza o requisito ("sem Operation" se não houver), como já exige o contrato. O resultado do script entra literal; o que o agente concluiu por leitura vem marcado como leitura.
11. **Implantação.** O script segue com os demais em `.apm/hooks/scripts/`, mas **não** entra em `harness.json` (não é hook) nem no `sensors_command` (o Stop e o pre-commit rodariam em `proposal`, quando os testes ainda não existem). `apm install` copia a pasta inteira, como já faz com `_gherkin.py`.
12. **Testes.** `tests/hooks/test_spec_trace.py` chama o script como processo em projetos temporários (como `test_gherkin_sensor.py`), com casos em tabela: coberto, sem teste, herdado vs alterado, prefixo mais longo, órfão, ambíguo, `--change`, `--tests`, exclusões, `.md` ignorado, arquivo ilegível e binário, sem `openspec/`, sem bytecode e árvore intacta. `tests/agents/test_reviewer_scenarios.py` confere o texto do reviewer (trechos, ferramentas inalteradas, neutralidade, severidades) e as cópias implantadas idênticas à fonte (agente e script).

## Decisões em aberto (do humano)

Assumidas as recomendações nos artefatos; "Decisões do humano" fica vazia até a aprovação.

- **Q1. Como o reviewer confere.** Recomendação: script só-leitura `spec-trace.py` achado por `Glob`, com `grep -F` como reserva em prosa. Custo: ~150 linhas de script e ~230 de teste. Risco: o script reimplementa o casamento e pode divergir da prosa (mitigado por um teste que compara os dois num caso); `python3` ausente cai na reserva. Alternativa A (só prosa): custo menor, mas o modelo faria dezenas de `grep` à mão e erraria a lista de cenários herdados/alterados, que exige comparar spec principal e delta. Alternativa B (script no `sensors_command`): quebra o Stop em `proposal` e pune cenários herdados.
- **Q2. Escopo.** Recomendação: exigir só cenário novo ou alterado da change; relatar o herdado como informativo; `--all` fora. Custo: a comparação com a spec principal (~25 linhas). Risco: um requisito `MODIFIED` cujo cenário herdado nunca teve teste continua sem teste para sempre (fica visível como informativo; o humano decide fazer um retrofit). Alternativa: exigir todos os cenários do requisito tocado (mais seguro, mas é o atrito da prova: o coder teria de ligar testes antigos).
- **Q3. Bloco vs `#### Scenario:`.** Recomendação: um teste por `Cenário:` do bloco; extras só informativos. Risco: um extra com comportamento distinto fica sem teste e depende do julgamento do agente. Alternativa: exigir também os extras (mais testes por requisito, ruído).
- **Q4. Severidades.** Recomendação: tabela do item 8 (cenário sem teste e falso verde = alta = `REPROVADO`). Custo: mais `REPROVADO`. Risco: atrito quando um teste cobre o cenário sem o marcador (por isso o rebaixamento a média com o arquivo citado). Alternativa: tudo média (o merge passaria com cenário sem prova).
- **Q5. Nome de subteste.** Recomendação: conferir só o fonte (item 9). Sem custo; sem risco conhecido.
- **Q6. Onde mora e quem roda.** Recomendação: `.apm/hooks/scripts/spec-trace.py`, só o reviewer o roda, fora do `harness.json` e do `sensors_command`. Alternativa: pasta nova `.apm/scripts/` (não provada como implantada pelo `apm install`, risco).
- **Q7. Arquivos pesquisados.** Recomendação: raiz inteira menos as pastas do item 6 e menos `.md`. Risco: em monorepo grande a busca é lenta (limite de 1 MiB por arquivo mitiga) e um `Spec:` em código de produção conta como ligação (o agente confirma lendo). Alternativa: exigir `--tests` (obriga o agente a adivinhar a pasta de testes, e a pasta varia por stack).
- **Q8. Teste fraco.** Recomendação: julgamento do agente por leitura (afirma o `Então`? falharia sem o código?) mais a comparação com o motivo do vermelho do coder, quando vier no pedido. Fora: acrescentar ao skill da F3 a linha "o vermelho vem da asserção do cenário, não de erro do ambiente" (o achado da prova), que mexeria em `acceptance-from-spec` (outra capability); recomendo uma change própria depois.
- **Q9. Fonte V2.0 não lida.** Peço o trecho literal da história e das restrições, se diferirem do resumo do pedido.
- **Q10. Tamanho do PR.** Código ~190 linhas e testes ~290; limite de PR não informado. Se o limite for ~200, dividir em (1) `_gherkin.parse_scenarios` + script + `test_spec_trace.py`; (2) reviewer + `test_reviewer_scenarios.py`. A ordem entre as duas não importa, mas a 2 cita o nome do script.

### Ações do humano fora do código
- Em cada projeto-alvo: depois de `apm update` e `apm install --target claude,copilot`, conferir que o script foi implantado (`Glob **/spec-trace.py`).
- Decidir se cenários herdados sem teste merecem um retrofit (change própria).
- Push, PR (depois dos PRs #33 a #36 da F3), mesclagem; arquivar `reviewer-confere-cenarios` e rodar a retrospectiva depois do merge.

## Risks / Trade-offs

- [Confiança verde, mas o reviewer real só se prova num projeto] → testes provam o script e o texto; a prova real é disparar o reviewer num projeto de prova com um cenário sem teste, um órfão e um herdado (task 6.4).
- [`Spec:` presente e teste fraco: o script só prova o texto] → o agente lê cada teste ligado (Decisão 8); o script nunca declara "aceitação provada".
- [`__pycache__` sujando o `git status`] → `dont_write_bytecode` antes do import, `-B` na chamada e teste que confere a pasta dos scripts.
- [Colisão de literal e prefixo] → prefixo mais longo, `AMBIGUO` na colisão exata.
- [Cenário renomeado numa change faz o teste antigo virar órfão] → é o alvo do `ORFAO`; o coder atualiza a linha.
- [Falsos órfãos em fixtures] → neste repositório os testes têm exemplos de `Spec:` em strings e aparecem como `ORFAO`; o agente os descarta ao ler (informado no README).
- [Mais `REPROVADO`] → intencional (rotina de quem opera, no README).

## Migration Plan

1. Testes vermelhos (`test_spec_trace.py`, `test_reviewer_scenarios.py`).
2. `_gherkin.parse_scenarios`, depois `spec-trace.py`, depois a edição do reviewer.
3. Sessão principal: `apm install --target claude,copilot`, README, conferir cópias.
4. Prova em projeto de prova (task 6.4).
5. Rollback: reverter o commit; nada é publicado antes do PR de release.

## Decisão do Emiliano: cenários de comportamento do modelo

Dois cenários de `sdlc-agent-roles` descrevem comportamento do modelo e ficam **`SEM_TESTE` conhecidos**, cobertos só pela prova de comportamento (task 6.4):

- `Reviewer confere cada cenário contra um teste / Revisão de change com cenários`
- `Achados de cenário e veredito / Cenário novo sem teste`

Escolha (b): não ligar `Spec:` a um teste de texto que pareça provar o comportamento. O texto do agente já é guardado por testes estruturais sem `Spec:`. Por isso `spec-trace.py --change reviewer-confere-cenarios` sai 2 nesta change: os dois `SEM_TESTE` são esperados e devem ser citados no PR como "conhecidos, cobertos pela 6.4".

## Estimativa de tamanho

- **Código**: `spec-trace.py` ~150, `_gherkin.parse_scenarios` ~15, `sdlc-reviewer.agent.md` +~25: **~190 linhas**.
- **Testes** (estimados à parte): `test_spec_trace.py` em tabela, ~1,4 vez a lógica do script (~165) = ~230; `test_reviewer_scenarios.py` em tabela, ~60: **~290 linhas**.
- Documentação (sessão principal): README ~25 linhas.
- Total ~480 linhas; excede ~200 se esse for o limite do PR (Q10).
