from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

MAX_TITLE_LENGTH = 60

try:
    from memory_config import get_memory_client
except ImportError:  # pragma: no cover - fallback for isolated execution
    get_memory_client = None

try:
    from model_router import get_model_response
except ImportError:  # pragma: no cover - fallback for isolated execution
    get_model_response = None


@dataclass
class TaskItem:
    id: str
    title: str
    description: str
    category: str
    priority: int = 2
    dependencies: List[str] = field(default_factory=list)
    assigned_agent: str = ""
    status: str = "pending"
    result: str = ""
    error: str = ""


class AnalysisAgent:
    name = "analysis"

    def analyze(self, task_text: str) -> List[TaskItem]:
        parts = [p.strip() for p in task_text.replace("\n", ".").split(".") if p.strip()]
        if not parts:
            parts = [task_text.strip() or "Tarea principal"]

        items: List[TaskItem] = []
        for index, part in enumerate(parts, start=1):
            category = self._categorize(part)
            dependencies = [items[-1].id] if items and category in {"execution", "validation"} else []
            items.append(
                TaskItem(
                    id=f"T{index}",
                    title=part[:MAX_TITLE_LENGTH],
                    description=part,
                    category=category,
                    dependencies=dependencies,
                )
            )
        return items

    @staticmethod
    def _categorize(text: str) -> str:
        lowered = text.lower()
        if any(word in lowered for word in ["valid", "test", "verific"]):
            return "validation"
        if any(word in lowered for word in ["coord", "orquest", "flujo", "dependenc"]):
            return "orchestration"
        if any(word in lowered for word in ["anal", "diagn", "clasific"]):
            return "analysis"
        return "execution"


class OrchestrationAgent:
    name = "orchestration"
    agent_by_category = {
        "analysis": "analysis",
        "orchestration": "orchestration",
        "execution": "execution",
        "validation": "validation",
    }

    def assign(self, items: List[TaskItem], priority_map: Optional[Dict[str, int]] = None) -> None:
        for item in items:
            item.assigned_agent = self.agent_by_category.get(item.category, "execution")
            if priority_map and item.id in priority_map:
                item.priority = priority_map[item.id]

    @staticmethod
    def next_ready(items: List[TaskItem]) -> Optional[TaskItem]:
        finished = {item.id for item in items if item.status == "completed"}
        for item in sorted(items, key=lambda current: (current.priority, current.id)):
            if item.status != "pending":
                continue
            if all(dep in finished for dep in item.dependencies):
                return item
        return None


class ExecutionAgent:
    name = "execution"

    def __init__(self, model_callable: Optional[Callable[..., str]] = None):
        self.model_callable = model_callable

    def execute(self, item: TaskItem) -> str:
        if self.model_callable is None:
            return f"[execution] Completado {item.id}: {item.description}"
        prompt = f"Materializa solución para la subtarea {item.id}: {item.description}"
        return self.model_callable(prompt=prompt)


class ValidationAgent:
    name = "validation"

    @staticmethod
    def validate(item: TaskItem, candidate_result: Optional[str] = None) -> str:
        result = item.result if candidate_result is None else candidate_result
        if not result.strip():
            raise ValueError(f"Resultado vacío para {item.id}")
        if "error" in result.lower():
            raise ValueError(f"Resultado inválido para {item.id}")
        return f"[validation] {item.id} validada"


class AgentTaskSystem:
    def __init__(
        self,
        user_id: str = "default_user",
        memory_client: Optional[Any] = None,
        model_callable: Optional[Callable[..., str]] = None,
    ):
        self.user_id = user_id
        self.analysis_agent = AnalysisAgent()
        self.orchestration_agent = OrchestrationAgent()
        self.execution_agent = ExecutionAgent(model_callable=model_callable or get_model_response)
        self.validation_agent = ValidationAgent()
        self.memory_client = memory_client
        if self.memory_client is None and get_memory_client:
            self.memory_client = get_memory_client(user_id=user_id)
        self.messages: List[Dict[str, Any]] = []

    def decompose_and_assign(self, task_text: str, priority_map: Optional[Dict[str, int]] = None) -> List[TaskItem]:
        items = self.analysis_agent.analyze(task_text)
        self.orchestration_agent.assign(items, priority_map=priority_map)
        self._report("analysis", "decomposition_ready", {"total_subtasks": len(items)})
        return items

    def execute_plan(self, items: List[TaskItem]) -> List[TaskItem]:
        while True:
            next_item = self.orchestration_agent.next_ready(items)
            if next_item is None:
                break
            self._run_item(next_item)
        return items

    def run(self, task_text: str, priority_map: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        items = self.decompose_and_assign(task_text, priority_map=priority_map)
        executed_items = self.execute_plan(items)
        return {
            "subtasks": [item.__dict__ for item in executed_items],
            "messages": self.messages,
            "progress": self.progress(executed_items),
        }

    def progress(self, items: List[TaskItem]) -> Dict[str, int]:
        total = len(items)
        completed = len([item for item in items if item.status == "completed"])
        failed = len([item for item in items if item.status == "failed"])
        return {"total": total, "completed": completed, "failed": failed}

    def _run_item(self, item: TaskItem) -> None:
        item.status = "running"
        self._report("orchestration", "subtask_started", {"task_id": item.id, "agent": item.assigned_agent})
        try:
            if item.assigned_agent == "analysis":
                item.result = f"[analysis] {item.description}"
            elif item.assigned_agent == "orchestration":
                item.result = f"[orchestration] Flujo definido para {item.id}"
            elif item.assigned_agent == "validation":
                item.result = self.validation_agent.validate(item, candidate_result=item.description)
            else:
                item.result = self.execution_agent.execute(item)
                validation = self.validation_agent.validate(item)
                self._report("validation", "subtask_validated", {"task_id": item.id, "validation": validation})

            item.status = "completed"
            self._report("orchestration", "subtask_completed", {"task_id": item.id})
            self._persist_memory(item)
        except (ValueError, RuntimeError, TypeError) as exc:
            item.error = str(exc)
            item.status = "failed"
            self._report("validation", "subtask_failed", {"task_id": item.id, "error": item.error})

    def _persist_memory(self, item: TaskItem) -> None:
        if not self.memory_client:
            return
        memory_text = f"{item.id}::{item.category}::{item.result}"
        try:
            self.memory_client.add(memory_text, user_id=self.user_id)
        except Exception:  # pragma: no cover - external provider
            self._report("analysis", "memory_warning", {"task_id": item.id, "message": "No se pudo persistir memoria"})

    def _report(self, sender: str, event: str, payload: Dict[str, Any]) -> None:
        self.messages.append(
            {
                "sender": sender,
                "event": event,
                "priority": payload.get("priority", 2),
                "payload": payload,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
