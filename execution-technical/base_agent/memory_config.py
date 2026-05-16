# memory_config.py
# Configuración base de memoria persistente (Mem0 style)

try:
    from mem0 import Memory
except ImportError:
    Memory = None

def get_memory_client(user_id: str = "dador_de_suenos"):
    if Memory is None:
        print("Mem0 no instalado. Usando memoria simple en memoria.")
        return None
    
    config = {
        "vector_store": {
            "provider": "chroma",
            "config": {
                "collection_name": "dador_suenos_memoria",
                "path": "./chroma_db"
            }
        }
    }
    m = Memory.from_config(config)
    return m

# Uso básico
# memory = get_memory_client()
# memory.add("El usuario ama el símbolo del Vórtice", user_id="dador_de_suenos")