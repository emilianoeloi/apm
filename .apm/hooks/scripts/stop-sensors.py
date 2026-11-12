#!/usr/bin/env python3
"""Stop hook — só deixa a sessão encerrar se os sensores do projeto passarem.

O comando de sensores vem do harness.config.json do projeto (campo
"sensors_command"). Sem comando — sem arquivo, sem campo, campo vazio ou de tipo
errado — o encerramento é sempre permitido: o hook nunca depende de Makefile,
de linguagem ou de ferramenta de um projeto específico.

Contrato:
  exit 0  -> encerramento permitido
  exit 2  -> encerramento bloqueado; stderr traz o código e o final da saída do sensor

Stdlib only — veja _common.py.
"""

import os
import signal
import subprocess
import sys

from _common import cfg_int, cfg_str, load_config, project_root, read_payload, run

DEFAULT_TIMEOUT_SECONDS = 50  # abaixo do timeout de 60 s do registro do hook
OUTPUT_TAIL_CHARS = 3000


def _tail(text: str) -> str:
    return text[-OUTPUT_TAIL_CHARS:]


def _kill_group(process: "subprocess.Popen") -> None:
    """Mata o sensor e tudo o que ele iniciou; sem grupo de processos (Windows), mata só o processo."""
    try:
        if hasattr(os, "killpg"):
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
    except (OSError, ProcessLookupError):
        pass


def main() -> None:
    payload = read_payload()

    # Segunda tentativa de encerrar depois de um bloqueio: libera, para nunca entrar em laço.
    if payload.get("stop_hook_active") is True:
        sys.exit(0)

    root = project_root()
    config = load_config(root)

    command = cfg_str(config, "sensors_command", "").strip()
    if not command:
        sys.exit(0)

    timeout = cfg_int(config, "sensors_timeout_seconds", DEFAULT_TIMEOUT_SECONDS, minimum=1, maximum=3600)

    try:
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=str(root),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
            start_new_session=True,  # o sensor e seus filhos formam um grupo, para matar tudo no estouro
        )
    except OSError as error:
        sys.stderr.write(f"Não foi possível iniciar os sensores ({error}); encerramento permitido.\n")
        sys.exit(0)

    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        _kill_group(process)
        stdout, stderr = process.communicate()
        sys.stderr.write(
            f"Sensores excederam o tempo limite de {timeout}s; corrija antes de encerrar.\n"
            f"Comando: {command}\n{_tail((stdout or '') + (stderr or ''))}"
        )
        sys.exit(2)

    if process.returncode == 0:
        sys.exit(0)

    sys.stderr.write(
        f"Sensores falharam (código {process.returncode}); corrija antes de encerrar.\n"
        f"Comando: {command}\n{_tail((stdout or '') + (stderr or ''))}"
    )
    sys.exit(2)


if __name__ == "__main__":
    run(main, "stop-sensors")
