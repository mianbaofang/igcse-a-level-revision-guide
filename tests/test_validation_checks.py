import json

from intl_exam_guide.models import (
    AssessmentPaper,
    GuidePlan,
    GuideRunOptions,
    PracticeItem,
    Qualification,
    SourceRecord,
    SourceSnippet,
    Topic,
    TopicGuide,
    VisualBrief,
)
from intl_exam_guide.validation.checks import (
    duplicate_practice_question_topics,
    expected_topic_marker,
    has_zh_placeholder_text,
    issues_to_dict,
    is_contents_or_index_snippet,
    is_cross_subject_borrowed_practice,
    is_placeholder_practice_question,
    mixed_language_label_matches,
    normalize_practice_question,
    review_summary,
    validate_custom_image_provider,
    validate_plan,
    validate_guides,
    validate_html_language,
    validate_html_output,
    validate_html_visual_and_diagram_blocks,
    validate_image_assets,
    validate_output_package,
    validate_practice_item,
    validate_preflight_and_source,
    validate_qualification_notes,
    validate_topic_coverage,
    validate_visual_briefs,
)


def valid_plan() -> GuidePlan:
    topic = Topic(
        title="3.1 Source documents",
        points=["Students should explain source documents."],
        source_snippets=[
            SourceSnippet(
                page=12,
                text="Students should explain source documents and books of prime entry.",
                matched_term="source documents",
            )
        ],
    )
    return GuidePlan(
        qualification=Qualification(
            title="International GCSE Accounting (9215)",
            code="9215",
            qualification_type="international_gcse",
            subject_area="Accounting",
            page_url="https://example.test/accounting",
            summary=["International GCSE linear qualification."],
            topics=[topic],
            assessments=[AssessmentPaper(title="Paper 1")],
            source=SourceRecord(
                provider="oxfordaqa",
                page_url="https://example.test/accounting",
                specification_url="https://example.test/spec.pdf",
                specification_sha256="abc123",
            ),
            audience_note="International GCSE linear qualification for international students outside the UK.",
        ),
        run_options=GuideRunOptions(
            requested_subject="Accounting",
            image_provider="prompt-queue",
            explanation_style="friendly",
            output_language="en",
        ),
        topic_guides=[
            TopicGuide(
                topic_title=topic.title,
                essence="Source documents provide evidence for accounting entries.",
                analogy="Treat each invoice like a transaction label.",
                mini_worked_example="A sales invoice is first recorded in the sales day book.",
                worked_solution_steps=["Identify", "Classify", "Record", "Check"],
                pitfall="Do not post every invoice directly to final accounts.",
                checklist=["Name the document", "Choose the book", "Post the total"],
                diagram_brief="Show source documents flowing into books of prime entry.",
            )
        ],
        practice_items=[
            PracticeItem(
                topic_title=topic.title,
                command_word="Explain",
                difficulty="medium",
                focus_point="source document routing",
                question="Explain where a sales invoice is recorded first.",
                answer_frame=["Name document", "Name book", "Explain purpose"],
                public_solution_steps=["Read", "Identify", "Record", "Check"],
                answer_checkpoints=["Sales invoice", "Sales day book", "Ledger later"],
                source_points=["Students should explain source documents."],
            )
        ],
        visual_briefs=[
            VisualBrief(
                topic_title=topic.title,
                focus_point="source document flow",
                trigger="scenario flow relationship",
                visual_type="source-document ledger",
                complexity="infographic",
                image_provider="prompt-queue",
                prompt="Create a source document flow infographic.",
                source_points=["Students should explain source documents."],
            )
        ],
        diagram_briefs=[],
        revision_stages=["Read", "Practise"],
    )


