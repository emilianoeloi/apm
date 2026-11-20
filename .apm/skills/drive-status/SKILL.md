---
name: drive-status
description: >-
  Salva um registro de status no Google Drive ao fim de toda interação que mudou
  algo no projeto (código, fase, branch, commit, PR, merge, decisão ou bloqueio),
  com numeração crescente e nunca editando um status antigo. Use quando o projeto
  guarda seu histórico de progresso como arquivos `<PROJETO>_STATUS_V<n>.md` numa
  pasta do Drive, em vez de (ou além de) commits e issues.
license: MIT
metadata:
  author: local
  version: "1.0"
---

# Skill — Status no Drive

Alguns fluxos de trabalho usam uma pasta do Google Drive como painel de progresso entre
sessões e entre pessoas: cada interação relevante termina com um arquivo novo,
`<PROJETO>_STATUS_V<n>.md`, na pasta do projeto. Esse arquivo é o que outra sessão (ou outro
projeto, como um painel agregador) lê para saber onde as coisas estão, sem precisar abrir o
repositório.

## Quando salvar

- **Ao fim de toda interação que mudar algo**: código escrito, fase do harness alterada,
  branch criada, commit feito, PR aberto, PR mesclado, uma decisão tomada (mesmo sem código),
  ou um bloqueio identificado.
- **Nunca** numa interação só de leitura (responder uma pergunta, mostrar um arquivo, explicar
  algo) sem nenhuma das mudanças acima.
- Dizer "status atualizado" ou "vou registrar isso" sem de fato criar o arquivo não conta —
  é a mesma armadilha de dizer "commitei" sem rodar `git commit`.

## Numeração

1. Leia o status mais novo da pasta antes de escrever (ordene os arquivos pelo número da
   versão, não por ordem alfabética de texto — `V10` vem depois de `V9`).
2. O arquivo novo é a versão seguinte, `V<n+1>`.
3. **Nunca edite um arquivo de status antigo.** Histórico de progresso é append-only; corrigir
   um erro do passado é registrar isso no status novo, não reescrever o antigo.
4. Pasta sem nenhum status ainda: comece em `V1`.

## Campos mínimos

- Data e hora, no fuso do projeto (ex.: `America/Sao_Paulo`).
- Onda/fase do trabalho (se o projeto tiver esse conceito) e fase do harness de SDLC, se houver
  (`proposal`/`apply`/`review`/`done`, ou equivalente).
- Branch.
- Commits relevantes (hash curto basta).
- PR (número e estado, se houver).
- O que foi feito (até ~5 linhas; resumo, não o diff inteiro).
- O que foi testado e o que não foi testado.
- Próximo passo.
- Bloqueios (ou "nenhum").

Dado que não existe ou não se aplica vira **"não informado"**, nunca uma suposição.

## Se o Drive falhar

Salve o conteúdo num arquivo local do repositório (ex.: `docs/STATUS.md`) e avise
explicitamente, no fim da resposta, que o status não foi ao Drive e por quê. Não trate isso
como um erro silencioso — quem lê o painel agregador do Drive não vai saber que esta sessão
aconteceu.

## Onde a regra vive

- Se o projeto é um só, a regra fica no `CLAUDE.md`/`AGENTS.md` da raiz, com o ID da pasta do
  Drive e o nome do `<PROJETO>`.
- Se vários projetos de uma mesma pessoa/time compartilham a mesma convenção (uma pasta "mãe"
  no Drive com uma subpasta por projeto), a regra pode subir para a configuração global do
  agente (ex.: `~/.claude/CLAUDE.md`), descrevendo como derivar `<PROJETO>` do nome da pasta,
  para não repetir a regra em cada repositório.
