# 📅 Plano de Desenvolvimento - Chat Crown
**Período:** 1 semana (5 dias úteis)  
**Equipe:** Luigi & Kayke  
**Objetivo:** MVP funcional + features essenciais

---

## 🎯 MVP (Mínimo Viável)
- ✅ Registro de gastos via mensagem natural
- ✅ Categorização automática (regex + IA fallback)
- ✅ Comando `/resumo` com gastos do mês
- ✅ Comando `/ajuda` com instruções

---

## 📊 Divisão de Responsabilidades

### 👨‍💻 Luigi - Backend & Banco de Dados
- Setup inicial do projeto
- Configuração do banco de dados
- Models e ORM
- Business logic (services)
- Integração com Groq API

### 👨‍💻 Kayke - Bot & Handlers
- Configuração do Telegram Bot
- Handlers de comandos
- Formatação de mensagens
- Testes do bot
- Deploy

---

## 📆 DIA 1 - Segunda-feira: Setup & Fundação

### Luigi (6-8h)
- [ ] **Setup do Projeto**
  - [ ] Criar estrutura de pastas do projeto
  - [ ] Setup com `uv` (gerenciador de pacotes rápido)
  - [ ] Criar `pyproject.toml` com dependências:
    ```bash
    # Instalar dependências
    uv sync
    
    # Principais dependências:
    # - fastapi, uvicorn (web framework)
    # - python-telegram-bot (bot)
    # - sqlalchemy, psycopg2 (database)
    # - alembic (migrations)
    # - groq (IA)
    # - pydantic-settings (config)
    ```
  - [ ] Criar `.env.example` com variáveis necessárias
  - [ ] Setup do `.gitignore` para Python

- [ ] **Banco de Dados - Supabase**
  - [ ] Criar conta no Supabase
  - [ ] Criar novo projeto PostgreSQL
  - [ ] Configurar conexão local
  - [ ] Testar conectividade

- [ ] **Models (SQLAlchemy)**
  - [ ] Criar `models/user.py`:
    - `id`, `telegram_id`, `username`, `created_at`
  - [ ] Criar `models/expense.py`:
    - `id`, `user_id`, `amount`, `category`, `description`, `date`, `created_at`
  - [ ] Criar `models/category.py`:
    - `id`, `name`, `emoji`
  - [ ] Configurar Alembic para migrations
  - [ ] Rodar primeira migration

### Kayke (6-8h)
- [ ] **Setup do Telegram Bot**
  - [ ] Criar bot no BotFather (Telegram)
  - [ ] Obter e salvar Bot Token
  - [ ] Estudar documentação python-telegram-bot
  - [ ] Criar estrutura básica do bot

- [ ] **Estrutura do Projeto - Bot**
  - [ ] Criar `bot/` directory structure:
    ```
    bot/
    ├── __init__.py
    ├── handlers/
    │   ├── __init__.py
    │   ├── start.py
    │   ├── help.py
    │   └── message.py
    ├── keyboards.py
    └── formatters.py
    ```

- [ ] **Comandos Básicos**
  - [ ] Implementar `/start` handler
    - Mensagem de boas-vindas
    - Registro automático do usuário (mock por enquanto)
  - [ ] Implementar `/ajuda` handler
    - Listar todos os comandos
    - Listar categorias disponíveis com emojis:
      - 🙏 Dízimos/Contribuição
      - 🏠 Moradia
      - 🍽️ Alimentação
      - 🚗 Transporte
      - 💳 Dívidas
      - 🎮 Lazer
      - 👕 Vestuário
      - 💊 Saúde
      - 📚 Educação
      - 📦 Diversos
      - 💰 Seguros/Poupanças/Investimento
    - Exemplos de uso

**🎯 Meta do Dia:** Projeto estruturado, banco de dados rodando, bot respondendo comandos básicos

---

## 📆 DIA 2 - Terça-feira: Core Features (Registro de Gastos)

### Luigi (6-8h)
- [ ] **Database Layer**
  - [ ] Criar `database/connection.py` - gerenciador de conexões
  - [ ] Criar `repositories/user_repository.py`:
    - `create_user(telegram_id, username)`
    - `get_user_by_telegram_id(telegram_id)`
  - [ ] Criar `repositories/expense_repository.py`:
    - `create_expense(user_id, amount, category, description, date)`
    - `get_expenses_by_user(user_id, start_date, end_date)`
    - `get_expense_by_id(expense_id)`
  - [ ] Testar repositories com dados mock

