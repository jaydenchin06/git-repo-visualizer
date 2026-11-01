from typing import Optional

# Longest piece of code we'll send to the AI, to keep requests small and cheap
MAX_CODE_CHARS = 20000


def build_prompt(code: str, name: str, symbol_type: str, language: Optional[str]) -> str:
    """Builds the question we'll ask the AI about a piece of code."""
    language_name = language or "unknown language"
    return (
        f"Explain this {language_name} {symbol_type} called `{name}` to a student who is new to this codebase.\n"
        "Start with a one-sentence summary of what it does, then walk through how it works step by step, "
        "and point out anything surprising or easy to get wrong.\n\n"
        f"```{language or ''}\n{code[:MAX_CODE_CHARS]}\n```"
    )


def explain_code(code: str, name: str, symbol_type: str, language: Optional[str]) -> str:
    """
    Asks an AI to explain a piece of code.

    No AI provider is connected yet. To connect one, send build_prompt(...) to its
    API here and return the text of its reply. Read the API key from an environment
    variable (put it in backend/.env, which is gitignored) rather than in the code.

    Returns:
        The explanation as text (Markdown is fine)
    """
    prompt = build_prompt(code, name, symbol_type, language)
    return (
        "**AI isn't connected yet.**\n\n"
        "When it is, this is the question it will be asked:\n\n"
        f"{prompt}"
    )
