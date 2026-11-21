# Design

## Context

O coder (`.apm/agents/sdlc-coder.agent.md`) executa as Operations do canvas, tem a ferramenta `Skill`, escreve só em `code_prefixes` (`.apm/`, `scripts/`, `tests/`) e já relata o vermelho do TDD. A F1 fixou o bloco Gherkin por requisito; a F2 trouxe `_gherkin.py` (`effective_requirements`) e o sensor. Os skills vivem em `.apm/skills/<nome>/SKILL.md` e o `apm install` os copia para `.claude/skills/` e `.agents/skills/` (e os agentes para `.claude/agents/` e `.github/agents/`). Os testes de contrato dos agentes (`tests/agents/test_contract.py`) conferem neutralidade (`STACK_TERMS`), skills citadas e cópias idênticas. O coder **não** tem `AskUserQuestion`: ele não consegue perguntar ao humano, só devolver a pergunta à sessão principal.

Não li a especificação APM_SETUP_V2.0 no Drive; uso os critérios e restrições do pedido.

## Goals / Non-Goals

**Goals:**
- Todo cenário aprovado vira ao menos um teste de aceitação ligado à spec, que falha antes do código e passa depois.
- Stack-agnóstico: o skill descobre o framework; sem framework, propõe e para.
- Texto que um teste estático consegue proteger, e uma convenção de ligação que a F4 possa conferir.

**Non-Goals:**
- Conferir cenário contra teste (F4, reviewer).
- Executar o Gherkin (`.feature`, runner de BDD) ou gerar código de teste por script.
- Instalar ferramenta, editar `harness.config.json` ou `CLAUDE.md` (fora de `code_prefixes`).
- Perfis de SDLC ou novo framework de testes no pacote.

## Decisions

