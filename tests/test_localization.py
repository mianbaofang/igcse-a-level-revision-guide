from intl_exam_guide.models import Topic
from intl_exam_guide.planning.localization import (
    zh_point_labels,
    zh_topic_reference,
    zh_visual_type,
    zh_visual_trigger,
)


def test_zh_topic_reference_uses_topic_code_or_generic_reference():
    assert zh_topic_reference(Topic(title="A2 Ledger entries")) != zh_topic_reference(
        Topic(title="Ledger entries")
    )
    assert "A2" in zh_topic_reference(Topic(title="A2 Ledger entries"))
    assert "3.1" in zh_topic_reference(Topic(title="3.1 Source documents"))


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
    assert labels[4] == "考点要求 5"


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


def test_zh_visual_trigger_covers_process_structure_graph_flow_and_default_routes():
    triggers = {
        "apparatus process observation": "process",
        "spatial structure model": "structure",
        "curve graph movement": "graph",
        "scenario flow relationship": "flow",
        "plain visual support": "default",
    }
    outputs = {name: zh_visual_trigger(trigger) for trigger, name in triggers.items()}

    assert set(outputs) == {"process", "structure", "graph", "flow", "default"}
    assert outputs == {
        "process": "需要同时看清装置、步骤和观察结果，单纯文字不够直观。",
        "structure": "结构关系需要空间示意，单纯文字容易误解。",
        "graph": "曲线、坐标或移动方向需要图上标注。",
        "flow": "场景、因果和流程需要用箭头串起来。",
        "default": "这个知识点用图文结合更容易理解和复习。",
    }
