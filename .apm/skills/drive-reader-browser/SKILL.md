---
name: drive-reader-browser
description: >-
  Lê arquivos e pastas do Google Drive direto do navegador, usando o token OAuth
  que o Firebase Authentication já entrega no login (sem backend, sem chave de
  serviço). Use quando o app é estático (sem servidor) e precisa ler conteúdo do
  Drive do usuário logado: listar subpastas, achar o arquivo mais novo por nome,
  baixar `.md`/texto, ou exportar um Google Docs como texto.
license: MIT
metadata:
  author: local
  version: "1.0"
---

# Skill — Ler o Google Drive do navegador, sem backend

Para um app estático (Firebase Hosting, sem servidor) que já autentica com Google via
Firebase Auth, o token OAuth do próprio login basta para chamar a Drive API v3 direto do
navegador — não precisa de Cloud Function nem de chave de serviço. Este skill cobre como
fazer isso com segurança e sem reinventar os limites básicos.

## Pré-requisitos

- Login com `GoogleAuthProvider`, com `provider.addScope("https://www.googleapis.com/auth/drive.readonly")`
  antes do `signInWithPopup`/`signInWithRedirect`.
- `GoogleAuthProvider.credentialFromResult(result).accessToken` é o token a usar no cabeçalho.
- A **Google Drive API** precisa estar ativada no projeto do Google Cloud (não vem ativada por
  padrão mesmo com o Firebase Auth funcionando); sem isso, toda chamada devolve 403
  `accessNotConfigured`.

## Toda chamada

```
GET https://www.googleapis.com/drive/v3/<recurso>
Authorization: Bearer <token>
Cache-Control: no-store   (ou fetch com { cache: "no-store" })
```

Nunca passe o token como `?access_token=` na URL: ele vaza em logs de proxy, histórico do
navegador e `Referer`. Sempre no cabeçalho `Authorization`.

## Operações comuns

- **Listar subpastas de uma pasta:** `files?q='<id>' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false&fields=nextPageToken,files(id,name)&pageSize=100`.
  Siga `nextPageToken` até esgotar ou até um teto de páginas (proteção contra pasta gigante).
- **Achar arquivos por nome dentro de uma pasta:** troque o `q` por
  `'<id>' in parents and name contains '<termo>' and trashed=false`. O `contains` da Drive API
  casa por termo, não por regex; filtre e ordene no cliente (por exemplo, escolher a maior
  versão por um parser de nome próprio) em vez de confiar só na busca.
- **Baixar conteúdo de um `.md`/texto:** `GET files/<id>?alt=media`.
- **Exportar um Google Docs como texto:** `GET files/<id>/export?mimeType=text/plain` (Docs
  nativo não aceita `alt=media`; o `mimeType` do arquivo diz se é Docs nativo
  `application/vnd.google-apps.document` ou um arquivo de texto comum).
- `pageSize` máximo de `files.list` é 1000; valores maiores são limitados pela API, não é erro.
- Valide todo ID de pasta/arquivo com um formato simples (ex.: `/^[\w-]+$/`) antes de
  colocá-lo em `q=` ou na URL — a Drive API aceita IDs como parte da query, e um ID com aspas
  não validado é um vetor de injeção na própria consulta.

## Limites e resiliência (um app sem backend tem que se defender sozinho)

- **Concorrência:** limite o número de requisições simultâneas (ex.: 6), com uma fila simples;
  não dispare uma requisição por item de uma lista grande de uma vez.
- **Tempo limite por requisição:** use `AbortController` com um teto (ex.: 8s); trate o abort
  como falha isolada do item, não do app inteiro.
- **Tamanho de leitura:** limite quantos bytes você lê de um arquivo (ex.: 512 KiB), checando
  `size` quando presente e cortando a leitura em fluxo quando ausente (Docs exportado não
  informa `size` antecipadamente). Um app que lê qualquer conteúdo de qualquer tamanho que
  outra pessoa escreveu no Drive é vulnerável a um arquivo gigante travando a aba.
- **Isolamento de falha:** erro ao ler um item (404, 429, 500, rede, tempo esgotado) não deve
  impedir os outros itens de carregar; devolva um resultado parcial com o item marcado em erro.

- **Teste o teto de concorrência medindo o máximo simultâneo**, não só o total: um teste que
  conta as chamadas finais passa mesmo se o limite não existir. Use uma porta falsa com atraso
  e registre quantas chamadas estão em voo ao mesmo tempo.
- **Leitor só de leitura e reutilizável:** exponha uma fábrica de leitor que só faz `GET`, para
  mais de um consumidor (uma tela e uma sincronização) usarem o mesmo código; um 401 vira um
  código próprio (ex. sessão expirada), tratado pelo chamador, em vez de uma exceção genérica.

## Mapa de erros HTTP

- **401:** o token venceu ou é inválido. Pare todas as leituras em andamento (aborte-as),
  descarte resultados que ainda chegarem depois, e peça novo login — não tente renovar
  silenciosamente um token de popup/redirect sem um refresh real.
- **403, motivo `accessNotConfigured`:** a Drive API não está ativada no projeto (passo do
  console, não do código).
- **403, motivos `rateLimitExceeded`, `userRateLimitExceeded`, `dailyLimitExceeded`:** limite de
  taxa ou de cota; trate como transitório (equivalente a 429), não como "sem permissão".
- **403, demais motivos** (incluindo corpo de erro ilegível): trate como "a pessoa não concedeu
  o escopo do Drive" — o consentimento OAuth granular permite ao usuário desmarcar escopos
  individualmente, então o login pode suceder sem o Drive.
  Os nomes exatos de todos os motivos de 403 nem sempre aparecem na documentação pública da
  Drive API; confirme contra uma chamada real quando a diferença importar.
- **404, 429, 5xx:** erro do item específico; não interrompa os demais.

## Segurança do conteúdo lido

- Texto vindo do Drive é conteúdo de terceiros (qualquer pessoa com acesso de escrita à pasta
  pode gravar o que quiser). Nunca injete esse texto em `innerHTML`/`outerHTML`/
  `insertAdjacentHTML`; use sempre `textContent` ou equivalente seguro.
- Nunca imprima o conteúdo lido, o token ou o e-mail do usuário no console do navegador.
- Se esse conteúdo alimenta algum parser de texto (regex, etc.), veja a seção "Entrada não
  confiável" do skill `code-review`: a mesma entrada hostil que quebra um parser pode travar a
  leitura inteira.

## Cache

Nada é persistido em disco por este skill: o conteúdo lido vive só em memória, pelo tempo da
aba. Se o app precisar de cache entre sessões, isso é uma decisão separada e deliberada — não
um efeito colateral da leitura do Drive.
