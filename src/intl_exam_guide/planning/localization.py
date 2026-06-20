from __future__ import annotations

import re

from intl_exam_guide.models import Topic


ZH_POINT_KEYWORDS = [
    (("si units", "standard prefixes"), "SI 单位与词头"),
    (("record measurements", "precision"), "测量记录精度"),
    (("mean values", "anomalous"), "平均值与异常值"),
    (("tables and graphs", "represent data"), "表格与图像表示数据"),
    (("speed", "distance travelled", "per unit time"), "速度概念"),
    (("distance-time",), "距离-时间图像"),
    (("balanced and unbalanced forces",), "平衡力与非平衡力"),
    (("force and motion relationships",), "力与运动关系"),
    (("observable properties",), "可观察性质"),
    (("physical changes", "chemical changes"), "物理变化与化学变化"),
    (("conservation of mass",), "质量守恒"),
    (("source document", "purchase invoice", "sales invoice", "invoice"), "原始凭证与发票"),
    (("prime entry", "purchases journal", "sales journal"), "初始记录账簿"),
    (("ledger", "double entry"), "分类账与复式记账"),
    (("trial balance",), "试算平衡"),
    (("bank reconciliation", "unpresented cheque", "outstanding banking"), "银行对账"),
    (("control account", "suspense account", "correction of errors"), "账户核对与错误更正"),
    (("depreciation", "non-current asset"), "折旧与非流动资产"),
    (("irrecoverable", "receivables", "payables"), "应收应付与坏账处理"),
    (("accrual", "prudence", "going concern", "accounting concepts"), "会计概念应用"),
    (("financial statements", "income statement", "statement of financial position"), "财务报表"),
    (("profitability", "liquidity", "ratio"), "比率分析"),
    (("demand", "supply", "market"), "市场需求与供给"),
    (("production", "land", "labour", "capital", "enterprise"), "生产要素"),
    (("opportunity cost", "choice", "scarcity"), "选择与机会成本"),
    (("set", "venn"), "集合与韦恩图"),
    (("triangle", "geometry", "bearing", "construction"), "几何图形与标注"),
    (("statistics", "probability", "data"), "统计与概率"),
    (("bond", "structure"), "结构与性质"),
    (("chromatography",), "色谱与分离"),
    (("gas test", "gas tests"), "气体检验"),
    (("particle", "states of matter", "diffusion"), "粒子模型"),
    (("acid", "alkali", "pH", "neutralisation"), "酸碱与 pH"),
]


def zh_topic_reference(topic: Topic) -> str:
    match = re.match(r"^\s*([A-Z]\d+[A-Z]?|\d+(?:\.\d+)+)\b", topic.title)
    if match:
        return f"第 {match.group(1)} 节"
    return "本节内容"

def zh_point_label(point: str, index: int = 0) -> str:
    text = re.sub(r"\s+", " ", point.strip())
    lowered = text.lower()
    for keywords, label in ZH_POINT_KEYWORDS:
        if any(keyword.lower() in lowered for keyword in keywords):
            return label
    if re.search(r"[\u4e00-\u9fff]", text):
        return text[:24]
    return f"考点要求 {index + 1}"

def zh_point_labels(points: list[str]) -> list[str]:
    return [zh_point_label(point, index) for index, point in enumerate(points)]

def zh_visual_type(visual_type: str) -> str:
    text = visual_type.lower()
    if "source-document" in text or "prime-entry" in text or "ledger" in text or "accounting process" in text:
        return "会计记录流程图"
    if "verification" in text or "reconciliation" in text or "trial balance" in text:
        return "核对与调节流程图"
    if "financial-statement" in text or "financial statement" in text or "ratio-analysis" in text:
        return "财务报表与比率信息图"
    if "accounting adjustment" in text or "concept-effect" in text:
        return "会计调整影响信息图"
    if "chromatography" in text or "lab" in text:
        return "实验流程信息图"
    if "gas" in text:
        return "气体检验观察信息图"
    if "particle" in text or "states" in text:
        return "粒子模型示意图"
    if "bond" in text or "structure" in text:
        return "结构与性质关系信息图"
    if re.search(r"\bph\b", text) or "acid" in text or "alkali" in text or "neutralisation" in text:
        return "酸碱与流程示意图"
    if "demand" in text or "supply" in text or "market" in text:
        return "市场曲线与情境信息图"
    if "production" in text:
        return "生产要素场景信息图"
    if "set" in text or "venn" in text:
        return "集合与韦恩图信息图"
    if "triangle" in text or "geometry" in text:
        return "几何标注图"
    if "statistics" in text or "probability" in text:
        return "统计与概率图表"
    return "图文结合学习图"

def zh_visual_trigger(trigger: str) -> str:
    text = trigger.lower()
    if "apparatus" in text or "process" in text:
        return "需要同时看清装置、步骤和观察结果，单纯文字不够直观。"
    if "spatial" in text or "structure" in text:
        return "结构关系需要空间示意，单纯文字容易误解。"
    if "curve" in text or "graph" in text:
        return "曲线、坐标或移动方向需要图上标注。"
    if "scenario" in text or "flow" in text:
        return "场景、因果和流程需要用箭头串起来。"
    return "这个知识点用图文结合更容易理解和复习。"