- [ ] **AI Processor - Parte 1 (Regex)**
  - [ ] Criar `services/ai_processor.py`
  - [ ] Implementar parser com regex para padrões comuns:
    - "50 almoco" → {amount: 50, category: "Alimentação", desc: "almoco"}
    - "100 uber" → {amount: 100, category: "Transporte", desc: "uber"}
    - "30,50 café" → {amount: 30.50, category: "Alimentação", desc: "café"}
  - [ ] Criar dicionário de keywords por categoria
  - [ ] Testar com 20+ exemplos diferentes

### Kayke (6-8h)
- [ ] **Message Handler - Registro de Gastos**
  - [ ] Criar `handlers/expense_handler.py`
  - [ ] Implementar lógica de detecção de mensagem de gasto
  - [ ] Integrar com AI Processor (Luigi)
  - [ ] Criar feedback de confirmação visual:
    ```
    ✅ Registrado!
    💰 Valor: R$ 50,00
    📂 Categoria: Alimentação
    📝 Descrição: almoco
    🗓️ Data: 14/10/2025
    ```

- [ ] **User Service Integration**
  - [ ] Criar `services/user_service.py`
  - [ ] Implementar auto-registro no `/start`
  - [ ] Middleware para verificar se usuário existe
  - [ ] Se não existir, criar automaticamente

- [ ] **Testes Manuais**
  - [ ] Testar registro de gastos com diferentes formatos
  - [ ] Documentar casos que funcionam/não funcionam
  - [ ] Criar lista de melhorias para Dia 3

**🎯 Meta do Dia:** Usuário consegue registrar gastos via mensagens naturais e receber confirmação

---

## 📆 DIA 3 - Quarta-feira: IA & Relatórios

### Luigi (6-8h)
- [ ] **AI Processor - Parte 2 (Groq API)**
  - [ ] Criar conta no Groq
  - [ ] Obter API key
  - [ ] Implementar fallback para Groq quando regex falhar
  - [ ] Criar prompt otimizado:
    ```
    Analise esta mensagem de gasto e retorne JSON:
    Mensagem: "{user_message}"
    Categorias válidas: [lista das 11 categorias]
    
    Retorne: {"amount": float, "category": string, "description": string}
    ```
  - [ ] Implementar tratamento de erros da API
  - [ ] Adicionar cache simples para mensagens repetidas
  - [ ] Testar com 30+ casos diversos

- [ ] **Expense Service**
  - [ ] Criar `services/expense_service.py`
  - [ ] `register_expense(user_id, message)` - usa AI Processor
  - [ ] `get_monthly_summary(user_id, month, year)` - agregações
  - [ ] `get_expenses_by_category(user_id, category, month, year)`
  - [ ] Calcular totais e percentuais por categoria

### Kayke (6-8h)
- [ ] **Comando /resumo**
  - [ ] Criar `handlers/summary_handler.py`
  - [ ] Integrar com `expense_service.get_monthly_summary()`
  - [ ] Formatar mensagem bonita:
    ```
    📊 RESUMO DE OUTUBRO/2025
    
    💰 Total Gasto: R$ 2.450,00
    
    📂 Por Categoria:
    🍽️ Alimentação: R$ 650,00 (26.5%)
    🚗 Transporte: R$ 420,00 (17.1%)
    🏠 Moradia: R$ 800,00 (32.7%)
    🎮 Lazer: R$ 280,00 (11.4%)
    📦 Outros: R$ 300,00 (12.2%)
    
    📈 Média diária: R$ 81,67
    ```
  - [ ] Adicionar emoji e cores
  - [ ] Tratar caso sem gastos registrados

- [ ] **Testes de Integração**
  - [ ] Fluxo completo: registro → confirmação → resumo
  - [ ] Testar com múltiplos usuários
  - [ ] Testar casos extremos (valores grandes, negativos, etc)

**🎯 Meta do Dia:** MVP completo! Registro com IA + Resumo mensal funcionando

---

## 📆 DIA 4 - Quinta-feira: Features Avançadas

