# ChatRedes TCP

Aplicação de chat desenvolvida em Python utilizando comunicação por sockets TCP.

O sistema permite que vários clientes se conectem a um servidor central, realizem login com um apelido, consultem os usuários conectados e enviem mensagens privadas.

## Integrantes

- Ana Clara Francisca - 22.2.8096
- Ewerton Gomes Barcia - 22.2.8066

## Funcionalidades

- comunicação cliente-servidor utilizando TCP;
- conexão simultânea de vários clientes;
- uso de uma thread para cada cliente conectado;
- validação de apelidos duplicados;
- listagem de usuários conectados;
- envio de mensagens privadas;
- interface gráfica desenvolvida com Tkinter;
- interface de terminal;
- encerramento de sessão com logout;
- tratamento de desconexões inesperadas;
- tratamento de fragmentação e agrupamento de mensagens TCP;
- testes unitários;
- testes de integração com sockets reais.

## Tecnologias utilizadas

- Python 3;
- sockets TCP;
- módulo `threading`;
- Tkinter;
- `unittest`.

A aplicação utiliza apenas módulos da biblioteca padrão do Python. Portanto, não é necessário instalar bibliotecas externas para executar o sistema.

## Configuração

As configurações de rede estão localizadas em:

```text
chat_tcp/common/config.py
```

Exemplo de configuração:

```python
HOST_SERVIDOR = "0.0.0.0"
HOST_CLIENTE = "127.0.0.1"
PORTA = 5000
TAMANHO_BUFFER = 1024
CODIFICACAO = "utf-8"
TERMINADOR = "\n"
```

## Execução do sistema

Execute os comandos no diretório raiz do projeto.

### 1. Iniciar o servidor

```bash
python servidor.py
```

O servidor ficará aguardando conexões na porta configurada.

### 2. Iniciar o cliente gráfico

Abra outro terminal e execute:

```bash
python cliente_gui.py
```

Para testar a comunicação, execute pelo menos dois clientes gráficos em terminais diferentes.
