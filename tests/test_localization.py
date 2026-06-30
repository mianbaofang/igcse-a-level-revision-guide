from intl_exam_guide.models import Topic
from intl_exam_guide.planning.localization import (
    zh_point_label,
    zh_point_labels,
    zh_teachable_topic_title,
    zh_topic_reference,
    zh_visual_type,
    zh_visual_trigger,
)


def test_zh_topic_reference_uses_topic_code_or_generic_reference():
    assert zh_topic_reference(Topic(title="A2 Ledger entries")) == "第 A2 节"
    assert zh_topic_reference(Topic(title="3.1 Source documents")) == "第 3.1 节"
    assert zh_topic_reference(Topic(title="Ledger entries")) == "本节内容"


def test_zh_point_labels_maps_known_keywords_and_keeps_chinese_text():
    labels = zh_point_labels(
        [
            "source document purchase invoice",
            "demand and supply market",
            "triangle geometry construction",
            "已经是中文考点，应该保留原文",
            "unmatched source statement",
        ]
    )

    assert len(labels) == 5
    assert labels[0] == "原始凭证与发票"
    assert labels[1] == "市场需求与供给"
    assert labels[2] == "几何图形与标注"
    assert labels[3] == "已经是中文考点，应该保留原文"[:24]
    assert labels[4] == "未匹配来源陈述"


def test_chinese_point_label_uses_source_phrase_not_numbered_placeholder():
    assert zh_point_label("Their graphs, symmetries and periodicity", 0) == "图像、对称性与周期性"


def test_chinese_point_label_keeps_economics_topics_specific():
    phrases = [
        "Movements along a demand curve",
        "Shifts of a supply curve",
        "Calculation of PED",
        "Definitions of terms associated with market failure",
        "Government intervention to address market failure",
        "Supply-side policy measures",
        "Causes of inflation",
        "Determination of foreign exchange rate in foreign exchange market",
        "definitions of floating exchange rate, appreciation and depreciation",
    ]

    labels = [zh_point_label(phrase, index) for index, phrase in enumerate(phrases)]

    assert labels == [
        "需求曲线上的移动",
        "供给曲线移动",
        "需求价格弹性计算",
        "市场失灵",
        "政府干预",
        "供给侧政策",
        "通货膨胀",
        "外汇汇率",
        "浮动汇率",
    ]
    assert len(set(labels)) == len(labels)
    assert "市场需求与供给" not in labels


def test_chinese_point_label_does_not_emit_raw_english_fallback():
    label = zh_point_label("unmatched source statement", 4)

    assert label == "未匹配来源陈述"
    assert not any("a" <= character.lower() <= "z" for character in label)
    assert label != "考点要求 5"


def test_zh_point_labels_do_not_match_ph_inside_mathematics_graphs():
    labels = zh_point_labels(
        [
            "Quadratic functions and their graphs.",
            "Graphs of functions; sketching curves defined by simple equations.",
        ]
    )

    assert labels == ["二次函数图像", "函数图像"]
    assert all("酸碱" not in label for label in labels)


def test_zh_point_labels_do_not_treat_all_graphs_as_function_graphs():
    labels = zh_point_labels(
        [
            "Plot a cooling curve from experimental data.",
            "Interpret a distance-time graph for motion.",
            "Sketch the graph of a quadratic function.",
            "Explain the function of the liver.",
            "Describe business functions in an organization.",
        ]
    )

    assert labels == [
        "冷却曲线",
        "距离-时间图像",
        "二次函数",
        "肝脏功能",
        "组织中的业务职能",
    ]


def test_uncoded_math_graph_topic_prefers_teachable_point_label():
    assert zh_teachable_topic_title("Graph of a quadratic function", 1) == "二次函数"
    assert zh_teachable_topic_title("P1 Graph of a quadratic function", 1) == "P1 二次函数"


def test_uncoded_graph_titles_avoid_broad_or_math_specific_leakage():
    assert zh_teachable_topic_title("Distance-time graph", 1) == "距离-时间图像"
    assert zh_teachable_topic_title("Graphs of business functions", 1) == "业务职能图"
    assert zh_teachable_topic_title("Plot a cooling curve from experimental data.", 1) == "冷却曲线"


def test_as_math_quadratic_subtopics_do_not_collapse_to_same_chinese_title():
    labels = [
        zh_teachable_topic_title("P1.1 - Algebra: Quadratic functions and their graphs", 0),
        zh_teachable_topic_title("P1.1 - Algebra: The discriminant of a quadratic function", 1),
        zh_teachable_topic_title("P1.1 - Algebra: Factorisation of quadratic polynomials", 2),
        zh_teachable_topic_title("P1.1 - Algebra: Completing the square", 3),
        zh_teachable_topic_title("P1.1 - Algebra: Solution of quadratic equations", 4),
    ]

    assert labels == [
        "P1.1 代数：二次函数图像",
        "P1.1 代数：二次函数判别式",
        "P1.1 代数：二次多项式因式分解",
        "P1.1 代数：配方法",
        "P1.1 代数：二次方程求解",
    ]
    assert len(set(labels)) == len(labels)


def test_as_math_discrete_random_variable_subtopics_stay_specific():
    labels = [
        zh_teachable_topic_title("S1.2 - Discrete random variables: Discrete random variables", 0),
        zh_teachable_topic_title(
            "S1.2 - Discrete random variables: Measures of central tendency in probability distributions",
            1,
        ),
        zh_teachable_topic_title(
            "S1.2 - Discrete random variables: Measures of spread in probability distributions",
            2,
        ),
    ]

    assert labels == [
        "S1.2 离散随机变量：随机变量",
        "S1.2 离散随机变量：集中趋势量",
        "S1.2 离散随机变量：离散程度量",
    ]
    assert len(set(labels)) == len(labels)


