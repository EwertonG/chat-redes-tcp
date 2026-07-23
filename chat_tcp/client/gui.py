import tkinter as tk
from tkinter import messagebox

from chat_tcp.client.cliente import ClienteChat
from chat_tcp.common.protocolo import interpretar_mensagem


class InterfaceGrafica:

    def __init__(self) -> None:
        self._janela = tk.Tk()
        self._janela.title("Chat TCP")
        self._janela.geometry("700x500")
        self._janela.minsize(700,550)

        self._cliente: ClienteChat | None = None
        self._apelido: str | None = None

        # Cada chave representa um usuário e cada valor é a lista de
        # mensagens trocadas com esse usuário.
        self._conversas: dict[str, list[str]] = {}
        self._usuario_selecionado: str | None = None

        self._criar_tela_login()

        self._janela.protocol(
            "WM_DELETE_WINDOW",
            self._fechar_janela,
        )

    def executar(self) -> None:
        self._janela.mainloop()

    def _limpar_janela(self) -> None:
        for componente in self._janela.winfo_children():
            componente.destroy()

    # =========================================================
    # Tela de login
    # =========================================================

    def _criar_tela_login(self) -> None:
        self._limpar_janela()
        self._janela.geometry("400x250")

        quadro = tk.Frame(self._janela)
        quadro.pack(
            expand=True,
            padx=20,
            pady=20,
        )

        tk.Label(
            quadro,
            text="Chat TCP",
            font=("Arial", 14, "bold"),
        ).pack(pady=(0, 20))

        tk.Label(
            quadro,
            text="Apelido:",
        ).pack(anchor="w")

        self._entrada_apelido = tk.Entry(
            quadro,
            width=30,
        )
        self._entrada_apelido.pack(
            fill="x",
            pady=5,
        )
        self._entrada_apelido.focus()

        tk.Button(
            quadro,
            text="Conectar",
            command=self._conectar,
            width=15,
        ).pack(pady=10)

        self._rotulo_status = tk.Label(
            quadro,
            text="Desconectado",
        )
        self._rotulo_status.pack(pady=5)

        self._entrada_apelido.bind(
            "<Return>",
            lambda evento: self._conectar(),
        )

    def _conectar(self) -> None:
        apelido = self._entrada_apelido.get().strip()

        if not apelido:
            messagebox.showwarning(
                "Aviso",
                "Digite um apelido.",
            )
            return

        self._rotulo_status.configure(
            text="Conectando...",
        )
        self._janela.update_idletasks()

        try:
            self._cliente = ClienteChat()

            self._cliente.conectar(
                callback_mensagem=self._receber_mensagem,
                callback_desconexao=self._tratar_desconexao,
            )

            self._cliente.enviar_login(apelido)

            self._apelido = apelido
            self._conversas = {}
            self._usuario_selecionado = None

            self._criar_tela_chat()

        except Exception as erro:
            if self._cliente is not None:
                self._cliente.encerrar()

            self._cliente = None
            self._apelido = None

            self._rotulo_status.configure(
                text="Desconectado",
            )

            messagebox.showerror(
                "Erro",
                f"Não foi possível conectar ao servidor.\n\n{erro}",
            )

    # =========================================================
    # Tela principal
    # =========================================================

    def _criar_tela_chat(self) -> None:
        self._limpar_janela()
        self._janela.geometry("700x500")

        # Cabeçalho
        quadro_superior = tk.Frame(
            self._janela,
            relief="groove",
            borderwidth=1,
        )
        quadro_superior.pack(
            fill="x",
            padx=10,
            pady=(10, 5),
        )

        tk.Label(
            quadro_superior,
            text="Chat TCP",
            font=("Arial", 12, "bold"),
        ).pack(
            side="left",
            padx=10,
            pady=8,
        )

        tk.Label(
            quadro_superior,
            text=f"Usuário: {self._apelido}",
        ).pack(
            side="right",
            padx=10,
        )

        self._rotulo_conexao = tk.Label(
            quadro_superior,
            text="Conectado",
        )
        self._rotulo_conexao.pack(
            side="right",
            padx=10,
        )

        # Área principal
        quadro_principal = tk.Frame(self._janela)
        quadro_principal.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5,
        )

        # Lista de usuários
        quadro_usuarios = tk.LabelFrame(
            quadro_principal,
            text="Usuários conectados",
        )
        quadro_usuarios.pack(
            side="left",
            fill="y",
            padx=(0, 10),
        )

        quadro_lista = tk.Frame(quadro_usuarios)
        quadro_lista.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5,
        )

        self._lista_usuarios = tk.Listbox(
            quadro_lista,
            width=22,
            height=10,
            exportselection=False,
        )
        self._lista_usuarios.pack(
            side="left",
            fill="both",
            expand=True,
        )

        barra_usuarios = tk.Scrollbar(
            quadro_lista,
            command=self._lista_usuarios.yview,
        )
        barra_usuarios.pack(
            side="right",
            fill="y",
        )

        self._lista_usuarios.configure(
            yscrollcommand=barra_usuarios.set,
        )

        self._lista_usuarios.bind(
            "<<ListboxSelect>>",
            self._selecionar_usuario,
        )

        tk.Button(
            quadro_usuarios,
            text="Atualizar usuários",
            command=self._solicitar_lista,
        ).pack(
            fill="x",
            padx=5,
            pady=(0, 5),
        )

        # Área de conversa
        quadro_conversa = tk.LabelFrame(
            quadro_principal,
            text="Conversa",
        )
        quadro_conversa.pack(
            side="left",
            fill="both",
            expand=True,
        )

        quadro_conversa.grid_columnconfigure(
            0,
            weight=1,
        )

        quadro_conversa.grid_rowconfigure(
            1,
            weight=1,
        )

        self._rotulo_conversa = tk.Label(
            quadro_conversa,
            text="Selecione um usuário para conversar",
            anchor="w",
        )
        self._rotulo_conversa.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=5,
            pady=5,
        )

        # Histórico de mensagens
        quadro_mensagens = tk.Frame(
            quadro_conversa,
        )

        quadro_mensagens.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=5,
        )

        quadro_mensagens.grid_columnconfigure(
            0,
            weight=1,
        )

        quadro_mensagens.grid_rowconfigure(
            0,
            weight=1,
        )

        self._area_mensagens = tk.Text(
            quadro_mensagens,
            state="disabled",
            wrap="word",
            height=10,
        )

        self._area_mensagens.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        barra_mensagens = tk.Scrollbar(
            quadro_mensagens,
            command=self._area_mensagens.yview,
        )

        barra_mensagens.grid(
            row=0,
            column=1,
            sticky="ns",
        )

        self._area_mensagens.configure(
            yscrollcommand=barra_mensagens.set,
        )

        # Área para escrever a mensagem
        quadro_envio = tk.Frame(
            quadro_conversa,
        )

        quadro_envio.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=5,
            pady=5,
        )

        quadro_envio.grid_columnconfigure(
            0,
            weight=1,
        )

        tk.Label(
            quadro_envio,
            text="Mensagem:",
        ).grid(
            row=0,
            column=0,
            sticky="w",
        )

        self._entrada_mensagem = tk.Entry(
            quadro_envio,
            state="disabled",
        )

        self._entrada_mensagem.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=5,
        )

        quadro_botoes = tk.Frame(
            quadro_envio,
        )

        quadro_botoes.grid(
            row=2,
            column=0,
            sticky="ew",
        )

        tk.Button(
            quadro_botoes,
            text="Sair",
            command=self._logout,
            width=12,
        ).pack(
            side="left",
        )

        self._botao_enviar = tk.Button(
            quadro_botoes,
            text="Enviar",
            command=self._enviar_mensagem,
            state="disabled",
            width=12,
        )

        self._botao_enviar.pack(
            side="right",
        )

        self._entrada_mensagem.bind(
            "<Return>",
            self._enviar_com_atalho,
        )

        self._solicitar_lista()

    # =========================================================
    # Ações do usuário
    # =========================================================

    def _selecionar_usuario(self, evento=None) -> None:
        selecao = self._lista_usuarios.curselection()

        if not selecao:
            return

        usuario = self._lista_usuarios.get(selecao[0])

        self._usuario_selecionado = usuario

        self._rotulo_conversa.configure(
            text=f"Conversa com: {usuario}",
        )

        self._entrada_mensagem.configure(
            state="normal",
        )

        self._botao_enviar.configure(
            state="normal",
        )

        self._mostrar_conversa(usuario)
        self._entrada_mensagem.focus()

    def _solicitar_lista(self) -> None:
        if self._cliente is None:
            return

        try:
            self._cliente.solicitar_lista()
        except Exception as erro:
            messagebox.showerror(
                "Erro",
                f"Não foi possível solicitar a lista.\n\n{erro}",
            )

    def _enviar_com_atalho(self, evento=None) -> str:
        self._enviar_mensagem()

        # Impede que o Enter seja inserido na caixa após o envio.
        return "break"

    def _enviar_mensagem(self) -> None:
        if self._cliente is None:
            return

        destinatario = self._usuario_selecionado

        texto = self._entrada_mensagem.get().strip()

        if not destinatario:
            messagebox.showwarning(
                "Aviso",
                "Selecione um usuário.",
            )
            return

        if not texto:
            messagebox.showwarning(
                "Aviso",
                "Digite uma mensagem.",
            )
            return

        try:
            self._cliente.enviar_mensagem(
                destinatario,
                texto,
            )

            self._adicionar_na_conversa(
                destinatario,
                f"Você: {texto}",
            )

            self._entrada_mensagem.delete(
                0,
                tk.END,
            )
            self._entrada_mensagem.focus()

        except Exception as erro:
            messagebox.showerror(
                "Erro",
                f"Não foi possível enviar a mensagem.\n\n{erro}",
            )

    def _logout(self) -> None:
        cliente = self._cliente
        self._cliente = None

        if cliente is not None:
            try:
                cliente.enviar_logout()
            except Exception:
                pass

            cliente.encerrar()

        self._apelido = None
        self._conversas = {}
        self._usuario_selecionado = None

        self._criar_tela_login()

    # =========================================================
    # Mensagens recebidas do servidor
    # =========================================================

    def _receber_mensagem(self, mensagem: str) -> None:
        # O receptor executa em outra thread. O after garante que qualquer
        # alteração visual seja feita pela thread principal do Tkinter.
        self._janela.after(
            0,
            lambda: self._processar_mensagem(mensagem),
        )

    def _processar_mensagem(self, mensagem: str) -> None:
        try:
            comando, campos = interpretar_mensagem(mensagem)
        except (ValueError, TypeError):
            print(f"Mensagem inválida recebida: {mensagem}")
            return

        if comando == "MESSAGE":
            if len(campos) < 2:
                return

            remetente = campos[0]
            texto = campos[1]

            self._adicionar_na_conversa(
                remetente,
                f"{remetente}: {texto}",
            )

        elif comando == "USERS":
            usuarios = self._normalizar_lista_usuarios(campos)
            self._atualizar_lista_usuarios(usuarios)

        elif comando == "ERROR":
            texto = campos[0] if campos else "Erro desconhecido"

            messagebox.showerror(
                "Erro do servidor",
                texto,
            )

        elif comando == "OK":
            texto = campos[0] if campos else "Operação realizada"
            print(f"Servidor: {texto}")

        elif comando == "SENT":
            # A mensagem enviada já é mostrada na conversa local.
            pass

        elif comando == "INFO":
            texto = campos[0] if campos else ""
            print(f"Servidor: {texto}")

        else:
            print(f"Servidor: {mensagem}")

    def _normalizar_lista_usuarios(
        self,
        campos: list[str] | tuple[str, ...],
    ) -> list[str]:
        """
        Aceita tanto:
            USERS;ana;joao
        quanto:
            USERS;ana,joao
        """
        usuarios: list[str] = []

        for campo in campos:
            partes = campo.split(",")

            for parte in partes:
                usuario = parte.strip()

                if usuario:
                    usuarios.append(usuario)

        return usuarios

    def _atualizar_lista_usuarios(
        self,
        usuarios: list[str],
    ) -> None:
        usuarios_disponiveis = [
            usuario
            for usuario in usuarios
            if usuario and usuario != self._apelido
        ]

        self._lista_usuarios.delete(
            0,
            tk.END,
        )

        for usuario in usuarios_disponiveis:
            self._lista_usuarios.insert(
                tk.END,
                usuario,
            )

        if self._usuario_selecionado in usuarios_disponiveis:
            indice = usuarios_disponiveis.index(
                self._usuario_selecionado
            )

            self._lista_usuarios.selection_set(indice)
            self._lista_usuarios.activate(indice)
            return

        self._usuario_selecionado = None

        self._rotulo_conversa.configure(
            text="Selecione um usuário para conversar",
        )

        self._entrada_mensagem.configure(
            state="normal",
        )
        self._entrada_mensagem.delete(
            0,
            tk.END,
        )
        self._entrada_mensagem.configure(
            state="disabled",
        )

        self._botao_enviar.configure(
            state="disabled",
        )

        self._limpar_area_mensagens()

    # =========================================================
    # Conversas
    # =========================================================

    def _adicionar_na_conversa(
        self,
        usuario: str,
        texto: str,
    ) -> None:
        if usuario not in self._conversas:
            self._conversas[usuario] = []

        self._conversas[usuario].append(texto)

        if usuario == self._usuario_selecionado:
            self._mostrar_conversa(usuario)

    def _mostrar_conversa(self, usuario: str) -> None:
        self._area_mensagens.configure(
            state="normal",
        )

        self._area_mensagens.delete(
            "1.0",
            tk.END,
        )

        mensagens = self._conversas.get(
            usuario,
            [],
        )

        if not mensagens:
            self._area_mensagens.insert(
                tk.END,
                "Nenhuma mensagem nesta conversa.\n",
            )
        else:
            for mensagem in mensagens:
                self._area_mensagens.insert(
                    tk.END,
                    mensagem + "\n",
                )

        self._area_mensagens.configure(
            state="disabled",
        )
        self._area_mensagens.see(tk.END)

    def _limpar_area_mensagens(self) -> None:
        self._area_mensagens.configure(
            state="normal",
        )
        self._area_mensagens.delete(
            "1.0",
            tk.END,
        )
        self._area_mensagens.configure(
            state="disabled",
        )

    # =========================================================
    # Desconexão e encerramento
    # =========================================================

    def _tratar_desconexao(self) -> None:
        self._janela.after(
            0,
            self._mostrar_desconexao,
        )

    def _mostrar_desconexao(self) -> None:
        # Evita exibir o aviso quando a desconexão foi causada pelo logout.
        if self._cliente is None:
            return

        cliente = self._cliente
        self._cliente = None

        cliente.encerrar()

        self._apelido = None
        self._conversas = {}
        self._usuario_selecionado = None

        messagebox.showwarning(
            "Desconectado",
            "A conexão com o servidor foi encerrada.",
        )

        self._criar_tela_login()

    def _fechar_janela(self) -> None:
        cliente = self._cliente
        self._cliente = None

        if cliente is not None:
            try:
                cliente.enviar_logout()
            except Exception:
                pass

            cliente.encerrar()

        self._janela.destroy()


def iniciar_interface_grafica() -> None:
    interface = InterfaceGrafica()
    interface.executar()