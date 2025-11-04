# Chat Crown - Finance Control Bot for Telegram.

## Resumo do Projeto
Bot de Telegram para controle financeiro pessoal onde usuários podem registrar seus gastos através de mensagens naturais. O bot utiliza IA para categorizar automaticamente os gastos e gera relatórios mensais detalhados.

### Exemplo de uso
```bash
Usuário: "50 almoco"
Bot: ✅ Registrado: R$ 50,00 em Alimentação

Usuário: /resumo
Bot: 📊 Você gastou R$ 1.234,00 este mês
     • Alimentação: R$ 450,00 (36%)
     • Transporte: R$ 320,00 (26%)
     ...
```

## Arquitetura
```bash
┌─────────────┐
│   Usuário   │
│  (Telegram) │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│        Telegram Bot API             │
│    (Webhook/Polling Handler)        │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│         FastAPI Backend             │
│  ┌─────────────────────────────┐    │
│  │  Bot Handlers & Commands    │    │
│  └────────┬────────────────────┘    │
│           │                         │
│  ┌────────▼────────────────────┐    │
│  │    Business Services        │    │
│  │  • User Service             │    │
│  │  • Expense Service          │    │
│  │  • AI Processor             │    │
│  │  • Report Generator         │    │
│  └────────┬────────────────────┘    │
│           │                         │
│  ┌────────▼────────────────────┐    │
│  │    Database Layer           │    │
│  │  (SQLAlchemy ORM)           │    │
│  └────────┬────────────────────┘    │
└───────────┼─────────────────────────┘
            │
            ▼
   ┌────────────────┐      ┌──────────────┐
   │  PostgreSQL    │      │   Groq API   │
   │   (Supabase)   │      │  (IA/LLM)    │
   └────────────────┘      └──────────────┘
```

## Fluxo de Dados
1. Registro de uma saída
```bash 
Usuário envia: "50 almoco"
       ↓
Telegram Bot recebe mensagem
       ↓
Handler identifica como gasto (não é comando)
       ↓
AI Processor analisa:
  → Tenta regex primeiro (rápido, grátis)
  → Se falhar, usa Groq API (IA)
       ↓
Extrai: {valor: 50, categoria: "Alimentação", descrição: "almoco"}
       ↓
Expense Service salva no banco
       ↓
Bot responde: "✅ Registrado: R$ 50,00 em Alimentação"
```

2. Consulta de dados
```bash
Usuário: /resumo
       ↓
Command Handler processa
       ↓
Report Service:
  → Busca gastos do mês no banco
  → Agrupa por categoria
  → Calcula totais e percentuais
       ↓
Formatter formata mensagem bonita
       ↓
Bot envia relatório formatado
```

## 🛠️ Stack Tecnológica
- Backend
    - Linguagem: Python 3.11+
    - Framework: FastAPI 0.104+
- Bot
    - Biblioteca: python-telegram-bot 20.7+
- Banco de Dados
    - SGBD: PostgreSQL 15+
    - ORM: SQLAlchemy 2.0+
    - Hosting: Supabase (free tier)
- Processamento da mensagem: 
    - Regex + Keywords
    - Fallback: IA (Groq API)
- Infraestrutura
    - Hospedagem: Railway (free tier)
    - CI/CD com github
