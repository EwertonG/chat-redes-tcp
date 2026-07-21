import unittest

from chat_tcp.common.protocolo import (
    LOGIN,
    MESSAGE,
    criar_login,
    criar_logout,
    criar_mensagem,
    criar_solicitacao_lista,
    codificar_mensagem,
    interpretar_mensagem,
    montar_mensagem,
    criar_confirmacao_envio,
    criar_lista_usuarios,
    criar_mensagem_recebida,
    criar_resposta_erro,
    criar_resposta_ok,
)


class ProtocoloTests(unittest.TestCase):
    """Testa a criação e interpretação das mensagens."""

    def test_criar_login(self) -> None:
        resultado = criar_login("henrique")

        self.assertEqual(
            resultado,
            "LOGIN;henrique"
        )

    def test_criar_solicitacao_lista(self) -> None:
        resultado = criar_solicitacao_lista()

        self.assertEqual(
            resultado,
            "LIST"
        )

    def test_criar_mensagem(self) -> None:
        resultado = criar_mensagem(
            "joao",
            "Olá"
        )

        self.assertEqual(
            resultado,
            "MESSAGE;joao;Olá"
        )

    def test_criar_logout(self) -> None:
        resultado = criar_logout()

        self.assertEqual(
            resultado,
            "LOGOUT"
        )

    def test_codificar_mensagem(self) -> None:
        resultado = codificar_mensagem(
            "LOGIN;henrique"
        )

        self.assertEqual(
            resultado,
            b"LOGIN;henrique\n"
        )

    def test_interpretar_login(self) -> None:
        tipo, campos = interpretar_mensagem(
            "LOGIN;henrique\n"
        )

        self.assertEqual(tipo, LOGIN)
        self.assertEqual(campos, ["henrique"])

    def test_interpretar_mensagem(self) -> None:
        tipo, campos = interpretar_mensagem(
            "MESSAGE;joao;Olá"
        )

        self.assertEqual(tipo, MESSAGE)
        self.assertEqual(
            campos,
            ["joao", "Olá"]
        )

    def test_texto_pode_conter_ponto_e_virgula(self) -> None:
        tipo, campos = interpretar_mensagem(
            "MESSAGE;joao;Olá; tudo bem?"
        )

        self.assertEqual(tipo, MESSAGE)
        self.assertEqual(
            campos,
            ["joao", "Olá; tudo bem?"]
        )

    def test_apelido_vazio_deve_gerar_erro(self) -> None:
        with self.assertRaises(ValueError):
            criar_login("")

    def test_apelido_com_separador_deve_gerar_erro(self) -> None:
        with self.assertRaises(ValueError):
            criar_login("henrique;silva")

    def test_mensagem_vazia_deve_gerar_erro(self) -> None:
        with self.assertRaises(ValueError):
            criar_mensagem("joao", "")

    def test_tipo_desconhecido_deve_gerar_erro(self) -> None:
        with self.assertRaises(ValueError):
            montar_mensagem("COMANDO_INEXISTENTE")
    
    def test_criar_resposta_ok(self) -> None:
        resultado = criar_resposta_ok(
        "Login realizado"
        )

        self.assertEqual(
            resultado,
            "OK;Login realizado",
        )

    def test_criar_resposta_erro(self) -> None:
        resultado = criar_resposta_erro(
            "Apelido já está em uso"
        )

        self.assertEqual(
            resultado,
            "ERROR;Apelido já está em uso",
        )

    def test_criar_lista_usuarios(self) -> None:
        resultado = criar_lista_usuarios(
            ["ana", "henrique"]
        )

        self.assertEqual(
            resultado,
            "USERS;ana;henrique",
        )

    def test_criar_mensagem_recebida(self) -> None:
        resultado = criar_mensagem_recebida(
            "henrique",
            "Olá",
        )

        self.assertEqual(
            resultado,
            "MESSAGE;henrique;Olá",
        )

    def test_criar_confirmacao_envio(self) -> None:
        resultado = criar_confirmacao_envio("ana")

        self.assertEqual(
            resultado,
            "SENT;ana",
        )


if __name__ == "__main__":
    unittest.main()