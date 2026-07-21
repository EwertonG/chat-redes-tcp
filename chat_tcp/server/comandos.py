"""Processamento dos comandos recebidos pelo servidor."""

import socket

from chat_tcp.common.protocolo import (
    LIST,
    LOGIN,
    LOGOUT,
    MESSAGE,
    codificar_mensagem,
    criar_confirmacao_envio,
    criar_lista_usuarios,
    criar_mensagem_recebida,
    criar_resposta_erro,
    criar_resposta_ok,
    interpretar_mensagem,
)
from chat_tcp.server.clientes import GerenciadorClientes


class ProcessadorComandos:

    def __init__(
        self,
        clientes: GerenciadorClientes,
    ) -> None:
        self._clientes = clientes

    def enviar(
        self,
        conexao: socket.socket,
        mensagem: str,
    ) -> bool:

        try:
            conexao.sendall(
                codificar_mensagem(mensagem)
            )
            return True
        except OSError:
            return False

    def processar(
        self,
        conexao: socket.socket,
        mensagem: str,
    ) -> bool:

        try:
            tipo, campos = interpretar_mensagem(mensagem)
        except ValueError as erro:
            self.enviar(
                conexao,
                criar_resposta_erro(str(erro)),
            )
            return True

        if tipo == LOGIN:
            return self._processar_login(
                conexao,
                campos,
            )

        if tipo == LIST:
            return self._processar_list(
                conexao,
                campos,
            )

        if tipo == MESSAGE:
            return self._processar_message(
                conexao,
                campos,
            )

        if tipo == LOGOUT:
            return self._processar_logout(
                conexao,
                campos,
            )

        self.enviar(
            conexao,
            criar_resposta_erro(
                "Comando não suportado"
            ),
        )

        return True

    def _processar_login(
        self,
        conexao: socket.socket,
        campos: list[str],
    ) -> bool:
        """Processa o comando LOGIN."""

        if len(campos) != 1:
            self.enviar(
                conexao,
                criar_resposta_erro(
                    "Formato esperado: LOGIN;apelido"
                ),
            )
            return True

        if self._clientes.buscar_apelido(conexao) is not None:
            self.enviar(
                conexao,
                criar_resposta_erro(
                    "Esta conexão já possui login"
                ),
            )
            return True

        apelido = campos[0].strip()

        try:
            registrado = self._clientes.registrar(
                apelido,
                conexao,
            )
        except ValueError as erro:
            self.enviar(
                conexao,
                criar_resposta_erro(str(erro)),
            )
            return True

        if not registrado:
            self.enviar(
                conexao,
                criar_resposta_erro(
                    "Apelido já está em uso"
                ),
            )
            return True

        self.enviar(
            conexao,
            criar_resposta_ok(
                "Login realizado"
            ),
        )

        return True

    def _processar_list(
        self,
        conexao: socket.socket,
        campos: list[str],
    ) -> bool:
        """Processa o comando LIST."""

        if campos:
            self.enviar(
                conexao,
                criar_resposta_erro(
                    "Formato esperado: LIST"
                ),
            )
            return True

        if not self._esta_autenticado(conexao):
            self._enviar_erro_autenticacao(conexao)
            return True

        usuarios = self._clientes.listar()

        self.enviar(
            conexao,
            criar_lista_usuarios(usuarios),
        )

        return True

    def _processar_message(
        self,
        conexao: socket.socket,
        campos: list[str],
    ) -> bool:
        """Processa o comando MESSAGE."""

        if len(campos) != 2:
            self.enviar(
                conexao,
                criar_resposta_erro(
                    "Formato esperado: "
                    "MESSAGE;destinatario;texto"
                ),
            )
            return True

        remetente = self._clientes.buscar_apelido(
            conexao
        )

        if remetente is None:
            self._enviar_erro_autenticacao(conexao)
            return True

        destinatario = campos[0].strip()
        texto = campos[1].strip()

        if not destinatario:
            self.enviar(
                conexao,
                criar_resposta_erro(
                    "Destinatário não pode ficar vazio"
                ),
            )
            return True

        if not texto:
            self.enviar(
                conexao,
                criar_resposta_erro(
                    "Mensagem não pode ficar vazia"
                ),
            )
            return True

        conexao_destinatario = (
            self._clientes.buscar_conexao(
                destinatario
            )
        )

        if conexao_destinatario is None:
            self.enviar(
                conexao,
                criar_resposta_erro(
                    "Destinatário não encontrado"
                ),
            )
            return True

        enviada = self.enviar(
            conexao_destinatario,
            criar_mensagem_recebida(
                remetente,
                texto,
            ),
        )

        if not enviada:
            self._clientes.remover(destinatario)

            self.enviar(
                conexao,
                criar_resposta_erro(
                    "Não foi possível entregar a mensagem"
                ),
            )
            return True

        self.enviar(
            conexao,
            criar_confirmacao_envio(
                destinatario
            ),
        )

        return True

    def _processar_logout(
        self,
        conexao: socket.socket,
        campos: list[str],
    ) -> bool:
        """Processa o comando LOGOUT."""

        if campos:
            self.enviar(
                conexao,
                criar_resposta_erro(
                    "Formato esperado: LOGOUT"
                ),
            )
            return True

        apelido = self._clientes.remover_por_conexao(
            conexao
        )

        if apelido is None:
            self.enviar(
                conexao,
                criar_resposta_erro(
                    "Cliente não autenticado"
                ),
            )
            return False

        self.enviar(
            conexao,
            criar_resposta_ok(
                "Logout realizado"
            ),
        )

        return False

    def _esta_autenticado(
        self,
        conexao: socket.socket,
    ) -> bool:
        """Verifica se a conexão possui login."""

        return (
            self._clientes.buscar_apelido(conexao)
            is not None
        )

    def _enviar_erro_autenticacao(
        self,
        conexao: socket.socket,
    ) -> None:
        """Informa que o cliente precisa executar LOGIN."""

        self.enviar(
            conexao,
            criar_resposta_erro(
                "Execute LOGIN antes deste comando"
            ),
        )