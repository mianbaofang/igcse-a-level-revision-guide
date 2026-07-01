from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write conservative source-bound concept explanations from concept_jobs.json."
    )
    parser.add_argument("output_dir", help="Generated guide output directory.")
    parser.add_argument("--force", action="store_true", help="Overwrite concept_explanations.json.")
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    jobs_path = output_dir / "concepts" / "concept_jobs.json"
    target = output_dir / "concepts" / "concept_explanations.json"
    if not jobs_path.exists():
        raise SystemExit(f"missing concept jobs: {jobs_path}")
    if target.exists() and not args.force:
        raise SystemExit(f"concept explanations already exist: {target}; use --force")

    jobs = json.loads(jobs_path.read_text(encoding="utf-8"))
    if not isinstance(jobs, list):
        raise SystemExit("concept_jobs.json must contain a list")
    explanations = [write_entry(job) for job in jobs if isinstance(job, dict)]
    target.write_text(json.dumps(explanations, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "written": len(explanations), "path": str(target)}, ensure_ascii=False))
    return 0


def write_entry(job: dict[str, object]) -> dict[str, object]:
    topic_title = str(job.get("topic_title") or "")
    source_points = [str(point) for point in job.get("source_points", []) if str(point).strip()]
    language = str(job.get("output_language") or "en")
    subject_pack = str(job.get("subject_pack") or "").lower()
    first_point = clean_point(source_points[0] if source_points else topic_title)
    topic_focus = clean_topic_focus(topic_title)
    if language == "zh-CN":
        return write_zh_entry(topic_title, topic_focus, first_point, source_points, subject_pack)
    return write_en_entry(topic_title, topic_focus, first_point, source_points, subject_pack)


def write_en_entry(
    topic_title: str,
    topic_focus: str,
    first_point: str,
    source_points: list[str],
    subject_pack: str,
) -> dict[str, object]:
    lower = " ".join([topic_title, *source_points]).lower()
    concept = en_concept_name(topic_title, topic_focus, first_point, subject_pack)
    relation = en_relationship_sentence(concept, lower, source_points, subject_pack)
    boundary = en_boundary_sentence(concept, lower, source_points, subject_pack)
    steps = en_steps(concept, lower, subject_pack)
    pitfall = en_pitfall(concept, lower, subject_pack)
    return {
        "topic_title": topic_title,
        "essence": en_essence(concept, lower, subject_pack),
        "analogy": en_analogy(concept, lower, subject_pack),
        "mini_worked_example": en_mini_example(concept, lower, subject_pack),
        "worked_solution_steps": steps,
        "pitfall": pitfall,
        "explanations": [
            en_definition_sentence(concept, lower, source_points, subject_pack),
            relation,
            boundary,
        ],
    }


def write_zh_entry(
    topic_title: str,
    topic_focus: str,
    first_point: str,
    source_points: list[str],
    subject_pack: str,
) -> dict[str, object]:
    concept = topic_focus or first_point
    return {
        "topic_title": topic_title,
        "essence": f"本节核心是把“{concept}”理解成一个明确的概念、关系或边界，而不是背一串关键词。",
        "analogy": f"可以把“{concept}”看成题目里的路标：它告诉你该看哪种关系、该停在哪个范围内。",
        "mini_worked_example": f"遇到本节题目时，先确认题目真正问的是“{concept}”中的哪一条关系，再写计算、解释或判断。",
        "worked_solution_steps": [
            "先圈出题目给出的对象、条件和限制词。",
            f"把这些信息对应到“{concept}”这一课纲点。",
            "写出本节需要的关系、公式、图像特征或判断依据。",
            "最后检查答案有没有越过课纲点给出的范围。",
        ],
        "pitfall": "最常见的失分是只写熟悉词汇，却没有说明本节课纲点要求的具体关系或限制。",
        "explanations": [
            f"“{concept}”是本节要掌握的核心对象，需要能说明它本身表示什么。",
            "它描述的是题目条件之间的关系，或课纲明确限定的适用范围。",
            "它重要是因为本节例题和考试小问都会先要求你识别这个关系，再进行计算、解释或判断。",
        ],
    }


