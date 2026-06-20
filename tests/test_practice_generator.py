from intl_exam_guide.models import SourceSnippet, Topic
from intl_exam_guide.planning.practice_generator import (
    build_practice_item,
    concrete_example,
    concrete_example_zh,
)


def test_build_practice_item_uses_requested_style_and_source_snippets():
    topic = Topic(
        title="3.1.2 - Sources and recording of data",
        points=["Source documents are purchase invoices and sales invoices."],
        source_snippets=[
            SourceSnippet(
                page=12,
                text="Source documents include purchase invoices and sales invoices.",
                matched_term="Source documents",
            )
        ],
    )

    item = build_practice_item(
        topic,
        topic.points,
        number=0,
        qualification_type="international_gcse",
        explanation_style="detective",
        output_language="en",
        subject_area="Accounting",
    )

    combined = " ".join([item.question, *item.public_solution_steps]).lower()
    assert item.command_word == "state"
    assert item.source_snippets == topic.source_snippets
    assert item.question.startswith("Case file:")
    assert "purchase invoice" in combined or "sales invoice" in combined
    assert "ledger" in combined


def test_accounting_and_chemistry_examples_route_to_subject_specific_branches():
    accounting_question, _, accounting_steps, _ = concrete_example(
        Topic(
            title="3.1.2 - Sources and recording of data",
            points=["Source documents are purchase invoices and sales invoices."],
        ),
        "Source documents are purchase invoices and sales invoices.",
        0,
        "Accounting",
    )
    accounting_text = " ".join([accounting_question, *accounting_steps]).lower()

    chemistry_question, _, chemistry_steps, _ = concrete_example(
        Topic(
            title="3.6.4 - Molar concentrations",
            points=["Concentration is related to number of moles and volume of solution."],
        ),
        "Concentration is related to number of moles and volume of solution.",
        0,
        "Chemistry",
    )
    chemistry_text = " ".join([chemistry_question, *chemistry_steps]).lower()

    assert "ledger" in accounting_text
    assert "ratio 2:5" not in accounting_text
    assert "concentration" in chemistry_text
    assert "mol/dm3" in chemistry_text
    assert "ledger" not in chemistry_text


def test_mathematics_algebra_example_is_not_generic():
    question, frame, steps, checkpoints = concrete_example(
        Topic(title="A2 - Algebra and equations", points=["Solve linear equations."]),
        "Solve linear equations.",
        0,
        "Mathematics",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "solve 3(x - 2) + 5 = 20" in combined
    assert "x = 7" in combined
    assert "memorised phrase" not in combined


def test_biology_example_is_subject_specific():
    question, frame, steps, checkpoints = concrete_example(
        Topic(title="Cell membranes", points=["Osmosis across cell membranes."]),
        "Osmosis across cell membranes.",
        0,
        "Biology",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "water moves out" in combined
    assert "osmosis" in combined
    assert "ledger" not in combined


def test_economics_example_is_subject_specific():
    question, frame, steps, checkpoints = concrete_example(
        Topic(title="Basic economic problem", points=["Scarcity creates economic choices."]),
        "Scarcity creates economic choices.",
        0,
        "Economics",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "scarce" in combined
    assert "choose" in combined or "choice" in combined
    assert "ledger" not in combined


def test_generic_example_fallback_remains_exam_focused():
    question, frame, steps, checkpoints = concrete_example(
        Topic(title="Unmapped topic", points=["Use the named concept accurately."]),
        "Use the named concept accurately.",
        0,
        "Unmapped Subject",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "memorised phrase" in combined
    assert "command word" in combined
    assert "evidence from the question" in combined


def test_chinese_practice_example_keeps_student_facing_text_chinese():
    question, frame, steps, checkpoints = concrete_example_zh(
        Topic(
            title="3.1.2 - Sources and recording of data",
            points=["Source documents are purchase invoices and sales invoices."],
        ),
        "Source documents are purchase invoices and sales invoices.",
        0,
        "Accounting",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints])

    assert "原始凭证" in combined
    assert "购货发票" in combined
    assert "source document" not in combined.lower()
    assert "purchase invoice" not in combined.lower()
