---
name: acceptance-from-spec
description: Use na fase apply, antes de implementar uma Operation que realiza um requisito com Cenário aprovado na spec da change. Faz o coder escrever primeiro o teste de aceitação ligado ao cenário pela linha Spec:, provar o vermelho (comando e contagem de falhas, sem stubs), implementar e provar o verde pelo sensors_command. Descobre o framework de teste do projeto; sem framework, propõe a ferramenta e para, sem instalar nada, esperando a aprovação do humano.
license: MIT
metadata:
  author: Emiliano Barbosa
  version: "1.1"
---

# Skill — Aceitação a partir da spec (teste primeiro, por cenário)

Cada `Cenário:` aprovado da change vira ao menos um teste de aceitação, escrito **antes** do código,
visto falhar (vermelho) e depois passar (verde). O skill não fixa framework: descreve o que fazer e o
que relatar. Quem usa é o `sdlc-coder`, com a fase `apply` declarada.

## Antes de começar

1. Leia o arquivo raiz do agente (`CLAUDE.md` ou `AGENTS.md`) e o `harness.config.json`. Anote
   `code_prefixes` (onde você pode escrever testes) e `sensors_command`. Campo ausente ou vazio: diga
   "não informado" e não suponha.
2. Confirme a fase `apply` pelo `phase_cli.py show`. Outra fase: pare e avise.

## Passos

### 1. Listar os cenários

Leia os deltas em `openspec/changes/<change>/specs/*/spec.md`. Pegue os blocos `gherkin` (com
`Cenário:`) dos requisitos sob `## ADDED Requirements` e `## MODIFIED Requirements`. `REMOVED` não gera
teste. Os `#### Scenario:` extras (WHEN/THEN) só viram teste se descreverem um comportamento observável
distinto. Monte a lista: capability, nome do requisito, título do cenário. Um teste por `Cenário:`.
Em requisito `MODIFIED`, o `Cenário:` idêntico (título e passos) ao da spec principal é *herdado*:
não precisa de teste novo e vai no relatório como informativo; o cenário novo ou de passos alterados
exige teste. O `#### Scenario:` extra que ganhar teste leva a linha
`Extra: <capability> / <nome do requisito> / <título do #### Scenario>`, nunca `Spec:` (o `spec-trace`
apontaria `ORFAO`).
Se nenhum requisito ADDED/MODIFIED traz `Cenário:` no bloco `gherkin`, o skill não se aplica: não invente
teste, registre isso no relatório e siga com as Operations normalmente.

### 2. Descobrir o framework de teste

Procure nesta ordem e **pare no primeiro achado**:

1. o arquivo raiz do agente declara a ferramenta e o comando de teste;
2. o `sensors_command` do `harness.config.json` roda testes;
3. já existem pastas e arquivos de teste, e o manifesto de build do projeto os usa.

Achou: use o mesmo framework, a mesma pasta (dentro de `code_prefixes`) e a mesma convenção de nomes.
Duas fontes que se contradizem: pare e reporte o conflito. Não nomeie nem imponha ferramenta.

### 3. Sem framework: proponha e Pare

Nenhuma das três fontes achou framework? **Pare** na Operation que tem `Cenário:`. Nada escrito: não
escreva teste, não instale nada, não edite configuração. Devolva à sessão principal, para a aprovação
do Emiliano, o relatório "BLOQUEADO: ferramenta de teste não definida (nada escrito, aguardando
ferramenta)" com 1 a 3 opções. Prefira a que acompanha a toolchain do projeto. Cada opção traz: motivo,
custo, pasta dos testes, comando e como entraria no `sensors_command`. Só prossiga quando o brief trouxer
a ferramenta aprovada. Operations sem `Cenário:` seguem normalmente, sem teste de aceitação, e vão como
**pendente** no relatório; só a Operation com cenário fica bloqueada. Registrar a escolha em `CLAUDE.md`
ou `harness.config.json` fica como pendência para a sessão principal (fora de `code_prefixes`).

### 4. Escrever o teste ligado ao cenário

Escreva o teste de aceitação do cenário, no estilo do projeto. Ele traz, em comentário, no nome ou no
rótulo do teste, a linha literal, com os três textos copiados da spec:

```
Spec: <capability> / <nome do requisito> / <título do cenário>
```

