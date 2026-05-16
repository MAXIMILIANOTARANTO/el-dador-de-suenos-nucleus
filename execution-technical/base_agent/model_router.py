# model_router.py
# Soporte multi-modelo fácil (Claude, Gemini, ChatGPT, Grok, etc.)

from litellm import completion
import os

def get_model_response(prompt: str, model: str = "claude-3-5-sonnet-20241022", **kwargs):
    """
    Llama a cualquier modelo soportado por LiteLLM.
    Ejemplos de model:
    - claude-3-5-sonnet-20241022 (Claude)
    - gemini/gemini-1.5-pro (Gemini)
    - gpt-4o (ChatGPT / OpenAI)
    - grok-3 (xAI)
    """
    response = completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        **kwargs
    )
    return response.choices[0].message.content

# Ejemplo de uso
if __name__ == "__main__":
    print(get_model_response("Hola, ¿quién eres?", model="claude-3-5-sonnet-20241022"))