def test_preflight_topic_guide_practice_and_visual_validators_pin_error_messages():
    plan = valid_plan()
    plan.run_options.requested_subject = ""
    plan.run_options.explanation_style = "unsupported"
    plan.run_options.output_language = "bilingual"
    plan.run_options.image_provider = "gpt-image-2"
    plan.qualification.source.specification_url = None
    plan.qualification.source.specification_sha256 = None
    plan.qualification.assessments = []
    plan.topic_guides = []
    plan.practice_items = []
    plan.visual_briefs = []
    plan.qualification.topics[0].points = []
    plan.qualification.topics[0].source_snippets = []

    preflight = [issue.message for issue in validate_preflight_and_source(plan)]
    topics = [issue.message for issue in validate_topic_coverage(plan)]

    assert "Missing preflight subject selection." in preflight
    assert "Missing or unsupported explanation style selection." in preflight
    assert "Missing or unsupported output language selection." in preflight
    assert "Missing or unsupported image-provider selection." in preflight
    assert "Missing specification PDF URL." in preflight
    assert "Specification PDF hash was not recorded." in preflight
    assert "No assessment papers were extracted." in preflight
    assert "Topic guide coverage does not match topic count." in preflight
    assert "No topics were selected for visual explanation." in preflight
    assert "Missing authored guide block for topic: 3.1 Source documents" in topics
    assert "Missing practice item for topic: 3.1 Source documents" in topics
    assert "Syllabus topic has no extracted body points: 3.1 Source documents" in topics
    assert "No PDF source snippet matched for topic: 3.1 Source documents" in topics


def test_preflight_catches_downloaded_specification_and_custom_provider_edges(monkeypatch):
    plan = valid_plan()
    plan.run_options.image_provider = "custom"
    plan.run_options.image_model = "SenseNova U1 Fast"
    plan.run_options.image_endpoint_url = "https://example.test/v1/images/generations"
    plan.run_options.image_api_key_env = "IMAGE_KEY_FOR_TEST"
    plan.qualification.source.specification_path = "spec.pdf"
    plan.qualification.source.provider = "cambridge"
    plan.qualification.provider = "cambridge"
    plan.qualification.source.syllabus_year_range = "2027-2029"
    plan.qualification.topics[0].title = "Content unit 1"
    plan.qualification.assessments = []
    monkeypatch.delenv("IMAGE_KEY_FOR_TEST", raising=False)

    messages = [issue.message for issue in validate_preflight_and_source(plan)]

    assert "Custom image provider environment variable is not set: IMAGE_KEY_FOR_TEST" in messages
    assert "Only 1 syllabus topics were extracted from a downloaded specification PDF." in messages
    assert (
        "Downloaded specification fell back to generic Content unit topics; "
        "the syllabus parser needs a more precise provider-specific match."
    ) in messages
    assert "Cambridge syllabus range is present but selected exam year was not recorded." in messages
    assert "No assessment papers were extracted." in messages

    plan.run_options.image_model = None
    plan.run_options.image_endpoint_url = None
    plan.run_options.image_api_key_env = None
    custom_messages = [issue.message for issue in validate_custom_image_provider(plan.run_options)]
    assert "Custom image provider is missing a model name." in custom_messages
    assert "Custom image provider is missing an endpoint URL." in custom_messages
    assert "Custom image provider is missing an API-key environment variable name." in custom_messages


