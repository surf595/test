import unittest
from types import ModuleType
from unittest.mock import patch


def _fake_qdrant_module() -> ModuleType:
    module = ModuleType("qdrant_client")

    class FakeQdrantClient:
        def __init__(self, *args, **kwargs):
            pass

    module.QdrantClient = FakeQdrantClient
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


def _fake_openai_module() -> ModuleType:
    module = ModuleType("openai")

    class OpenAI:
        def __init__(self, *args, **kwargs):
            pass

    module.OpenAI = OpenAI
    return module


def _fake_dotenv_module() -> ModuleType:
    module = ModuleType("dotenv")

    def load_dotenv(*args, **kwargs):
        return True

    module.load_dotenv = load_dotenv
    return module


class RetrievalTests(unittest.TestCase):
    def test_keyword_score_has_positive_intersection(self):
        with patch.dict(
            "sys.modules",
            {
                "qdrant_client": _fake_qdrant_module(),
                "qdrant_client.models": _fake_qdrant_models_module(),
                "openai": _fake_openai_module(),
                "dotenv": _fake_dotenv_module(),
            },
        ):
            from pdm_bot.app.retrieval import keyword_score

            score = keyword_score("психодинамический конфликт", "Конфликт в психодинамической модели")
            self.assertGreater(score, 0)


    def test_hybrid_score_combines_vector_and_keyword(self):
        with patch.dict(
            "sys.modules",
            {
                "qdrant_client": _fake_qdrant_module(),
                "qdrant_client.models": _fake_qdrant_models_module(),
                "openai": _fake_openai_module(),
                "dotenv": _fake_dotenv_module(),
            },
        ):
            from pdm_bot.app.retrieval import hybrid_score

            self.assertAlmostEqual(hybrid_score(0.8, 0.2), 0.65)


    def test_normalize_scope_basic(self):
        with patch.dict(
            "sys.modules",
            {
                "qdrant_client": _fake_qdrant_module(),
                "qdrant_client.models": _fake_qdrant_models_module(),
                "openai": _fake_openai_module(),
                "dotenv": _fake_dotenv_module(),
            },
        ):
            from pdm_bot.app.retrieval import normalize_scope

            self.assertEqual(normalize_scope("Group Analysis!!!"), "group_analysis")

    def test_unknown_scope_falls_back_to_all(self):
        with patch.dict(
            "sys.modules",
            {
                "qdrant_client": _fake_qdrant_module(),
                "qdrant_client.models": _fake_qdrant_models_module(),
                "openai": _fake_openai_module(),
                "dotenv": _fake_dotenv_module(),
            },
        ):
            from pdm_bot.app.retrieval import matches_domain_scope

            payload = {"corpus": "anything"}
            self.assertTrue(matches_domain_scope("unknown_scope", payload))

    def test_domain_scope_matching_is_strict_and_alias_based(self):
        with patch.dict(
            "sys.modules",
            {
                "qdrant_client": _fake_qdrant_module(),
                "qdrant_client.models": _fake_qdrant_models_module(),
                "openai": _fake_openai_module(),
                "dotenv": _fake_dotenv_module(),
            },
        ):
            from pdm_bot.app.retrieval import matches_domain_scope

            payload = {
                "corpus": "group-analysis",
                "section": "group analysis",
                "doc_type": "pdf",
                "source_name": "Group Analysis Basics",
            }
            self.assertTrue(matches_domain_scope("group_analysis", payload))
            self.assertFalse(matches_domain_scope("diagnosis", payload))


if __name__ == "__main__":
    unittest.main()