1. **Onde o skill mora.** `.apm/skills/acceptance-from-spec/SKILL.md`, público (processo e harness, não conhecimento de domínio; ver `skill-retrospective`). Frontmatter igual ao dos skills autorais: `name`, `description` (quando usar, em português), `license: MIT`, `metadata` (`author`, `version`). Corpo curto (meta: até ~120 linhas), sem pasta de referências nem script: é instrução, não ferramenta. Passos do corpo: (1) listar cenários, (2) descobrir framework, (3) escrever teste ligado, (4) vermelho, (5) código, (6) verde, (7) relatório.
2. **Como o coder o invoca.** Edição só de texto em `sdlc-coder.agent.md`: um item em "O que você faz", antes do item que executa as Operations: "Para cada Operation que realiza um requisito com `Cenário:` aprovado, use o skill `acceptance-from-spec` **antes** de implementar", e uma linha em "Entregável" exigindo o teste, o vermelho e o verde por cenário. O nome entra entre crases (como os demais), então `SKILLS_BY_ROLE` do `test_contract.py` passa a exigi-lo e o regex de "skills citadas existem" passa a cobri-lo. Cuidado com `STACK_TERMS`: nada de nomes de ferramenta no agente. O coder não ganha ferramenta nova nem limite novo.
3. **Quais cenários.** Os `Cenário:` do bloco gherkin dos requisitos `ADDED`/`MODIFIED` dos deltas em `openspec/changes/<change>/specs/*/spec.md` (os que o sensor da F2 garante existirem); `REMOVED` não gera teste. Os `#### Scenario:` extras (WHEN/THEN) são recomendados mas não obrigatórios: cada um vira teste só se descrever comportamento observável distinto. O skill lê o markdown direto (formato fixo da F1); **não depende de `_gherkin.py`**, cujo caminho implantado varia por host. Quem quiser listar por código dentro deste repo usa `effective_requirements` (útil à F4).
4. **Convenção de ligação.** Linha literal `Spec: <capability> / <nome do requisito> / <título do cenário>`, com os três textos copiados da spec, em comentário na sintaxe da stack, ou no nome/rótulo/descrição do teste quando o framework os aceita. O separador ` / ` é o mesmo da saída do sensor. Um teste pode cobrir mais de um cenário repetindo a linha; um cenário pode ter vários testes. A busca da F4 é um `grep -F` por requisito; o título é único dentro do requisito (regra da F1), por isso a trinca é a chave. Limitação: título ou nome que contenha ` / ` fica ambíguo (Q1).
5. **Provar o vermelho sem stubs.** O coder roda o teste de aceitação recém-escrito com o comando mais estreito que o framework oferecer (senão o `sensors_command`), registra `comando`, `N falhas`, e classifica o vermelho: *asserção* (o comportamento ainda falta) ou *símbolo ausente* (a função/módulo de produção ainda não existe; em stacks compiladas é a forma normal de vermelho). Proibido criar implementação vazia ou valor fixo só para o teste executar. Se o teste já passa antes do código, algo está errado (teste fraco ou funcionalidade já existente): o coder relata e não segue em silêncio. Evidência só no relatório (o coder não escreve fora de `code_prefixes`; guardar em arquivo é Q4).
6. **Verde.** Depois do código, rodar o teste estreito e o `sensors_command` inteiro; relatar a contagem. O skill confere se o `sensors_command` de fato executa os testes de aceitação (por exemplo, a pasta ou o filtro); se não executa ou está vazio, diz "sensores não configurados"/aponta a lacuna e **não** afirma que passaram. Isso é o ponto frágil do critério 2: sem esse cuidado "verde pelos sensores" seria vazio.
7. **Descoberta do framework.** Ordem, parando no primeiro achado: (a) arquivo raiz do agente (`CLAUDE.md`/`AGENTS.md`) declara ferramenta e comando de teste; (b) `sensors_command` do `harness.config.json`; (c) pasta/arquivos de teste existentes e o manifesto de build do projeto (o skill descreve a busca por tipo de arquivo, sem listar nomes de ferramentas). Achou: usa o mesmo framework, a mesma pasta e a mesma convenção de nomes. Conflito entre fontes (CLAUDE.md diz uma coisa, os testes usam outra): pára e reporta.
8. **Sem framework: propor e PARAR.** O skill manda: não escrever teste, não instalar, não editar configuração; devolver à sessão principal uma proposta com 1 a 3 opções (preferir a que acompanha a toolchain do projeto; sem framework novo se o projeto já tem runner), cada uma com motivo, custo, pasta dos testes, comando e como compor no `sensors_command`; pedir a aprovação do Emiliano. O coder não pergunta ao humano (sem `AskUserQuestion`), então a pergunta volta no relatório. A sessão principal registra a escolha (arquivo raiz do agente; `sensors_command` se aplicável) e redispara o coder com a ferramenta aprovada no brief. A tabela "ferramenta por stack" no pacote continua "não informado".
9. **Teste do skill (`tests/agents/test_acceptance_skill.py`).** Em tabela: existência e frontmatter (`name` = pasta, `description`, `license`); trechos obrigatórios (`Spec:`, `Cenário:`, `vermelho`, `verde`, `contagem de falhas`, `sensors_command`, `harness.config.json`, `Pare`, `aprovação`, `não instal`, `code_prefixes`); neutralidade (`STACK_TERMS` do `test_contract` e os quatro termos, no skill); tamanho máximo; o coder cita o skill antes das Operations; cópias em `.claude/skills/` e `.agents/skills/` idênticas à fonte; o exemplo de marcador do skill casa com o regex canônico do teste. `test_contract.py` ganha o skill em `SKILLS_BY_ROLE["sdlc-coder"]` e no regex de citação. O comportamento do modelo não é provado aqui (ver Riscos).
10. **Só adições.** Nenhum hook, `_gherkin.py`, spec ou agente além do coder muda. O `harness.json` não muda (o sensor da F2 continua igual).

## Decisões em aberto (do humano)