def test_guide_practice_and_visual_validators_pin_branch_specific_messages():
    plan = valid_plan()
    guide = plan.topic_guides[0]
    guide.essence = ""
    guide.worked_solution_steps = ["One", "Two"]
    guide.checklist = ["One"]
    practice = plan.practice_items[0]
    practice.command_word = ""
    practice.public_solution_steps = ["One", "Two"]
    practice.answer_checkpoints = ["One"]
    practice.question = "Answer an original short exam-style question."
    visual = plan.visual_briefs[0]
    visual.focus_point = ""
    visual.prompt = ""

    guide_messages = [issue.message for issue in validate_guides(plan)]
    practice_messages = [issue.message for issue in validate_practice_item(plan, practice)]
    visual_messages = [issue.message for issue in validate_visual_briefs(plan)]

    assert "Incomplete topic guide block: 3.1 Source documents" in guide_messages
    assert "Worked example has fewer than 4 public steps: 3.1 Source documents" in guide_messages
    assert "Checklist is too short: 3.1 Source documents" in guide_messages
    assert "Practice item is missing a command word: 3.1 Source documents" in practice_messages
    assert "Practice item has too few solution steps: 3.1 Source documents" in practice_messages
    assert "Practice item has too few answer checkpoints: 3.1 Source documents" in practice_messages
    assert (
        "Practice item is an authoring frame, not a concrete worked example: 3.1 Source documents"
        in practice_messages
    )
    assert "Visual brief is missing a focus point: 3.1 Source documents" in visual_messages
    assert "Visual brief is missing an image prompt: 3.1 Source documents" in visual_messages


def test_qualification_notes_and_output_package_pin_release_quality_edges(tmp_path):
    plan = valid_plan()
    plan.qualification.source.listing_qualification_type = "gcse"
    plan.qualification.audience_note = "A qualification."
    plan.qualification.summary = []

    gcse_messages = [issue.message for issue in validate_qualification_notes(plan)]
    assert "Source listing metadata conflicts with International GCSE type." in gcse_messages
    assert "GCSE audience note does not explicitly mention international students." in gcse_messages
    assert "GCSE audience note does not explain that the course is for use outside the UK." in gcse_messages
    assert "GCSE guide does not mention the linear qualification structure." in gcse_messages

    plan.qualification.qualification_type = "international_as_a_level"
    plan.qualification.source.listing_qualification_type = "international_gcse"
    plan.qualification.provider = "pearson"
    plan.qualification.source.provider = "pearson"
    as_messages = [issue.message for issue in validate_qualification_notes(plan)]
    assert "Source listing metadata conflicts with AS-A-level type." in as_messages
    assert "AS-A-level guide does not mention the modular qualification structure." in as_messages

    output_messages = [issue.message for issue in validate_output_package(plan, tmp_path)]
    assert any(message.startswith("Sections directory is missing:") for message in output_messages)
    assert any(message.startswith("Images directory is missing:") for message in output_messages)
    assert "Run options file is missing from output directory." in output_messages
    assert any(message.startswith("Handbook package manifest is missing:") for message in output_messages)

    (tmp_path / "sections").mkdir()
    (tmp_path / "images").mkdir()
    (tmp_path / "run-options.json").write_text("{}", encoding="utf-8")
    (tmp_path / "handbook-package.json").write_text("{}", encoding="utf-8")
    output_messages = [issue.message for issue in validate_output_package(plan, tmp_path)]
    assert "Sections directory has only 0 section files." in output_messages
    assert "Visual manifest is missing from images directory." in output_messages


def test_html_language_output_assets_and_summary_helpers_have_direct_contracts(tmp_path):
    plan = valid_plan()
    html_path = tmp_path / "guide.html"
    html_path.write_text(
        '<html lang="en"><body><h1>3.1 Source documents</h1>'
        "How to Study Study Roadmap One-Sentence Essence Method Worked Example "
        "Solution Check Exam Pitfall Source anchor Concept Map "
        '<figure class="visual-example"></figure>'
        '<div class="topic-diagram"></div>'
        "复习路线 / Study Roadmap"
        "</body></html>",
        encoding="utf-8",
    )
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    (images_dir / "visual_manifest.json").write_text(
        json.dumps(
            [
                {
                    "complexity": "infographic",
                    "asset_status": "external-generation-required",
                    "file": None,
                }
            ]
        ),
        encoding="utf-8",
    )

    html_issues = [issue.message for issue in validate_html_output(plan, html_path)]
    language_issues = [issue.message for issue in validate_html_language("zh-CN", "How to Study")]
    image_issues = [issue.message for issue in validate_image_assets(plan, images_dir)]
    summary = review_summary(plan, html_path=html_path, output_dir=tmp_path)

    assert any("bilingual mixed-language label" in message for message in html_issues)
    assert any("English output contains Chinese characters" in message for message in html_issues)
    assert "Chinese output contains an English template phrase: How to Study" in language_issues
    assert any("infographic briefs are queued for external image generation" in message for message in image_issues)
    assert summary["topics"] == 1
    assert summary["pending_infographic_assets"] == 1
    assert summary["topic_diagrams_in_html"] == 1
    assert mixed_language_label_matches("<p>复习路线 / Study Roadmap</p>")
    assert expected_topic_marker("3.1 Source documents", 1, "zh-CN") == "第 3.1 节"
    assert issues_to_dict(validate_html_language("en", ""))[0] == {
        "severity": "error",
        "message": "HTML missing required section phrase: How to Study",
    }
    assert duplicate_practice_question_topics([plan.practice_items[0], plan.practice_items[0]]) == [
        "3.1 Source documents"
    ]


