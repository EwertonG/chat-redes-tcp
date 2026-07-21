"""Testes do processamento de comandos do servidor."""

import socket
import unittest

from chat_tcp.common.config import CODIFICACAO
from chat_tcp.server.clientes import GerenciadorClientes
from chat_tcp.server.comandos import ProcessadorComandos


class ProcessadorComandosTests(unittest.TestCase):
    """Testa os comandos sem iniciar um servidor real."""

    def setUp(self) -> None:
        self.clientes = GerenciadorClientes()

        self.processador = ProcessadorComandos(
            self.clientes
        )

        (
            self.cliente_1,
            self.servidor_1,
        ) = socket.socketpair()

        (
            self.cliente_2,
            self.servidor_2,
        ) = socket.socketpair()

        self.cliente_1.settimeout(1)
        self.cliente_2.settimeout(1)

    def tearDown(self) -> None:
        sockets = [
            self.cliente_1,
            self.servidor_1,
            self.cliente_2,
            self.servidor_2,
        ]

        for conexao in sockets:
            try:
                conexao.close()
            except OSError:
                pass

    def receber(
        self,
        conexao: socket.socket,
    ) -> str:
        """Recebe uma resposta emitida pelo processador."""

        return (
            conexao.recv(1024)
            .decode(CODIFICACAO)
            .strip()
        )

    def test_login_deve_registrar_cliente(self) -> None:
        continuar = self.processador.processar(
            self.servidor_1,
            "LOGIN;henrique",
        )

        resposta = self.receber(self.cliente_1)

        self.assertTrue(continuar)
        self.assertEqual(
            resposta,
            "OK;Login realizado",
        )

        self.assertTrue(
            self.clientes.existe("henrique")
        )

    def test_login_repetido_deve_ser_rejeitado(
        self,
    ) -> None:
        self.processador.processar(
            self.servidor_1,
            "LOGIN;henrique",
        )

        self.receber(self.cliente_1)

        self.processador.processar(
            self.servidor_2,
            "LOGIN;henrique",
        )

        resposta = self.receber(self.cliente_2)

        self.assertEqual(
            resposta,
            "ERROR;Apelido já está em uso",
        )

    def test_list_deve_retornar_usuarios(self) -> None:
        self.processador.processar(
            self.servidor_1,
            "LOGIN;henrique",
        )
        self.receber(self.cliente_1)

        self.processador.processar(
            self.servidor_2,
            "LOGIN;ana",
        )
        self.receber(self.cliente_2)

        self.processador.processar(
            self.servidor_1,
            "LIST",
        )

        resposta = self.receber(self.cliente_1)

        self.assertEqual(
            resposta,
            "USERS;ana;henrique",
        )

    def test_message_deve_ser_encaminhada(self) -> None:
        self.processador.processar(
            self.servidor_1,
            "LOGIN;henrique",
        )
        self.receber(self.cliente_1)

        self.processador.processar(
            self.servidor_2,
            "LOGIN;ana",
        )
        self.receber(self.cliente_2)

        self.processador.processar(
            self.servidor_1,
            "MESSAGE;ana;Olá",
        )

        mensagem_recebida = self.receber(
            self.cliente_2
        )

        confirmacao = self.receber(
            self.cliente_1
        )

        self.assertEqual(
            mensagem_recebida,
            "MESSAGE;henrique;Olá",
        )

        self.assertEqual(
            confirmacao,
            "SENT;ana",
        )

    def test_message_para_usuario_inexistente(
        self,
    ) -> None:
        self.processador.processar(
            self.servidor_1,
            "LOGIN;henrique",
        )
        self.receber(self.cliente_1)

        self.processador.processar(
            self.servidor_1,
            "MESSAGE;inexistente;Olá",
        )

        resposta = self.receber(self.cliente_1)

        self.assertEqual(
            resposta,
            "ERROR;Destinatário não encontrado",
        )

    def test_comando_sem_login_deve_ser_rejeitado(
        self,
    ) -> None:
        self.processador.processar(
            self.servidor_1,
            "LIST",
        )

        resposta = self.receber(self.cliente_1)

        self.assertEqual(
            resposta,
            "ERROR;Execute LOGIN antes deste comando",
        )

    def test_logout_deve_remover_cliente(self) -> None:
        self.processador.processar(
            self.servidor_1,
            "LOGIN;henrique",
        )
        self.receber(self.cliente_1)

        continuar = self.processador.processar(
            self.servidor_1,
            "LOGOUT",
        )

        resposta = self.receber(self.cliente_1)

        self.assertFalse(continuar)

        self.assertEqual(
            resposta,
            "OK;Logout realizado",
        )

        self.assertFalse(
            self.clientes.existe("henrique")
        )


if __name__ == "__main__":
    unittest.main()