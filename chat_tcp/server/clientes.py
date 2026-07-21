import socket
import threading


class GerenciadorClientes:

    def __init__(self) -> None:
        self._clientes: dict[str, socket.socket] = {}
        self._lock = threading.Lock()

    def registrar(
        self,
        apelido: str,
        conexao: socket.socket,
    ) -> bool:

        apelido = apelido.strip()

        if not apelido:
            raise ValueError("O apelido não pode ficar vazio")

        with self._lock:
            if apelido in self._clientes:
                return False

            self._clientes[apelido] = conexao
            return True

    def remover(self, apelido: str) -> socket.socket | None:

        with self._lock:
            return self._clientes.pop(apelido, None)

    def remover_por_conexao(
        self,
        conexao: socket.socket,
    ) -> str | None:

        with self._lock:
            for apelido, socket_cliente in self._clientes.items():
                if socket_cliente is conexao:
                    del self._clientes[apelido]
                    return apelido

        return None

    def buscar_conexao(
        self,
        apelido: str,
    ) -> socket.socket | None:

        with self._lock:
            return self._clientes.get(apelido)

    def buscar_apelido(
        self,
        conexao: socket.socket,
    ) -> str | None:

        with self._lock:
            for apelido, socket_cliente in self._clientes.items():
                if socket_cliente is conexao:
                    return apelido

        return None

    def listar(self) -> list[str]:

        with self._lock:
            return sorted(self._clientes.keys())

    def existe(self, apelido: str) -> bool:

        with self._lock:
            return apelido in self._clientes

    def quantidade(self) -> int:

        with self._lock:
            return len(self._clientes)