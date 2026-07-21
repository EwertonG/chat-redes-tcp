import unittest

from chat_tcp.common import config


class ConfigTests(unittest.TestCase):
    """Testa os valores básicos da configuração."""

    def test_porta_deve_ser_inteira(self) -> None:
        self.assertIsInstance(config.PORTA, int)

    def test_porta_deve_ser_valida(self) -> None:
        self.assertGreater(config.PORTA, 0)
        self.assertLessEqual(config.PORTA, 65535)

    def test_codificacao_deve_ser_utf8(self) -> None:
        self.assertEqual(config.CODIFICACAO, "utf-8")

    def test_terminador_deve_ser_quebra_de_linha(self) -> None:
        self.assertEqual(config.TERMINADOR, "\n")


if __name__ == "__main__":
    unittest.main()