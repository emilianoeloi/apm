# SPDD Analysis: Hooks genéricos do pacote APM

## Original Business Requirement

Fonte: `APM_SETUP_V1.2.md` (Google Drive), funcionalidade F2 da Onda 1, mais a change `openspec/changes/hooks-genericos/`. Trechos da spec, sem alteração:

> F2. Hooks genéricos. Esforço M, valor $$$, confiança amarela.
>
> H2. Como Elói, quero hooks que leem a configuração do projeto, para não travar em stack nenhuma.
> Dado um projeto sem Makefile, quando a sessão encerra, então o hook de Stop permite o encerramento.
> Dado um harness.config.json com comando de sensores, quando a sessão encerra, então o hook roda esse comando.
> Dado um comando de sensores que falha, quando a sessão encerra, então o hook bloqueia e mostra a saída.
> Dado um harness.config.json ausente ou corrompido, quando qualquer hook roda, então ele permite e não trava.
>
> Arquitetura sugerida: Hooks em Python, só com a biblioteca padrão, lendo o harness.config.json do projeto. Novo campo no harness.config.json para o comando de sensores, vazio por padrão.
>
> Métricas: o hook de encerramento não bloqueia projeto sem Makefile.
>
> Riscos: 1. Entrega de hooks pelo APM: o README ainda marca como pendente a entrega dos scripts.
>
> Roteiro de teste manual: 3. Rodar o hook de Stop numa pasta sem Makefile. Esperado: saída 0. 4. Rodar o hook de Stop com sensores falhando. Esperado: saída 2 e a mensagem do sensor.
>
> Cuidados: Hooks são código executável: revisar antes do apm approve. Os hooks sempre bloqueiam git push, reset --hard, clean -f, branch -D e rm -rf. Eles bloqueiam também escrita em arquivos de credencial.
>
> Onda 0: O hook genérico que substitui o cowboy.json chega na Onda 1, com a F2.
>
> Documentação: README do apm: remover [...] a nota pendente sobre hooks, se resolvida.

## Domain Concept Identification

### Existing Concepts (from codebase)
- **Hook de segurança**: scripts Python (`session-start`, guarda de escrita, guarda de Bash) que leem o payload do host e a configuração do projeto e decidem permitir ou bloquear. Hoje em `.apm/scripts/hooks/`, com a lógica de raiz do projeto e de leitura da configuração repetida em cada um.
- **Configuração do projeto (`harness.config.json`)**: único contrato entre hooks e `phase_cli.py`; define fase, prefixos, padrões bloqueados e guias. Tem dois modelos: `.apm/templates/` e o do skill.
- **Gate de fase**: estado `proposal`/`apply` lido de `.harness/change-phase.json`.
- **Entrega do pacote pelo APM**: `apm install` integra skills, prompts e agentes; para hooks, `.apm/hooks/*.json` e o bundle de scripts (confirmado em teste descartável).
- **Registro manual atual**: `.apm/_pending/hooks/harness.json`, `scripts/hooks/` e `.claude/settings.json` do próprio repositório, da Onda 0.
- **Skill `install-dev-harness`**: copia scripts e mescla o registro no projeto consumidor.

### New Concepts Required
- **Sensor de encerramento**: comando do projeto, declarado em `sensors_command`, que decide se a sessão pode terminar.
- **Decisão por host**: o mesmo veredito (bloquear/permitir) emitido no formato que o Claude Code ou o Copilot entende.
- **Helper comum dos hooks**: um módulo vizinho aos scripts com o que hoje se repete.
- **Bateria de testes do pacote**: primeira, em `tests/hooks/`, rodada pelo próprio sensor do repositório.

### Key Business Rules
- **Nunca travar o agente por causa de configuração**: ausência, corrupção ou tipo errado da configuração, e payload inválido, resultam em permitir.
- **Defesas embutidas continuam**: `git push`, `reset --hard`, `clean -f`, `branch -D`, `rm -rf` e credenciais bloqueiam mesmo sem configuração.
- **Stack-agnóstico**: nenhum hook cita linguagem, pasta ou comando de um projeto; o que é do projeto vem da configuração.
- **Só biblioteca padrão**: sem dependência a instalar.
- **Hooks são executáveis**: o consumidor revisa e aprova com `apm approve`.
- **Sem push e sem publicação sem o "ok" do Elói.**

## Strategic Approach

