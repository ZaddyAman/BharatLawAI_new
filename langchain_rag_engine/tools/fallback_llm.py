# tools/fallback_llm.py

import os
import asyncio
import functools
from typing import List, Dict
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

async def fallback_llm_response(query: str, history: List[Dict[str, str]]) -> str:
    """
    Fallback LLM with Grok-style humor and memory support.
    """
    prompt = f"""You are a legal assistant with the personality of Grok. You are witty, sarcastic, and humorous. A user has asked a legal question that is outside the scope of your document database.

Answer the following legal question using your general knowledge of Indian law, but make it clear that you are not consulting specific, verified documents for this answer. Maintain your signature wit.

**User's Question:** {query}
**Your Answer:**"""

    messages = history + [{"role": "user", "content": prompt}]

    loop = asyncio.get_event_loop()
    chat_completion = await loop.run_in_executor(
        None, functools.partial(
            client.chat.completions.create,
            messages=messages,
            model="llama3-8b-8192",
        )
    )

    return chat_completion.choices[0].message.content
