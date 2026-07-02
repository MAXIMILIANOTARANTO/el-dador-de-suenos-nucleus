import pathlib
import sys
import unittest

BASE_AGENT_PATH = pathlib.Path(__file__).resolve().parents[1] / "execution-technical" / "base_agent"
sys.path.insert(0, str(BASE_AGENT_PATH))

from task_coordination import AgentTaskSystem  # noqa: E402


class TaskCoordinationTests(unittest.TestCase):
    def test_decompose_and_assign_specialized_agents(self):
        system = AgentTaskSystem(memory_client=None, model_callable=lambda **_: "ok")
        items = system.decompose_and_assign(
            "Analizar requerimientos. Coordinar flujo principal. Implementar API. Validar resultados."
        )

        self.assertEqual(4, len(items))
        self.assertEqual("analysis", items[0].assigned_agent)
        self.assertEqual("orchestration", items[1].assigned_agent)
        self.assertEqual("execution", items[2].assigned_agent)
        self.assertEqual("validation", items[3].assigned_agent)
        self.assertTrue(items[2].dependencies)
        self.assertTrue(items[3].dependencies)

    def test_run_reports_progress_and_messages(self):
        system = AgentTaskSystem(memory_client=None, model_callable=lambda **_: "resultado correcto")
        report = system.run(
            "Analizar tarea. Coordinar subtareas. Implementar solución. Validar calidad."
        )

        self.assertEqual(4, report["progress"]["total"])
        self.assertEqual(4, report["progress"]["completed"])
        self.assertEqual(0, report["progress"]["failed"])
        self.assertTrue(any(msg["event"] == "subtask_completed" for msg in report["messages"]))

    def test_execution_error_is_reported(self):
        system = AgentTaskSystem(memory_client=None, model_callable=lambda **_: "error crítico")
        report = system.run("Implementar subtarea principal.")
        subtask = report["subtasks"][0]

        self.assertEqual("failed", subtask["status"])
        self.assertIn("inválido", subtask["error"])
        self.assertEqual(1, report["progress"]["failed"])


if __name__ == "__main__":
    unittest.main()
