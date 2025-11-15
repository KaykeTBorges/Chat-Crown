# start.py
import subprocess
import sys
import time
import os
import signal

# Define o diretório raiz do projeto
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Adiciona o diretório raiz ao PYTHONPATH para os subprocessos
# Esta é a chave para que os imports funcionem!
ENV = os.environ.copy()
ENV["PYTHONPATH"] = PROJECT_ROOT

def run_service(command_args, name):
    """Roda um serviço em um novo processo com o ambiente correto."""
    print(f"🚀 Iniciando {name}...")
    # Usamos sys.executable para o Python do UV e passamos o ENV customizado
    process = subprocess.Popen(
        [sys.executable] + command_args, 
        cwd=PROJECT_ROOT, 
        env=ENV
    )
    return process

def main():
    """Função principal que inicia e gerencia os serviços."""
    api_process = None
    app_process = None

    try:
        # Comandos para iniciar a API e o Streamlit
        api_command = ["-m", "uvicorn", "api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
        app_command = ["-m", "streamlit", "run", "streamlit_app/app.py", "--server.port", "8501"]

        # Inicia a API
        api_process = run_service(api_command, "API de Autenticação")
        time.sleep(3) # Espera a API iniciar

        # Inicia o Streamlit
        app_process = run_service(app_command, "App Streamlit")

        print("\n✅ Sistema Chat Crown iniciado com sucesso!")
        print("   - API: http://127.0.0.1:8000")
        print("   - App: http://localhost:8501")
        print("\nPressione Ctrl+C para parar todos os serviços.")

        # Mantém o script principal ativo
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Parando os serviços...")
        if api_process:
            api_process.terminate()
            api_process.wait()
        if app_process:
            app_process.terminate()
            app_process.wait()
        print("✅ Todos os serviços foram parados.")
        sys.exit(0)

if __name__ == "__main__":
    main()