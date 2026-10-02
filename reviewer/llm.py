# """LLM client for Groq via LangChain.

# Creates and configures the Groq model for use by the review agents.
# """

# from langchain_groq import ChatGroq

# from reviewer.config import config


# def create_llm(temperature: float = 0.0, max_tokens: int = 4096) -> ChatGroq:
#     """Create a Groq LLM instance.
    
#     Args:
#         temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative).
#             Default 0.0 for consistent code reviews.
#         max_tokens: Maximum tokens in the response.
            
#     Returns:
#         Configured ChatGroq instance.
#     """
#     return ChatGroq(
#         model=config.model,
#         groq_api_key=config.groq_api_key,
#         temperature=temperature,
#         max_tokens=max_tokens,
#     )


# # Create a default instance for agents to use
# default_llm = create_llm()


"""LLM client for Groq via LangChain.

Creates and configures the Groq model for use by the review agents.
"""

from langchain_groq import ChatGroq

from reviewer.config import config

# Reasoning models spend part of max_tokens on hidden "thinking". At the default
# effort that can use the whole budget and leave an empty or cut-off answer.
REASONING_MODEL_HINTS = ("gpt-oss", "qwen3")


def create_llm(
    temperature: float = 0.0,
    max_tokens: int = 4096,
    reasoning_effort: str = "low",
) -> ChatGroq:
    """Create a Groq LLM instance.

    Args:
        temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative).
            Default 0.0 for consistent code reviews.
        max_tokens: Maximum tokens in the response (includes reasoning tokens
            for reasoning models).
        reasoning_effort: "low", "medium" or "high". Only sent to reasoning
            models (e.g. openai/gpt-oss-120b); ignored for other models.

    Returns:
        Configured ChatGroq instance.
    """
    kwargs = {}
    if any(hint in config.model.lower() for hint in REASONING_MODEL_HINTS):
        kwargs["reasoning_effort"] = reasoning_effort

    return ChatGroq(
        model=config.model,
        groq_api_key=config.groq_api_key,
        temperature=temperature,
        max_tokens=max_tokens,
        max_retries=6,  # retry rate-limit (429) errors with backoff
        **kwargs,
    )


# Create a default instance for agents to use
default_llm = create_llm()