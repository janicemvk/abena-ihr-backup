from main_orchestrator import IntelligenceLayer

try:
    il = IntelligenceLayer()
    print("Database engine created successfully:", il.engine)
except Exception as e:
    print(f"❌ Error creating database engine: {e}") 