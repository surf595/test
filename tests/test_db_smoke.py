import unittest
from types import ModuleType
from uuid import uuid4
from unittest.mock import patch


def _fake_dotenv_module() -> ModuleType:
    module = ModuleType("dotenv")

    def load_dotenv(*args, **kwargs):
        return True

    module.load_dotenv = load_dotenv
    return module


class DbSmokeTests(unittest.TestCase):
    def test_users_messages_jobs_smoke(self):
        with patch.dict("sys.modules", {"dotenv": _fake_dotenv_module()}):
            from pdm_bot.app.db import (
                create_job,
                get_recent_messages,
                get_user_row,
                init_db,
                list_jobs,
                save_message,
                update_job,
            )

            init_db()
            chat_id = f"test-{uuid4()}"

            user = get_user_row(chat_id)
            self.assertEqual(user["chat_id"], chat_id)

            save_message(chat_id, "user", "привет")
            save_message(chat_id, "assistant", "здравствуйте")
            recent = get_recent_messages(chat_id, limit=5)
            self.assertGreaterEqual(len(recent), 2)
            self.assertEqual(recent[-1]["role"], "assistant")

            job_id = create_job("full_reindex", '{"chat_id":"smoke"}')
            update_job(job_id, "done")
            jobs = list_jobs(limit=20)
            self.assertTrue(any(int(j["id"]) == job_id and j["status"] == "done" for j in jobs))


if __name__ == "__main__":
    unittest.main()
