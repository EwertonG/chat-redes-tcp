"""Interface de terminal do cliente."""

import threading

from chat_tcp.client.cliente import ClienteChat
from chat_tcp.common.protocolo import (
    ERROR,
    MESSAGE,
    OK,
    SENT,
    USERS,
    interpretar_mensagem,
)

class InterfaceTerminal:

    def __init__(self) -> None:
        self._cliente = ClienteChat()
        self._executando = True
        self._evento_login = threading.Event()
        self._login_aceito = False

    def executar(self) -> None:
        """Inicia o fluxo principal da interface."""

        self._mostrar_cabecalho()

        try:
            self._cliente.conectar(
                callback_mensagem=self._processar_resposta,
                callback_desconexao=self._servidor_desconectado,
            )

        except ConnectionError as erro:
            print(f"Erro: {erro}")
            return

        try:
            apelido = input("Informe seu nickname: ").strip()

            if not apelido:
                print("O nickname não pode ficar vazio.")
                return

            self._cliente.enviar_login(apelido)

            self._evento_login.wait(timeout=5)

            if not self._login_aceito:
                print(
                    "Não foi possível realizar o login."
                )
                return

            self._mostrar_ajuda()

            while (
                self._executando
                and self._cliente.esta_conectado()
            ):
                try:
                    entrada = input("> ").strip()
                except EOFError:
                    break

                if not entrada:
                    continue

                self._processar_entrada(entrada)

        except KeyboardInterrupt:
            print("\nEncerrando cliente...")

        except ConnectionError as erro:
            print(f"\nErro: {erro}")

        finally:
            self._encerrar_cliente()

    def _processar_entrada(
        self,
        entrada: str,
    ) -> None:

        if entrada == "/list":
            self._cliente.solicitar_lista()
            return

        if entrada == "/logout":
            self._cliente.enviar_logout()
            self._executando = False
            return

        if entrada == "/help":
            self._mostrar_ajuda()
            return

        if entrada.startswith("/message "):
            partes = entrada.split(" ", 2)

            if len(partes) != 3:
                print(
                    "Uso: /message nickname mensagem"
                )
                return

            destinatario = partes[1]
            texto = partes[2]

            try:
                self._cliente.enviar_mensagem(
                    destinatario,
                    texto,
                )
            except ValueError as erro:
                print(f"Erro: {erro}")

            return

        print(
            "Comando inválido. Digite /help."
        )

    def _processar_resposta(
        self,
        mensagem: str,
    ) -> None:

        try:
            tipo, campos = interpretar_mensagem(
                mensagem
            )
        except ValueError:
            print(f"\nServidor: {mensagem}")
            return

        if tipo == OK:
            texto = campos[0] if campos else "Operação realizada"

            print(f"\n[OK] {texto}")

            if texto == "Login realizado":
                self._login_aceito = True
                self._evento_login.set()

            return

        if tipo == ERROR:
            texto = campos[0] if campos else "Erro desconhecido"

            print(f"\n[ERROR] {texto}")

            if not self._evento_login.is_set():
                self._evento_login.set()

            return

        if tipo == USERS:
            if campos:
                print(
                    "\nUsuários conectados: "
                    + ", ".join(campos)
                )
            else:
                print(
                    "\nNenhum usuário conectado."
                )

            return

        if tipo == MESSAGE:
            if len(campos) == 2:
                remetente = campos[0]
                texto = campos[1]

                print(
                    f"\n[{remetente}] {texto}"
                )
            return

        if tipo == SENT:
            destinatario = (
                campos[0]
                if campos
                else "destinatário"
            )

            print(
                f"\nMensagem enviada para {destinatario}."
            )
            return

        print(f"\nServidor: {mensagem}")

    def _servidor_desconectado(self) -> None:
        """Executado quando o servidor encerra a conexão."""

        if self._executando:
            print(
                "\nA conexão com o servidor foi encerrada."
            )

        self._executando = False
        self._evento_login.set()

    def _encerrar_cliente(self) -> None:

        self._cliente.encerrar()

    @staticmethod
    def _mostrar_cabecalho() -> None:
        """Exibe o nome da aplicação."""

        print("=" * 40)
        print("ChatRedes TCP")
        print("=" * 40)

    @staticmethod
    def _mostrar_ajuda() -> None:
        """Exibe os comandos disponíveis."""

        print()
        print("Comandos disponíveis:")
        print("/list")
        print("/message nickname mensagem")
        print("/logout")
        print("/help")
        print()