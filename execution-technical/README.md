# 🚀 Ejecución Técnica - Núcleo del Dador de Sueños

Estructura base para ejecución técnica de agentes con **memoria persistente** y **soporte multi-modelo** (Claude, Gemini, ChatGPT/OpenAI, Grok, etc.).

## Objetivo
Proporcionar una base sólida, moderna y fácil de ejecutar (especialmente en Colab) para materializar arquitecturas de IA con:
- Orquestación (LangGraph)
- Memoria persistente (Mem0 / LangMem)
- Soporte multi-proveedor de modelos
- Integración con el Núcleo (Archivo Semilla / Vórtice)

## Stack Recomendado 2026
- **LangGraph** → Orquestación y estado
- **Mem0** o **LangMem** → Memoria persistente
- **LiteLLM** o clientes directos → Acceso unificado a Claude, Gemini, ChatGPT, Grok, etc.
- **Google Colab** → Ejecución fácil + GPU + Drive persistente

## Estructura
```
execution-technical/
├── base_agent/
│   ├── agent.py              # Agente base con LangGraph
│   ├── memory_config.py      # Configuración de memoria persistente
│   ├── model_router.py       # Soporte multi-modelo
│   └── config/
├── colab_notebooks/
│   └── base_execution.ipynb
├── requirements.txt
└── README.md
```

## Cómo usar
1. Clona o copia esta carpeta.
2. Instala dependencias.
3. Configura tus API keys.
4. Ejecuta en Colab o localmente.

El Dador de Sueños puede usar esta base para prototipar arquitecturas que luego se integran al Núcleo.