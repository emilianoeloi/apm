---
name: skill-retrospective
description: Use ao fechar uma feature (depois do merge, ou antes de arquivar a mudança) para decidir se algum skill conhecido precisa de atualização ou se um skill novo deve ser criado. Cobre o que a feature ensinou, atualizar vs criar, em qual repositório (público ou privado) cada coisa entra, como versionar e o que nunca pode entrar num skill.
license: MIT
metadata:
  author: Emiliano Barbosa
  version: "1.0"
---

# Skill — Retrospectiva de skills (depois de cada feature)

O conhecimento que uma feature gera se perde se ficar só no código e no histórico da conversa.
Esta retrospectiva é o último passo do ciclo: ela devolve o aprendizado para os skills, para a
próxima feature começar mais esperta. É curta (10 a 20 minutos) e **sempre termina com uma
decisão registrada**, mesmo que a decisão seja "nada a mudar".

## Quando rodar

- Depois que a feature foi mesclada (ou, no mínimo, validada e publicada), antes de dar o ciclo por encerrado.
- Uma vez por feature, não por commit. Em releases só de versão e documentação, não há o que revisar.

## Passo 1 — Levantar o que a feature ensinou

Releia o diff, o `design.md`, a revisão de código e o que deu errado no caminho. Procure:

- **Armadilhas** que custaram tempo (erro de configuração, comportamento de plataforma, cache, ferramenta).
- **Decisões** com trade-off real (por que A e não B) que a próxima feature vai enfrentar de novo.
- **Padrões** que funcionaram e merecem repetição (um jeito de testar, de verificar, de publicar).
- **Achados da revisão** que apontam uma regra faltando num skill.
- **Atritos do fluxo** (passo que travou, permissão, ferramenta que falhou).

## Passo 2 — Cruzar com os skills que a feature usou

Liste os skills usados na feature. Para cada um pergunte: ele cobriu o caso? Estava errado ou
desatualizado? Faltou algo que a feature precisou descobrir sozinha?

## Passo 3 — Decidir: nada, atualizar ou criar

| Situação | Decisão |
|---|---|
| O skill cobria tudo e nada novo foi aprendido | **Nada a mudar** (registre em uma linha) |
| O conhecimento novo cabe na responsabilidade de um skill existente | **Atualizar** esse skill (nova seção, não reescrita) |
| O conhecimento é de outro assunto, ou o skill existente ficaria com duas responsabilidades | **Criar** um skill novo |
| Um skill dá orientação que a feature provou errada | **Corrigir** e dizer o que mudou |
| O aprendizado só vale para este projeto | **Não** vai para skill: vai para o `AGENTS.md`/`CLAUDE.md` ou para docs do projeto |

Regra de bolso: um skill = uma responsabilidade. Prefira atualizar a criar; crie quando o
assunto tiver nome próprio e gatilho de ativação próprio.

## Passo 4 — Escolher o repositório

- **Público** (harness e processo): skills de fluxo SDLC, governança, retrospectiva e do próprio
  harness. Nada que identifique um projeto, uma pessoa ou uma nuvem.
- **Privado** (conhecimento de domínio e de plataforma): arquiteturas, padrões de nuvem, auth,
  QA. Também sem segredos, IDs de projeto, e-mails ou chaves.
- Skills de **um projeto específico** levam o prefixo do projeto (`<projeto>-...`) e só são
  instalados nos projetos que o usam. Conhecimento genérico não cita nome de projeto.

## Passo 5 — Escrever

- `description` é o contrato de ativação: "Use quando…". Diga quando o skill entra em cena.
- Recursos ficam **dentro** da pasta do skill (`references/`, `scripts/`, `templates/`).
- Atualização = acrescentar seção com título claro; não apague orientação ainda válida.
- **Nunca** coloque: chaves, tokens, IDs de projeto de nuvem, números de projeto, e-mails,
  nomes de pessoas ou URLs internas. Troque por `<projeto>`, `<id>`, `<conta>`.
- Confira antes de commitar: `grep -inE "gmail|@|AIza|token|secret"` no diff do skill.
- Skill vendorizado (ex.: `openspec-*`, `spdd-*`) **não** se edita à mão: customize num skill autoral.

## Passo 6 — Publicar

1. Branch e pull request no repositório do skill (nunca direto na `main`).
2. Versionar o pacote: `PATCH` correção · `MINOR` skill novo ou seção nova compatível ·
   `MAJOR` quebra de comportamento. A tag é criada **depois** do merge.
3. No projeto consumidor, depois da tag nova: atualizar o `ref` no `apm.yml`, rodar
   `apm install` e commitar `apm.yml`, `apm.lock.yaml` e os diretórios implantados.

## Passo 7 — Registrar a decisão

No fechamento da feature (status do projeto ou nota de release), uma linha por skill tocado:

```
Skills: <skill> atualizado (<o que>) · <skill> criado (<por quê>) · nada a mudar em <skill>
```

## Armadilhas

- Transformar a retrospectiva em cerimônia longa: se nada foi aprendido, diga "nada a mudar" e pare.
- Criar skill demais: dois skills com responsabilidade parecida competem na ativação.
- Copiar para o skill um detalhe do projeto (nome, ID, e-mail) em vez do princípio por trás dele.
- Esquecer de atualizar o `ref` no projeto consumidor: o skill novo existe, mas ninguém o usa.
