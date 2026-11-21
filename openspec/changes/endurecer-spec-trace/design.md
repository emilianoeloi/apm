# Design

## Context

`spec-trace.py` (F4) é só leitura e vive em `.apm/hooks/scripts/`. Duas funções interessam: `read_text(path)` (hoje `os.lstat` + `S_ISREG`, depois `open(path, "rb")`) e `ends_title(rest)` (hoje: resto vazio ou começa, após `lstrip()`, por caractere não alfanumérico). O `sdlc-reviewer` manda achar o script por `Glob **/spec-trace.py`. A prova do reviewer (`docs/roteiro-de-teste.md`, "Prova do reviewer") mostrou o atrito 4. As revisões da F4 trouxeram os itens 1 a 3.

`str.lstrip()` sem argumento já remove espaço, tab e NBSP; por isso os subtestes de tab e NBSP (item 3) **já passam**: são testes de caracterização, não de correção.

Não li a V2.0 no Drive; esta change não depende dela.

## Goals / Non-Goals

**Goals:**
- Fechar a janela de corrida da leitura sem mudar o comportamento observável (link, FIFO e dispositivo continuam ignorados).
- Tornar o fim do título uma regra explícita, estreita e testada.
- Dizer ao reviewer qual cópia do script usar e qual é o plano B sem `Glob`.

**Non-Goals:**
- Novas ferramentas, hooks ou entrada no `sensors_command`; mexer em skill, coder ou planner (F5, outra branch).
- Detectar `Spec:` só como palavra inteira (Q5); modo `--all`; ler `.md`.

## Decisions

1. **Leitura (Q1).** `read_text` passa a: ignorar `.md` pela extensão (como hoje); `os.open(path, O_RDONLY | O_NONBLOCK | O_NOFOLLOW)`, tomando cada flag por `getattr(os, "O_NOFOLLOW", 0)` (stack e sistema agnósticos, sem quebrar onde a flag falta); `os.fstat(fd)` e `S_ISREG` no descritor; ler no máximo `MAX_BYTES + 1` do descritor e fechar no `finally`. `OSError` (inclusive `ELOOP` de link, `ENXIO` de FIFO sem escritor, falta de permissão) continua virando `None`. Não há mais `lstat` por caminho, então não há janela. Em arquivo regular `O_NONBLOCK` não muda nada. O `os.walk` não segue links de pasta, como hoje.
2. **Fim do título (Q2).** Constante `CLOSERS` (tupla) no topo do script; `ends_title(rest)` vira: `rest = rest.lstrip()`; `True` se vazio ou `rest.startswith(CLOSERS)`. Valor inicial: `*/`, `-->`, `--]]`, `--}}`, `%}`, `?>`, `"`, `'`, `` ` ``, `)`, `]`, `}`, `#`, `//`. Cobre `*/` (C e afins), HTML/XML, Lua, templates, PHP, aspas e parêntese de rótulo de teste, `#` e `//` de comentário depois do marcador. Sufixos como `-`, `_`, `.`, `(`, `,` e letras ou dígitos não casam. A docstring e o `--help` trazem a regra. Acrescentar um fechamento no futuro é uma linha na constante.
3. **Teste da corrida (determinístico).** Um subprocesso Python (`python3 -B -I -c`) carrega o script por `importlib` e troca `os.open` por um invólucro que (a) grava as flags recebidas, (b) troca o arquivo por um FIFO (`os.unlink` + `os.mkfifo`) e (c) delega ao `os.open` real. A asserção é que as flags contêm `O_NONBLOCK` e `O_NOFOLLOW` e que `read_text` devolve `None` dentro do prazo. Com o código atual o invólucro nunca é chamado (o `open` embutido não passa por `os.open`), então o vermelho vem da asserção das flags, não de erro de ambiente. O subprocesso evita `sys.dont_write_bytecode = True` vazar para o processo de teste.
4. **Reviewer (Q4).** Em "Cenários x testes → Como conferir": a cópia certa é a implantada do host, em `.claude/hooks/apm/.apm/hooks/scripts/spec-trace.py` ou `.github/hooks/scripts/apm/.apm/hooks/scripts/spec-trace.py`; ignorar as de `apm_modules/` (são cópias de dependência, não a do host); sem `Glob`, `find . -name spec-trace.py -not -path "*/apm_modules/*"`. Sem nome de ferramenta de teste e sem os termos de neutralidade. `tools` fica `Read, Grep, Glob, Bash`.
5. **Specs.** `MODIFIED` com texto integral nos requisitos tocados (cenários idênticos aos da principal são herdados e não exigem teste; os novos exigem a linha `Spec:`). O requisito `Fim do título do marcador` é `ADDED` porque a regra não estava escrita em nenhum requisito (só no docstring e em testes extras).
6. **Cenários só de prova humana.** Nenhum cenário novo é só de prova humana: os do bloco são provados por teste (o de cópia certa do script prova o **texto** do agente, não o comportamento do modelo). O comportamento do modelo escolhendo a cópia certa, sem `Glob`, é uma prova humana de tasks (6.4), sem `Cenário:` próprio.
7. **Migração (impacto).** Ver "Decisões em aberto, Q2": a regra mais estrita pode transformar `COBERTO` em `ORFAO` + `SEM_TESTE` (reprova) num marcador com sufixo fora de `CLOSERS`.

