from chat_tcp.common.config import CODIFICACAO, TERMINADOR


# Comandos cliente
LOGIN = "LOGIN"
LIST = "LIST"
MESSAGE = "MESSAGE"
LOGOUT = "LOGOUT"

# Respostas servidor
OK = "OK"
ERROR = "ERROR"
USERS = "USERS"
INFO = "INFO"
SENT = "SENT"


TIPOS_VALIDOS = {
    LOGIN,
    LIST,
    MESSAGE,
    LOGOUT,
    OK,
    ERROR,
    USERS,
    INFO,
    SENT,
}


def validar_campo_simples(valor: str, nome: str) -> str:

    valor = valor.strip()

    if not valor:
        raise ValueError(f"{nome} não pode ficar vazio")

    if ";" in valor:
        raise ValueError(f"{nome} não pode conter ponto e vírgula")

    if "\n" in valor or "\r" in valor:
        raise ValueError(f"{nome} não pode conter quebra de linha")

    return valor


def validar_texto(texto: str) -> str:

    texto = texto.strip()

    if not texto:
        raise ValueError("A mensagem não pode ficar vazia")

    if "\n" in texto or "\r" in texto:
        raise ValueError("A mensagem não pode conter quebra de linha")

    return texto


def montar_mensagem(tipo: str, *campos: str) -> str:

    tipo = tipo.strip().upper()

    if tipo not in TIPOS_VALIDOS:
        raise ValueError(f"Tipo de mensagem desconhecido: {tipo}")

    partes = [tipo]

    for campo in campos:
        campo = str(campo)

        if "\n" in campo or "\r" in campo:
            raise ValueError(
                "Os campos não podem conter quebra de linha"
            )

        partes.append(campo)

    return ";".join(partes)


def criar_login(apelido: str) -> str:

    apelido = validar_campo_simples(apelido, "Apelido")
    return montar_mensagem(LOGIN, apelido)


def criar_solicitacao_lista() -> str:

    return montar_mensagem(LIST)


def criar_mensagem(destinatario: str, texto: str) -> str:

    destinatario = validar_campo_simples(
        destinatario,
        "Destinatário"
    )

    texto = validar_texto(texto)

    return montar_mensagem(
        MESSAGE,
        destinatario,
        texto
    )


def criar_logout() -> str:

    return montar_mensagem(LOGOUT)

def criar_resposta_ok(texto: str) -> str:

    texto = validar_texto(texto)
    return montar_mensagem(OK, texto)


def criar_resposta_erro(texto: str) -> str:

    texto = validar_texto(texto)
    return montar_mensagem(ERROR, texto)


def criar_lista_usuarios(usuarios: list[str]) -> str:

    usuarios_validados = [
        validar_campo_simples(usuario, "Usuário")
        for usuario in usuarios
    ]

    return montar_mensagem(
        USERS,
        *usuarios_validados,
    )


def criar_mensagem_recebida(
    remetente: str,
    texto: str,
) -> str:

    remetente = validar_campo_simples(
        remetente,
        "Remetente",
    )

    texto = validar_texto(texto)

    return montar_mensagem(
        MESSAGE,
        remetente,
        texto,
    )


def criar_confirmacao_envio(destinatario: str) -> str:

    destinatario = validar_campo_simples(
        destinatario,
        "Destinatário",
    )

    return montar_mensagem(
        SENT,
        destinatario,
    )


def codificar_mensagem(mensagem: str) -> bytes:

    mensagem = mensagem.rstrip("\r\n")

    if "\n" in mensagem or "\r" in mensagem:
        raise ValueError(
            "A mensagem do protocolo não pode conter quebra de linha interna"
        )

    mensagem_completa = mensagem + TERMINADOR

    return mensagem_completa.encode(CODIFICACAO)


def interpretar_mensagem(mensagem: str) -> tuple[str, list[str]]:

    mensagem = mensagem.rstrip("\r\n")

    if not mensagem:
        raise ValueError("Mensagem vazia")

    partes = mensagem.split(";", 2)

    tipo = partes[0].strip().upper()
    campos = partes[1:]

    if tipo not in TIPOS_VALIDOS:
        raise ValueError(f"Tipo de mensagem desconhecido: {tipo}")

    return tipo, campos