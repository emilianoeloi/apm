# SPDD Analysis: Endurecer o spec-trace (F6)

## Original Business Requirement

Pedido da sessão principal (verbatim, trecho): "Planeje a F6 do apm: "Endurecer o spec-trace" (follow-up das revisões da F4; fora da spec V2.0, escolhido pelo Emiliano). [...] Só adições e correções; stack-agnóstico; o reviewer continua somente leitura."

Ressalvas e achados abertos:
1. (baixa) `read_text` faz `lstat` antes do `open`: há uma janela de corrida (arquivo trocado por FIFO entre as duas chamadas) e o `open` não usa `O_NOFOLLOW`/`O_NONBLOCK`. Sugestão do reviewer: `os.open` com `O_RDONLY|O_NONBLOCK|O_NOFOLLOW` e `fstat` no descritor.
2. (baixa) `ends_title`: sufixos `_`, `.`, `-` e `(` depois do título ainda contam como fechamento de comentário (por exemplo `Caso - feliz` e `Um_2` casam com `Caso`); mais permissivo que o necessário. Decida: aceitar só fechamentos conhecidos (`*/`, `")`, `'''`, `"""`, `-->`, `#`...) ou documentar o limite; recomende.
3. (baixa) Faltam subtestes com tab e espaço não separável (NBSP) antes do fechamento em tests/hooks/test_spec_trace.py.
4. (média, atrito da prova) O reviewer, numa execução sem a ferramenta Glob, usou `find` e achou 4 cópias do script (3 em `apm_modules/`). O agente deve dizer que a cópia certa é a implantada do host (`.claude/hooks/apm/...` ou `.github/hooks/scripts/apm/...`), fora de `apm_modules/`, e que `find` é o plano B quando não há Glob.
5. (informativa) A prova também mostrou: o script não confere ordem/legibilidade... (apenas se você achar algo mais relevante lendo o código; não invente).

Decida e documente: quais ajustes entram (recomendação por Q), o impacto em projetos que já usam o spec-trace (a regra de fechamento mais estrita pode virar ORFAO em marcadores antes aceitos: avalie o risco e o aviso de migração), e o tamanho.

## Domain Concept Identification

### Existing Concepts (from codebase)
- **Marcador `Spec:`** (F3/F4): linha literal `Spec: <capability> / <requisito> / <cenário>` ligando teste e cenário; casamento por prefixo mais longo.
- **Fim do título** (`ends_title`): decide se o resto da linha depois do título é fechamento de comentário (casa) ou texto (não casa, vira `ORFAO`). Hoje: vazio ou não alfanumérico.
- **Leitura de arquivo de busca** (`read_text`): ignora `.md`, não regular, grande, binário e ilegível; usa `lstat` e depois `open`.
- **Estados** `COBERTO`, `SEM_TESTE`, `HERDADO_SEM_TESTE`, `ORFAO`, `AMBIGUO` e a saída 0 ou 2; `SEM_TESTE` reprova, `ORFAO` e `AMBIGUO` são média.
- **`sdlc-reviewer`**: acha o script por `Glob **/spec-trace.py`; a prova real mostrou que, sem `Glob`, ele cai em `find` e vê cópias de `apm_modules/`.
- **Implantação por host**: `.claude/hooks/apm/.apm/hooks/scripts/` e `.github/hooks/scripts/apm/.apm/hooks/scripts/`; cópias de dependência em `apm_modules/`.
- **Gate de Gherkin** (F2) e testes de cópias idênticas, que denunciam texto do agente ou script fora da fonte.

### New Concepts Required
- **Fechamento conhecido** (`CLOSERS`): lista curta e extensível dos tokens que podem seguir o título; torna a regra explícita e testável.
- **Abertura sem corrida**: abrir o arquivo já sem seguir link e sem bloquear e conferir o tipo no próprio descritor.
- **Cópia certa do script**: a do host, fora de `apm_modules/`; `find` como plano B.

### Key Business Rules
- O script só prova o vínculo; um falso `COBERTO` é pior que um `ORFAO` (o vínculo parece provado sem ser).
- O script nunca escreve e nunca trava; qualquer arquivo estranho é ignorado.
- O reviewer continua somente leitura (`Read, Grep, Glob, Bash`).
- Só adições e correções; nenhum nome de ferramenta de teste.

## Strategic Approach

