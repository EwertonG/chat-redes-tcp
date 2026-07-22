import unittest
from unittest.mock import MagicMock

from chat_tcp.client.cliente import ClienteChat


class ClienteChatTests(unittest.TestCase):
    """Testa o envio das mensagens do cliente."""

    def setUp(self) -> None:
        self.cliente = ClienteChat()

        self.socket_mock = MagicMock()

        self.cliente._conexao = self.socket_mock
        self.cliente._conectado = True

    def test_enviar_login(self) -> None:
        self.cliente.enviar_login("henrique")

        self.socket_mock.sendall.assert_called_once_with(
            b"LOGIN;henrique\n"
        )

    def test_solicitar_lista(self) -> None:
        self.cliente.solicitar_lista()

        self.socket_mock.sendall.assert_called_once_with(
            b"LIST\n"
        )

    def test_enviar_mensagem(self) -> None:
        self.cliente.enviar_mensagem(
            "ana",
            "Olá",
        )

        self.socket_mock.sendall.assert_called_once_with(
            "MESSAGE;ana;Olá\n".encode("utf-8")
        )

    def test_enviar_logout(self) -> None:
        self.cliente.enviar_logout()

        self.socket_mock.sendall.assert_called_once_with(
            b"LOGOUT\n"
        )

    def test_enviar_sem_conexao_deve_gerar_erro(
        self,
    ) -> None:
        self.cliente._conectado = False

        with self.assertRaises(ConnectionError):
            self.cliente.solicitar_lista()


if __name__ == "__main__":
    unittest.main()