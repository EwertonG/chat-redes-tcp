import socket
import threading
import unittest

from chat_tcp.client.receptor import ReceptorMensagens


class ReceptorMensagensTests(unittest.TestCase):
    """Testa o recebimento assíncrono de mensagens."""

    def setUp(self) -> None:
        (
            self.socket_cliente,
            self.socket_servidor,
        ) = socket.socketpair()

    def tearDown(self) -> None:
        for conexao in (
            self.socket_cliente,
            self.socket_servidor,
        ):
            try:
                conexao.close()
            except OSError:
                pass

    def test_receber_mensagem_completa(self) -> None:
        mensagens: list[str] = []
        evento = threading.Event()

        def callback(mensagem: str) -> None:
            mensagens.append(mensagem)
            evento.set()

        receptor = ReceptorMensagens(
            self.socket_cliente,
            callback,
        )

        receptor.iniciar()

        self.socket_servidor.sendall(
            b"OK;Login realizado\n"
        )

        recebido = evento.wait(timeout=1)

        receptor.parar()

        self.assertTrue(recebido)
        self.assertEqual(
            mensagens,
            ["OK;Login realizado"],
        )

    def test_receber_duas_mensagens(self) -> None:
        mensagens: list[str] = []
        evento = threading.Event()

        def callback(mensagem: str) -> None:
            mensagens.append(mensagem)

            if len(mensagens) == 2:
                evento.set()

        receptor = ReceptorMensagens(
            self.socket_cliente,
            callback,
        )

        receptor.iniciar()

        self.socket_servidor.sendall(
            b"OK;Login realizado\nUSERS;ana;joao\n"
        )

        recebido = evento.wait(timeout=1)

        receptor.parar()

        self.assertTrue(recebido)

        self.assertEqual(
            mensagens,
            [
                "OK;Login realizado",
                "USERS;ana;joao",
            ],
        )

    def test_receber_mensagem_fragmentada(self) -> None:
        mensagens: list[str] = []
        evento = threading.Event()

        def callback(mensagem: str) -> None:
            mensagens.append(mensagem)
            evento.set()

        receptor = ReceptorMensagens(
            self.socket_cliente,
            callback,
        )

        receptor.iniciar()

        self.socket_servidor.sendall(
            b"MESSAGE;ana;Ola"
        )

        self.socket_servidor.sendall(
            b" mundo\n"
        )

        recebido = evento.wait(timeout=1)

        receptor.parar()

        self.assertTrue(recebido)
        self.assertEqual(
            mensagens,
            ["MESSAGE;ana;Ola mundo"],
        )


if __name__ == "__main__":
    unittest.main()