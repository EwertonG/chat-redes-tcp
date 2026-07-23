import socket
import threading
from collections.abc import Callable

from chat_tcp.common.config import (
    CODIFICACAO,
    TAMANHO_BUFFER,
    TERMINADOR,
)


class ReceptorMensagens:

    def __init__(
        self,
        conexao: socket.socket,
        callback: Callable[[str], None],
        callback_desconexao: Callable[[], None] | None = None,
    ) -> None:
        self._conexao = conexao
        self._callback = callback
        self._callback_desconexao = callback_desconexao

        self._ativo = False
        self._thread: threading.Thread | None = None

    def iniciar(self) -> None:
        """Inicia a thread responsável pelo recebimento."""

        if self._ativo:
            return

        self._ativo = True

        self._thread = threading.Thread(
            target=self._receber,
            daemon=True,
        )

        self._thread.start()

    def parar(self) -> None:
        """Interrompe o laço de recebimento."""

        self._ativo = False

    def esta_ativo(self) -> bool:
        """Informa se o receptor está ativo."""

        return self._ativo

    def _receber(self) -> None:

        buffer = ""

        try:
            while self._ativo:
                dados = self._conexao.recv(
                    TAMANHO_BUFFER
                )

                if not dados:
                    break

                buffer += dados.decode(CODIFICACAO)

                while TERMINADOR in buffer:
                    mensagem, buffer = buffer.split(
                        TERMINADOR,
                        1,
                    )

                    if mensagem:
                        self._callback(mensagem)

        except (ConnectionResetError, OSError):
            pass

        except UnicodeDecodeError:
            self._callback(
                "ERROR;Dados inválidos recebidos do servidor"
            )

        finally:
            self._ativo = False

            if self._callback_desconexao is not None:
                self._callback_desconexao()