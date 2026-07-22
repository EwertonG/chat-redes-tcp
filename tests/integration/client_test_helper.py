import socket
import time

from chat_tcp.common.config import (
    CODIFICACAO,
    TAMANHO_BUFFER,
    TERMINADOR,
)
from chat_tcp.common.protocolo import codificar_mensagem


class ClienteTeste:

    def __init__(
        self,
        host: str,
        porta: int,
    ) -> None:
        self._host = host
        self._porta = porta

        self._socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )

        self._socket.settimeout(2)

        self._buffer = ""

    def conectar(self) -> None:
        """Conecta ao servidor."""

        self._socket.connect(
            (self._host, self._porta)
        )

    def enviar(self, mensagem: str) -> None:
        """Envia uma mensagem do protocolo."""

        self._socket.sendall(
            codificar_mensagem(mensagem)
        )

    def enviar_bytes(self, dados: bytes) -> None:
        """Envia bytes diretamente ao servidor."""

        self._socket.sendall(dados)

    def receber(self) -> str:
        """
        Aguarda e retorna uma mensagem completa.

        Mantém dados excedentes no buffer.
        """

        limite = time.monotonic() + 2

        while TERMINADOR not in self._buffer:
            if time.monotonic() >= limite:
                raise TimeoutError(
                    "Tempo excedido aguardando resposta"
                )

            dados = self._socket.recv(
                TAMANHO_BUFFER
            )

            if not dados:
                raise ConnectionError(
                    "Conexão encerrada pelo servidor"
                )

            self._buffer += dados.decode(
                CODIFICACAO
            )

        mensagem, self._buffer = (
            self._buffer.split(
                TERMINADOR,
                1,
            )
        )

        return mensagem

    def fechar(self) -> None:
        """Encerra o socket utilizado no teste."""

        try:
            self._socket.shutdown(
                socket.SHUT_RDWR
            )
        except OSError:
            pass

        try:
            self._socket.close()
        except OSError:
            pass