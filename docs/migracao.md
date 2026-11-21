# Guia de migração

Este guia reúne o que muda, de forma incompatível, entre as versões do pacote. Para a lista completa de mudanças por versão, veja o [CHANGELOG](../CHANGELOG.md).

- [Da 1.x para a 2.0](#da-1x-para-a-20)
- [Do skill de aceitação 1.0 para o 1.1](#do-skill-de-aceitação-10-para-o-11)
- [Da 0.3.x para a 1.0](#da-03x-para-a-10)

## Da 1.x para a 2.0

A 2.0 torna o SDLC do pacote **verificável**: todo requisito da spec tem um cenário Gherkin conferido por sensor, e todo cenário novo tem um teste de aceitação escrito antes do código e conferido na revisão. É uma versão **incompatível** para quem já usa a 1.x, porque o fluxo passa a falhar onde antes passava:

| O que muda | Efeito num projeto da 1.x | O que fazer |
|---|---|---|
| Specs com bloco Gherkin ([Sensor de Gherkin](../README.md#sensor-de-gherkin)) | O sensor `gherkin-sensor.py` sai 2 em todo requisito sem bloco, e o hook `PostToolUse` o mostra depois de um `openspec validate` | Faça o retrofit das specs numa change própria, só com o bloco, e arquive-a antes da próxima feature. Opcional: componha o sensor ao `sensors_command` |
| `sdlc-coder` e o skill `acceptance-from-spec` ([Testes de aceitação](../README.md#testes-de-aceitação)) | O coder escreve primeiro o teste de cada `Cenário:`, com a linha `Spec:`, e prova o vermelho e o verde; sem ferramenta de teste, para com `BLOQUEADO` | Garanta uma ferramenta de teste aprovada no arquivo raiz do agente e um `sensors_command` que a execute |
| `sdlc-reviewer` e o `spec-trace.py` ([Conferência de cenários](../README.md#conferência-de-cenários-na-revisão)) | O reviewer reprova cenário novo ou alterado sem teste ligado, e o falso verde | Ligue cada teste ao cenário pela linha `Spec:`; cenários antigos não são exigidos |
| Convenções do skill 1.1 e fim do título do marcador | Extras levam `Extra:`; depois do título só vale um fechamento de comentário conhecido, e outro sufixo vira `ORFAO` | Deixe o marcador sozinho no fim da linha |
| Planner | As tasks de teste têm um teste por `Cenário:` do bloco | Nada a fazer |

**Passos**

1. Atualize a dependência para a `v2.0.0` no `apm.yml`.
2. Rode `apm install --target claude,copilot`. Revise os scripts de hook novos: são código executável.
3. Faça o retrofit das specs (um bloco `gherkin` por requisito).
4. Rode `openspec validate --specs --strict` e o sensor de Gherkin.
5. Só então declare a primeira fase `proposal`.

Sem o retrofit, o primeiro `openspec validate` já mostra os requisitos sem cenário. A prova do fluxo em projetos reais está no [roteiro de teste](roteiro-de-teste.md).

## Do skill de aceitação 1.0 para o 1.1

Atualize a dependência do apm e rode `apm install`. Não há mudança de configuração: as convenções (vermelho pela asserção, `Extra:` nos extras, linha `Spec:` de fixture montada por constante, cenário só de prova humana como `SEM_TESTE` conhecido) passam a valer nas próximas changes, e o coder passa a reportar falso verde e cenário só de prova humana.

**Fim do título do marcador.** Se um projeto usa um fechamento de comentário fora da lista conhecida, o cenário passa a sair `ORFAO` mais `SEM_TESTE`. O `ORFAO` mostra a linha exata, e o caminho durável é deixar o marcador sozinho no fim da linha (a forma canônica). Acrescentar o fechamento à constante `CLOSERS` exige editar o script implantado, e o `apm install` o sobrescreve.

## Da 0.3.x para a 1.0

A limpeza do projeto de origem (`cowboy`, uma calculadora em COBOL) removeu, de forma **incompatível**:

- os agentes `cobol-vibecoder`, `cobol-planner`, `cobol-coder`, `cobol-reviewer` e `readme-writer`;
- os prompts `criar-programa`, `implementar-soma`, `implementar-subtracao`, `implementar-log`, `testar-programa`, `atualizar-readme` e `manutencao-repositorio`;
- as skills `cobol-calculadora`, `vibe-coding-fundamentals` e `readme-manutencao`;
- o hook de encerramento `cowboy.json` (rodava `make fitness`) e o script de pre-commit que compilava COBOL.

O conteúdo não foi movido: quem ainda precisa dele deve manter a dependência na tag `v0.3.1`, que guarda o estado antigo. O hook de encerramento que o substitui é genérico (veja [Hooks](../README.md#hooks)), e os agentes de SDLC são os `sdlc-*` descritos em [Agentes de SDLC](../README.md#agentes-de-sdlc). Os agentes da 0.3.x não têm equivalente direto.
