    # 💡 IDEA.md — The Chat Crown Project

    This document provides a complete vision, architecture, feature set, and development guide for the **Chat Crown** project.

    ---

    ## 🎯 Project Vision

    **Chat Crown** is a comprehensive personal finance management system designed for simplicity and power. It bridges the convenience of a Telegram bot with the depth of a full-featured web dashboard, allowing users to effortlessly track expenses, set financial goals, and gain deep insights into their financial health.

    The project is built around the philosophy that financial management should be accessible, automated, and insightful, integrating seamlessly into a user's daily life.

    ---

    ## 🧱 Core Components & Architecture

    The system is composed of four main components that work together to deliver a cohesive experience.

    1.  **Telegram Bot**: The primary point of interaction for quick, on-the-go financial logging. Users can register transactions, request summaries, and manage their data using natural language and simple commands.

    2.  **Streamlit Web App**: A powerful dashboard for deep dives into financial data. It provides visualizations, detailed reports, goal tracking, and advanced transaction management.

    3.  **FastAPI Backend**: The central nervous system of the project. It handles all business logic, data persistence, and serves as the secure bridge for authentication between the bot and the web app.

    4.  **Database**: The single source of truth for all user data, built with SQLAlchemy for flexibility and scalability.

    ### Architecture Diagram

    ```
    +-------------+      +-----------------+      +-----------------+      +--------------+
    |             |      |                 |      |                 |      |              |
    | Telegram Bot| <--> |  FastAPI Backend| <--> |   Database      |      |   Streamlit  |
    |             |      |   (Services)    |      |   (SQLAlchemy)  |      |   Web App    |
    |             |      |                 |      |                 |      |              |
    +-------------+      +--------+--------+      +-----------------+      +--------------+
                                |
                                | (Secure Token Validation)
                                |
                                v
                        +-----------------+
                        |                 |
                        |   Session Mgmt   |
                        | (Redis / File)  |
                        |                 |
                        +-----------------+
    ```

    ---

    ## 🔐 Authentication & Security

    Security and user convenience are paramount. The project uses a **Magic Link authentication flow** initiated via the Telegram Bot.

    ### Authentication Flow

    1.  **Initiation**: The user types `/login` in the Telegram Bot.
    2.  **Code Generation**: The Bot calls the FastAPI backend (`/auth/generate_code`) to generate a unique, one-time-use 6-digit code associated with the user's `telegram_id`.
    3.  **Code Delivery**: The Bot sends the code to the user with a link to the Streamlit web app.
    4.  **Token Exchange**: The user navigates to the web app and enters the 6-digit code.
    5.  **Validation**: The Streamlit app sends the code to the backend (`/auth/validate_code`). The backend validates the code, retrieves the associated `telegram_id`, and invalidates the code.
    6.  **Session Creation**: Upon successful validation, a secure session is created in Streamlit using `st.session_state`, storing the `telegram_id`. The user is now logged in.

    **Key Security Principle**: The primary identifier for all data is the `telegram_id`, which is guaranteed to be unique and verified by Telegram. No passwords are ever stored or used.

    ---

    ## 🛠️ Technology Stack

    *   **Backend**: Python 3.10+, FastAPI, Uvicorn
    *   **Frontend**: Streamlit
    *   **Bot Framework**: `python-telegram-bot`
    *   **Database**: SQLAlchemy ORM (compatible with PostgreSQL, SQLite, etc.)
    *   **Package Management**: `uv` for fast and reliable dependency management.
    *   **Development**: Monorepo structure for unified dependency management and code sharing.

    ---

    ## 🗂️ Project Structure

    The project follows a clean, modular monorepo structure.

    ```
    chat-crown/
    │
    ├── .env                           # Environment variables (secrets)
    ├── pyproject.toml                  # Project metadata and dependencies (uv)
    │
    ├── api/                           # FastAPI Backend
    │   └── main.py                     # API endpoints for auth and future services
    │
    ├── bot/                            # Telegram Bot
    │   ├── bot.py                      # Main bot application and handler registration
    │   └── handlers/                   # Command and callback logic
    │       ├── start_handler.py
    │       ├── login_handler.py
    │       ├── message_handler.py
    │       ├── list_handler.py
    │       ├── edit_handler.py
    │       ├── delete_handler.py
    │       └── ...
    │
    ├── streamlit_app/                  # Streamlit Web Application
    │   ├── app.py                      # Main entry point, navigation, and auth logic
    │   ├── pages/                      # Multi-page application files
    │   │   ├── 0_🚀_Início_Rápido.py
    │   │   ├── 1_📊_Dashboard.py
    │   │   └── ...
    │   └── utils.py                    # Shared utilities (e.g., auth check)
    │
    ├── services/                       # Business Logic Layer
    │   ├── users_service.py
    │   ├── transactions_service.py
    │   ├── goals_service.py
    │   ├── budget_service.py
    │   ├── finance_calculator.py
    │   └── database.py                 # Database connection and session management
    │
    ├── models/                         # SQLAlchemy Database Models
    │   ├── base.py
    │   ├── user.py
    │   ├── transaction.py
    │   ├── goal.py
    │   └── budget.py
    │
    └── config/
        └── config.py                   # Configuration management from .env
    ```

    ---

    ## 📊 Database Schema

    The database is designed around the `User` model, with all user-specific data linked by `telegram_id`.

    *   **`User`**: Stores user information from Telegram (`telegram_id`, `username`, `first_name`).
    *   **`Transaction`**: Core financial data. Each transaction is linked to a `User` via `telegram_id`.
    *   **`FinancialGoal`**: User-defined savings goals, linked by `telegram_id`.
    *   **`Budget`**: Monthly spending limits per category, linked by `telegram_id`.

    All foreign keys in `Transaction`, `FinancialGoal`, and `Budget` tables reference `users.telegram_id`.

    ---

    ## ✨ Key Features

    ### Telegram Bot Features
    *   **Natural Language Parsing**: Register transactions by simply typing "lunch 25.50".
    *   **Smart Categorization**: AI-powered (or rule-based) transaction categorization.
    *   **Quick Summaries**: Get a monthly financial summary with the `/resumo` command.
    *   **Full CRUD**: List, edit, and delete transactions directly within the chat using an inline keyboard.
    *   **Secure Login**: Generate one-time codes to access the web dashboard.

    ### Streamlit Web App Features
    *   **Interactive Dashboard**: Visualize income, expenses, and savings with charts and metrics.
    *   **Daily Budget Control (Breno Method)**: Track daily spending against calculated limits.
    *   **Goal Management**: Set, track, and visualize progress towards financial goals.
    *   **Budget Tracking**: Define and monitor monthly budgets per category.
    *   **Detailed Reporting**: Generate in-depth reports and analyze spending patterns.
    *   **Transaction Management**: Full CRUD interface for managing the transaction history.

    ---

    ## 🚀 Development Guide

    ### Setup

    1.  **Clone the repository**.
    2.  **Install dependencies** using `uv`:
        ```bash
        uv sync
        ```
    3.  **Configure environment** by creating a `.env` file with the necessary tokens and URLs (see `config/config.py`).
    4.  **Run all services** with a single command:
        ```bash
        uv run start.py
        ```
        This script will launch both the FastAPI backend and the Streamlit app.

    ### Code Standards

    *   **Architecture**: A clear layered architecture (UI -> Handlers -> Services -> Models -> DB) is enforced. The UI layer (Bot/Streamlit) never interacts directly with the database.
    *   **Identifier**: All user-specific data operations must use `telegram_id` as the primary key.
    *   **Services**: All business logic resides in the `services/` directory.

    ---

    ## 🗺️ Future Roadmap

    *   **Real-time Webhooks**: Replace long-polling with webhooks for instant bot responses and notifications.
    *   **Advanced AI Insights**: Implement machine learning models to provide predictive spending analysis and personalized financial advice.
    *   **Investment Portfolio Tracking**: Add functionality to track stocks, crypto, and other investments.
    *   **Mobile Application**: Develop a native mobile app (React Native/Flutter) for an enhanced on-the-go experience.
    *   **Multi-currency Support**: Enable users to manage finances in different currencies.
    *   **Export & Integrations**: Allow data export to formats like OFX and integrate with external accounting software.

    ---

    This document serves as the definitive guide for the Chat Crown project, ensuring all contributors have a clear understanding of its vision, architecture, and goals.