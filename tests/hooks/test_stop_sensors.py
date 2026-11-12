"""Cenários da spec sensor-gate: o Stop só bloqueia quando o sensor do projeto falha."""

import os
import signal
import time
from pathlib import Path

from tests.hooks._util import ProjectCase

STOP = "stop-sensors.py"


class StopSensorsTest(ProjectCase):
    def stop(self, payload=None, timeout: int = 30):
        return self.run_hook(STOP, payload if payload is not None else {"hook_event_name": "Stop"}, timeout=timeout)

    # --- Encerramento sem sensores configurados é permitido

    def test_sem_configuracao_nem_makefile_permite(self):
        result = self.stop()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")

    def test_comando_vazio_permite(self):
        self.write_config({"sensors_command": ""})
        self.assertEqual(self.stop().returncode, 0)

    def test_comando_que_nao_e_texto_permite(self):
        self.write_config({"sensors_command": 5})
        result = self.stop()
        self.assertEqual(result.returncode, 0)
        self.assertNoTraceback(result)

    def test_makefile_com_alvo_que_falha_e_ignorado(self):
        (self.root / "Makefile").write_text("fitness:\n\tfalse\n", encoding="utf-8")
        self.assertEqual(self.stop().returncode, 0)

    def test_configuracao_corrompida_permite(self):
        self.write_config("{ isto não é json")
        result = self.stop()
        self.assertEqual(result.returncode, 0)
        self.assertNoTraceback(result)

    def test_configuracao_que_nao_e_objeto_permite(self):
        self.write_config("[1, 2, 3]")
        self.assertEqual(self.stop().returncode, 0)

    def test_payload_invalido_nao_trava(self):
        result = self.stop("isto não é json")
        self.assertEqual(result.returncode, 0)
        self.assertNoTraceback(result)

    # --- Sensores configurados rodam na raiz do projeto

    def test_sensor_que_passa_permite(self):
        self.write_config({"sensors_command": "exit 0"})
        self.assertEqual(self.stop().returncode, 0)

    def test_sensor_roda_na_raiz_do_projeto(self):
        self.write_config({"sensors_command": "pwd > cwd.txt"})
        result = self.stop()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(Path((self.root / "cwd.txt").read_text().strip()).resolve(), self.root)

    # --- Sensores com falha bloqueiam o encerramento

    def test_sensor_que_falha_bloqueia_e_mostra_a_saida(self):
        self.write_config({"sensors_command": "echo sensor-quebrou; exit 3"})
        result = self.stop()
        self.assertEqual(result.returncode, 2)
        self.assertIn("sensor-quebrou", result.stderr)
        self.assertIn("3", result.stderr)

    def test_saida_do_sensor_em_stderr_tambem_aparece(self):
        self.write_config({"sensors_command": "echo erro-no-stderr 1>&2; exit 1"})
        result = self.stop()
        self.assertEqual(result.returncode, 2)
        self.assertIn("erro-no-stderr", result.stderr)

    def test_saida_enorme_e_cortada_no_final(self):
        self.write_config({"sensors_command": "python3 -c \"print('x' * 20000); print('FIM-DA-SAIDA')\"; exit 1"})
        result = self.stop()
        self.assertEqual(result.returncode, 2)
        self.assertIn("FIM-DA-SAIDA", result.stderr)
        self.assertLess(len(result.stderr), 4000)

    def test_sensor_que_estoura_o_tempo_bloqueia(self):
        self.write_config({"sensors_command": "sleep 5", "sensors_timeout_seconds": 1})
        result = self.stop(timeout=20)
        self.assertEqual(result.returncode, 2)
        self.assertIn("tempo", result.stderr.lower())

    def test_estouro_do_tempo_nao_deixa_processo_orfao(self):
        self.write_config({"sensors_command": "sleep 30 & echo $! > filho.pid; wait", "sensors_timeout_seconds": 1})
        result = self.stop(timeout=20)
        self.assertEqual(result.returncode, 2)
        filho = int((self.root / "filho.pid").read_text().strip())
        for _ in range(20):
            try:
                os.kill(filho, 0)
            except ProcessLookupError:
                return
            time.sleep(0.1)
        os.kill(filho, signal.SIGKILL)
        self.fail("o processo filho do sensor continuou vivo depois do estouro de tempo")

    def test_timeout_invalido_usa_o_padrao(self):
        self.write_config({"sensors_command": "exit 0", "sensors_timeout_seconds": "muito"})
        self.assertEqual(self.stop().returncode, 0)

    # --- Encerramento já forçado não entra em laço

    def test_stop_hook_active_libera_sem_rodar_o_comando(self):
        self.write_config({"sensors_command": "touch rodou.txt; exit 1"})
        result = self.stop({"hook_event_name": "Stop", "stop_hook_active": True})
        self.assertEqual(result.returncode, 0)
        self.assertFalse((self.root / "rodou.txt").exists())


if __name__ == "__main__":
    import unittest

    unittest.main()
