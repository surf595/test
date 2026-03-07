"""Backward-compatible entrypoint.

Запускает модульную версию бота из `pdm_bot.app.main`.
"""

from pdm_bot.app.main import main


if __name__ == "__main__":
    main()