def test_as_math_common_source_requirements_do_not_use_core_topic_fallbacks():
    phrases = [
        "Geometrical interpretation of algebraic solution of equations and use of intersection points of graphs.",
        "Knowledge of the effect of simple transformations on the graph of y = f (x).",
        "The intersection of a straight line and a curve.",
        "Differentiation of x n, where n is a rational number.",
        "Indefinite integration as the reverse of differentiation.",
        "Approximation of the area under a curve using the trapezium rule.",
        "The equation of a circle in the form.",
        "The sine and cosine rules.",
        "Solution of simple trigonometric equations in a given interval of degrees or radians.",
        "Logarithms and the laws of logarithms.",
        "Assigning probabilities to events using relative frequencies or equally likely outcomes.",
        "Mean and variance of the sum or difference of two independent discrete random variables.",
        "Conditions for application of a Bernoulli distribution.",
        "Knowledge and use of constant acceleration equations.",
        "Relationship between displacement, velocity and acceleration.",
        "Newton’s three laws of motion.",
        "The principle of conservation of momentum applied to two particles.",
    ]

    labels = [zh_point_label(phrase, index) for index, phrase in enumerate(phrases)]
    titles = [
        zh_teachable_topic_title(f"P1.1 - Algebra: {phrase}", index)
        for index, phrase in enumerate(phrases)
    ]

    assert not any("本节核心主题" in label for label in labels)
    assert not any("本节核心主题" in title for title in titles)


def test_as_math_localization_does_not_treat_ordinary_set_as_venn_diagram():
    assert (
        zh_point_label(
            "Questions involving regions partially above and below the x-axis will not be set.",
            0,
        )
        == "曲线与 x 轴围成面积"
    )
    assert (
        zh_point_label(
            "Questions will not be set requiring knowledge of points of inflection.",
            1,
        )
        != "集合与韦恩图"
    )
    assert (
        zh_point_label(
            "Newton’s three laws of motion, including resistive forces in a straight line.",
            2,
        )
        == "牛顿三大运动定律"
    )


def test_zh_visual_type_maps_subject_visual_routes_to_specific_labels():
    routes = {
        "source-document ledger": "会计记录流程图",
        "trial balance verification": "核对与调节流程图",
        "financial statement ratio-analysis": "财务报表与比率信息图",
        "accounting adjustment concept-effect": "会计调整影响信息图",
        "chromatography lab": "实验流程信息图",
        "gas test": "气体检验观察信息图",
        "particle states": "粒子模型示意图",
        "bond structure": "结构与性质关系信息图",
        "pH acid neutralisation": "酸碱与流程示意图",
        "demand supply market": "市场曲线与情境信息图",
        "production factors": "生产要素场景信息图",
        "set venn": "集合与韦恩图信息图",
        "triangle geometry": "几何标注图",
        "statistics probability": "统计与概率图表",
        "plain infographic": "图文结合学习图",
    }

    assert {route: zh_visual_type(route) for route in routes} == routes


def test_zh_visual_type_final_edge_terms_have_standalone_routes():
    assert zh_visual_type("accounting process") == "会计记录流程图"
    assert zh_visual_type("neutralisation") == "酸碱与流程示意图"


def test_zh_visual_type_or_conditions_work_as_standalone_triggers():
    standalone_routes = {
        "prime-entry": "会计记录流程图",
        "ledger": "会计记录流程图",
        "reconciliation": "核对与调节流程图",
        "trial balance": "核对与调节流程图",
        "financial-statement": "财务报表与比率信息图",
        "ratio-analysis": "财务报表与比率信息图",
        "concept-effect": "会计调整影响信息图",
        "lab": "实验流程信息图",
        "states": "粒子模型示意图",
        "structure": "结构与性质关系信息图",
        "acid": "酸碱与流程示意图",
        "alkali": "酸碱与流程示意图",
        "supply": "市场曲线与情境信息图",
        "market": "市场曲线与情境信息图",
        "venn": "集合与韦恩图信息图",
        "probability": "统计与概率图表",
    }

    assert {route: zh_visual_type(route) for route in standalone_routes} == standalone_routes


def test_zh_visual_trigger_covers_process_structure_graph_flow_and_default_routes():
    triggers = {
        "apparatus observation": "apparatus",
        "process observation": "process",
        "spatial model": "spatial",
        "structure model": "structure",
        "curve movement": "curve",
        "graph movement": "graph",
        "scenario relationship": "scenario",
        "flow relationship": "flow",
        "plain visual support": "default",
    }
    outputs = {name: zh_visual_trigger(trigger) for trigger, name in triggers.items()}

    assert set(outputs) == {
        "apparatus",
        "process",
        "spatial",
        "structure",
        "curve",
        "graph",
        "scenario",
        "flow",
        "default",
    }
    assert outputs == {
        "apparatus": "需要同时看清装置、步骤和观察结果，单纯文字不够直观。",
        "process": "需要同时看清装置、步骤和观察结果，单纯文字不够直观。",
        "spatial": "结构关系需要空间示意，单纯文字容易误解。",
        "structure": "结构关系需要空间示意，单纯文字容易误解。",
        "curve": "曲线、坐标或移动方向需要图上标注。",
        "graph": "曲线、坐标或移动方向需要图上标注。",
        "scenario": "场景、因果和流程需要用箭头串起来。",
        "flow": "场景、因果和流程需要用箭头串起来。",
        "default": "这个知识点用图文结合更容易理解和复习。",
    }
