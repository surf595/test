from telegram import InlineKeyboardButton, InlineKeyboardMarkup

MODE_TITLES = {"analytic": "Аналитический", "diagnostic": "Диагностический", "supportive": "Поддерживающий", "general": "Общий"}
TONE_TITLES = {"attuned": "Чуткий", "neutral": "Нейтральный", "structured": "Структурный", "warm": "Тёплый"}
DEPTH_TITLES = {"brief": "Кратко", "medium": "Средне", "deep": "Глубоко"}
DOMAIN_SCOPE_TITLES = {
    "all": "Вся библиотека",
    "pdm": "Только PDM",
    "group_analysis": "Только группанализ",
    "diagnosis": "Только диагностика",
}
STYLE_TITLES = {
    "clinical": "Клинический",
    "human": "Человеческий",
    "educational": "Учебный",
    "supervisory": "Супервизионный",
}
CITATION_TITLES = {
    "sources": "С источниками",
    "minimal": "Минимально",
    "none": "Без источников",
}
LANGUAGE_TITLES = {"auto": "Авто", "ru": "Русский", "en": "Английский"}
VERBOSITY_TITLES = {"brief": "Кратко", "medium": "Средне", "detailed": "Подробно"}


def render_profile(user_row) -> str:
    return (
        "Текущие настройки:\n"
        f"• режим: {MODE_TITLES.get(user_row['mode'], user_row['mode'])}\n"
        f"• тон: {TONE_TITLES.get(user_row['tone'], user_row['tone'])}\n"
        f"• глубина: {DEPTH_TITLES.get(user_row['depth'], user_row['depth'])}\n"
        f"• стиль: {STYLE_TITLES.get(user_row['response_style'], user_row['response_style'])}\n"
        f"• цитирование: {CITATION_TITLES.get(user_row['citation_mode'], user_row['citation_mode'])}\n"
        f"• область поиска: {DOMAIN_SCOPE_TITLES.get(user_row['domain_scope'], user_row['domain_scope'])}\n"
        f"• язык: {LANGUAGE_TITLES.get(user_row['language_pref'], user_row['language_pref'])}\n"
        f"• детализация: {VERBOSITY_TITLES.get(user_row['verbosity'], user_row['verbosity'])}\n"
        f"• источники: {'вкл' if int(user_row['sources_enabled']) == 1 else 'выкл'}\n"
        f"• отладка: {'вкл' if int(user_row['debug_enabled']) == 1 else 'выкл'}\n"
    )


def mode_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Аналитический", callback_data="mode:analytic"), InlineKeyboardButton("Диагностический", callback_data="mode:diagnostic")],
        [InlineKeyboardButton("Поддерживающий", callback_data="mode:supportive"), InlineKeyboardButton("Общий", callback_data="mode:general")],
    ])


def tone_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Чуткий", callback_data="tone:attuned"), InlineKeyboardButton("Нейтральный", callback_data="tone:neutral")],
        [InlineKeyboardButton("Структурный", callback_data="tone:structured"), InlineKeyboardButton("Тёплый", callback_data="tone:warm")],
    ])


def depth_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("Кратко", callback_data="depth:brief"), InlineKeyboardButton("Средне", callback_data="depth:medium"), InlineKeyboardButton("Глубоко", callback_data="depth:deep")]])