- **Q1. Formato do marcador.** Recomendação: `Spec: <capability> / <requisito> / <cenário>` numa linha. Custo: o coder copia três textos. Risco: título com ` / ` fica ambíguo (a F4 tolera dividindo pelo primeiro e pelo último separador). Alternativa: só o título do cenário no nome do teste (mais curto, ambíguo entre requisitos) ou um identificador gerado (precisa de ferramenta).
- **Q2. Um teste por `Cenário:` (recomendado) ou por requisito?** Custo: mais testes; o bloco da F1 costuma ter 1 cenário, então é pouco. Risco da alternativa: requisito com vários cenários coberto por um teste só, sem prova de cada comportamento.
- **Q3. Quem escreve o plano de testes.** Recomendação: só o coder usa o skill; o planner continua só pondo "testes primeiro" no `tasks.md`. Alternativa: o planner também citar o skill (edição do planner, mais superfície).
- **Q4. Onde fica a evidência de vermelho/verde.** Recomendação: só no relatório do coder (já é o padrão de "Evidência de TDD"). Alternativa: arquivo de evidência em `tests/` ou em `openspec/changes/<c>/` (o coder não escreve em `openspec/`; custo de um artefato novo).
- **Q5. Vermelho por símbolo ausente conta?** Recomendação: sim, declarado como tal, porque em stacks compiladas é a única forma de vermelho sem stub. Risco: um erro de digitação no teste parece vermelho; mitigado por exigir que o relatório cite a mensagem de falha.
- **Q6. Sem framework: o que o coder devolve.** Recomendação: relatório "BLOQUEADO: ferramenta de teste não definida" com as opções, sem nenhuma escrita. Alternativa: escrever os testes em texto (pseudocódigo) num arquivo de `tests/` para o humano ver; mais conveniente, mas é escrita antes da aprovação.
- **Q7. Registrar a ferramenta aprovada.** Recomendação: a sessão principal grava no `CLAUDE.md` do projeto (fonte de verdade), e no `sensors_command` se faltar. Alternativa: chave nova no `harness.config.json` (muda o contrato do config; não nesta change).
- **Q8. Helper para listar cenários.** Recomendação: nenhum agora (sem script; o skill lê o markdown). Alternativa: modo `--list-scenarios` no `gherkin-sensor.py` (mexe no F2; o caminho implantado varia por host, então o coder não o acharia de forma estável).
- **Q9. Aplicar `STACK_TERMS` ao skill (recomendado).** Custo: o skill não pode exemplificar com nomes de ferramentas, só descrever. Risco: texto um pouco mais abstrato.
- **Q10. Fonte V2.0 não lida.** Peço o trecho literal da H3 e das restrições, se diferirem do resumo.

A seção "Decisões do humano" fica vazia até a aprovação.

### Ações do humano fora do código
- Em cada projeto-alvo: depois de `apm update`, conferir se o `sensors_command` roda os testes de aceitação; se não houver ferramenta de teste, aprovar a proposta do coder na primeira `apply`.
- Registrar a ferramenta aprovada no `CLAUDE.md` do projeto (ou pedir à sessão principal).
- Push, PR, mesclagem; arquivar `acceptance-from-spec` e rodar a retrospectiva depois do merge.

## Risks / Trade-offs

- [Confiança amarela: o comportamento do modelo não é provável por teste estático] → o teste prova o texto (skill e coder); a prova real é uma execução do coder num projeto de prova, com o relatório mostrando vermelho e verde, registrada no PR (task 6.4).
- [Critério 2 vazio se o `sensors_command` não roda a aceitação] → o skill confere e relata a lacuna; README avisa.
- [Coder inventa testes que passam de primeira] → regra: se o teste não está vermelho, relatar; o reviewer (F4) fecha o ciclo.
- [Skill neutro demais para ser acionável] → instruções por comportamento (onde procurar, o que relatar), sem nomes de ferramenta; exemplos genéricos.
- [Marcador copiado errado] → a F4 detecta; até lá, o teste do repo não confere projetos-alvo.
- [Mais um passo na primeira `apply` sem ferramenta] → intencional (critério 3); documentado como mudança de rotina e no aviso de migração.
- [`.claude/` e `.github/` implantados divergirem] → teste de cópias idênticas; `apm install` roda pela sessão principal.

## Migration Plan

1. Testes vermelhos (`test_acceptance_skill.py`, ajustes do `test_contract.py`).
2. Skill, depois a edição do coder.
3. Sessão principal: `apm install --target claude,copilot`, README (seção e aviso), conferir cópias.
4. Prova num projeto de prova (task 6.4).
5. Rollback: reverter o commit; nada é publicado antes do PR de release.

## Estimativa de tamanho

- Texto de produção: `SKILL.md` ~110 linhas, `sdlc-coder.agent.md` +~14, `test_contract.py` ~+6: ~130 linhas.
- Testes (tabela de casos, ~1,4 vez a lógica equivalente; a "lógica" aqui é pequena porque o produto é texto): `test_acceptance_skill.py` ~120 linhas, ajustes ~8: ~130 linhas de teste, estimadas à parte.
- Documentação (sessão principal): README ~30 linhas.
- Limite de PR: não informado; ~260 linhas no total, cabe numa Operation só. Se o limite for ~200, dividir: (1) skill + teste; (2) edição do coder + contrato.
