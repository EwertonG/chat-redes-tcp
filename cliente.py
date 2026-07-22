from chat_tcp.client.interface import InterfaceTerminal


def iniciar_cliente() -> None:
    """Cria e executa a interface do cliente."""

    interface = InterfaceTerminal()
    interface.executar()


if __name__ == "__main__":
    iniciar_cliente()