### Luigi (6-8h)
- [ ] **Report Service**
  - [ ] Criar `services/report_service.py`
  - [ ] `get_detailed_report(user_id, month, year)`:
    - Lista de todos os gastos do mês
    - Subtotais por categoria
    - Comparativo com mês anterior
    - Maiores gastos
  - [ ] `compare_months(user_id, month1, month2)`:
    - Diferença percentual total
    - Diferença por categoria
    - Categorias que aumentaram/diminuíram

- [ ] **Expense Management**
  - [ ] Adicionar ao `expense_repository.py`:
    - `update_expense(expense_id, amount, category, description)`
    - `delete_expense(expense_id)`
    - `get_recent_expenses(user_id, limit=10)` - últimos N gastos
  - [ ] Validações de ownership (usuário só edita seus gastos)

### Kayke (6-8h)
- [ ] **Comando /relatorio**
  - [ ] Criar `handlers/report_handler.py`
  - [ ] Keyboard inline com opções:
    - "📅 Mês Atual"
    - "📆 Mês Anterior"
    - "📊 Comparar Meses"
  - [ ] Formatar relatório detalhado com lista de gastos
  - [ ] Paginação se houver muitos gastos (>20)

- [ ] **Comando /categoria**
  - [ ] Criar `handlers/category_handler.py`
  - [ ] Parser de argumento: `/categoria Alimentação`
  - [ ] Listar todos os gastos daquela categoria no mês
  - [ ] Mostrar total da categoria
  - [ ] Keyboard para navegar entre categorias

- [ ] **Comando /editar - Parte 1**
  - [ ] Criar `handlers/edit_handler.py`
  - [ ] Mostrar últimos 5 gastos do usuário
  - [ ] Keyboard inline para selecionar qual editar
  - [ ] Opções: "✏️ Editar Valor" | "🗑️ Deletar"

**🎯 Meta do Dia:** Relatórios detalhados e navegação por categorias funcionando

---

## 📆 DIA 5 - Sexta-feira: Edição, Polish & Deploy

### Luigi (6-8h)
- [ ] **Finalizações Backend**
  - [ ] Implementar logging estruturado
  - [ ] Adicionar tratamento de erros global
  - [ ] Criar `config.py` centralizado
  - [ ] Documentar código crítico
  - [ ] Testes de carga básicos

- [ ] **Deploy - Railway (Backend)**
  - [ ] Criar conta no Railway
  - [ ] Conectar repositório GitHub
  - [ ] Configurar variáveis de ambiente
  - [ ] Deploy do backend
  - [ ] Testar conectividade Supabase → Railway

- [ ] **Migrations & Seeds**
  - [ ] Popular tabela de categorias com as 11 categorias
  - [ ] Scripts de backup do banco
  - [ ] Documentar processo de restore

### Kayke (6-8h)
- [ ] **Comando /editar - Parte 2**
  - [ ] Implementar fluxo de edição de valor:
    - Bot: "Qual o novo valor?"
    - User: "75"
    - Bot: "✅ Valor atualizado!"
  - [ ] Implementar confirmação de deleção:
    - Keyboard: "⚠️ Confirmar Exclusão" | "❌ Cancelar"
  - [ ] Implementar edição de categoria
  - [ ] Implementar edição de descrição

- [ ] **Polish & UX**
  - [ ] Revisar todas as mensagens do bot
  - [ ] Garantir consistência de emojis
  - [ ] Adicionar mensagens de loading ("⏳ Processando...")
  - [ ] Melhorar tratamento de erros com mensagens amigáveis
  - [ ] Implementar comando `/cancelar` para interromper operações

- [ ] **Deploy - Railway (Bot)**
  - [ ] Configurar webhook do Telegram → Railway
  - [ ] Deploy do bot
  - [ ] Testes em produção
  - [ ] Monitoramento de erros

- [ ] **Testes Finais**
  - [ ] Teste de todos os comandos em produção
  - [ ] Teste com 2-3 usuários reais
  - [ ] Documentar bugs encontrados

**🎯 Meta do Dia:** Aplicação completa em produção, funcional e polida!

---

## 📁 Estrutura Final do Projeto

