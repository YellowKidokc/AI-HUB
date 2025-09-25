from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence


@dataclass(slots=True)
class Prompt:
    name: str
    system: str
    prefix: str
    suffix: str
    replace: bool
    temperature: float = 0.2

    def build_message(self, text: str) -> str:
        return f"{self.prefix}{text}{self.suffix}"


def default_prompts() -> Sequence[Prompt]:
    return (
        Prompt(
            name="Fix spelling & grammar",
            system="You are an English spelling corrector and grammar improver. Reply ONLY with the corrected text—no explanations.",
            prefix="Correct the spelling (American English) and grammar of the following:\n\n",
            suffix="",
            replace=True,
            temperature=0.0,
        ),
        Prompt(
            name="Rewrite for clarity",
            system="",
            prefix="Improve the writing for clarity and conciseness and correct spelling and grammar:\n\n",
            suffix="",
            replace=True,
        ),
        Prompt(
            name="Make shorter",
            system="",
            prefix="Make the following shorter while preserving meaning:\n\n",
            suffix="",
            replace=True,
        ),
        Prompt(
            name="Make longer",
            system="",
            prefix="Expand the following text with more detail while staying on-topic:\n\n",
            suffix="",
            replace=True,
            temperature=0.7,
        ),
        Prompt(
            name="More professional",
            system="",
            prefix="Rewrite the following to sound professional and polished:\n\n",
            suffix="",
            replace=True,
        ),
        Prompt(
            name="Simplify language",
            system="",
            prefix="Simplify the language of the following text so it is accessible to a wide audience:\n\n",
            suffix="",
            replace=True,
        ),
        Prompt(
            name="Proofread (bullet suggestions)",
            system="You are an English proofreader. Review the text and return a detailed bullet list of issues and suggested fixes with reasons.",
            prefix="My text is the following:\n\n",
            suffix="",
            replace=False,
            temperature=0.0,
        ),
        Prompt(
            name="Summarize",
            system="",
            prefix="Summarize the following text:\n\n",
            suffix="",
            replace=False,
        ),
        Prompt(
            name="Explain",
            system="",
            prefix="Explain the following text in simple terms:\n\n",
            suffix="",
            replace=False,
        ),
        Prompt(
            name="Find action items",
            system="",
            prefix="Identify any action items in the following text and present them as bullet points after a one-sentence summary:\n\n",
            suffix="",
            replace=False,
        ),
        Prompt(
            name="Code – Optimize",
            system="You are an assistant to a software engineer. Given code, optimize for time and space complexity and explain the changes.",
            prefix="Improve and explain how to optimize the following code:\n\n",
            suffix="",
            replace=False,
        ),
    )