Exemplo: `Spec: checkout / Pagamento aprovado / Cartão válido confirma o pedido`. O separador é ` / `.
Um teste pode cobrir mais de um cenário repetindo a linha. Título ou nome com ` / ` é ambíguo: avise.
Fixture ou exemplo de teste que precise de uma linha `Spec:` com três campos: monte-a por constante
(rótulo concatenado em tempo de execução). A linha literal no fonte do teste sai como `ORFAO`.

### 5. Vermelho (antes do código)

Rode o teste com o comando mais estreito que o framework oferecer (senão, o `sensors_command`).
Relate o comando, a contagem de falhas e o motivo do vermelho: **asserção** que falha, ou **símbolo de
produção ainda inexistente**. Cite a mensagem de falha, para um erro de digitação não passar por vermelho.
O vermelho vem da asserção do `Então` do cenário (conteúdo da saída ou efeito observável).
Não aceite como vermelho o erro do ambiente (arquivo, módulo ou comando ausente, código de saída
genérico): relate a asserção que falhou. Em linguagem compilada, o símbolo de produção ausente declarado vale. Teste que
passa com o programa ausente é falso verde: rode-o antes de o programa existir e reforce-o afirmando o
conteúdo, não só o código de saída.
Proibido criar implementação vazia ou valor fixo só para o teste executar (sem stubs). Se o teste já
passa antes do código, relate (teste fraco ou funcionalidade já existente) e não siga em silêncio. Se
não conseguir observar o vermelho, diga que pulou e por quê.

### 6. Implementar

Escreva o código mínimo da Operation, dentro de `code_prefixes`, até o teste do cenário passar.

### 7. Verde (depois do código)

Rode o teste estreito e depois o `sensors_command` inteiro; relate a contagem de falhas, separada da
execução vermelha. Confira que o `sensors_command` de fato executa os testes de aceitação (pasta ou
filtro). Se estiver vazio ou não os executar, diga "sensores não configurados" ou aponte a lacuna e
**nunca** afirme que a aceitação passou pelos sensores.

### 8. Relatório por cenário

Para cada cenário: a linha `Spec:`, o arquivo do teste, o vermelho (comando, contagem de falhas,
motivo) e o verde (comando, contagem). Cenário sem teste com a sua linha `Spec:` entra como
**pendente**; não declare a Operation concluída. Liste também as pendências fora de `code_prefixes`.
Cenário cujo comportamento é do modelo e só uma prova humana cobre: relate como pendente de prova humana
(`SEM_TESTE` conhecido), com a decisão do humano; não crie teste que finja cobri-lo
nem o ligue por `Spec:`. Liste à parte os extras anotados, os herdados (informativo) e as provas humanas.

## Armadilhas

- **O `spec-trace` lê qualquer linha com `Spec:` como cenário.** Uma constante de rótulo em teste (por exemplo `const SPEC = 'Spec: cap / req / '`) vira cenário órfão no relatório. Monte o rótulo sem o prefixo literal na mesma linha (por exemplo `ROTULO = 'Spec'` e `` `${ROTULO}: cap / req / ${cenario}` ``) e deixe a linha `Spec:` completa só no comentário acima de cada teste.
- **Vermelho de módulo que ainda não existe.** `ERR_MODULE_NOT_FOUND` prova só a ausência do módulo, não a asserção de cada cenário, e criar um stub no projeto é proibido. Para contar falhas por asserção, copie o projeto para uma pasta temporária fora do repositório, ponha lá um módulo descartável cujas funções devolvam `undefined` e rode os testes na cópia: o vermelho vem das asserções, e a cópia some. Relate os dois vermelhos (módulo ausente e por asserção) e diga que o segundo foi na cópia.
- **Teste que espera "vazio" passa com o stub.** Cenários cujo `Então` é lista vazia, `null` ou mensagem em branco passam mesmo com o stub descartável; eles só provam algo junto com um caso que exija conteúdo. Diga quais passaram no vermelho e por quê.

## Limites

- Escreva só em `code_prefixes`. Não instale ferramenta, não mude fase, canvas, spec nem hooks.
- Este skill prova o texto do ciclo; o comportamento do modelo só se prova num projeto real.

## Garantias de rede ou desempenho

Quando o cenário garante ausência de requisição, de cache ou de custo (por exemplo, "voltar sem nova leitura"), o teste estrutural só prova a forma do código, não o comportamento na rede. No cenário, marque a prova manual que é bloqueante (por exemplo, a aba Rede do navegador sem requisição nova) e não trate o teste estrutural como suficiente.