```
chat-crown/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── PLAN.md
├── IDEA.md
├── main.py                 # Entry point
├── config.py               # Configurações centralizadas
│
├── models/                 # SQLAlchemy Models
│   ├── __init__.py
│   ├── user.py
│   ├── expense.py
│   └── category.py
│
├── database/               # Database Setup
│   ├── __init__.py
│   └── connection.py
│
├── repositories/           # Data Access Layer
│   ├── __init__.py
│   ├── user_repository.py
│   ├── expense_repository.py
│   └── category_repository.py
│
├── services/               # Business Logic
│   ├── __init__.py
│   ├── user_service.py
│   ├── expense_service.py
│   ├── ai_processor.py
│   └── report_service.py
│
├── bot/                    # Telegram Bot
│   ├── __init__.py
│   ├── bot.py              # Bot setup
│   ├── keyboards.py        # Inline keyboards
│   ├── formatters.py       # Message formatting
│   └── handlers/
│       ├── __init__.py
│       ├── start.py
│       ├── help.py
│       ├── expense_handler.py
│       ├── summary_handler.py
│       ├── report_handler.py
│       ├── category_handler.py
│       └── edit_handler.py
│
├── alembic/                # Database Migrations
│   └── versions/
│
└── tests/                  # Testes (se houver tempo)
    ├── test_ai_processor.py
    └── test_repositories.py
```

---

## 🔑 Variáveis de Ambiente (.env)

```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Database (Supabase)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Groq API
GROQ_API_KEY=your_groq_api_key_here

# App Config
ENVIRONMENT=production
LOG_LEVEL=INFO
```

---

## ✅ Checklist de Entrega

### MVP (Obrigatório)
- [ ] Usuário registra gasto com mensagem natural
- [ ] Bot categoriza automaticamente (regex + IA)
- [ ] Comando `/resumo` mostra gastos do mês
- [ ] Comando `/ajuda` funcional
- [ ] Deploy em produção funcionando

### Features Essenciais (Alta Prioridade)
- [ ] Comando `/relatorio` com detalhes
- [ ] Comando `/categoria [X]` para filtrar
- [ ] Comando `/editar` para corrigir gastos
- [ ] Comparativo entre meses
- [ ] Histórico de gastos recentes

### Polish (Se houver tempo)
- [ ] Testes automatizados
- [ ] Documentação completa no README
- [ ] Gráficos/visualizações (se possível)
- [ ] Notificações de gastos altos
- [ ] Export de dados (CSV/Excel)

---

## 🚨 Riscos & Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Groq API instável | Média | Alto | Sempre ter regex como fallback |
| Deploy complicado | Alta | Médio | Reservar dia inteiro (dia 5) |
| Regex não funciona bem | Alta | Médio | Priorizar integração com IA desde dia 3 |
| Supabase free tier limites | Baixa | Alto | Monitorar uso, ter plano B (SQLite) |
| Tempo insuficiente | Média | Alto | Focar no MVP dias 1-3, features opcionais depois |

---

## 💡 Dicas de Colaboração

1. **Daily Sync (15min/dia)**
   - O que fiz ontem?
   - O que farei hoje?
   - Algum bloqueio?

2. **Comunicação**
   - Usar issues do GitHub para bugs
   - PRs pequenos e frequentes
   - Code review rápido (max 1h)

3. **Git Workflow**
   - Branch `main` sempre deployável
   - Feature branches: `feature/comando-resumo`
   - Commits descritivos: "feat: adiciona comando /resumo"

4. **Integração Contínua**
   - Luigi finaliza service → avisa Kayke
   - Kayke testa handler → feedback para Luigi
   - Integrar no mesmo dia para evitar acúmulo

---

## 📈 Métricas de Sucesso

- ✅ Bot responde em <2s para mensagens normais
- ✅ Bot responde em <5s quando usa IA (Groq)
- ✅ 90%+ de mensagens categorizadas corretamente
- ✅ Zero crashes em produção
- ✅ 3+ usuários testam e aprovam

---

## 📚 Recursos Úteis

- [python-telegram-bot docs](https://docs.python-telegram-bot.org/)
- [FastAPI docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 docs](https://docs.sqlalchemy.org/)
- [Groq API docs](https://console.groq.com/docs)
- [Supabase docs](https://supabase.com/docs)
- [Railway docs](https://docs.railway.app/)

---

**Boa sorte, Luigi e Kayke! 🚀🎉**

*Última atualização: 14/10/2025*

