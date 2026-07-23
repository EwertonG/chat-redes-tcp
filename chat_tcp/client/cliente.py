import socket
import threading
from collections.abc import Callable

from chat_tcp.common.config import (
    HOST_CLIENTE,
    PORTA,
)
from chat_tcp.common.protocolo import (
    codificar_mensagem,
    criar_login,
    criar_logout,
    criar_mensagem,
    criar_solicitacao_lista,
)
from chat_tcp.client.receptor import ReceptorMensagens


class ClienteChat:

    def __init__(
        self,
        host: str = HOST_CLIENTE,
        porta: int = PORTA,
    ) -> None:
        self._host = host
        self._porta = porta

        self._conexao: socket.socket | None = None
        self._receptor: ReceptorMensagens | None = None
        self._conectado = False

        self._lock_envio = threading.Lock()

    def conectar(
        self,
        callback_mensagem: Callable[[str], None],
        callback_desconexao: Callable[[], None] | None = None,
    ) -> None:

        if self._conectado:
            raise RuntimeError(
                "O cliente já está conectado"
            )

        conexao = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )

        try:
            conexao.connect(
                (self._host, self._porta)
            )
        except OSError as erro:
            conexao.close()

            raise ConnectionError(
                "Não foi possível conectar ao servidor"
            ) from erro

        self._conexao = conexao
        self._conectado = True

        self._receptor = ReceptorMensagens(
            conexao=conexao,
            callback=callback_mensagem,
            callback_desconexao=callback_desconexao,
        )

        self._receptor.iniciar()

    def enviar_login(self, apelido: str) -> None:

        self.enviar(
            criar_login(apelido)
        )

    def solicitar_lista(self) -> None:

        self.enviar(
            criar_solicitacao_lista()
        )

    def enviar_mensagem(
        self,
        destinatario: str,
        texto: str,
    ) -> None:

        self.enviar(
            criar_mensagem(
                destinatario,
                texto,
            )
        )

    def enviar_logout(self) -> None:

        self.enviar(
            criar_logout()
        )

    def enviar(self, mensagem: str) -> None:

        if not self._conectado:
            raise ConnectionError(
                "O cliente não está conectado"
            )

        if self._conexao is None:
            raise ConnectionError(
                "Socket do cliente indisponível"
            )

        dados = codificar_mensagem(mensagem)

        try:
            with self._lock_envio:
                self._conexao.sendall(dados)

        except OSError as erro:
            self.encerrar()

            raise ConnectionError(
                "Não foi possível enviar a mensagem"
            ) from erro

    def esta_conectado(self) -> bool:

        return self._conectado

    def encerrar(self) -> None:

        self._conectado = False

        if self._receptor is not None:
            self._receptor.parar()
            self._receptor = None

        if self._conexao is not None:
            try:
                self._conexao.shutdown(
                    socket.SHUT_RDWR
                )
            except OSError:
                pass

            try:
                self._conexao.close()
            except OSError:
                pass

            self._conexao = None