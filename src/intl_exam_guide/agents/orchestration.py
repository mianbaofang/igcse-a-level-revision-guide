from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

AGENT_ORCHESTRATION_FILE = "agent-orchestration.json"


@dataclass(frozen=True)
class AgentRole:
    """A recorded role in the handbook production workflow."""

    role_id: str
    label: str
    responsibility: str
    status: str
    evidence: list[str] = field(default_factory=list)
    independent_from: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def default_agent_roles(final_review_complete: bool = False) -> list[AgentRole]:
    reviewer_status = "complete" if final_review_complete else "pending"
    reviewer_evidence = ["final-review-packet.json"] if final_review_complete else []
    return [
        AgentRole(
            role_id="syllabus_outline_analyst",
            label="Syllabus and outline analyst",
            responsibility=(
                "Parse provider syllabus evidence into CourseSpec and LearningUnit records."
            ),
            status="complete",
            evidence=["qualification.json", "delivery-contract.json"],
        ),
        AgentRole(
            role_id="handbook_writer",
            label="Handbook writer",
            responsibility=(
                "Create source-bound PedagogicalUnit content, practice, visuals, and HTML/PDF output."
            ),
            status="complete",
            evidence=["guide-plan.json", "handbook-package.json", "guide.html"],
        ),
        AgentRole(
            role_id="final_reviewer",
            label="Independent final reviewer",
            responsibility=(
                "Inspect rendered output and review evidence independently before final handoff."
            ),
            status=reviewer_status,
            evidence=reviewer_evidence,
            independent_from=["syllabus_outline_analyst", "handbook_writer"],
        ),
    ]


def agent_orchestration_payload(final_review_complete: bool = False) -> dict[str, object]:
    roles = default_agent_roles(final_review_complete=final_review_complete)
    return {
        "schema_version": "v0.4-agent-orchestration",
        "mode": "role-separated",
        "roles": [role.to_dict() for role in roles],
        "final_reviewer_independent": final_reviewer_is_independent(roles),
        "required_sequence": [
            "syllabus_outline_analyst",
            "handbook_writer",
            "final_reviewer",
        ],
    }


def final_reviewer_is_independent(roles: list[AgentRole] | list[dict[str, Any]]) -> bool:
    reviewer = _role_by_id(roles, "final_reviewer")
    if not reviewer:
        return False
    independent_from = set(_role_value(reviewer, "independent_from", []))
    return {"syllabus_outline_analyst", "handbook_writer"}.issubset(independent_from)


def write_agent_orchestration(output_dir: Path, final_review_complete: bool = False) -> Path:
    path = output_dir / AGENT_ORCHESTRATION_FILE
    path.write_text(
        json.dumps(
            agent_orchestration_payload(final_review_complete=final_review_complete),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return path


def _role_by_id(
    roles: list[AgentRole] | list[dict[str, Any]],
    role_id: str,
) -> AgentRole | dict[str, Any] | None:
    for role in roles:
        if _role_value(role, "role_id") == role_id:
            return role
    return None


def _role_value(role: AgentRole | dict[str, Any], key: str, default: Any = None) -> Any:
    if isinstance(role, AgentRole):
        return getattr(role, key, default)
    return role.get(key, default)
