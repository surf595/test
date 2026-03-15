import unittest

from pdm_bot.app.prompts import build_system_prompt, route_task_type


class PromptTests(unittest.TestCase):

    def test_route_task_type_variants(self):
        self.assertEqual(route_task_type("что такое перенос"), "definition")
        self.assertEqual(route_task_type("сравни перенос и контрперенос"), "comparison")
        self.assertEqual(route_task_type("клиент пришел с тревогой"), "clinical")
        self.assertEqual(route_task_type("назови источник и автора"), "bibliography")

    def test_build_system_prompt_smoke(self):
        row = {
            "mode": "analytic",
            "tone": "neutral",
            "depth": "medium",
            "response_style": "clinical",
            "citation_mode": "sources",
            "domain_scope": "all",
            "language_pref": "ru",
            "verbosity": "medium",
        }

        prompt = build_system_prompt(row, "что такое перенос")

        self.assertIn("психодинамически ориентированный ассистент", prompt)
        self.assertIn("Тип задачи", prompt)


if __name__ == "__main__":
    unittest.main()