def test_validation_small_helpers_have_direct_branch_contracts():
    assert is_placeholder_practice_question(
        "How the syllabus idea could be used in an exam question."
    )
    assert normalize_practice_question("Case file:  Explain source documents. ") == (
        "explain source documents."
    )
    assert duplicate_practice_question_topics(object()) == []
    assert not is_contents_or_index_snippet(
        SourceSnippet(page=2, text="Students should explain source documents.", matched_term="source")
    )
    assert is_contents_or_index_snippet(
        SourceSnippet(page=12, text="Contents Specification at a glance", matched_term="contents")
    )
    assert is_contents_or_index_snippet(
        SourceSnippet(
            page=2,
            text="Source document index",
            matched_term="contents",
        )
    )
    assert is_cross_subject_borrowed_practice(
        "Find the hypotenuse of a right-angled triangle.",
        "Accounting",
    )
    assert not is_cross_subject_borrowed_practice(
        "Find the hypotenuse of a right-angled triangle.",
        "Mathematics",
    )
    assert has_zh_placeholder_text(["官方大纲要求 本单元第 1 个细分要求"])


def test_html_visual_block_validator_catches_missing_visual_and_diagram_counts():
    plan = valid_plan()

    messages = [
        issue.message
        for issue in validate_html_visual_and_diagram_blocks(plan, "<html></html>")
    ]

    assert "HTML missing required visual explanation block." in messages
    assert "HTML has 0 topic diagrams for 1 topics." in messages


def test_expected_topic_marker_localizes_all_keyword_fallback_groups():
    cases = {
        "Measurement data graph": "测量与数据",
        "Force and motion": "力与运动",
        "Material change": "材料与变化",
        "Particle state solid liquid gas": "粒子模型与物质状态",
        "Bond structure": "结构与性质",
        "Acid alkali pH": "酸碱与 pH",
        "Accounting ledger bookkeeping": "会计记录",
        "Financial statement profit position": "财务报表",
        "Ratio liquidity profitability": "比率分析",
        "Demand supply market": "市场供需",
        "Opportunity scarcity choice": "选择与机会成本",
        "Set Venn": "集合与韦恩图",
        "Triangle Pythagoras geometry": "几何图形",
        "Statistics probability": "统计与概率",
    }

    assert {title: expected_topic_marker(title, 1, "zh-CN") for title in cases} == cases


def test_validate_plan_aggregates_html_pdf_and_output_package_checks(tmp_path):
    plan = valid_plan()
    html_path = tmp_path / "missing.html"
    pdf_path = tmp_path / "missing.pdf"

    messages = [issue.message for issue in validate_plan(plan, html_path, pdf_path, tmp_path)]

    assert any(message.startswith("HTML output is missing:") for message in messages)
    assert any(message.startswith("PDF output is missing:") for message in messages)
    assert any(message.startswith("Sections directory is missing:") for message in messages)
    assert any(message.startswith("Images directory is missing:") for message in messages)


