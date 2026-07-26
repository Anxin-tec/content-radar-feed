from __future__ import annotations

import re


STRONG_TERMS = (
    "人工智能",
    "生成式ai",
    "aigc",
    "大模型",
    "chatgpt",
    "openai",
    "anthropic",
    "claude",
    "gemini",
    "deepseek",
    "gpt-",
    "llama",
    "mistral",
    "copilot",
    "cursor",
    "sora",
    "智能体",
    "ai agent",
    "机器学习",
    "多模态",
    "推理模型",
)
CONTEXT_TERMS = (
    "英伟达",
    "nvidia",
    "gpu",
    "算力",
    "机器人",
    "自动驾驶",
)
AI_TOKEN = re.compile(r"(?i)(?:^|[^a-z])ai(?:$|[^a-z])")


def is_ai_related(title: str) -> bool:
    normalized = title.casefold()
    return (
        any(term in normalized for term in STRONG_TERMS)
        or bool(AI_TOKEN.search(normalized))
        or any(term in normalized for term in CONTEXT_TERMS)
    )
