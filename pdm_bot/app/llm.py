from typing import List, Optional

from openai import OpenAI

from .config import OPENAI_API_KEY, OPENAI_CHAT_MODEL, OPENAI_EMBED_MODEL

client: Optional[OpenAI] = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def require_client() -> OpenAI:
    if client is None:
        raise RuntimeError("OpenAI client не инициализирован")
    return client


def embedding_for_text(text: str) -> List[float]:
    response = require_client().embeddings.create(model=OPENAI_EMBED_MODEL, input=text)
    return response.data[0].embedding


def embeddings_for_texts(texts: List[str]) -> List[List[float]]:
    response = require_client().embeddings.create(model=OPENAI_EMBED_MODEL, input=texts)
    return [item.embedding for item in response.data]


def ask_llm(system_prompt: str, context_block: str, history_messages: List[dict], user_text: str) -> str:
    context_message = (
        "Ниже релевантные фрагменты библиотеки:\n\n" + context_block
        if context_block.strip()
        else "Релевантный контекст из библиотеки не найден."
    )

    messages = [{"role": "system", "content": system_prompt}, {"role": "system", "content": context_message}]
    messages.extend(history_messages)
    messages.append({"role": "user", "content": user_text})

    completion = require_client().chat.completions.create(
        model=OPENAI_CHAT_MODEL,
        temperature=0.5,
        messages=messages,
    )
    text = completion.choices[0].message.content or ""
    return text.strip() or "Не удалось сформировать ответ."
