from __future__ import annotations

import json
from pathlib import Path

from intl_exam_guide.models import GuidePlan, Topic
from intl_exam_guide.planning.localization import zh_teachable_topic_title


CONCEPT_REVIEW_FILE = "concept_explanations.json"


def build_concept_jobs(plan: GuidePlan) -> list[dict[str, object]]:
    topics = {topic.title: topic for topic in plan.qualification.topics}
    jobs: list[dict[str, object]] = []
    for index, guide in enumerate(plan.topic_guides, start=1):
        topic = topics.get(guide.topic_title)
        jobs.append(
            {
                "id": f"concept_{index:03d}",
                "topic_title": guide.topic_title,
                "student_title": student_topic_title(topic, index, plan.run_options.output_language),
                "output_language": plan.run_options.output_language,
                "current_draft": guide.checklist[:3],
                "source_points": (topic.points if topic else []),
                "source_pages": [snippet.page for snippet in (topic.source_snippets if topic else [])],
                "task": concept_task_text(plan.run_options.output_language),
            }
        )
    return jobs


def student_topic_title(topic: Topic | None, index: int, language: str) -> str:
    if topic is None:
        return f"Topic {index}"
    if language == "zh-CN":
        return zh_teachable_topic_title(topic.title, index)
    return topic.title


def concept_task_text(language: str) -> str:
    if language == "zh-CN":
        return (
            "写 2-3 条学生可直接阅读的中文概念解释。只围绕 topic_title 和 source_points；"
            "说明这个概念是什么、描述什么关系或边界、为什么是本节核心。"
            "不要写做题动作清单，不要写“会识别/会操作/会检查”，不要引入相邻章节。"
        )
    return (
        "Write 2-3 student-facing concept explanation bullets. Stay inside "
        "topic_title and source_points; explain what the concept is, what "
        "relationship or boundary it describes, and why it is central. Do not "
        "write a procedural checklist or import adjacent topics."
    )


def concept_jobs_markdown(jobs: list[dict[str, object]]) -> str:
    lines = [
        "# Concept Explanation Jobs",
        "",
        "These jobs are for the LLM concept-writing pass before final delivery.",
        "",
    ]
    for job in jobs:
        lines.extend(
            [
                f"## {job['id']} - {job['student_title']}",
                "",
                f"- Topic: {job['topic_title']}",
                f"- Task: {job['task']}",
                "- Source points:",
            ]
        )
        source_points = job.get("source_points", [])
        if isinstance(source_points, list):
            for point in source_points:
                lines.append(f"  - {point}")
        lines.append("")
    return "\n".join(lines)


def write_concept_jobs(plan: GuidePlan, output_dir: Path) -> list[dict[str, object]]:
    concepts_dir = output_dir / "concepts"
    concepts_dir.mkdir(parents=True, exist_ok=True)
    jobs = build_concept_jobs(plan)
    (concepts_dir / "concept_jobs.json").write_text(
        json.dumps(jobs, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (concepts_dir / "concept_jobs.md").write_text(
        concept_jobs_markdown(jobs),
        encoding="utf-8",
    )
    return jobs


def reviewed_concept_titles(output_dir: Path) -> set[str]:
    path = output_dir / "concepts" / CONCEPT_REVIEW_FILE
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    entries = data.get("concept_explanations", data) if isinstance(data, dict) else data
    titles: set[str] = set()
    if isinstance(entries, dict):
        titles.update(str(title) for title in entries)
        return titles
    if isinstance(entries, list):
        for entry in entries:
            if isinstance(entry, dict) and entry.get("topic_title"):
                titles.add(str(entry["topic_title"]))
    return titles