## Decisões em aberto (do humano)

Assumidas as recomendações nos artefatos; "Decisões do humano" fica vazia até a aprovação.

- **Q1. Endurecer a leitura (item 1).** Recomendação: sim, `os.open` com `O_NONBLOCK | O_NOFOLLOW` e `fstat` no descritor. Custo: cerca de 10 linhas. Risco: `getattr(os, "O_NOFOLLOW", 0)` degrada em sistema sem a flag (então só o `fstat` protege contra FIFO; ainda sem travar, por `O_NONBLOCK`). Alternativa: manter o `lstat` e documentar a corrida (custo zero, mas um FIFO plantado na janela trava o script até o prazo do `Bash`).
- **Q2. Fim do título (item 2).** Recomendação: **A, lista de fechamentos conhecidos** (`CLOSERS`). Alternativas: **B** só documentar o limite (zero risco de migração, mas `Caso - feliz` continua cobrindo `Caso` e um typo vira falso `COBERTO`, que é o oposto do que o script quer provar); **C** lista de rejeição (`_ . - (`), que quebra `-->` e é mais frágil. Custo de A: ~8 linhas. Risco: fechamento de comentário de linguagem fora da lista vira `ORFAO` + `SEM_TESTE`, que **reprova** (alta). Mitigação: a lista cobre as famílias comuns; o `ORFAO` mostra a linha; a forma canônica (marcador sozinho no fim da linha) não depende da lista; acrescentar um fechamento é uma linha. **Impacto em projetos que já usam**: o spec-trace só existe a partir do PR #38 e a tag `v1.5.0` é anterior; se esta change for mesclada antes da publicação da F4, ninguém migra. Se a F4 for publicada antes, avisar no README e no CHANGELOG ("depois do título só valem fim de linha ou fechamento conhecido; conserte a linha ou ponha o marcador sozinho no fim") e orientar o reviewer a rebaixar a média o `SEM_TESTE` cujo teste ligue o cenário com sufixo fora da lista (a regra "cobertura sem a linha `Spec:`" já cobre). Perguntas ao Emiliano: a F4 já foi publicada? Quer mais algum fechamento na lista?
- **Q3. Subtestes de tab e NBSP (item 3).** Recomendação: sim, dentro do teste do cenário "Fechamento conhecido depois do título" (uma tabela de fechamentos x espaços: `" "`, `"\t"`, `" "`, `""`). Custo baixo. Risco: nasce verde (caracterização); a prova de que ele morde é uma mutação manual (trocar `lstrip()` por `lstrip(" ")`, ver falhar, reverter), registrada no relatório.
- **Q4. Cópia certa do script no reviewer (item 4).** Recomendação: sim, nos termos da decisão 4. Custo: ~3 linhas de prosa. Risco: o texto cita os dois caminhos de host; se o APM mudar o destino, o texto envelhece (o teste de cópias implantadas apontaria). Alternativa: só "fora de `apm_modules/`", sem caminhos (mais robusto, menos útil).
- **Q5. `Spec:` dentro de palavra (observação, item 5).** `line.find("Spec:")` casa `InSpec:` ou `MySpec:` e pode gerar `ORFAO` se a linha tiver dois ` / `. Recomendação: **não** incluir agora (baixa, nunca observada, e estreitar o marcador é mudança de contrato); registrar para uma próxima rodada. Alternativa: exigir início de palavra antes de `Spec:` (um `re` pequeno).
- **Q6. Tamanho do PR.** Código ~25 linhas (script) mais ~4 linhas de prosa do agente; testes ~100 linhas (a maior parte é o harness da corrida). Testes em tabela valem ~1,4x o código segundo a regra usual, mas aqui o código é minúsculo e o harness da corrida pesa: previsto ~100, ~4x. Limite de PR não informado; recomendo um PR só.

### Ações do humano fora do código
- Dizer se a F4 já foi publicada e se há projeto externo com `Spec:` e sufixo fora da lista (Q2).
- Aprovar as recomendações Q1 a Q6.
- Prova humana (6.4): disparar o reviewer **sem** a ferramenta `Glob`, num projeto com `apm_modules/` contendo cópias do script, e registrar qual cópia ele usou.

### Decisões do humano
Plano aprovado pelo Emiliano com Q1 a Q6 como recomendadas e a lista `CLOSERS` como proposta (a lista continua uma constante extensível). A F4 está mesclada (#38) mas a tag `v1.6.0` ainda não existe (o PR de release #39 não foi mesclado); se um fechamento faltar, vira `ORFAO` e se acrescenta à constante.

## Risks / Trade-offs

- **`SEM_TESTE` espúrio por fechamento fora da lista** → mitigado por `ORFAO` com a linha exata, forma canônica e constante extensível (Q2).
- **Teste da corrida acoplado à implementação** (`os.open`) → aceito: o contrato é "abre sem seguir link e sem bloquear"; o teste de FIFO e de link por processo (já existentes) continuam provando o comportamento.
- **Teste verde de nascença** (tab/NBSP e "Fechamento conhecido") → declarado; prova por mutação manual.
- **Texto do agente cita caminhos de host** → o teste de cópias implantadas denuncia mudança.
