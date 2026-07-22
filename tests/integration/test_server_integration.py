import threading
import time
import unittest

from chat_tcp.server.servidor import ServidorChat
from tests.integration.client_test_helper import ClienteTeste


class ServerIntegrationTests(unittest.TestCase):
    """Testa o funcionamento completo do servidor TCP."""

    def setUp(self) -> None:
        self.servidor = ServidorChat(
            host="127.0.0.1",
            porta=0,
        )

        self.thread_servidor = threading.Thread(
            target=self.servidor.iniciar,
            daemon=True,
        )

        self.thread_servidor.start()

        limite = time.monotonic() + 2

        while not self.servidor.ativo:
            if time.monotonic() >= limite:
                self.fail(
                    "O servidor não iniciou"
                )

            time.sleep(0.01)

        self.porta = self.servidor.porta
        self.clientes: list[ClienteTeste] = []

    def tearDown(self) -> None:
        for cliente in self.clientes:
            cliente.fechar()

        self.servidor.encerrar()

        self.thread_servidor.join(
            timeout=2
        )

    def criar_cliente(self) -> ClienteTeste:
        """Cria e conecta um cliente ao servidor."""

        cliente = ClienteTeste(
            host="127.0.0.1",
            porta=self.porta,
        )

        cliente.conectar()
        self.clientes.append(cliente)

        return cliente

    def realizar_login(
        self,
        cliente: ClienteTeste,
        apelido: str,
    ) -> str:
        """Envia LOGIN e retorna a resposta."""

        cliente.enviar(
            f"LOGIN;{apelido}"
        )

        return cliente.receber()

    def test_cliente_deve_realizar_login(self) -> None:
        cliente = self.criar_cliente()

        resposta = self.realizar_login(
            cliente,
            "henrique",
        )

        self.assertEqual(
            resposta,
            "OK;Login realizado",
        )

    def test_login_duplicado_deve_ser_rejeitado(
        self,
    ) -> None:
        cliente_1 = self.criar_cliente()
        cliente_2 = self.criar_cliente()

        resposta_1 = self.realizar_login(
            cliente_1,
            "henrique",
        )

        resposta_2 = self.realizar_login(
            cliente_2,
            "henrique",
        )

        self.assertEqual(
            resposta_1,
            "OK;Login realizado",
        )

        self.assertEqual(
            resposta_2,
            "ERROR;Apelido já está em uso",
        )

    def test_list_deve_retornar_clientes_conectados(
        self,
    ) -> None:
        cliente_1 = self.criar_cliente()
        cliente_2 = self.criar_cliente()

        self.realizar_login(
            cliente_1,
            "henrique",
        )

        self.realizar_login(
            cliente_2,
            "ana",
        )

        cliente_1.enviar("LIST")

        resposta = cliente_1.receber()

        self.assertEqual(
            resposta,
            "USERS;ana;henrique",
        )

    def test_message_deve_chegar_ao_destinatario(
        self,
    ) -> None:
        remetente = self.criar_cliente()
        destinatario = self.criar_cliente()

        self.realizar_login(
            remetente,
            "henrique",
        )

        self.realizar_login(
            destinatario,
            "ana",
        )

        remetente.enviar(
            "MESSAGE;ana;Olá, Ana"
        )

        mensagem_recebida = (
            destinatario.receber()
        )

        confirmacao = remetente.receber()

        self.assertEqual(
            mensagem_recebida,
            "MESSAGE;henrique;Olá, Ana",
        )

        self.assertEqual(
            confirmacao,
            "SENT;ana",
        )

    def test_logout_deve_remover_cliente(
        self,
    ) -> None:
        cliente_1 = self.criar_cliente()
        cliente_2 = self.criar_cliente()

        self.realizar_login(
            cliente_1,
            "henrique",
        )

        self.realizar_login(
            cliente_2,
            "ana",
        )

        cliente_2.enviar("LOGOUT")

        resposta_logout = cliente_2.receber()

        self.assertEqual(
            resposta_logout,
            "OK;Logout realizado",
        )

        time.sleep(0.1)

        cliente_1.enviar("LIST")

        resposta_lista = cliente_1.receber()

        self.assertEqual(
            resposta_lista,
            "USERS;henrique",
        )

    def test_desconexao_inesperada_deve_remover_cliente(
        self,
    ) -> None:
        cliente_1 = self.criar_cliente()
        cliente_2 = self.criar_cliente()

        self.realizar_login(
            cliente_1,
            "henrique",
        )

        self.realizar_login(
            cliente_2,
            "ana",
        )

        cliente_2.fechar()

        time.sleep(0.2)

        cliente_1.enviar("LIST")

        resposta = cliente_1.receber()

        self.assertEqual(
            resposta,
            "USERS;henrique",
        )

    def test_servidor_deve_processar_mensagem_fragmentada(
        self,
    ) -> None:
        cliente = self.criar_cliente()

        cliente.enviar_bytes(
            b"LOGIN;hen"
        )

        cliente.enviar_bytes(
            b"rique\n"
        )

        resposta = cliente.receber()

        self.assertEqual(
            resposta,
            "OK;Login realizado",
        )

    def test_servidor_deve_processar_multiplas_mensagens(
        self,
    ) -> None:
        cliente = self.criar_cliente()

        cliente.enviar_bytes(
            b"LOGIN;henrique\nLIST\n"
        )

        resposta_login = cliente.receber()
        resposta_lista = cliente.receber()

        self.assertEqual(
            resposta_login,
            "OK;Login realizado",
        )

        self.assertEqual(
            resposta_lista,
            "USERS;henrique",
        )


if __name__ == "__main__":
    unittest.main()