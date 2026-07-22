"""Implementação principal do servidor TCP."""

import socket
import threading

from chat_tcp.common.config import (
    CODIFICACAO,
    HOST_SERVIDOR,
    PORTA,
    TAMANHO_BUFFER,
    TERMINADOR,
)
from chat_tcp.server.clientes import GerenciadorClientes
from chat_tcp.server.comandos import ProcessadorComandos


class ServidorChat:

    def __init__(
        self,
        host: str = HOST_SERVIDOR,
        porta: int = PORTA,
    ) -> None:
        self._host = host
        self._porta = porta

        self._clientes = GerenciadorClientes()

        self._processador = ProcessadorComandos(
            self._clientes
        )

        self._socket_servidor: socket.socket | None = None
        self._ativo = False
        self._threads_clientes: list[threading.Thread] = []

    def iniciar(self) -> None:

        if self._ativo:
            raise RuntimeError(
                "O servidor já está em execução"
            )

        self._socket_servidor = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )

        self._socket_servidor.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1,
        )

        self._socket_servidor.bind(
            (self._host, self._porta)
        )

        self._socket_servidor.listen()
        self._socket_servidor.settimeout(0.5)

        self._ativo = True

        endereco_real = (
            self._socket_servidor.getsockname()
        )

        print(
            f"Servidor iniciado em "
            f"{endereco_real[0]}:{endereco_real[1]}"
        )

        try:
            while self._ativo:
                try:
                    conexao, endereco = (
                        self._socket_servidor.accept()
                    )
                except socket.timeout:
                    continue
                except OSError:
                    if not self._ativo:
                        break

                    raise

                print(
                    "Nova conexão recebida de "
                    f"{endereco[0]}:{endereco[1]}"
                )

                thread_cliente = threading.Thread(
                    target=self._atender_cliente,
                    args=(conexao, endereco),
                    daemon=True,
                )

                self._threads_clientes.append(
                    thread_cliente
                )

                thread_cliente.start()

        except KeyboardInterrupt:
            print("\nEncerrando servidor...")

        finally:
            self.encerrar()

    def _atender_cliente(
        self,
        conexao: socket.socket,
        endereco: tuple[str, int],
    ) -> None:

        buffer = ""

        try:
            while True:
                dados = conexao.recv(TAMANHO_BUFFER)

                if not dados:
                    break

                buffer += dados.decode(CODIFICACAO)

                while TERMINADOR in buffer:
                    mensagem, buffer = buffer.split(
                        TERMINADOR,
                        1,
                    )

                    if not mensagem:
                        continue

                    manter_conexao = (
                        self._processador.processar(
                            conexao,
                            mensagem,
                        )
                    )

                    if not manter_conexao:
                        return

        except UnicodeDecodeError:
            print(
                "Dados inválidos recebidos de "
                f"{endereco[0]}:{endereco[1]}"
            )

        except ConnectionResetError:
            print(
                "Conexão encerrada abruptamente por "
                f"{endereco[0]}:{endereco[1]}"
            )

        except OSError as erro:
            print(
                "Erro de conexão com "
                f"{endereco[0]}:{endereco[1]}: {erro}"
            )

        finally:
            apelido = (
                self._clientes.remover_por_conexao(
                    conexao
                )
            )

            if apelido is not None:
                print(
                    f"Cliente desconectado: {apelido}"
                )
            else:
                print(
                    "Conexão encerrada: "
                    f"{endereco[0]}:{endereco[1]}"
                )

            try:
                conexao.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

            conexao.close()

    def encerrar(self) -> None:

        self._ativo = False
        
        if self._socket_servidor is not None:
            try:
                self._socket_servidor.shutdown(
                    socket.SHUT_RDWR
                )
            except OSError:
                pass

            try:
                self._socket_servidor.close()
            except OSError:
                pass

            self._socket_servidor = None
    
    @property
    def porta(self) -> int:

        if self._socket_servidor is not None:
            return self._socket_servidor.getsockname()[1]

        return self._porta


    @property
    def ativo(self) -> bool:
        """Informa se o servidor está em execução."""

        return self._ativo

def iniciar_servidor() -> None:

    servidor = ServidorChat()
    servidor.iniciar()