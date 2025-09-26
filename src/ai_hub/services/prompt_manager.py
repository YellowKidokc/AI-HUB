from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence


@dataclass(slots=True)
class Prompt:
    """Represents a reusable instruction snippet."""

    slug: str
    name: str
    system: str
    prefix: str
    suffix: str
    replace: bool
    temperature: float = 0.2
    order: int = 100

    def build_message(self, text: str) -> str:
        return f"{self.prefix}{text}{self.suffix}"


class PromptCatalog:
    """In-memory catalog that supports lookups by slug or index."""

    def __init__(self, prompts: Iterable[Prompt]):
        ordered = sorted(prompts, key=lambda prompt: prompt.order)
        self._prompts: list[Prompt] = ordered
        self._index: dict[str, Prompt] = {prompt.slug: prompt for prompt in ordered}

    def __iter__(self) -> Iterator[Prompt]:
        return iter(self._prompts)

    def all(self) -> list[Prompt]:
        return list(self._prompts)

    def get(self, index: int) -> Prompt:
        return self._prompts[index]

    def get_by_slug(self, slug: str) -> Prompt:
        return self._index[slug]

    def to_sequence(self) -> Sequence[Prompt]:
        return tuple(self._prompts)

    @classmethod
    def from_path(cls, path: Path | None) -> "PromptCatalog":
        if path and path.exists():
            with path.open("r", encoding="utf-8") as handle:
                raw_prompts = json.load(handle)
            prompts = [
                Prompt(
                    slug=item["slug"],
                    name=item.get("name", item["slug"].replace("_", " ").title()),
                    system=item.get("system", ""),
                    prefix=item.get("prefix", ""),
                    suffix=item.get("suffix", ""),
                    replace=bool(item.get("replace", False)),
                    temperature=float(item.get("temperature", 0.2)),
                    order=int(item.get("order", 100)),
                )
                for item in raw_prompts
            ]
            return cls(prompts)
        return cls(default_prompts())


def default_prompts() -> Sequence[Prompt]:
    return (
        Prompt(
            slug="fix",
            name="Fix spelling & grammar",
            system="You are an English spelling corrector and grammar improver. Reply ONLY with the corrected text—no explanations.",
            prefix="Correct the spelling (American English) and grammar of the following:\n\n",
            suffix="",
            replace=True,
            temperature=0.0,
            order=10,
        ),
        Prompt(
            slug="clarity",
            name="Rewrite for clarity",
            system="",
            prefix="Improve the writing for clarity and conciseness and correct spelling and grammar:\n\n",
            suffix="",
            replace=True,
            order=20,
        ),
        Prompt(
            slug="shorten",
            name="Make shorter",
            system="",
            prefix="Make the following shorter while preserving meaning:\n\n",
            suffix="",
            replace=True,
            order=30,
        ),
        Prompt(
            slug="lengthen",
            name="Make longer",
            system="",
            prefix="Expand the following text with more detail while staying on-topic:\n\n",
            suffix="",
            replace=True,
            temperature=0.7,
            order=40,
        ),
        Prompt(
            slug="professional",
            name="More professional",
            system="",
            prefix="Rewrite the following to sound professional and polished:\n\n",
            suffix="",
            replace=True,
            order=50,
        ),
        Prompt(
            slug="simplify",
            name="Simplify language",
            system="",
            prefix="Simplify the language of the following text so it is accessible to a wide audience:\n\n",
            suffix="",
            replace=True,
            order=60,
        ),
        Prompt(
            slug="proofread",
            name="Proofread (bullet suggestions)",
            system="You are an English proofreader. Review the text and return a detailed bullet list of issues and suggested fixes with reasons.",
            prefix="My text is the following:\n\n",
            suffix="",
            replace=False,
            temperature=0.0,
            order=70,
        ),
        Prompt(
            slug="summarize",
            name="Summarize",
            system="",
            prefix="Summarize the following text:\n\n",
            suffix="",
            replace=False,
            order=80,
        ),
        Prompt(
            slug="explain",
            name="Explain",
            system="",
            prefix="Explain the following text in simple terms:\n\n",
            suffix="",
            replace=False,
            order=90,
        ),
        Prompt(
            slug="action_items",
            name="Find action items",
            system="",
            prefix="Identify any action items in the following text and present them as bullet points after a one-sentence summary:\n\n",
            suffix="",
            replace=False,
            order=100,
        ),
        Prompt(
            slug="code_optimize",
            name="Code – Optimize",
            system="You are an assistant to a software engineer. Given code, optimize for time and space complexity and explain the changes.",
            prefix="Improve and explain how to optimize the following code:\n\n",
            suffix="",
            replace=False,
            order=110,
        ),
    )
