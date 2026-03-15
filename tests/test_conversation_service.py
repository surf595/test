import unittest
from types import ModuleType
from unittest.mock import patch


def _fake_dotenv_module() -> ModuleType:
    module = ModuleType("dotenv")

    def load_dotenv(*args, **kwargs):
        return True

    module.load_dotenv = load_dotenv
    return module


def _fake_openai_module() -> ModuleType:
    module = ModuleType("openai")

    class OpenAI:
        def __init__(self, *args, **kwargs):
            pass

    module.OpenAI = OpenAI
    return module


def _fake_qdrant_module() -> ModuleType:
    module = ModuleType("qdrant_client")

    class QdrantClient:
        def __init__(self, *args, **kwargs):
            pass

    module.QdrantClient = QdrantClient
    return module


def _fake_qdrant_models_module() -> ModuleType:
    module = ModuleType("qdrant_client.models")

    class Distance:
        COSINE = "Cosine"

    class VectorParams:
        def __init__(self, *args, **kwargs):
            pass

    module.Distance = Distance
    module.VectorParams = VectorParams
    return module


class ConversationServiceTests(unittest.TestCase):
    def test_build_assistant_reply_graceful_on_generation_error(self):
        user_row = {
            "domain_scope": "all",
            "sources_enabled": 1,
            "debug_enabled": 1,
        }

        with patch.dict(
            "sys.modules",
            {
                "dotenv": _fake_dotenv_module(),
                "openai": _fake_openai_module(),
                "qdrant_client": _fake_qdrant_module(),
                "qdrant_client.models": _fake_qdrant_models_module(),
            },
        ):
            from pdm_bot.app.services import conversation_service

            with patch.object(conversation_service, "save_message") as save_mock, patch.object(
                conversation_service, "get_user_row", return_value=user_row
            ), patch.object(conversation_service, "_history_for_chat", return_value=[]), patch.object(
                conversation_service, "retrieve_context_safe", return_value=([], False)
            ), patch.object(conversation_service, "build_context_and_sources", return_value=("", [])), patch.object(
                conversation_service, "build_system_prompt", return_value="system"
            ), patch.object(conversation_service, "ask_llm", side_effect=RuntimeError("llm down")):
                answer = conversation_service.build_assistant_reply("chat-1", "вопрос", 3, 5)

        self.assertIn("не удалось сформировать полноценный ответ", answer)
        self.assertIn("generation=ошибка", answer)
        self.assertGreaterEqual(save_mock.call_count, 2)


if __name__ == "__main__":
    unittest.main()
