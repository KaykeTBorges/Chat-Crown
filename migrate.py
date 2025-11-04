from services.database import db_manager

print("🔧 Testando criação de tabelas...")

# Testar conexão
if db_manager.test_connection():
    print("✅ Conexão com banco OK")
else:
    print("❌ Erro na conexão")
    exit()

# Criar tabelas
if db_manager.create_tables():
    print("✅ create_tables() retornou True")
else:
    print("❌ create_tables() retornou False")

print("🎯 Verifique manualmente no Supabase se as tabelas aparecem!")