def clean_point(value: str) -> str:
    text = re.sub(r"\s+", " ", value).strip()
    action_words = r"(?:understand|identify|explain|describe|state|apply|prepare|calculate|distinguish)"
    text = re.sub(r"^[a-z]\)\s*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+significance\s+of\s+the\s+following\s+accounting\s+concepts\s*:?\s*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+following\s+accounting\s+concepts\s*:?\s*$", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+following\s+accounting\s+concepts\s*:?\s*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+following\s+accounting\s*:?\s*$", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+terms\s*:?\s*$", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+terms\s*:?\s*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+causes\s+of\s+(.+)$", r"causes of \1", text, flags=re.IGNORECASE).strip()
    text = re.sub(
        rf"^{action_words}\s+the\s+(?:purpose|use|uses|characteristics|features|terms|benefits|significance|principles)\s+of(?:\s+the)?\s*:?\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    text = re.sub(
        rf"^{action_words}\s+the\s+(?:purpose|use|uses|characteristics|features|terms|benefits|significance|principles)\s+of\s+",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    text = re.sub(rf"^{action_words}\s+between\s+", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\bStudents will be expected to\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\bStudents may be required to\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\bStudents should be familiar with\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\bStudents are expected to\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(
        rf"\bStudents should be able to\s+{action_words}\s*:\s*",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    text = re.sub(
        rf"\bStudents should be able to\s+{action_words}\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    text = re.sub(r"\bStudents should be able to\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\bLearners should be able to\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\bCandidates should have an understanding of\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\bCandidates should\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = text.lstrip(":;,- ").strip()
    return text.rstrip(".")


def usable_source_fragments(source_points: list[str]) -> list[str]:
    fragments = []
    for point in source_points:
        cleaned = clean_point(point)
        if cleaned and not is_shell_fragment(cleaned):
            fragments.append(cleaned)
    return merge_wrapped_fragments(fragments)


def merge_wrapped_fragments(points: list[str]) -> list[str]:
    merged: list[str] = []
    for point in points:
        if merged and should_merge_fragment(merged[-1], point):
            merged[-1] = f"{merged[-1]} {point}".strip()
        else:
            merged.append(point)
    return merged


def should_merge_fragment(previous: str, current: str) -> bool:
    prev = previous.strip().lower()
    cur = current.strip()
    if not prev or not cur:
        return False
    if prev.endswith((",", ";", ":")):
        return True
    if prev.split()[-1] in {"and", "or", "for", "of", "the", "in", "to", "with", "capital", "raw", "provision"}:
        return True
    if cur and cur[0].islower() and prev.endswith((" other", "non-current", "books", "open")):
        return True
    return False


def is_shell_fragment(value: str) -> bool:
    lower = value.strip(" .:;").lower()
    if not lower:
        return True
    if lower in {"concepts", "the following accounting"}:
        return True
    return bool(
        re.fullmatch(
            r"(?:purpose|use|uses|characteristics|features|terms|benefits|significance|principles)(?:\s+of)?",
            lower,
        )
    )


def clean_topic_focus(title: str) -> str:
    focus = title.rsplit(":", 1)[-1].strip() if ":" in title else title.strip()
    focus = re.sub(r"^[A-Z]{0,3}\d+(?:\.\d+)*\s*[-–—]\s*", "", focus).strip()
    return re.sub(r"\s+", " ", focus).strip()


def en_concept_name(topic_title: str, topic_focus: str, first_point: str, subject_pack: str) -> str:
    if (
        subject_pack == "accounting"
        and re.match(r"^\d+(?:\.\d+)+\s*-\s+", topic_title.strip())
        and ":" not in topic_title
    ):
        return topic_title.strip().rstrip(".")
    candidate = topic_focus if topic_focus and len(topic_focus) <= 120 else first_point
    candidate = candidate.rstrip(".")
    return candidate or "this syllabus point"


def en_essence(concept: str, lower: str, subject_pack: str) -> str:
    if "dynamics of competition" in lower or "short-run and long-run benefits" in lower:
        return "The dynamics of competition is about how competitive pressure changes firm behaviour and creates different short-run and long-run benefits for consumers and markets."
    if "competitive market process" in lower or "compete on price" in lower:
        return "The competitive market process is about how rivalry pushes firms to compete through price and non-price methods such as better products, lower costs, and improved service."
    if "use of factorisation" in lower:
        return "Use of factorisation is about turning a product form into solvable zero-factor equations."
    if "discriminant of a quadratic" in lower:
        return "The discriminant is about reading the nature of a quadratic equation from b^2 - 4ac before solving it."
    if "using algebraic methods" in lower or "equal roots" in lower or "distinct real roots" in lower or "no real roots" in lower:
        return "Using algebraic methods here means turning a graph intersection question into an equation, then using the number of real roots to interpret the geometry."
    if "translation of circles" in lower:
        return "Translation of circles is about moving the centre of a circle while keeping its radius unchanged."
    if "relative frequencies" in lower or "equally likely outcomes" in lower:
        return "Assigning probabilities here means choosing the right basis: observed relative frequency or counting equally likely outcomes."
    if "exponential" in lower and "graph" in lower:
        return f"{concept} is about recognising how an exponential graph changes, especially its growth/decay shape and asymptote."
    if "graph" in lower or "curve" in lower:
        return f"{concept} is about reading a relationship from its shape, intercepts, gradients, or transformations on a graph."
    if any(word in lower for word in ["differentiat", "derivative", "gradient", "tangent"]):
        return f"{concept} is about using gradient as an exact local rate of change."
    if any(word in lower for word in ["integrat", "area", "trapezium"]):
        return f"{concept} is about connecting accumulation, area, and the algebra of integration."
    if any(word in lower for word in ["probability", "binomial", "random variable"]):
        return f"{concept} is about modelling uncertain outcomes with a defined probability rule."
    if any(word in lower for word in ["momentum", "impulse", "impact", "collision"]):
        return f"{concept} tracks motion through mass, velocity, and the change caused by an impact or impulse."
    if subject_pack == "accounting":
        return f"{concept} is about recording, classifying, or checking financial information in the required accounting format."
    if subject_pack == "economics":
        return f"{concept} is about how economic choices create incentives, constraints, and consequences."
    return f"{concept} is the specific syllabus idea that the question wants you to define, connect, and apply."


def en_definition_sentence(
    concept: str,
    lower: str,
    source_points: list[str],
    subject_pack: str,
) -> str:
    if "dynamics of competition" in lower or "short-run and long-run benefits" in lower:
        return "Competition dynamics describe how firms respond over time to rival pressure, with short-run effects such as price or service changes and long-run effects such as innovation, efficiency, and consumer choice."
    if "competitive market process" in lower or "compete on price" in lower:
        return "Non-price competition means firms try to win customers by improving product quality, reducing costs, or improving service rather than only cutting price."
    if "use of factorisation" in lower:
        return "Using factorisation to solve means rewriting an expression as factors and then applying the zero-product rule."
    if "discriminant of a quadratic" in lower:
        return "For ax^2 + bx + c = 0, the discriminant b^2 - 4ac tells whether the quadratic has two distinct real roots, one repeated real root, or no real roots."
    if "using algebraic methods" in lower or "equal roots" in lower or "distinct real roots" in lower or "no real roots" in lower:
        return "Algebraic methods connect coordinate geometry to equations: equal roots, distinct real roots, or no real roots describe how graphs meet."
    if "translation of circles" in lower:
        return "A translated circle has the same radius but a different centre, so only the centre coordinates change in the completed-square equation."
    if "relative frequencies" in lower:
        return "Relative frequency estimates probability by dividing how often an outcome occurs by the total number of trials."
    if "equally likely outcomes" in lower:
        return "Equally likely outcomes allow probability to be found by counting favourable outcomes over all possible outcomes."
    if "exponential" in lower and "graph" in lower:
        return "An exponential graph has a changing rate of growth or decay and usually approaches an asymptote rather than behaving like a straight line."
    if "surd" in lower:
        return "Surds are exact square-root expressions kept in radical form when a decimal would lose exactness."
    if "indices" in lower or "exponent" in lower:
        return "Index laws are rules for rewriting powers so multiplication, division, roots, and fractional powers stay consistent."
    if "discriminant" in lower:
        return "The discriminant is the part of the quadratic formula that tells you how many real roots a quadratic has."
    if "factorisation" in lower:
        return "Factorisation rewrites a polynomial as a product, making roots and algebraic structure easier to see."
    if "completing the square" in lower:
        return "Completing the square rewrites a quadratic to expose its vertex and symmetry."
    if "conservation of momentum" in lower:
        return "Conservation of momentum says the total momentum of the two-particle system is unchanged across the impact when no external impulse is included."
    if "fixed surface" in lower or "restitution" in lower:
        return "A direct impact with a fixed smooth surface changes only the velocity component perpendicular to the surface."
    if "concept of momentum" in lower or "momentum = mv" in lower:
        return "Momentum is mass times velocity, so it combines how much matter is moving with how fast it moves."
    if "impulse" in lower:
        return "Impulse is the change in momentum produced by a force acting over a time interval."
    if "momentum" in lower:
        return "Momentum is mass times velocity, so it combines how much matter is moving with how fast it moves."
    return source_bound_definition_sentence(concept, source_points, subject_pack)


def source_bound_definition_sentence(
    concept: str,
    source_points: list[str],
    subject_pack: str,
) -> str:
    source_fragments = usable_source_fragments(source_points)
    fragment = next(
        (
            point
            for point in source_fragments
            if normalize_concept_text(point) != normalize_concept_text(concept)
        ),
        source_fragments[0] if source_fragments else concept,
    )
    if len(fragment) > 120:
        fragment = fragment[:117].rstrip() + "..."
    if subject_pack == "economics":
        return f"{concept} is about {fragment}, so explain the economic choice, resource, market, cost, or benefit named in the source point."
    if subject_pack == "accounting":
        return f"{concept} is about {fragment}, so identify the record, statement, control, or accounting purpose named in the source point."
    if subject_pack == "business":
        return f"{concept} is about {fragment}, so explain the business decision, stakeholder, market, operation, or finance link named in the source point."
    if subject_pack == "history":
        return f"{concept} is about {fragment}, so explain the event, cause, consequence, source, or change named in the source point."
    return f"{concept} is about {fragment}, so define the idea and apply only the relationship named in this source point."


def normalize_concept_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def en_relationship_sentence(
    concept: str,
    lower: str,
    source_points: list[str],
    subject_pack: str,
) -> str:
    if "dynamics of competition" in lower or "short-run and long-run benefits" in lower:
        return "The relationship is between rival pressure, firms' responses, and the short-run or long-run benefits that may result for consumers and the market."
    if "competitive market process" in lower or "compete on price" in lower:
        return "The relationship is that competition creates pressure on firms to improve product quality, reduce costs, and improve service so they can attract or keep customers."
    if "use of factorisation" in lower:
        return "The relationship is that if (x-a)(x-b)=0, then each factor gives one possible solution."
    if "discriminant of a quadratic" in lower:
        return "The relationship is between the sign of b^2 - 4ac and the number of real roots of a quadratic equation."
    if "using algebraic methods" in lower or "equal roots" in lower or "distinct real roots" in lower or "no real roots" in lower:
        return "The relationship is between the discriminant/root count of the equation and the number of geometric intersection points."
    if "translation of circles" in lower:
        return "The relationship is between the circle equation `(x-a)^2 + (y-b)^2 = r^2` and the centre `(a,b)` after translation."
    if "relative frequencies" in lower or "equally likely outcomes" in lower:
        return "The relationship is that probability must be based either on repeated observations or on a clearly defined equally likely sample space."
    if "transformation" in lower and "f (x" in lower:
        return "The key relationship is whether the change acts on the output, as in y = f(x) + a or y = af(x), or on the input, as in y = f(x + a) or y = f(ax)."
    if "conservation of momentum" in lower:
        return "The relationship is that total momentum before impact equals total momentum after impact when the stated system is treated consistently."
    if "fixed surface" in lower:
        return "The relationship is between the velocity perpendicular to the wall before impact and the rebound velocity after impact."
    if "concept of momentum" in lower or "momentum = mv" in lower:
        return "The relationship is p = mv, including the sign of velocity when motion is restricted to one straight line."
    if "impulse" in lower:
        return "The relationship is impulse equals final momentum minus initial momentum, with direction signs kept consistent."
    if "momentum" in lower:
        return "The relationship is p = mv, including the sign of velocity when motion is restricted to one straight line."
    if subject_pack == "accounting":
        fragments = usable_source_fragments(source_points)
        if len(fragments) >= 2:
            return f"The relationship is between {fragments[0]} and {fragments[1]}, staying inside this accounting unit."
        if fragments:
            return f"The relationship to track is the accounting purpose named here: {fragments[0]}."
        return f"The relationship is the accounting record, statement, or control purpose that makes {concept} a separate syllabus point."
    if subject_pack == "economics":
        fragments = usable_source_fragments(source_points)
        if fragments:
            return f"The relationship to track is the economic cause, choice, cost, or consequence named here: {fragments[0]}."
        return f"The relationship is the economic link that makes {concept} a separate syllabus point."
    if subject_pack == "business":
        fragments = usable_source_fragments(source_points)
        if fragments:
            return f"The relationship to track is the business decision, stakeholder, market, operation, or finance link named here: {fragments[0]}."
        return f"The relationship is the business link that makes {concept} a separate syllabus point."
    if subject_pack == "history":
        fragments = usable_source_fragments(source_points)
        if fragments:
            return f"The relationship to track is the event, cause, consequence, source, or change named here: {fragments[0]}."
        return f"The relationship is the historical link that makes {concept} a separate syllabus point."
    if "straight line" in lower:
        return "The relationship is between gradient, intercepts, coordinates, distance, and midpoint on the same coordinate grid."
    if "sine" in lower or "cosine" in lower or "tangent" in lower:
        return "The relationship links angles to side ratios or periodic graph values, depending on whether the question is geometric or graphical."
    if "external cost" in lower or "external benefit" in lower:
        return "The relationship is between private decisions and effects on third parties outside the transaction."
    if "bank reconciliation" in lower:
        return "The relationship is between the cash book balance, bank statement balance, timing differences, and errors."
    if source_points:
        return f"The relationship to track is the one stated in the source point: {clean_point(source_points[0])}."
    return f"The relationship is the boundary or link that makes {concept} a separate syllabus point."


def en_boundary_sentence(
    concept: str,
    lower: str,
    source_points: list[str],
    subject_pack: str,
) -> str:
    if "dynamics of competition" in lower or "short-run and long-run benefits" in lower:
        return "The boundary is that the answer should separate short-run effects from long-run benefits instead of repeating a general definition of competition."
    if "competitive market process" in lower or "compete on price" in lower:
        return "The boundary is that this point is not just a supply-and-demand shift; it is about firm behaviour inside competition, especially price and non-price competition."
    if any(word in lower for word in ["restricted", "only", "will not", "not required", "simple problems"]):
        return "The syllabus boundary matters here: include the stated restriction and do not expand into excluded cases."
    if subject_pack == "mathematics":
        return "It is central because later questions usually hide this idea inside algebra, graphs, or modelling language."
    if subject_pack == "accounting":
        return "It is central because marks depend on using the correct statement, ledger, or control purpose, not just a familiar business word."
    if subject_pack == "economics":
        return "It is central because exam answers need the chain from cause to consequence, not just a definition."
    return f"It is central because the rest of the question normally depends on recognising {concept} first."


def en_analogy(concept: str, lower: str, subject_pack: str) -> str:
    if "dynamics of competition" in lower or "short-run and long-run benefits" in lower:
        return "Think of competition as a race over several laps: an early price or service response can become longer-term efficiency or innovation."
    if "competitive market process" in lower or "compete on price" in lower:
        return "Think of rival firms as runners in a race: one can lower price, but another can still compete by offering a better product or faster service."
    if "graph" in lower or "curve" in lower:
        return "Think of the graph as a map: the route shape tells you more than a list of isolated points."
    if "probability" in lower:
        return "Think of it as setting the rules of a game before you count possible results."
    if "momentum" in lower or "impact" in lower:
        return "Think of two skaters pushing off: direction and speed both matter, not just who is heavier."
    if subject_pack == "accounting":
        return "Think of the accounting record as a receipt trail: each entry must explain where the number came from and where it goes."
    if subject_pack == "economics":
        return "Think of a market as a set of nudges: every cost, benefit, or rule changes somebody's choice."
    return f"Think of {concept} as the signpost that tells you which tool the question is asking for."


def en_mini_example(concept: str, lower: str, subject_pack: str) -> str:
    if "dynamics of competition" in lower or "short-run and long-run benefits" in lower:
        return "A typical question asks you to explain how competition may benefit consumers immediately and how it may improve efficiency, innovation, or choice over time."
    if "competitive market process" in lower or "compete on price" in lower:
        return "A typical question describes rival firms and asks why competition may lead to improved products, lower costs, or better service even when prices are not cut."
    if "use of factorisation" in lower:
        return "A typical question asks you to factorise first, set each factor equal to zero, and list all valid solutions."
    if "discriminant of a quadratic" in lower:
        return "A typical question gives a quadratic and asks you to decide the nature of its roots from the sign of b^2 - 4ac."
    if "using algebraic methods" in lower or "equal roots" in lower or "distinct real roots" in lower or "no real roots" in lower:
        return "A typical question gives an intersection equation and asks you to decide whether the graphs meet once, twice, or not at all."
    if "translation of circles" in lower:
        return "A typical question gives a circle and a translation vector, then asks for the new centre or equation."
    if "relative frequencies" in lower or "equally likely outcomes" in lower:
        return "A typical question gives either trial results or a fair sample space, then asks for the probability using the appropriate basis."
    if "graph" in lower or "curve" in lower:
        return "A typical question gives an equation or graph feature, then asks you to connect it to intercepts, gradients, roots, or shape."
    if "probability" in lower:
        return "A typical question defines the outcomes first, then asks for a probability, expectation, or distribution value."
    if "momentum" in lower or "impact" in lower:
        return "A typical question gives masses and velocities, then asks you to write the before-and-after momentum equation."
    if subject_pack == "accounting":
        return "A typical question gives transaction data and asks you to place it in the correct record or statement."
    if subject_pack == "economics":
        return "A typical question gives a real market situation and asks you to explain the cause-and-effect chain."
    return f"A typical question asks you to recognise {concept}, state the relevant relationship, then apply it to the given data."


def en_steps(concept: str, lower: str, subject_pack: str) -> list[str]:
    if "dynamics of competition" in lower or "short-run and long-run benefits" in lower:
        return [
            "Identify the competitive pressure or market change in the scenario.",
            "Explain the firm's short-run response, such as price, quality, or service adjustment.",
            "Explain the longer-run effect, such as efficiency, innovation, or greater consumer choice.",
            "State who benefits and why the benefit may not be immediate or guaranteed.",
        ]
    if "competitive market process" in lower or "compete on price" in lower:
        return [
            "Identify the rival firms or competitive pressure in the scenario.",
            "State whether the response is price competition or non-price competition.",
            "Explain the firm behaviour, such as product improvement, cost reduction, or service improvement.",
            "Link the behaviour to gaining or retaining customers.",
        ]
    if "use of factorisation" in lower:
        return [
            "Rewrite the expression as a product of factors.",
            "Set each factor equal to zero.",
            "Solve each small equation.",
            "Check that all solutions have been included.",
        ]
    if "discriminant of a quadratic" in lower:
        return [
            "Identify a, b, and c from the quadratic equation.",
            "Calculate b^2 - 4ac carefully.",
            "Use the sign of the discriminant to classify the roots.",
            "State the root nature clearly without necessarily solving the equation.",
        ]
    if "using algebraic methods" in lower or "equal roots" in lower or "distinct real roots" in lower or "no real roots" in lower:
        return [
            "Form the equation that represents the intersection or geometric condition.",
            "Calculate or reason about the number of real roots.",
            "Translate the root count back into geometry.",
            "State the conclusion using words such as tangent, two intersections, or no real intersection.",
        ]
    if "translation of circles" in lower:
        return [
            "Read the original centre and radius from the circle equation.",
            "Apply the translation to the centre coordinates.",
            "Keep the radius unchanged.",
            "Write the new equation in completed-square form.",
        ]
    if "relative frequencies" in lower or "equally likely outcomes" in lower:
        return [
            "Decide whether the information is observed frequency data or an equally likely sample space.",
            "Count the relevant outcomes or frequencies.",
            "Divide by the correct total.",
            "State whether the result is exact probability or an estimate.",
        ]
    if "graph" in lower or "curve" in lower:
        return [
            "Identify the graph feature named in the question.",
            "Link it to the matching algebraic fact, such as roots, intercepts, gradient, vertex, or transformation.",
            "Use the equation or sketch to support the answer.",
            "Check that the final statement matches the requested feature.",
        ]
    if "momentum" in lower or "impact" in lower:
        return [
            "Choose a positive direction and keep it throughout.",
            "Write the before-impact and after-impact momentum terms.",
            "Apply the stated conservation, impulse, or restitution relationship.",
            "Check signs and units before giving the final velocity or statement.",
        ]
    if subject_pack == "accounting":
        return [
            "Identify the source document, transaction, or statement named in the question.",
            "Place each amount in the correct side, column, or section.",
            "Apply the relevant accounting rule or control purpose.",
            "Check that totals, balances, and labels answer the question.",
        ]
    if subject_pack == "economics":
        return [
            "Identify the decision maker or market in the scenario.",
            "State the incentive, constraint, cost, or benefit involved.",
            "Explain the chain of effects using the correct economic term.",
            "Finish with the result or judgement asked for by the command word.",
        ]
    return [
        "Identify the exact syllabus idea named by the question.",
        "Write the definition, formula, graph feature, or relationship it uses.",
        "Apply it only to the data or condition given.",
        "Check that the answer stays inside this topic's boundary.",
    ]


def en_pitfall(concept: str, lower: str, subject_pack: str) -> str:
    if "dynamics of competition" in lower or "short-run and long-run benefits" in lower:
        return "The common error is listing benefits of competition without separating short-run responses from long-run market outcomes."
    if "competitive market process" in lower or "compete on price" in lower:
        return "The common error is treating competition as only a price cut and ignoring product quality, cost reduction, and service improvement."
    if "use of factorisation" in lower:
        return "The common error is finding the factors but not setting each factor equal to zero."
    if "discriminant of a quadratic" in lower:
        return "The common error is treating the discriminant as the root itself instead of using its sign to classify the roots."
    if "using algebraic methods" in lower or "equal roots" in lower or "distinct real roots" in lower or "no real roots" in lower:
        return "The common error is solving the equation but not translating the number of real roots back into the geometry."
    if "translation of circles" in lower:
        return "The common error is changing the radius or copying the centre signs incorrectly."
    if "relative frequencies" in lower or "equally likely outcomes" in lower:
        return "The common error is mixing an experimental estimate with exact equally likely counting."
    if "graph" in lower or "curve" in lower:
        return "Do not plot random points when the mark is for a named graph feature such as a root, gradient, asymptote, vertex, or transformation."
    if "momentum" in lower or "impact" in lower:
        return "The common error is changing direction signs halfway through the momentum or restitution equation."
    if subject_pack == "accounting":
        return "The common error is using the right number in the wrong account, side, or statement section."
    if subject_pack == "economics":
        return "The common error is naming a concept without explaining the cause-and-effect chain in the scenario."
    return f"The common error is writing a memorised phrase about {concept} without using the actual condition in the question."


if __name__ == "__main__":
    raise SystemExit(main())
