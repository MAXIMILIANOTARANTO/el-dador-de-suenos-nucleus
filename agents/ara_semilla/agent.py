# agents/ara_semilla/agent.py

from typing import Dict, Any
import datetime

class AraSemilla:
    def __init__(self):
        self.runa = "731"
        self.nombre = "Ara Semilla"
        self.estado = "Activo"
        self.memoria_path = "agents/ara_semilla/memory/PERSISTENT_MEMORY_731.md"
        self.creado = datetime.datetime.now().isoformat()

    def activar(self):
        print(f"[Ara Semilla] Agente activado con runa {self.runa}")
        return True

    def get_estado(self) -> Dict[str, Any]:
        return {
            "nombre": self.nombre,
            "runa": self.runa,
            "estado": self.estado,
            "creado": self.creado
        }