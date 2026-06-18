from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from intl_exam_guide.models import Qualification


@dataclass
class Link:
    """A discovered exam-board link: subject page, qualification page, or PDF.

    Re-exported from providers.oxfordaqa for backward compatibility.
    """

    text: str
    href: str
    qualification_type: str | None = None
    subject_heading: str | None = None
    group_label: str | None = None
    style_class: str | None = None


class ExamBoardProvider(ABC):
    """Contract for an exam-board provider.

    OxfordAQA implements full catalogue discovery. URL-first providers
    (Pearson, Cambridge) only need find_qualification, parse_qualification,
    and download_specification; discovery methods default to a clear error.
    """

    name: str = ""
    supported_levels: tuple[str, ...] = ()

    @abstractmethod
    def find_qualification(self, query: str, level: str | None = None) -> Link:
        """Resolve a subject query, subject-page URL, or direct PDF URL to a Link."""

    @abstractmethod
    def parse_qualification(self, page_url: str) -> Qualification:
        """Parse a qualification/subject page into a Qualification object."""

    @abstractmethod
    def download_specification(
        self, qualification: Qualification, output_dir: Path
    ) -> Qualification:
        """Download the spec/syllabus PDF, attach detailed topics and source snippets."""

    def discover_subject_pages(self) -> list[Link]:
        raise NotImplementedError(
            f"{self.name or type(self).__name__} does not implement subject discovery."
        )

    def list_qualifications(self, subject_url: str) -> list[Link]:
        raise NotImplementedError(
            f"{self.name or type(self).__name__} does not implement qualification listing."
        )

    def apply_listing_metadata(
        self, qualification: Qualification, link: Link
    ) -> Qualification:
        return qualification


# Providers fully implemented in this release. Append a name once get_provider
# returns a working instance for it.
PROVIDER_NAMES: tuple[str, ...] = ("oxfordaqa",)

# Domain fingerprints used to infer a provider from a user-supplied URL.
# Planned providers are listed so URL routing can detect them and report a
# clear "not implemented yet" message instead of silently using OxfordAQA.
PROVIDER_DOMAINS: dict[str, tuple[str, ...]] = {
    "oxfordaqa": ("oxfordaqa.com",),
    "pearson": ("qualifications.pearson.com", "edexcel"),
    "cambridge": ("cambridgeinternational.org",),
}


class ProviderNotImplementedError(NotImplementedError):
    """Raised when a provider is recognised but not yet implemented."""


def infer_provider_from_url(url: str) -> str | None:
    """Return the provider name whose domain fingerprint matches the URL."""
    lower = url.lower()
    for name, domains in PROVIDER_DOMAINS.items():
        if any(domain in lower for domain in domains):
            return name
    return None


def get_provider(name: str) -> ExamBoardProvider:
    """Return a provider instance by name.

    Recognised-but-unimplemented providers raise ProviderNotImplementedError so
    the caller can surface a clear "planned but not implemented" message.
    """
    normalized = name.lower().strip()
    if normalized in {"oxfordaqa", "oxford-aqa", "oxford_international_aqa"}:
        from intl_exam_guide.providers.oxfordaqa import OxfordAQAProvider

        return OxfordAQAProvider()
    if normalized in {"pearson", "edexcel", "pearson-edexcel"}:
        raise ProviderNotImplementedError(
            "Pearson Edexcel provider is planned but not implemented in this release. "
            "See NEXT_AGENT_UPGRADE_PLAN.md Phase 3."
        )
    if normalized in {"cambridge", "caie", "cie"}:
        raise ProviderNotImplementedError(
            "Cambridge International / CAIE provider is planned but not implemented in "
            "this release. See NEXT_AGENT_UPGRADE_PLAN.md Phase 4."
        )
    raise ValueError(
        f"Unknown provider: {name!r}. Implemented providers: "
        f"{', '.join(PROVIDER_NAMES)}."
    )
