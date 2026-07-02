from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "write_concept_explanations_from_jobs.py"
SCRIPT_SPEC = spec_from_file_location("write_concept_explanations_from_jobs", SCRIPT_PATH)
assert SCRIPT_SPEC and SCRIPT_SPEC.loader
SCRIPT_MODULE = module_from_spec(SCRIPT_SPEC)
SCRIPT_SPEC.loader.exec_module(SCRIPT_MODULE)


def test_momentum_restricted_to_straight_line_does_not_use_coordinate_geometry():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "M1.4 - Momentum and impulse (Restricted to motion in a straight line): Concept of momentum",
            "source_points": ["Concept of momentum. Momentum = mv"],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )

    text = " ".join(entry["explanations"]).lower()
    assert "p = mv" in text
    assert "midpoint" not in text
    assert "intercepts" not in text


def test_competitive_market_process_explanation_is_not_generic_economics_template():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "3.1.4.5 - The competitive market process",
            "source_points": [
                "Firms do not just compete on price but competition will also lead firms to strive to improve products, reduce costs and improve the quality of the service provided."
            ],
            "output_language": "en",
            "subject_pack": "economics",
        }
    )

    text = " ".join(
        [
            entry["essence"],
            entry["analogy"],
            entry["mini_worked_example"],
            *entry["worked_solution_steps"],
            entry["pitfall"],
            *entry["explanations"],
        ]
    ).lower()
    assert "non-price competition" in text
    assert "improve product quality" in text
    assert "real market situation" not in text
    assert "set of nudges" not in text


def test_generic_economics_concept_explanation_uses_source_point_not_empty_template():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "3.1.1.1 - Economic activity",
            "source_points": [
                "Needs and wants",
                "The central purpose of economic activity",
                "The key economic decisions",
            ],
            "output_language": "en",
            "subject_pack": "economics",
        }
    )

    first = entry["explanations"][0].lower()

    assert "economic activity is about needs and wants" in first
    assert "names the exact idea" not in first
    assert "3.1.1.1" not in first


def test_accounting_business_topic_does_not_trigger_trigonometry_template():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "1.1 - Types of business organisation",
            "source_points": [
                "a) Explain the characteristics of:",
                "public sector organisations",
                "private sector organisations",
                "sole traders",
                "partnerships.",
            ],
            "output_language": "en",
            "subject_pack": "accounting",
        }
    )

    text = " ".join(entry["explanations"]).lower()

    assert "angles to side ratios" not in text
    assert "periodic graph values" not in text
    assert "public sector organisations" in text


def test_term_support_language_still_writes_english_concept_body():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "P1.1 Algebra: Quadratic functions",
            "source_points": ["Sketch and interpret quadratic graphs."],
            "output_language": "zh-CN",
            "subject_pack": "mathematics",
        }
    )

    text = " ".join(
        [
            entry["essence"],
            entry["analogy"],
            entry["mini_worked_example"],
            entry["pitfall"],
            *entry["worked_solution_steps"],
            *entry["explanations"],
        ]
    )

    assert "quadratic" in text.lower()
    assert not any("\u4e00" <= char <= "\u9fff" for char in text)


def test_business_topic_does_not_trigger_math_or_physics_templates():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "1.2 - Stakeholders",
            "source_points": [
                "Main stakeholders of businesses.",
                "Objectives of stakeholders and how they can conflict.",
            ],
            "output_language": "en",
            "subject_pack": "business",
        }
    )

    text = " ".join(
        [
            entry["essence"],
            entry["analogy"],
            entry["mini_worked_example"],
            entry["pitfall"],
            *entry["worked_solution_steps"],
            *entry["explanations"],
        ]
    ).lower()

    assert "business" in text
    assert "stakeholder" in text
    assert "angles to side ratios" not in text
    assert "periodic graph values" not in text
    assert "two skaters" not in text
    assert "masses and velocities" not in text
    assert "momentum equation" not in text


def test_accounting_depreciation_does_not_trigger_coordinate_geometry_template():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "2.5 - Depreciation",
            "source_points": [
                "a) Explain the causes of depreciation.",
                "b) Distinguish between straight line and reducing balance methods of depreciation.",
            ],
            "output_language": "en",
            "subject_pack": "accounting",
        }
    )

    text = " ".join(entry["explanations"]).lower()

    assert "gradient, intercepts, coordinates" not in text
    assert "causes of depreciation" in text


def test_same_named_accounting_units_keep_section_identity():
    first = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "2.5 - Depreciation",
            "source_points": ["a) Explain the causes of depreciation."],
            "output_language": "en",
            "subject_pack": "accounting",
        }
    )
    second = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "5.2 - Depreciation",
            "source_points": ["a) Explain the causes of depreciation."],
            "output_language": "en",
            "subject_pack": "accounting",
        }
    )

    assert first["explanations"] != second["explanations"]
    assert "2.5 - Depreciation" in first["explanations"][0]
    assert "5.2 - Depreciation" in second["explanations"][0]


def test_accounting_wrapped_source_points_are_merged_before_writing():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "5.3 - Irrecoverable debts",
            "source_points": [
                "a) Explain why it is necessary to provide a provision for",
                "irrecoverable debts.",
                "b) Distinguish between an irrecoverable debt and a provision for",
                "an irrecoverable debt.",
            ],
            "output_language": "en",
            "subject_pack": "accounting",
        }
    )

    text = " ".join(entry["explanations"]).lower()

    assert "provide a provision for irrecoverable debts" in text
    assert "provide a provision for and" not in text


def test_competition_dynamics_explanation_is_distinct_from_basic_competitive_process():
    basic = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "3.1.4.5 - The competitive market process",
            "source_points": [
                "Firms do not just compete on price but competition will also lead firms to strive to improve products, reduce costs and improve the quality of the service provided."
            ],
            "output_language": "en",
            "subject_pack": "economics",
        }
    )
    dynamic = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "3.3.3.8 - The dynamics of competition and competitive market processes",
            "source_points": [
                "Short-run and long-run benefits which may result from competition and competitive market processes."
            ],
            "output_language": "en",
            "subject_pack": "economics",
        }
    )

    assert basic["explanations"] != dynamic["explanations"]
    dynamic_text = " ".join(dynamic["explanations"]).lower()
    assert "short-run" in dynamic_text
    assert "long-run" in dynamic_text
