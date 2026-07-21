import socket
import unittest

from chat_tcp.server.clientes import GerenciadorClientes


class GerenciadorClientesTests(unittest.TestCase):
    """Teste de registro e consulta de clientes."""

    def setUp(self) -> None:
        self.gerenciador = GerenciadorClientes()

        self.socket_cliente_1 = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )

        self.socket_cliente_2 = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )

    def tearDown(self) -> None:
        self.socket_cliente_1.close()
        self.socket_cliente_2.close()

    def test_registrar_cliente(self) -> None:
        resultado = self.gerenciador.registrar(
            "henrique",
            self.socket_cliente_1,
        )

        self.assertTrue(resultado)
        self.assertTrue(
            self.gerenciador.existe("henrique")
        )

    def test_nao_permitir_apelido_repetido(self) -> None:
        self.gerenciador.registrar(
            "henrique",
            self.socket_cliente_1,
        )

        resultado = self.gerenciador.registrar(
            "henrique",
            self.socket_cliente_2,
        )

        self.assertFalse(resultado)
        self.assertEqual(
            self.gerenciador.quantidade(),
            1,
        )

    def test_apelido_vazio_deve_gerar_erro(self) -> None:
        with self.assertRaises(ValueError):
            self.gerenciador.registrar(
                "",
                self.socket_cliente_1,
            )

    def test_remover_cliente(self) -> None:
        self.gerenciador.registrar(
            "henrique",
            self.socket_cliente_1,
        )

        conexao_removida = self.gerenciador.remover(
            "henrique"
        )

        self.assertIs(
            conexao_removida,
            self.socket_cliente_1,
        )

        self.assertFalse(
            self.gerenciador.existe("henrique")
        )

    def test_remover_cliente_inexistente(self) -> None:
        resultado = self.gerenciador.remover(
            "inexistente"
        )

        self.assertIsNone(resultado)

    def test_remover_cliente_por_conexao(self) -> None:
        self.gerenciador.registrar(
            "henrique",
            self.socket_cliente_1,
        )

        apelido_removido = (
            self.gerenciador.remover_por_conexao(
                self.socket_cliente_1
            )
        )

        self.assertEqual(
            apelido_removido,
            "henrique",
        )

        self.assertEqual(
            self.gerenciador.quantidade(),
            0,
        )

    def test_buscar_conexao_por_apelido(self) -> None:
        self.gerenciador.registrar(
            "henrique",
            self.socket_cliente_1,
        )

        conexao = self.gerenciador.buscar_conexao(
            "henrique"
        )

        self.assertIs(
            conexao,
            self.socket_cliente_1,
        )

    def test_buscar_apelido_por_conexao(self) -> None:
        self.gerenciador.registrar(
            "henrique",
            self.socket_cliente_1,
        )

        apelido = self.gerenciador.buscar_apelido(
            self.socket_cliente_1
        )

        self.assertEqual(
            apelido,
            "henrique",
        )

    def test_listar_clientes_em_ordem_alfabetica(self) -> None:
        self.gerenciador.registrar(
            "maria",
            self.socket_cliente_1,
        )

        self.gerenciador.registrar(
            "ana",
            self.socket_cliente_2,
        )

        resultado = self.gerenciador.listar()

        self.assertEqual(
            resultado,
            ["ana", "maria"],
        )

    def test_quantidade_de_clientes(self) -> None:
        self.gerenciador.registrar(
            "henrique",
            self.socket_cliente_1,
        )

        self.gerenciador.registrar(
            "joao",
            self.socket_cliente_2,
        )

        self.assertEqual(
            self.gerenciador.quantidade(),
            2,
        )


if __name__ == "__main__":
    unittest.main()