"""Utilities for parsing Markdown product requirements documents."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Iterable

_HEADING_RE = re.compile(r"^(?P<level>#{2,3})\s+(?P<title>.+?)\s*$")
_PRIORITY_RE = re.compile(r"^\s*(?:[-*]\s*)?(?:priority|prio)\s*:\s*(?P<priority>.+?)\s*$", re.IGNORECASE)
_CHECKBOX_RE = re.compile(r"^\s*[-*]\s+\[(?P<mark>[ xX])]\s+(?P<text>.+?)\s*$")
_BULLET_RE = re.compile(r"^\s*[-*]\s+(?P<text>.+?)\s*$")
_ACCEPTANCE_HEADING_RE = re.compile(r"^\s*(?:#{3,4}\s*)?acceptance criteria\s*:??\s*$", re.IGNORECASE)
_FENCE_RE = re.compile(r"^\s*```")


@dataclass(frozen=True)
class AcceptanceCriterion:
    """A measurable condition that must be true for a feature to be complete."""

    text: str
    completed: bool = False

    def as_dict(self) -> dict[str, object]:
        return {"text": self.text, "completed": self.completed}


@dataclass(frozen=True)
class Feature:
    """A product feature extracted from a PRD section."""

    slug: str
    title: str
    priority: str = "unspecified"
    description: str = ""
    acceptance_criteria: tuple[AcceptanceCriterion, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "title": self.title,
            "priority": self.priority,
            "description": self.description,
            "acceptanceCriteria": [criterion.as_dict() for criterion in self.acceptance_criteria],
        }


@dataclass(frozen=True)
class PrdDocument:
    """Structured representation of a Markdown PRD."""

    source: str
    features: tuple[Feature, ...]

    def as_dict(self) -> dict[str, object]:
        return {"source": self.source, "features": [feature.as_dict() for feature in self.features]}


def parse_prd(markdown: str, *, source: str = "inline") -> PrdDocument:
    """Parse Markdown PRD text into a structured feature backlog.

    The parser treats level-two and level-three headings as feature boundaries.
    Within each feature, `Priority: ...` lines become priority metadata and
    checkbox bullets under an `Acceptance Criteria` label become criteria.
    """

    sections = _split_feature_sections(markdown.splitlines())
    features = tuple(_parse_feature(title, lines) for title, lines in sections)
    return PrdDocument(source=source, features=features)


def parse_prd_file(path: str | Path) -> PrdDocument:
    prd_path = Path(path)
    return parse_prd(prd_path.read_text(encoding="utf-8"), source=str(prd_path))


def _split_feature_sections(lines: Iterable[str]) -> list[tuple[str, list[str]]]:
    sections: list[tuple[str, list[str]]] = []
    current_title: str | None = None
    current_lines: list[str] = []

    in_fenced_code = False

    for line in lines:
        if _FENCE_RE.match(line):
            in_fenced_code = not in_fenced_code
            if current_title is not None:
                current_lines.append(line)
            continue

        match = _HEADING_RE.match(line) if not in_fenced_code else None
        if match:
            if current_title is not None:
                sections.append((current_title, current_lines))
            current_title = _clean_feature_title(match.group("title"))
            current_lines = []
            continue

        if current_title is not None:
            current_lines.append(line)

    if current_title is not None:
        sections.append((current_title, current_lines))

    return sections


def _parse_feature(title: str, lines: list[str]) -> Feature:
    priority = "unspecified"
    description_lines: list[str] = []
    criteria: list[AcceptanceCriterion] = []
    in_acceptance_criteria = False

    in_fenced_code = False

    for line in lines:
        if _FENCE_RE.match(line):
            in_fenced_code = not in_fenced_code
            continue

        if in_fenced_code:
            continue

        priority_match = _PRIORITY_RE.match(line)
        if priority_match:
            priority = priority_match.group("priority").strip().lower()
            continue

        if _ACCEPTANCE_HEADING_RE.match(line):
            in_acceptance_criteria = True
            continue

        checkbox_match = _CHECKBOX_RE.match(line)
        if checkbox_match:
            criteria.append(
                AcceptanceCriterion(
                    text=checkbox_match.group("text").strip(),
                    completed=checkbox_match.group("mark").lower() == "x",
                )
            )
            continue

        if in_acceptance_criteria:
            bullet_match = _BULLET_RE.match(line)
            if bullet_match:
                criteria.append(AcceptanceCriterion(text=bullet_match.group("text").strip()))
                continue

        if line.strip():
            description_lines.append(line.strip())

    return Feature(
        slug=_slugify(title),
        title=title,
        priority=priority,
        description="\n".join(description_lines).strip(),
        acceptance_criteria=tuple(criteria),
    )


def _clean_feature_title(title: str) -> str:
    return re.sub(r"^(?:feature|requirement|epic)\s*:\s*", "", title.strip(), flags=re.IGNORECASE)


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "untitled"