### Solution Direction
- Três correções pequenas no script (leitura e fim do título) e uma de prosa no agente, cada uma coberta por teste escrito antes. Specs por `MODIFIED` (texto integral) e um requisito `ADDED` para a regra do fim do título, que não estava escrita em requisito algum.

### Key Design Decisions
- **Q1 leitura**: `os.open` com `O_NONBLOCK|O_NOFOLLOW` e `fstat` → recomendado; troca um `lstat` por caminho (janela de corrida) por checagem no descritor; custo ~10 linhas.
- **Q2 fim do título**: lista de fechamentos conhecidos (A) → recomendado; B (documentar) mantém falso `COBERTO`; C (lista de rejeição) quebra `-->`.
- **Q3 tab/NBSP**: subtestes dentro do cenário "Fechamento conhecido"; nascem verdes (caracterização) e são provados por mutação manual.
- **Q4 cópia certa**: prosa no reviewer com os dois caminhos de host e `find` com `-not -path "*/apm_modules/*"`.
- **Q5 `Spec:` dentro de palavra**: fica de fora (muda o contrato do marcador; nunca observado).
- **Q6 tamanho**: um PR só.

### Alternatives Considered
- Manter `lstat` e documentar a corrida: simples, mas o script pode travar com FIFO plantado na janela.
- Rejeitar só `_ . - (`: menos código, mas rejeita `-->` e deixa passar `,` e `:`.
- Sem caminhos no texto do agente: mais robusto a mudança do APM, mas menos útil ao reviewer.

## Risk & Gap Analysis

### Requirement Ambiguities
- Quais fechamentos o Emiliano considera "conhecidos": a lista inicial é minha, a partir dos exemplos do pedido (`*/`, `")`, `'''`, `"""`, `-->`, `#`) mais famílias comuns; peço confirmação.
- Se a F4 já foi publicada (a tag `v1.5.0` é anterior ao PR #38; não verifiquei o release PR aberto): define se há migração real.
- Item 5 do pedido vem truncado ("não confere ordem/legibilidade..."); não o li por inteiro e não inventei requisito a partir dele.

### Edge Cases
- Marcador seguido de `;` ou `,` (por exemplo `t.Run("Spec: ... / Um");` termina em `"`, aceito; `Spec: ... / Um;` não): vira `ORFAO` por decisão.
- Título que o próprio cenário termina em pontuação: o resto vazio; a regra olha o que vem depois do título completo, então não afeta.
- Arquivo de texto trocado por link depois da listagem: `ELOOP` vira `None`.
- Sistema sem `O_NOFOLLOW`: `getattr(..., 0)` degrada; `fstat` e `O_NONBLOCK` ainda protegem contra FIFO.

### Technical Risks
- **`SEM_TESTE` espúrio** (alto efeito, baixa chance): marcador com fechamento fora da lista reprova. Mitigação: `ORFAO` mostra a linha, forma canônica independe da lista, a lista é uma constante; aviso no README e CHANGELOG.
- **Teste da corrida acoplado a `os.open`**: aceito, porque o contrato é a abertura sem seguir link e sem bloquear; os testes de FIFO e link por processo seguem como prova comportamental.
- **Testes verdes de nascença** (tab/NBSP, fechamentos conhecidos): `lstrip()` já remove tab e NBSP; prova por mutação manual.
- **Texto do agente com caminhos de host**: envelhece se o APM mudar o destino; o teste de cópias idênticas e o de texto denunciam.

### Acceptance Criteria Coverage
| AC# | Description | Addressable? | Gaps/Notes |
|-----|-------------|--------------|------------|
| 1 | Leitura sem janela de corrida (`O_NOFOLLOW`/`O_NONBLOCK`, `fstat`) | Yes | teste por subprocesso com `os.open` interceptado |
| 2 | Decidir fechamentos conhecidos vs documentar, com recomendação | Yes | A recomendado; B e C descritos |
| 3 | Subtestes de tab e NBSP | Yes | verdes de nascença, com mutação manual |
| 4 | Reviewer diz a cópia certa e o plano B | Yes | texto provado por teste; comportamento por prova humana (6.4) |
| 5 | Achado extra só se relevante | Partial | só `Spec:` dentro de palavra, deixado de fora (Q5); item truncado |
| 6 | Impacto e aviso de migração | Yes | F4 ainda não publicada até `v1.5.0`; aviso no README e CHANGELOG |
| 7 | Tamanho | Yes | código ~25 linhas + 4 de prosa; testes ~100 linhas |
