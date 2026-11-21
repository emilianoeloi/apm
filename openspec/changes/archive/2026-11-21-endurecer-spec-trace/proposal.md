# Proposal

## Why

As revisões da F4 (reviewer confere cenário contra teste) e a prova de comportamento do reviewer deixaram quatro pontos abertos no `spec-trace`. Esta change (F6) os fecha. Ela está fora da spec V2.0 (escolha do Emiliano); não li a V2.0 no Drive e nada aqui depende dela.

1. **Leitura com janela de corrida (baixa).** `read_text` faz `os.lstat` e só depois `open`. Entre as duas chamadas o arquivo pode virar FIFO ou link, e o `open` comum não usa `O_NOFOLLOW` nem `O_NONBLOCK`: o script pode travar.
2. **Fim do título frouxo (baixa).** `ends_title` aceita qualquer caractere não alfanumérico depois do título. `Caso - feliz`, `Um_2`, `Caso.` e `Caso (extra)` casam com `Caso` e saem `COBERTO`, em vez de `ORFAO`.
3. **Subtestes de espaço em branco ausentes (baixa).** Nada prova que tab e espaço não separável (NBSP) antes do fechamento de comentário continuam aceitos.
4. **Atrito da prova do reviewer (média).** Sem a ferramenta `Glob`, o reviewer usou `find` e achou 4 cópias do script, 3 em `apm_modules/`. O agente não diz qual é a cópia certa nem que `find` é o plano B.

Ao ler o código não achei nenhum outro defeito relevante além de uma observação que **fica de fora** (ver `design.md`, Q5): o marcador `Spec:` casa também dentro de uma palavra (`InSpec:`).

## What Changes

- **`spec-trace.py`, leitura (Q1)**: `read_text` abre com `os.open(path, O_RDONLY | O_NONBLOCK | O_NOFOLLOW)` (cada flag só onde o sistema a tem), confere `S_ISREG` com `os.fstat` no descritor e lê do descritor; link, FIFO e dispositivo continuam ignorados, sem travar mesmo se o arquivo for trocado depois da listagem.
- **`spec-trace.py`, fim do título (Q2)**: o resto da linha depois do título (sem espaço, tab ou NBSP à esquerda) passa a ser aceito só se for vazio ou começar por um fechamento conhecido (`CLOSERS`: `*/`, `-->`, `--]]`, `--}}`, `%}`, `?>`, `"`, `'`, `` ` ``, `)`, `]`, `}`, `#`, `//`). Qualquer outro resto não casa e a linha vira `ORFAO` (se tiver dois ou mais ` / `).
- **`sdlc-reviewer.agent.md` (Q4)**: o passo "Como conferir" diz que a cópia certa do script é a implantada do host (`.claude/hooks/apm/.apm/hooks/scripts/spec-trace.py` ou `.github/hooks/scripts/apm/.apm/hooks/scripts/spec-trace.py`), nunca a de `apm_modules/`, e que `find` (excluindo `apm_modules`) é o plano B quando não há `Glob`. `tools` não muda.
- **Specs**: delta em `spec-trace` (requisito `Busca em arquivos de teste com exclusões` modificado, requisito `Marcador órfão e marcador ambíguo são apontados` modificado, requisito `Fim do título do marcador` acrescentado), em `sdlc-agent-roles` (requisito do reviewer modificado) e em `pacote-generico` (aviso de migração modificado).
- **Testes**: subtestes novos em `tests/hooks/test_spec_trace.py` (corrida na leitura, fechamentos conhecidos com tab e NBSP, sufixos que viram `ORFAO`) e em `tests/agents/test_reviewer_scenarios.py` (cópia certa do script; README).

Só adições e correções; stack-agnóstico; o reviewer continua somente leitura (`Read, Grep, Glob, Bash`).

**Rotina de quem opera**: nenhuma etapa nova. Um marcador antigo com sufixo fora de `CLOSERS` passa a sair `ORFAO` (e o cenário, `SEM_TESTE`, que reprova). Isso vai para o README (sessão principal), o CHANGELOG e o aviso de migração.

**Impacto em projetos que já usam o spec-trace**: o `spec-trace` entrou na F4 (PR #38) e a última tag publicada é `v1.5.0`, anterior a ele (`git tag --contains 063b541` volta vazio). Se esta change entrar antes de a F4 ser publicada, nenhum projeto externo vê o comportamento antigo e o risco de migração é nulo; se a F4 for publicada antes, o risco é baixo (a forma canônica é a linha própria de comentário; o sufixo só aparece em comentário de bloco numa linha só) e o `ORFAO` mostra a linha exata a corrigir. Detalhe em `design.md`.

Fora desta change: `\b` antes de `Spec:` (Q5), modo `--all`, ligar o script ao `sensors_command`, novas ferramentas para o reviewer, mexer em skill, coder ou planner (F5 em outra branch).

## Capabilities

### New Capabilities
- Nenhuma capability nova.

### Modified Capabilities
- `spec-trace`: leitura robusta a troca de arquivo; regra explícita do fim do título; casamento "por prefixo" refinado.
- `sdlc-agent-roles`: o reviewer escolhe a cópia implantada do host e usa `find` como plano B.
- `pacote-generico`: o aviso de migração do README cita a regra do fim do título.

## Impact

- **Arquivos (apply, dentro de `code_prefixes`)**: `.apm/hooks/scripts/spec-trace.py`, `.apm/agents/sdlc-reviewer.agent.md`, `tests/hooks/test_spec_trace.py`, `tests/agents/test_reviewer_scenarios.py`.
- **Fora de `code_prefixes` (sessão principal)**: `README.md` (seção "Conferência de cenários na revisão": regra do fim do título e aviso de migração), `CHANGELOG.md`, cópias implantadas por `apm install --target claude,copilot` (`.claude/hooks/apm/`, `.github/hooks/scripts/apm/`, `.claude/agents/`, `.github/agents/`) e `apm.lock.yaml`, `CLAUDE.md` (opcional). `harness.config.json` não muda.
- **Release**: `fix(agents):` ou `fix(hooks):` (patch). Push, PR e merge são do Elói.
- **Risco principal**: o comportamento do reviewer sobre as cópias só se prova num projeto real (prova humana); o resto é determinístico.
