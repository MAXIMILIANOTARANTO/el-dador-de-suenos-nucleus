# agent.py
# Agente base con LangGraph + Memoria Persistente + Multi-Modelo

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from task_coordination import AgentTaskSystem

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    memory_context: str

def call_model(state: AgentState):
    # Aquí se integraría el model_router + memoria
    last_message = state["messages"][-1]
    # Ejemplo simple
    response = f"[Dador de Sueños] Procesando: {last_message}"
    return {"messages": [response]}

def build_agent():
    workflow = StateGraph(AgentState)
    workflow.add_node("call_model", call_model)
    workflow.set_entry_point("call_model")
    workflow.add_edge("call_model", END)
    return workflow.compile()


def build_task_system(user_id: str = "default_user"):
    """Crea el sistema de agentes especializados para división y coordinación."""
    return AgentTaskSystem(user_id=user_id)

# Uso
# agent = build_agent()
# result = agent.invoke({"messages": ["Hola"]})
# print(result)