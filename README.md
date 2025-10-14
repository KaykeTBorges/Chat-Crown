# 👑 Chat Crown

Bot de Telegram para controle financeiro pessoal com IA.

## 🚀 Quick Start

### Pré-requisitos
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) instalado
- Conta no Telegram (para criar o bot)
- Conta no Supabase (banco de dados)
- API Key do Groq (IA)

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/your-username/Chat-Crown.git
cd Chat-Crown
```

2. Instale as dependências com uv:
```bash
# uv criará automaticamente o ambiente virtual
uv sync
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o .env com suas credenciais
```

4. Configure o banco de dados:
```bash
# Execute as migrations
uv run alembic upgrade head
```

5. Execute o bot:
```bash
uv run python main.py
```

## 📖 Uso

### Registrar um gasto
Apenas envie uma mensagem natural para o bot:
```
50 almoco
100 uber
30.50 café
```

### Comandos disponíveis
- `/start` - Iniciar o bot e registrar-se
- `/ajuda` - Ver todos os comandos e categorias
- `/resumo` - Resumo dos gastos do mês
- `/relatorio` - Relatório detalhado com opções
- `/categoria [nome]` - Ver gastos de uma categoria específica
- `/editar` - Editar ou deletar gastos recentes

## 🏗️ Estrutura do Projeto

```
chat-crown/
├── models/          # SQLAlchemy models
├── repositories/    # Data access layer
├── services/        # Business logic
├── bot/            # Telegram bot handlers
├── database/       # Database configuration
└── alembic/        # Database migrations
```

## 🛠️ Desenvolvimento

### Com uv:
```bash
# Instalar dependências de desenvolvimento
uv sync --all-extras

# Rodar testes
uv run pytest

# Rodar linter
uv run ruff check .

# Formatar código
uv run ruff format .
```

## 📦 Tecnologias

- **Python 3.11+** - Linguagem
- **FastAPI** - Framework web
- **python-telegram-bot** - Bot do Telegram
- **SQLAlchemy** - ORM
- **PostgreSQL** - Banco de dados (Supabase)
- **Groq API** - IA para processamento de linguagem natural
- **uv** - Gerenciador de pacotes e ambientes

## 📝 License

MIT License - ver [LICENSE](LICENSE)

## 👥 Autores

- Luigi Schmitt
- Kayke Borges

