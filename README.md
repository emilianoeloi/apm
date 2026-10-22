# apm — harness package

Pacote APM privado com o harness extraído do `cowboy`.

Consumo (no projeto):

```yaml
dependencies:
  apm:
    - emilianoeloi/apm#v0.1.0
```

Layout: `.apm/skills/*`, `.apm/hooks/harness.json`, `.apm/scripts/*` (hooks, phase_cli, pre-commit), `.apm/templates/*` (harness.config.json, quadrante).

Pendente: confirmar como o APM entrega scripts de hook (ver perguntas na sessão).