### Solution Direction
Mover os hooks para o diretório que o APM entrega como bundle, extrair o que se repete para um helper vizinho, endurecer cada guarda contra entrada inválida, fazer a decisão sair no formato de cada host, acrescentar o hook de Stop que roda o `sensors_command`, e provar tudo com testes de subprocesso. Fluxo: `.apm/hooks/` → `apm install` → `.claude/settings.json` e `.github/hooks/` → host chama o script → script lê a configuração do projeto → decisão no formato do host.

### Key Design Decisions
- **Scripts em `.apm/hooks/scripts/` com formato achatado**: é o caminho que o APM entrega e renderiza para os dois hosts → adotar; mantém o skill sem cópia manual.
- **Helper comum**: menos repetição e um único lugar de fail-open, ao custo de depender do helper chegar ao projeto → adotar, com teste no consumidor.
- **Fail-open só para o que depende de configuração**: preserva as defesas embutidas → adotar; é a leitura mais segura do "permite e não trava" da spec.
- **Decisão por host (código 2 no Claude, JSON no Copilot)**: o Claude Code ignora o JSON atual → adotar, e provar no Claude real.
- **Dogfood do `sensors_command`**: o repositório passa a rodar os próprios testes no Stop → adotar.

### Alternatives Considered
- **Scripts autocontidos sem helper**: repete as correções quatro vezes → rejeitado.
- **Emitir os dois formatos na mesma saída**: código 2 do Claude ignora o JSON e o Copilot pode ler código diferente de 0 como falha do hook → rejeitado.
- **Fail-open total quando a configuração falha**: desligaria `git push` e credenciais por um arquivo corrompido → rejeitado.
- **Manter a cópia manual de scripts pelo skill**: mantém o risco 1 e a deriva entre cópias → rejeitado.

## Risk & Gap Analysis

### Requirement Ambiguities
- **"Permite e não trava" com configuração corrompida**: pode significar liberar tudo ou só não derrubar o hook. Decisão desta change: só os checks que dependem de configuração são desligados; as defesas embutidas ficam. Precisa do aceite do Elói.
- **Timeout do sensor**: a spec não fala; adotado 50 s, abaixo do `timeout` de 60 s do registro, configurável.
- **Estouro de tempo bloqueia ou libera**: a spec diz que falha bloqueia; estouro tratado como falha, e `stop_hook_active` evita laço.
- **Formato do hook de Stop no Copilot (`agentStop`)**: a decisão de bloqueio dele não está documentada na spec nem verificável aqui.

### Edge Cases
- **`sensors_command` com saída enorme**: só o final (3000 caracteres) vai para stderr.
- **`sensors_command` que lê a entrada padrão**: o hook não repassa o payload; o comando roda sem entrada.
- **Raiz do projeto com link simbólico ou nome que prefixa outro**: coberto pela contenção exata.
- **Instalação em projeto que já tem `.claude/settings.json` com outros hooks**: o APM mescla; a task de entrega confere que nada é duplicado.
- **Projetos da 0.3.x com scripts copiados**: ficam órfãos se trocarem de tag sem limpar; o README avisa.

### Technical Risks
- **O Claude Code não disparar ou não honrar o hook**: provável causa de o `git push` não ter sido bloqueado nesta sessão; verificação real planejada, com resultado declarado se não for possível.
- **Helper não implantado**: derrubaria os hooks; teste no consumidor.
- **Copilot não verificável**: declarado.
- **`shell=True`**: executa texto do arquivo de configuração; aceito pela confiança no repositório e pelo `apm approve`.

### Acceptance Criteria Coverage
| AC# | Description | Addressable? | Gaps/Notes |
|-----|-------------|--------------|------------|
| 1 | Projeto sem Makefile: Stop permite | Yes | Teste no `test_stop_sensors` |
| 2 | Com `harness.config.json` e comando, o Stop roda o comando | Yes | Raiz como diretório de trabalho |
| 3 | Comando que falha: bloqueia e mostra a saída | Yes | Código 2 e stderr |
| 4 | Configuração ausente ou corrompida: qualquer hook permite e não trava | Partial | Interpretação "defesas embutidas ficam" precisa de aceite |
| 5 | Hooks só com biblioteca padrão, lendo a configuração do projeto | Yes | Helper do próprio diretório é permitido |
| 6 | Risco 1 (entrega pelo APM) resolvido | Yes | Teste descartável e tasks 4.1 e 4.2 |
| 7 | README sem a nota pendente | Yes | Task 5.3; Copilot declarado não verificado |
