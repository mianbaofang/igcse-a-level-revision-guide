from intl_exam_guide.models import Topic, VisualBrief
from intl_exam_guide.planning.guide_plan import choose_visual_type
from intl_exam_guide.rendering.html import render_topic_visual_svg


def route(title: str, points: list[str], subject: str) -> tuple[str, str, str]:
    return choose_visual_type(Topic(title=title, points=points), points, subject)


def test_complex_subject_visuals_are_routed_to_infographic_queue():
    cases = [
        (
            "3.1 - Source documents and books of prime entry",
            ["source documents, books of prime entry, ledger accounts, double entry"],
            "Accounting",
            "ledger flow",
        ),
        (
            "2.1 - Markets and allocation of resources",
            ["demand, supply, equilibrium price, market changes"],
            "Economics",
            "demand-supply",
        ),
        (
            "8.3 - Gas tests",
            ["test for hydrogen, oxygen, carbon dioxide and chlorine using observations"],
            "Chemistry",
            "gas tests",
        ),
        (
            "4.1 - Set notation and Venn diagrams",
            ["use set notation including n(A), union, intersection and complement"],
            "Mathematics",
            "Venn",
        ),
        (
            "5.2 - Forces and motion",
            ["draw force arrows and explain acceleration in a real scenario"],
            "Physics",
            "force and motion",
        ),
    ]

    for title, points, subject, expected_phrase in cases:
        visual_type, complexity, trigger = route(title, points, subject)

        assert complexity == "infographic", (subject, visual_type, trigger)
        assert expected_phrase.lower() in visual_type.lower()


def test_simple_svg_routes_stay_subject_specific():
    cases = [
        (
            "1.2 - Ratio and proportion",
            ["use ratio notation and fractions on a number line"],
            "Mathematics",
            "number line",
            "Number line",
        ),
        (
            "6.1 - Right-angled triangles",
            ["use Pythagoras' theorem in a simple right-angled triangle"],
            "Mathematics",
            "triangle",
            "Right triangle",
        ),
        (
            "7.2 - Acids and alkalis",
            ["use the pH scale and describe neutralisation"],
            "Chemistry",
            "pH scale",
            "pH scale",
        ),
        (
            "3.4 - Distance-time graphs",
            ["interpret a distance-time graph"],
            "Physics",
            "distance-time",
            "Distance-time",
        ),
    ]

    for title, points, subject, visual_phrase, svg_title in cases:
        visual_type, complexity, _ = route(title, points, subject)
        svg = render_topic_visual_svg(
            VisualBrief(
                topic_title=title,
                focus_point=points[0],
                trigger="benchmark",
                visual_type=visual_type,
                complexity=complexity,
                image_provider="deterministic-svg",
                prompt="benchmark",
                source_points=points,
            ),
            index=1,
        )

        assert complexity == "svg-basic", (subject, visual_type)
        assert visual_phrase.lower() in visual_type.lower()
        assert svg_title in svg


def test_statistics_is_not_used_as_generic_fallback_for_unrelated_topics():
    unrelated_cases = [
        ("Accounting", "bank reconciliation", ["cash book, bank statement, unpresented cheques"]),
        ("Chemistry", "chromatography", ["separate dyes using chromatography and calculate Rf values"]),
        ("Economics", "opportunity cost", ["choices, scarcity, opportunity cost, trade-offs"]),
    ]

    for subject, title, points in unrelated_cases:
        visual_type, complexity, _ = route(title, points, subject)

        assert complexity == "infographic"
        assert "statistics" not in visual_type.lower()