def test_custom_image_provider_accepts_complete_environment(monkeypatch):
    plan = valid_plan()
    plan.run_options.image_provider = "custom"
    plan.run_options.image_model = "reviewed-model"
    plan.run_options.image_endpoint_url = "https://example.test/images"
    plan.run_options.image_api_key_env = "IMAGE_PROVIDER_OK"
    monkeypatch.setenv("IMAGE_PROVIDER_OK", "set")

    assert validate_custom_image_provider(plan.run_options) == []
    assert not [
        issue for issue in validate_preflight_and_source(plan)
        if issue.message.startswith("Custom image provider")
    ]


def test_chinese_placeholder_checks_cover_guide_practice_and_visual_branches():
    plan = valid_plan()
    plan.run_options.output_language = "zh-CN"
    plan.topic_guides[0].essence = "官方大纲要求 本单元第 1 个细分要求"
    plan.practice_items[0].question = "官方大纲要求 知识点 1"
    plan.visual_briefs[0].prompt = "官方大纲要求 知识单元 1"

    messages = [
        *[issue.message for issue in validate_guides(plan)],
        *[issue.message for issue in validate_practice_item(plan, plan.practice_items[0])],
        *[issue.message for issue in validate_visual_briefs(plan)],
    ]

    assert "Chinese topic guide contains generic syllabus placeholder text: 3.1 Source documents" in messages
    assert "Chinese practice item contains generic syllabus placeholder text: 3.1 Source documents" in messages
    assert "Chinese visual brief contains generic syllabus placeholder text: 3.1 Source documents" in messages


def test_image_assets_catch_missing_manifest_file_reference_and_svg_shortfall(tmp_path):
    plan = valid_plan()
    plan.visual_briefs.append(
        VisualBrief(
            topic_title="3.1 Source documents",
            focus_point="source flow",
            trigger="diagram",
            visual_type="source flow",
            complexity="svg-basic",
            image_provider="deterministic-svg",
            prompt="draw source flow",
            source_points=["Students should explain source documents."],
        )
    )
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    (images_dir / "visual_manifest.json").write_text(
        json.dumps([
            {"complexity": "infographic", "asset_status": "generated", "file": "missing.png"},
        ]),
        encoding="utf-8",
    )

    messages = [issue.message for issue in validate_image_assets(plan, images_dir)]

    assert "Images directory has 0 SVG drafts for 1 SVG-safe visual briefs." in messages
    assert "Visual manifest references a missing image file: missing.png" in messages
    assert "0/1 selected infographic briefs have generated raster assets." in messages


def test_review_summary_counts_generated_fallback_and_pending_assets(tmp_path):
    plan = valid_plan()
    output_dir = tmp_path
    images_dir = output_dir / "images"
    sections_dir = output_dir / "sections"
    images_dir.mkdir()
    sections_dir.mkdir()
    (sections_dir / "cover.txt").write_text("cover", encoding="utf-8")
    (output_dir / "handbook-package.json").write_text("{}", encoding="utf-8")
    (images_dir / "generated.png").write_bytes(b"png")
    (images_dir / "fallback.svg").write_text("<svg></svg>", encoding="utf-8")
    (images_dir / "visual_manifest.json").write_text(
        json.dumps([
            {"complexity": "infographic", "asset_status": "generated", "file": "generated.png"},
            {"complexity": "infographic", "asset_status": "svg-fallback-needs-review", "file": "fallback.svg"},
        ]),
        encoding="utf-8",
    )

    summary = review_summary(plan, output_dir=output_dir)

    assert summary["section_files"] == 1
    assert summary["image_files"] == 2
    assert summary["generated_infographic_assets"] == 1
    assert summary["svg_fallback_assets"] == 1
    assert summary["pending_infographic_assets"] == 1
    assert summary["has_visual_manifest"] is True
    assert summary["has_package_manifest"] is True
