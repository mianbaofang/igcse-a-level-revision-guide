from __future__ import annotations

import html
import re

from intl_exam_guide.models import VisualBrief


def render_topic_visual_svg(visual: VisualBrief, index: int, language: str = "en") -> str:
    if language == "zh-CN":
        return render_zh_visual_svg(visual, index)
    text = visual.visual_type.lower()
    tokens = set(re.findall(r"[a-z0-9]+", text))
    if any(word in text for word in ["ledger", "book-of-prime-entry", "source-document", "accounting process"]):
        return render_accounting_flow_svg(index, "en")
    if any(word in text for word in ["reconciliation", "verification", "trial balance"]):
        return render_reconciliation_svg(index, "en")
    if any(word in text for word in ["financial-statement", "financial statement", "ratio-analysis", "ratio analysis"]):
        return render_financial_statement_svg(index, "en")
    if any(word in text for word in ["demand-supply", "demand supply", "market scenario"]):
        return render_market_svg(index, "en")
    if any(word in text for word in ["factors of production", "production-chain", "opportunity-cost", "opportunity cost"]):
        return render_economic_flow_svg(index, "en")
    if any(word in text for word in ["set notation", "venn"]):
        return render_venn_svg(index, "en")
    if any(word in text for word in ["force and motion", "force arrows"]):
        return render_force_svg(index, "en")
    if any(word in text for word in ["gas tests", "common gas"]):
        return render_gas_tests_svg(index, "en")
    if any(word in tokens for word in ["acid", "acids", "base", "bases", "salt", "salts", "ph"]):
        return render_ph_svg(index)
    if any(word in text for word in ["solid", "liquid", "particle", "atom"]):
        return render_particles_svg(index)
    if any(word in text for word in ["bond", "ionic", "covalent", "metallic", "structure"]):
        return render_bonding_svg(index)
    if any(word in text for word in ["organic", "hydrocarbon", "carbon"]):
        return render_organic_svg(index)
    if any(
        word in text
        for word in ["chemical analysis", "chromatography", "identification of common gases", "identification of ions"]
    ):
        return render_analysis_svg(index)
    if any(word in text for word in ["distance-time", "motion graph"]):
        return render_motion_svg(index)
    if any(word in text for word in ["rate", "equilibrium"]):
        return render_rate_svg(index)
    if any(word in text for word in ["energy", "exothermic", "endothermic"]):
        return render_energy_svg(index)
    if any(word in text for word in ["number line", "fraction", "ratio"]):
        return render_number_svg(index)
    if any(word in text for word in ["function graph", "equation-balance", "algebra"]):
        return render_algebra_svg(index)
    if any(word in text for word in ["statistics chart", "probability"]):
        return render_statistics_svg(index)
    if any(
        word in text
        for word in ["geometry diagram", "triangle", "trigonometry", "pythagoras", "transformation"]
    ):
        return render_triangle_svg(index)
    if any(word in text for word in ["data table", "graph interpretation"]):
        return render_statistics_svg(index)
    return render_concept_fallback_svg(index, visual.visual_type or "Study visual")


def render_number_svg(index: int) -> str:
    ticks = []
    labels = []
    for value in range(-3, 4):
        x = 104 + (value + 3) * 56
        ticks.append(f'<path d="M{x} 170v16" stroke="#172033" stroke-width="3"/>')
        labels.append(
            f'<text x="{x - 7}" y="212" font-size="17" font-weight="800" fill="#172033">{value}</text>'
        )
    fraction_segments = []
    for number in range(4):
        color = "#1354a5" if number < 3 else "#edf4ff"
        fraction_segments.append(
            f'<rect x="{456 + number * 42}" y="112" width="42" height="56" fill="{color}" stroke="#172033" stroke-width="2"/>'
        )
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Number line, fraction bar, and ratio diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="52" y="70" fill="#1354a5" font-size="23" font-weight="800">Number sense</text>
  <path d="M88 178h368" stroke="#172033" stroke-width="4" marker-end="url(#numarrow-{index})"/>
  <defs><marker id="numarrow-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
  {''.join(ticks)}
  {''.join(labels)}
  <circle cx="328" cy="178" r="10" fill="#b83246"/>
  <text x="92" y="238" font-size="15" fill="#5b677a">
    <tspan x="92" dy="0">compare positions</tspan>
    <tspan x="92" dy="20">then check decimals and bounds</tspan>
  </text>
  <text x="454" y="94" font-size="19" font-weight="800" fill="#b83246">3 / 4</text>
  {''.join(fraction_segments)}
  <text x="454" y="198" font-size="16" fill="#5b677a">fraction bar: part-whole</text>
  <rect x="456" y="238" width="58" height="40" rx="8" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="3"/>
  <rect x="522" y="238" width="58" height="40" rx="8" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="3"/>
  <rect x="596" y="238" width="58" height="40" rx="8" fill="#fff1f3" stroke="#b83246" stroke-width="3"/>
  <text x="462" y="304" font-size="18" font-weight="800" fill="#1f7a5b">2</text>
  <text x="598" y="304" font-size="18" font-weight="800" fill="#b83246">1</text>
  <text x="504" y="314" font-size="15" fill="#5b677a">ratio blocks</text>
</svg>
"""


def render_algebra_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Function graph and equation balance</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="52" y="68" fill="#1354a5" font-size="23" font-weight="800">Algebra links symbols to shapes</text>
  <rect x="58" y="92" width="282" height="210" rx="14" fill="#f7fbff" stroke="#9cbce8"/>
  <path d="M96 262V118M96 262h210" stroke="#172033" stroke-width="4"/>
  <path d="M100 244C130 228 160 204 190 174C226 138 256 126 302 126" fill="none" stroke="#b83246" stroke-width="5"/>
  <path d="M97 207h208M145 262V120M195 262V120M245 262V120" stroke="#d7deea" stroke-width="2"/>
  <text x="110" y="136" font-size="18" font-weight="800" fill="#b83246">graph of a rule</text>
  <text x="248" y="286" font-size="17" font-weight="800">x</text>
  <text x="76" y="130" font-size="17" font-weight="800">y</text>
  <rect x="396" y="104" width="260" height="178" rx="16" fill="#fffaf1" stroke="#d99a24" stroke-width="3"/>
  <path d="M526 138v88M448 226h156" stroke="#172033" stroke-width="5" stroke-linecap="round"/>
  <path d="M468 154l-42 72h84z" fill="#edf4ff" stroke="#1354a5" stroke-width="3"/>
  <path d="M584 154l-42 72h84z" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="3"/>
  <text x="436" y="205" font-size="25" font-weight="800" fill="#1354a5">x + 3</text>
  <text x="564" y="205" font-size="25" font-weight="800" fill="#1f7a5b">7</text>
  <text x="430" y="82" font-size="18" font-weight="800" fill="#d99a24">equation balance</text>
  <text x="418" y="314" font-size="16" fill="#5b677a">transform both sides, then check the solution</text>
</svg>
"""


def render_statistics_svg(index: int) -> str:
    points = [(300, 228), (328, 205), (358, 214), (388, 174), (424, 158), (456, 126)]
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="7" fill="#b83246"/>' for x, y in points)
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Statistics chart and probability visual</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="52" y="68" fill="#1354a5" font-size="23" font-weight="800">Data becomes evidence</text>
  <rect x="58" y="94" width="178" height="190" rx="14" fill="#f7fbff" stroke="#9cbce8"/>
  <path d="M92 246V126M92 246h112" stroke="#172033" stroke-width="4"/>
  <rect x="108" y="200" width="24" height="46" fill="#1354a5"/>
  <rect x="144" y="170" width="24" height="76" fill="#1f7a5b"/>
  <rect x="180" y="140" width="24" height="106" fill="#d99a24"/>
  <text x="78" y="274" font-size="14" fill="#5b677a">compare groups</text>
  <rect x="268" y="94" width="210" height="190" rx="14" fill="#fffaf1" stroke="#d99a24"/>
  <path d="M300 246V120M300 246h168" stroke="#172033" stroke-width="4"/>
  {dots}
  <path d="M300 236L462 124" stroke="#1f7a5b" stroke-width="4" stroke-dasharray="8 7"/>
  <text x="310" y="274" font-size="14" fill="#5b677a">describe trend</text>
  <rect x="510" y="94" width="150" height="190" rx="14" fill="#fff7f8" stroke="#e5aab4"/>
  <circle cx="545" cy="164" r="7" fill="#b83246"/>
  <path d="M552 164h28M580 164l38-42M580 164l38 42" stroke="#172033" stroke-width="3" fill="none"/>
  <circle cx="624" cy="122" r="7" fill="#1f7a5b"/>
  <circle cx="624" cy="206" r="7" fill="#d99a24"/>
  <text x="528" y="238" font-size="14" fill="#5b677a">probability tree</text>
</svg>
"""


def render_particles_svg(index: int) -> str:
    dots = []
    for row in range(3):
        for col in range(4):
            dots.append(f'<circle cx="{92 + col * 22}" cy="{102 + row * 22}" r="7" fill="#1354a5"/>')
    liquid = [
        '<circle cx="330" cy="118" r="8" fill="#1f7a5b"/>',
        '<circle cx="356" cy="132" r="8" fill="#1f7a5b"/>',
        '<circle cx="315" cy="150" r="8" fill="#1f7a5b"/>',
        '<circle cx="372" cy="164" r="8" fill="#1f7a5b"/>',
        '<circle cx="342" cy="176" r="8" fill="#1f7a5b"/>',
    ]
    gas = [
        '<circle cx="535" cy="92" r="8" fill="#b83246"/>',
        '<circle cx="606" cy="125" r="8" fill="#b83246"/>',
        '<circle cx="558" cy="180" r="8" fill="#b83246"/>',
    ]
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Particle model diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="48" y="58" fill="#b83246" font-size="20" font-weight="800">Particle model</text>
  <rect x="70" y="82" width="130" height="130" rx="14" fill="#edf4ff" stroke="#9cbce8"/>
  <rect x="290" y="82" width="130" height="130" rx="14" fill="#ecf8f3" stroke="#a7d5c3"/>
  <rect x="510" y="82" width="130" height="130" rx="14" fill="#fff1f3" stroke="#e5aab4"/>
  {''.join(dots)}
  {''.join(liquid)}
  {''.join(gas)}
  <path d="M220 146h48" stroke="#d99a24" stroke-width="4" marker-end="url(#arrow-{index})"/>
  <path d="M440 146h48" stroke="#d99a24" stroke-width="4" marker-end="url(#arrow-{index})"/>
  <defs><marker id="arrow-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#d99a24"/></marker></defs>
  <text x="92" y="250" font-size="22" font-weight="800" fill="#1354a5">solid</text>
  <text x="322" y="250" font-size="22" font-weight="800" fill="#1f7a5b">liquid</text>
  <text x="552" y="250" font-size="22" font-weight="800" fill="#b83246">gas</text>
  <text x="70" y="292" font-size="16" fill="#5b677a">arrangement and movement explain state changes</text>
</svg>
"""


def render_triangle_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Right triangle diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="62" y="70" fill="#1354a5" font-size="22" font-weight="800">5-12-13 right triangle</text>
  <path d="M220 285h92L220 65z" fill="#ffffff" stroke="#111827" stroke-width="5"/>
  <path d="M220 259h26v26" fill="none" stroke="#111827" stroke-width="4"/>
  <text x="187" y="67" font-size="34" font-weight="800">A</text>
  <text x="320" y="306" font-size="34" font-weight="800">B</text>
  <text x="187" y="306" font-size="34" font-weight="800">C</text>
  <text x="245" y="324" font-size="25" font-weight="700">5 cm</text>
  <text x="120" y="184" font-size="25" font-weight="700">12 cm</text>
  <text x="288" y="166" font-size="25" font-weight="700">13 cm</text>
  <rect x="440" y="108" width="190" height="130" rx="14" fill="#f7fbff" stroke="#9cbce8"/>
  <text x="466" y="150" font-size="22" font-weight="800" fill="#b83246">c² = a² + b²</text>
  <text x="466" y="188" font-size="19" fill="#172033">5² + 12² = 169</text>
  <text x="466" y="222" font-size="19" fill="#172033">c = 13 cm</text>
</svg>
"""


def render_motion_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Distance-time graph</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="70" fill="#1354a5" font-size="23" font-weight="800">Distance-time graph</text>
  <path d="M100 280V92M100 280h500" stroke="#172033" stroke-width="4"/>
  <path d="M105 255L235 195L365 195L540 105" fill="none" stroke="#1354a5" stroke-width="6" stroke-linejoin="round"/>
  <circle cx="105" cy="255" r="7" fill="#b83246"/>
  <circle cx="235" cy="195" r="7" fill="#b83246"/>
  <circle cx="365" cy="195" r="7" fill="#b83246"/>
  <circle cx="540" cy="105" r="7" fill="#b83246"/>
  <path d="M235 195h130" stroke="#d99a24" stroke-width="5"/>
  <text x="118" y="104" font-size="17" font-weight="800" fill="#b83246">distance</text>
  <text x="552" y="310" font-size="17" font-weight="800" fill="#1f7a5b">time</text>
  <text x="128" y="236" font-size="16" fill="#5b677a">moving</text>
  <text x="260" y="184" font-size="16" fill="#9b6a10">stationary</text>
  <text x="430" y="136" font-size="16" fill="#5b677a">faster speed</text>
  <text x="104" y="322" font-size="15" fill="#5b677a">steeper line = greater speed</text>
</svg>
"""


def render_rate_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Rate of reaction graph</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <path d="M95 275V70M95 275h520" stroke="#172033" stroke-width="4"/>
  <path d="M100 260C180 150 255 100 410 94C500 91 565 91 615 91" fill="none" stroke="#1354a5" stroke-width="6"/>
  <path d="M100 260C170 190 250 160 420 156C505 154 570 154 615 154" fill="none" stroke="#d99a24" stroke-width="6"/>
  <text x="118" y="66" font-size="18" font-weight="800" fill="#b83246">product formed</text>
  <text x="548" y="306" font-size="18" font-weight="800" fill="#1f7a5b">time</text>
  <text x="430" y="88" font-size="18" fill="#1354a5">faster rate</text>
  <text x="430" y="150" font-size="18" fill="#9b6a10">slower rate</text>
</svg>
"""


def render_energy_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Reaction energy profile</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <path d="M90 280V70M90 280h540" stroke="#172033" stroke-width="4"/>
  <path d="M120 245C230 245 235 88 350 88C465 88 470 185 600 185" fill="none" stroke="#b83246" stroke-width="6"/>
  <path d="M145 245h92M505 185h92" stroke="#1f7a5b" stroke-width="5"/>
  <path d="M350 98v135" stroke="#d99a24" stroke-width="4" stroke-dasharray="8 7"/>
  <text x="120" y="270" font-size="17" font-weight="800">reactants</text>
  <text x="500" y="210" font-size="17" font-weight="800">products</text>
  <text x="365" y="160" font-size="18" fill="#9b6a10">activation energy</text>
  <text x="110" y="62" font-size="18" font-weight="800" fill="#b83246">energy</text>
</svg>
"""


def render_ph_svg(index: int) -> str:
    segments = []
    colors = ["#b83246", "#d45c3f", "#d99a24", "#95b84a", "#1f7a5b", "#217c9b", "#1354a5"]
    for i, color in enumerate(colors):
        segments.append(f'<rect x="{84 + i * 76}" y="146" width="76" height="54" fill="{color}"/>')
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">pH scale and salt preparation</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="70" y="88" font-size="24" font-weight="800" fill="#1354a5">pH scale</text>
  {''.join(segments)}
  <text x="86" y="226" font-size="18" font-weight="800">0</text>
  <text x="300" y="226" font-size="18" font-weight="800">7</text>
  <text x="590" y="226" font-size="18" font-weight="800">14</text>
  <text x="94" y="130" font-size="18" fill="#b83246">acid</text>
  <text x="312" y="130" font-size="18" fill="#1f7a5b">neutral</text>
  <text x="548" y="130" font-size="18" fill="#1354a5">alkali</text>
</svg>
"""


def render_organic_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Hydrocarbon chain diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="70" y="82" font-size="24" font-weight="800" fill="#1354a5">hydrocarbon model</text>
  <path d="M178 178h100h100h100" stroke="#172033" stroke-width="5"/>
  <g fill="#1354a5" stroke="#172033" stroke-width="3">
    <circle cx="178" cy="178" r="32"/><circle cx="278" cy="178" r="32"/>
    <circle cx="378" cy="178" r="32"/><circle cx="478" cy="178" r="32"/>
  </g>
  <g fill="#ffffff" font-size="24" font-weight="800" text-anchor="middle">
    <text x="178" y="187">C</text><text x="278" y="187">C</text>
    <text x="378" y="187">C</text><text x="478" y="187">C</text>
  </g>
  <text x="160" y="272" font-size="18" fill="#5b677a">structure helps explain reactions and properties</text>
</svg>
"""


def render_analysis_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Chromatography diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <rect x="140" y="72" width="170" height="235" rx="18" fill="#f7fbff" stroke="#9cbce8" stroke-width="3"/>
  <path d="M170 250h110" stroke="#1354a5" stroke-width="4"/>
  <path d="M225 250V98" stroke="#172033" stroke-width="3"/>
  <circle cx="225" cy="223" r="11" fill="#b83246"/>
  <circle cx="225" cy="178" r="11" fill="#d99a24"/>
  <circle cx="225" cy="130" r="11" fill="#1f7a5b"/>
  <path d="M430 96h105M430 154h105M430 212h105" stroke="#d7deea" stroke-width="4"/>
  <text x="430" y="88" font-size="18" font-weight="800" fill="#1f7a5b">separated spots</text>
  <text x="430" y="246" font-size="18" fill="#5b677a">compare position and colour</text>
</svg>
"""


def render_bonding_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Bonding and structure diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="70" y="74" font-size="24" font-weight="800" fill="#1354a5">bonding model</text>
  <rect x="74" y="104" width="150" height="150" rx="16" fill="#edf4ff" stroke="#9cbce8"/>
  <rect x="285" y="104" width="150" height="150" rx="16" fill="#ecf8f3" stroke="#a7d5c3"/>
  <rect x="496" y="104" width="150" height="150" rx="16" fill="#fff1f3" stroke="#e5aab4"/>
  <g fill="#1354a5"><circle cx="124" cy="150" r="16"/><circle cx="174" cy="150" r="16"/><circle cx="124" cy="202" r="16"/><circle cx="174" cy="202" r="16"/></g>
  <g fill="#ffffff" font-size="15" font-weight="800" text-anchor="middle"><text x="124" y="155">+</text><text x="174" y="155">-</text><text x="124" y="207">-</text><text x="174" y="207">+</text></g>
  <g stroke="#172033" stroke-width="4"><path d="M332 178h56"/><path d="M360 150v56"/></g>
  <g fill="#1f7a5b"><circle cx="332" cy="178" r="18"/><circle cx="388" cy="178" r="18"/><circle cx="360" cy="150" r="18"/><circle cx="360" cy="206" r="18"/></g>
  <g fill="#b83246"><circle cx="542" cy="150" r="16"/><circle cx="600" cy="150" r="16"/><circle cx="542" cy="204" r="16"/><circle cx="600" cy="204" r="16"/></g>
  <path d="M526 176h90M571 132v92" stroke="#d99a24" stroke-width="3" stroke-dasharray="6 6"/>
  <text x="116" y="286" font-size="20" font-weight="800" fill="#1354a5">ionic</text>
  <text x="315" y="286" font-size="20" font-weight="800" fill="#1f7a5b">covalent</text>
  <text x="530" y="286" font-size="20" font-weight="800" fill="#b83246">metallic</text>
</svg>
"""

def render_accounting_flow_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    labels = (
        ("原始凭证", "日记账", "分类账", "试算平衡")
        if zh
        else ("Source document", "Prime entry", "Ledger", "Trial balance")
    )
    title = "会计记录流程" if zh else "Accounting records flow"
    return render_flow_svg(index, title, labels, "#1354a5", "#1f7a5b")


def render_reconciliation_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    labels = (
        ("现金账", "银行对账单", "差异项目", "调整后余额")
        if zh
        else ("Cash book", "Bank statement", "Timing items", "Adjusted balance")
    )
    title = "核对与调节流程" if zh else "Verification and reconciliation"
    return render_flow_svg(index, title, labels, "#1f7a5b", "#d99a24")


def render_financial_statement_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "财务报表结构" if zh else "Financial statement layout"
    labels = (
        ("收入", "成本", "利润", "资产", "负债", "资本")
        if zh
        else ("Revenue", "Cost", "Profit", "Assets", "Liabilities", "Capital")
    )
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <rect x="64" y="104" width="260" height="198" rx="14" fill="#fffaf1" stroke="#d99a24" stroke-width="3"/>
  <rect x="396" y="104" width="260" height="198" rx="14" fill="#f7fbff" stroke="#9cbce8" stroke-width="3"/>
  <text x="88" y="142" font-size="20" font-weight="800" fill="#b83246">{html_escape(labels[0])}</text>
  <text x="88" y="182" font-size="20" font-weight="800" fill="#172033">- {html_escape(labels[1])}</text>
  <path d="M88 205h190" stroke="#d7deea" stroke-width="4"/>
  <text x="88" y="246" font-size="22" font-weight="800" fill="#1f7a5b">= {html_escape(labels[2])}</text>
  <text x="420" y="142" font-size="20" font-weight="800" fill="#1354a5">{html_escape(labels[3])}</text>
  <text x="420" y="184" font-size="20" font-weight="800" fill="#b83246">- {html_escape(labels[4])}</text>
  <path d="M420 205h190" stroke="#d7deea" stroke-width="4"/>
  <text x="420" y="246" font-size="22" font-weight="800" fill="#1f7a5b">= {html_escape(labels[5])}</text>
</svg>
"""


def render_market_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "市场供需图" if zh else "Demand and supply market diagram"
    demand = "需求" if zh else "Demand"
    supply = "供给" if zh else "Supply"
    price = "价格" if zh else "Price"
    qty = "数量" if zh else "Quantity"
    equilibrium = "均衡" if zh else "Equilibrium"
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="60" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <path d="M118 284V92M118 284h470" stroke="#172033" stroke-width="4"/>
  <path d="M150 118L548 260" stroke="#b83246" stroke-width="6"/>
  <path d="M150 260L548 118" stroke="#1f7a5b" stroke-width="6"/>
  <circle cx="350" cy="188" r="10" fill="#d99a24"/>
  <path d="M350 188v96M118 188h232" stroke="#d99a24" stroke-width="3" stroke-dasharray="7 6"/>
  <text x="555" y="266" font-size="18" font-weight="800" fill="#b83246">{html_escape(demand)}</text>
  <text x="552" y="126" font-size="18" font-weight="800" fill="#1f7a5b">{html_escape(supply)}</text>
  <text x="132" y="96" font-size="17" font-weight="800">{html_escape(price)}</text>
  <text x="520" y="314" font-size="17" font-weight="800">{html_escape(qty)}</text>
  <text x="366" y="184" font-size="17" font-weight="800" fill="#9b6a10">{html_escape(equilibrium)}</text>
</svg>
"""


def render_economic_flow_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    labels = (
        ("选择", "资源限制", "机会成本", "经济结果")
        if zh
        else ("Choice", "Scarce resources", "Opportunity cost", "Economic outcome")
    )
    title = "经济选择流程" if zh else "Economic choice flow"
    return render_flow_svg(index, title, labels, "#d99a24", "#1354a5")


def render_venn_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "集合与韦恩图" if zh else "Set notation and Venn regions"
    union = "并集" if zh else "Union"
    intersect = "交集" if zh else "Intersection"
    outside = "补集" if zh else "Complement"
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <rect x="86" y="104" width="360" height="198" rx="16" fill="#f7fbff" stroke="#172033" stroke-width="3"/>
  <circle cx="228" cy="200" r="82" fill="#1354a5" fill-opacity=".35" stroke="#1354a5" stroke-width="4"/>
  <circle cx="310" cy="200" r="82" fill="#b83246" fill-opacity=".32" stroke="#b83246" stroke-width="4"/>
  <text x="178" y="202" font-size="22" font-weight="800">A</text>
  <text x="350" y="202" font-size="22" font-weight="800">B</text>
  <text x="250" y="205" font-size="18" font-weight="800" fill="#172033">A ∩ B</text>
  <rect x="488" y="118" width="150" height="46" rx="10" fill="#edf4ff" stroke="#9cbce8"/>
  <rect x="488" y="178" width="150" height="46" rx="10" fill="#fff1f3" stroke="#e5aab4"/>
  <rect x="488" y="238" width="150" height="46" rx="10" fill="#fffaf1" stroke="#d99a24"/>
  <text x="508" y="148" font-size="18" font-weight="800" fill="#1354a5">{html_escape(union)}</text>
  <text x="508" y="208" font-size="18" font-weight="800" fill="#b83246">{html_escape(intersect)}</text>
  <text x="508" y="268" font-size="18" font-weight="800" fill="#9b6a10">{html_escape(outside)}</text>
</svg>
"""


def render_force_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "力与运动示意图" if zh else "Force and motion diagram"
    force = "合力" if zh else "resultant force"
    accel = "加速度方向" if zh else "acceleration"
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <rect x="258" y="152" width="170" height="88" rx="16" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <path d="M248 196h-126" stroke="#b83246" stroke-width="7" marker-end="url(#force-left-{index})"/>
  <path d="M438 196h164" stroke="#1f7a5b" stroke-width="9" marker-end="url(#force-right-{index})"/>
  <defs>
    <marker id="force-left-{index}" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M10 0 0 5 10 10z" fill="#b83246"/></marker>
    <marker id="force-right-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#1f7a5b"/></marker>
  </defs>
  <text x="284" y="204" font-size="22" font-weight="800">object</text>
  <text x="110" y="164" font-size="17" font-weight="800" fill="#b83246">smaller force</text>
  <text x="452" y="164" font-size="17" font-weight="800" fill="#1f7a5b">{html_escape(force)}</text>
  <text x="452" y="274" font-size="17" font-weight="800" fill="#1f7a5b">{html_escape(accel)} →</text>
</svg>
"""


def render_gas_tests_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "气体检验观察图" if zh else "Common gas tests observation chart"
    headers = (
        ("气体", "检验", "观察")
        if zh
        else ("Gas", "Test", "Observation")
    )
    rows = (
        (("氧气", "带火星木条", "复燃"), ("氢气", "燃着木条", "爆鸣"), ("二氧化碳", "石灰水", "变浑浊"))
        if zh
        else (("Oxygen", "glowing splint", "relights"), ("Hydrogen", "lit splint", "squeaky pop"), ("CO₂", "limewater", "turns cloudy"))
    )
    row_svg = []
    for row_index, row in enumerate(rows):
        y = 130 + row_index * 56
        row_svg.append(f'<rect x="70" y="{y - 30}" width="580" height="48" fill="#fbfcff" stroke="#d7deea"/>')
        row_svg.append(f'<text x="92" y="{y}" font-size="17" font-weight="800" fill="#1354a5">{html_escape(row[0])}</text>')
        row_svg.append(f'<text x="258" y="{y}" font-size="17" fill="#172033">{html_escape(row[1])}</text>')
        row_svg.append(f'<text x="486" y="{y}" font-size="17" fill="#1f7a5b">{html_escape(row[2])}</text>')
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <text x="92" y="100" font-size="15" font-weight="800" fill="#b83246">{html_escape(headers[0])}</text>
  <text x="258" y="100" font-size="15" font-weight="800" fill="#b83246">{html_escape(headers[1])}</text>
  <text x="486" y="100" font-size="15" font-weight="800" fill="#b83246">{html_escape(headers[2])}</text>
  {''.join(row_svg)}
</svg>
"""


def render_flow_svg(
    index: int,
    title: str,
    labels: tuple[str, str, str, str],
    primary: str,
    secondary: str,
) -> str:
    cards = []
    for position, label in enumerate(labels):
        x = 64 + position * 160
        color = primary if position % 2 == 0 else secondary
        cards.append(
            f'<rect x="{x}" y="138" width="124" height="84" rx="14" fill="#ffffff" stroke="{color}" stroke-width="4"/>'
            f'<text x="{x + 62}" y="188" font-size="16" font-weight="800" fill="{color}" text-anchor="middle">{html_escape(label)}</text>'
        )
        if position < 3:
            ax = x + 132
            cards.append(
                f'<path d="M{ax} 180h38" stroke="#172033" stroke-width="4" marker-end="url(#flow-arrow-{index})"/>'
            )
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="78" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <defs><marker id="flow-arrow-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
  {''.join(cards)}
</svg>
"""


def render_concept_fallback_svg(index: int, title: str) -> str:
    heading = title or "Study visual"
    labels = ("Key idea", "Question evidence", "Checked answer")
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(heading)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="76" font-size="24" font-weight="800" fill="#1354a5">{html_escape(heading[:48])}</text>
  <rect x="82" y="130" width="158" height="96" rx="16" fill="#edf4ff" stroke="#9cbce8" stroke-width="3"/>
  <rect x="282" y="130" width="158" height="96" rx="16" fill="#fffaf1" stroke="#d99a24" stroke-width="3"/>
  <rect x="482" y="130" width="158" height="96" rx="16" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="3"/>
  <path d="M246 178h30M446 178h30" stroke="#172033" stroke-width="4" marker-end="url(#concept-arrow-{index})"/>
  <defs><marker id="concept-arrow-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
  <text x="161" y="184" font-size="18" font-weight="800" fill="#1354a5" text-anchor="middle">{html_escape(labels[0])}</text>
  <text x="361" y="184" font-size="18" font-weight="800" fill="#9b6a10" text-anchor="middle">{html_escape(labels[1])}</text>
  <text x="561" y="184" font-size="18" font-weight="800" fill="#1f7a5b" text-anchor="middle">{html_escape(labels[2])}</text>
</svg>
"""


def render_zh_math_topic_svg(index: int, title: str, focus: str, variant: str) -> str:
    base_variant = variant.split(":", 1)[0]
    display_title = zh_math_specific_title(title, focus)
    labels_by_variant = {
        "algebra": ("识别结构", "代入变形", "检验解"),
        "calculus": ("看曲线", "取斜率", "判结论"),
        "integral": ("定边界", "算面积", "查符号"),
        "series": ("找首项", "看公差/公比", "写求和"),
        "trig": ("定角度", "选公式", "查周期"),
        "probability": ("列结果", "算概率", "验总和"),
        "mechanics": ("画受力", "列方程", "查方向"),
        "coordinate": ("定坐标", "写方程", "验几何"),
    }
    labels = labels_by_variant.get(base_variant, ("读图", "建模", "检查"))
    cards = []
    for position, label in enumerate(labels):
        x = 438
        y = 106 + position * 64
        cards.append(
            f'<rect x="{x}" y="{y}" width="202" height="44" rx="10" fill="#ffffff" '
            f'stroke="#d7deea" stroke-width="2"/>'
            f'<text x="{x + 18}" y="{y + 29}" font-size="18" font-weight="800" '
            f'fill="#172033">{html_escape(label)}</text>'
        )
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(display_title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="52" y="68" fill="#1354a5" font-size="24" font-weight="800">{html_escape(display_title)}</text>
  {svg_multiline_text(focus or title, 52, 100, 15, 24, 17, 800, "#5b677a")}
  <g>{render_zh_math_motif(index, variant, focus)}</g>
  <rect x="418" y="82" width="244" height="216" rx="16" fill="#f7fbff" stroke="#9cbce8" stroke-width="3"/>
  {''.join(cards)}
  <text x="438" y="282" font-size="15" fill="#5b677a">公式、条件、答案形式一起检查</text>
</svg>
"""


def zh_math_specific_title(default_title: str, focus: str) -> str:
    clean = re.sub(r"\s+", " ", (focus or "").strip(" 。.；;:："))
    if not clean or clean.lower() == "focus":
        return default_title
    clean = clean.replace("&lt;", "<").replace("&gt;", ">")
    if len(clean) > 16:
        clean = clean[:15] + "…"
    if clean.endswith("图解"):
        return clean
    return f"{clean}图解"


def zh_math_variant(base: str, text: str) -> str:
    if base == "algebra":
        if any(word in text for word in ["根式", "surd"]):
            return "algebra:surd"
        if any(word in text for word in ["指数", "indices", "exponents"]):
            return "algebra:index"
        if any(word in text for word in ["判别式", "discriminant"]):
            return "algebra:discriminant"
        if any(word in text for word in ["配方", "completing"]):
            return "algebra:complete-square"
        if any(word in text for word in ["因式", "factorisation", "factor theorem"]):
            return "algebra:factor"
        if any(word in text for word in ["不等式", "inequal"]):
            return "algebra:inequality"
        if any(word in text for word in ["除法", "余式", "division", "remainder"]):
            return "algebra:division"
        if any(word in text for word in ["变换", "平移", "反射", "伸缩", "transformation"]):
            return "algebra:transform"
        if any(word in text for word in ["联立", "simultaneous"]):
            return "algebra:simultaneous"
        return "algebra:quadratic"
    if base == "calculus":
        if any(word in text for word in ["记号", "notation"]):
            return "calculus:notation"
        if any(word in text for word in ["第一原理", "first principles"]):
            return "calculus:first-principles"
        if any(word in text for word in ["二阶", "second order"]):
            return "calculus:second"
        if any(word in text for word in ["多项式", "polynomial", "rational number"]):
            return "calculus:power-rule"
        if any(word in text for word in ["驻点", "最大", "最小", "stationary", "maxima", "minima"]):
            return "calculus:stationary"
        return "calculus:tangent"
    if base == "integral":
        if any(word in text for word in ["不定", "反导", "reverse", "indefinite"]):
            return "integral:reverse"
        if any(word in text for word in ["多项式", "rational number"]):
            return "integral:power-rule"
        if any(word in text for word in ["梯形", "trapezium"]):
            return "integral:trapezium"
        if any(word in text for word in ["定积分", "definite"]):
            return "integral:definite"
        return "integral:area"
    if base == "series":
        if any(word in text for word in ["等差", "arithmetic"]):
            return "series:arithmetic"
        if any(word in text for word in ["收敛", "|r|", "infinity", "convergent"]):
            return "series:infinity"
        if any(word in text for word in ["等比", "geometric"]):
            return "series:geometric"
        if any(word in text for word in ["二项式", "binomial"]):
            return "series:binomial"
        return "series:sequence"
    if base == "probability":
        if any(word in text for word in ["二项分布", "伯努利", "binomial", "bernoulli"]):
            return "probability:binomial"
        if any(word in text for word in ["随机变量", "均值", "方差", "标准差", "random variable", "variance"]):
            return "probability:table"
        if any(word in text for word in ["条件", "乘法", "加法", "conditional", "multiplication", "addition"]):
            return "probability:tree"
        return "probability:bars"
    if base == "mechanics":
        if any(word in text for word in ["速度", "位移", "加速度", "运动学", "velocity", "acceleration"]):
            return "mechanics:kinematics"
        if any(word in text for word in ["牛顿", "newton"]):
            return "mechanics:newton"
        if any(word in text for word in ["动量", "冲量", "碰撞", "momentum", "impulse", "impact"]):
            return "mechanics:momentum"
        return "mechanics:forces"
    if base == "coordinate":
        if any(word in text for word in ["圆", "circle"]):
            return "coordinate:circle"
        if any(word in text for word in ["交点", "intersection"]):
            return "coordinate:intersection"
        return "coordinate:line"
    return base


def render_zh_math_motif(index: int, variant: str, focus: str = "") -> str:
    if variant == "algebra:surd":
        return """
  <rect x="82" y="146" width="244" height="82" rx="14" fill="#fffaf1" stroke="#d99a24" stroke-width="4"/>
  <text x="104" y="198" font-size="34" font-weight="800" fill="#1354a5">√50 = 5√2</text>
  <path d="M110 244h190" stroke="#b83246" stroke-width="4"/>
  <text x="118" y="276" font-size="18" font-weight="800" fill="#b83246">化简 / 分母有理化</text>
"""
    if variant == "algebra:index":
        return """
  <rect x="86" y="126" width="80" height="80" rx="12" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <rect x="196" y="126" width="80" height="80" rx="12" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="4"/>
  <path d="M168 166h26" stroke="#172033" stroke-width="4" marker-end="url(#idx-arrow)"/>
  <text x="106" y="176" font-size="24" font-weight="800" fill="#1354a5">aᵐ</text>
  <text x="214" y="176" font-size="24" font-weight="800" fill="#1f7a5b">aⁿ</text>
  <text x="106" y="250" font-size="26" font-weight="800" fill="#b83246">aᵐaⁿ=aᵐ⁺ⁿ</text>
  <defs><marker id="idx-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
"""
    if variant == "algebra:discriminant":
        return """
  <path d="M78 270V112M78 270h284" stroke="#172033" stroke-width="4"/>
  <path d="M114 248C158 126 274 126 328 248" fill="none" stroke="#1354a5" stroke-width="6"/>
  <path d="M116 220h212" stroke="#d99a24" stroke-width="4" stroke-dasharray="8 6"/>
  <text x="102" y="118" font-size="24" font-weight="800" fill="#b83246">Δ=b²-4ac</text>
  <text x="112" y="306" font-size="18" font-weight="800" fill="#1f7a5b">看根的个数</text>
"""
    if variant == "algebra:complete-square":
        return """
  <rect x="78" y="118" width="118" height="118" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <rect x="204" y="118" width="70" height="118" fill="#fffaf1" stroke="#d99a24" stroke-width="4"/>
  <rect x="78" y="244" width="118" height="42" fill="#fffaf1" stroke="#d99a24" stroke-width="4"/>
  <text x="92" y="104" font-size="24" font-weight="800" fill="#b83246">x²+6x</text>
  <text x="106" y="318" font-size="22" font-weight="800" fill="#1f7a5b">(x+3)² - 9</text>
"""
    if variant == "algebra:factor":
        return """
  <rect x="76" y="138" width="104" height="70" rx="12" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <rect x="214" y="138" width="104" height="70" rx="12" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="4"/>
  <path d="M184 174h26" stroke="#172033" stroke-width="4" marker-end="url(#factor-arrow)"/>
  <text x="96" y="181" font-size="24" font-weight="800" fill="#1354a5">f(a)=0</text>
  <text x="228" y="181" font-size="24" font-weight="800" fill="#1f7a5b">(x-a)</text>
  <text x="102" y="260" font-size="20" font-weight="800" fill="#b83246">因式 / 余式定理</text>
  <defs><marker id="factor-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
"""
    if variant == "algebra:inequality":
        ticks = "".join(f'<path d="M{x} 202v18" stroke="#172033" stroke-width="3"/>' for x in [94, 142, 190, 238, 286, 334])
        return f"""
  <path d="M76 211h288" stroke="#172033" stroke-width="4" marker-end="url(#ineq-arrow)"/>
  {ticks}
  <circle cx="238" cy="211" r="12" fill="#ffffff" stroke="#b83246" stroke-width="5"/>
  <path d="M238 211h96" stroke="#b83246" stroke-width="8"/>
  <text x="102" y="146" font-size="24" font-weight="800" fill="#1354a5">解集写区间</text>
  <text x="130" y="270" font-size="22" font-weight="800" fill="#b83246">x ≥ a</text>
  <defs><marker id="ineq-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
"""
    if variant == "algebra:division":
        return """
  <rect x="78" y="124" width="252" height="60" rx="12" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <path d="M112 214h184M112 248h184" stroke="#172033" stroke-width="4"/>
  <text x="100" y="162" font-size="22" font-weight="800" fill="#1354a5">f(x) ÷ (x-a)</text>
  <text x="116" y="238" font-size="21" font-weight="800" fill="#b83246">商 + 余数</text>
  <text x="118" y="292" font-size="18" font-weight="800" fill="#1f7a5b">余数 = f(a)</text>
"""
    if variant == "algebra:transform":
        return """
  <path d="M80 270V116M80 270h278" stroke="#172033" stroke-width="4"/>
  <path d="M102 238C142 154 226 154 272 238" fill="none" stroke="#1354a5" stroke-width="5"/>
  <path d="M144 218C184 134 268 134 314 218" fill="none" stroke="#b83246" stroke-width="5" stroke-dasharray="8 6"/>
  <path d="M272 146h42" stroke="#d99a24" stroke-width="5" marker-end="url(#trans-arrow)"/>
  <text x="112" y="110" font-size="22" font-weight="800" fill="#1f7a5b">平移 / 反射 / 伸缩</text>
  <defs><marker id="trans-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#d99a24"/></marker></defs>
"""
    if variant == "algebra:simultaneous":
        return """
  <path d="M78 270V116M78 270h284" stroke="#172033" stroke-width="4"/>
  <path d="M104 246C148 144 260 144 326 246" fill="none" stroke="#1354a5" stroke-width="5"/>
  <path d="M104 232L332 142" stroke="#b83246" stroke-width="5"/>
  <circle cx="222" cy="186" r="9" fill="#d99a24"/>
  <text x="104" y="112" font-size="22" font-weight="800" fill="#1f7a5b">交点 = 联立解</text>
"""
    if variant == "calculus:notation":
        return """
  <rect x="76" y="128" width="272" height="106" rx="16" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <text x="100" y="176" font-size="31" font-weight="800" fill="#1354a5">f′(x)</text>
  <text x="212" y="176" font-size="31" font-weight="800" fill="#b83246">dy/dx</text>
  <text x="104" y="260" font-size="19" font-weight="800" fill="#1f7a5b">同一个导数意义</text>
"""
    if variant == "calculus:first-principles":
        return """
  <path d="M82 264V130M82 264h272" stroke="#172033" stroke-width="4"/>
  <path d="M104 240C150 206 198 164 328 142" fill="none" stroke="#1354a5" stroke-width="5"/>
  <path d="M158 216h96M254 216v-38" stroke="#b83246" stroke-width="4" stroke-dasharray="7 5"/>
  <text x="108" y="112" font-size="22" font-weight="800" fill="#b83246">h → 0</text>
  <text x="118" y="304" font-size="19" font-weight="800" fill="#1f7a5b">割线逼近切线</text>
"""
    if variant == "calculus:second":
        return """
  <path d="M82 272V118M82 272h280" stroke="#172033" stroke-width="4"/>
  <path d="M104 238C168 96 240 96 332 238" fill="none" stroke="#1354a5" stroke-width="6"/>
  <circle cx="218" cy="126" r="9" fill="#d99a24"/>
  <text x="112" y="108" font-size="22" font-weight="800" fill="#b83246">f″(x)</text>
  <text x="118" y="306" font-size="19" font-weight="800" fill="#1f7a5b">判断极大 / 极小</text>
"""
    if variant == "calculus:power-rule":
        return """
  <rect x="82" y="122" width="252" height="72" rx="14" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <rect x="82" y="218" width="252" height="72" rx="14" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="4"/>
  <path d="M208 197v18" stroke="#172033" stroke-width="4" marker-end="url(#pow-arrow)"/>
  <text x="108" y="166" font-size="27" font-weight="800" fill="#1354a5">xⁿ</text>
  <text x="108" y="263" font-size="27" font-weight="800" fill="#1f7a5b">nxⁿ⁻¹</text>
  <defs><marker id="pow-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
"""
    if variant == "calculus:stationary":
        return """
  <path d="M82 272V112M82 272h280" stroke="#172033" stroke-width="4"/>
  <path d="M104 246C144 126 202 126 226 190C250 254 304 254 344 138" fill="none" stroke="#1354a5" stroke-width="6"/>
  <circle cx="202" cy="142" r="8" fill="#b83246"/><circle cx="278" cy="238" r="8" fill="#1f7a5b"/>
  <path d="M168 142h70M244 238h70" stroke="#d99a24" stroke-width="4"/>
  <text x="106" y="104" font-size="20" font-weight="800" fill="#b83246">dy/dx = 0</text>
"""
    if variant == "integral:reverse":
        return """
  <rect x="82" y="128" width="108" height="72" rx="14" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <rect x="244" y="128" width="108" height="72" rx="14" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="4"/>
  <path d="M196 164h42" stroke="#172033" stroke-width="5" marker-end="url(#int-rev)"/>
  <text x="110" y="172" font-size="24" font-weight="800" fill="#1354a5">f′(x)</text>
  <text x="268" y="172" font-size="24" font-weight="800" fill="#1f7a5b">f(x)+c</text>
  <text x="98" y="264" font-size="22" font-weight="800" fill="#b83246">积分是求导的反向</text>
  <defs><marker id="int-rev" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
"""
    if variant == "integral:power-rule":
        return """
  <rect x="84" y="122" width="244" height="74" rx="14" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <rect x="84" y="222" width="244" height="74" rx="14" fill="#fffaf1" stroke="#d99a24" stroke-width="4"/>
  <text x="112" y="168" font-size="27" font-weight="800" fill="#1354a5">xⁿ</text>
  <text x="112" y="267" font-size="25" font-weight="800" fill="#9b6a10">xⁿ⁺¹/(n+1)</text>
"""
    if variant == "integral:trapezium":
        return """
  <path d="M80 274V126M80 274h282" stroke="#172033" stroke-width="4"/>
  <path d="M104 242L154 198L204 176L254 156L318 132" fill="none" stroke="#1354a5" stroke-width="5"/>
  <path d="M104 274V242L154 198V274ZM154 274V198L204 176V274ZM204 274V176L254 156V274ZM254 274V156L318 132V274Z" fill="#d99a24" fill-opacity=".28" stroke="#d99a24" stroke-width="3"/>
  <text x="110" y="112" font-size="22" font-weight="800" fill="#b83246">梯形近似</text>
"""
    if variant == "integral:definite":
        return """
  <path d="M80 274V126M80 274h282" stroke="#172033" stroke-width="4"/>
  <path d="M110 250C160 206 220 154 344 132" fill="none" stroke="#1354a5" stroke-width="6"/>
  <path d="M130 274V236M318 274V138" stroke="#b83246" stroke-width="4" stroke-dasharray="7 6"/>
  <path d="M130 236C176 196 226 164 318 138L318 274L130 274Z" fill="#d99a24" fill-opacity=".28"/>
  <text x="112" y="112" font-size="22" font-weight="800" fill="#b83246">a 到 b 的面积</text>
  <text x="124" y="310" font-size="20" font-weight="800" fill="#1354a5">∫ₐᵇ f(x) dx</text>
"""
    if variant == "series:arithmetic":
        return """
  <circle cx="106" cy="186" r="28" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <circle cx="184" cy="186" r="28" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <circle cx="262" cy="186" r="28" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <path d="M136 186h18M214 186h18" stroke="#172033" stroke-width="4"/>
  <text x="96" y="194" font-size="22" font-weight="800">a</text>
  <text x="168" y="194" font-size="22" font-weight="800">a+d</text>
  <text x="238" y="194" font-size="22" font-weight="800">a+2d</text>
  <text x="108" y="266" font-size="24" font-weight="800" fill="#b83246">Sₙ = n/2(...)</text>
"""
    if variant == "series:geometric":
        return """
  <rect x="86" y="206" width="36" height="36" fill="#1354a5"/>
  <rect x="150" y="184" width="58" height="58" fill="#1f7a5b"/>
  <rect x="236" y="148" width="92" height="92" fill="#d99a24"/>
  <path d="M124 224h24M210 213h24" stroke="#172033" stroke-width="4"/>
  <text x="94" y="126" font-size="24" font-weight="800" fill="#b83246">乘以 r</text>
  <text x="104" y="292" font-size="22" font-weight="800" fill="#1354a5">a, ar, ar²</text>
"""
    if variant == "series:infinity":
        return """
  <path d="M88 210C124 150 168 150 204 210C240 270 284 270 320 210C284 150 240 150 204 210C168 270 124 270 88 210Z" fill="none" stroke="#1354a5" stroke-width="6"/>
  <text x="92" y="122" font-size="24" font-weight="800" fill="#b83246">|r| &lt; 1</text>
  <text x="112" y="292" font-size="22" font-weight="800" fill="#1f7a5b">S∞ = a/(1-r)</text>
"""
    if variant == "series:binomial":
        return """
  <rect x="72" y="126" width="268" height="60" rx="14" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <path d="M136 194l-38 54M206 194v54M276 194l38 54" stroke="#172033" stroke-width="4"/>
  <text x="96" y="166" font-size="26" font-weight="800" fill="#1354a5">(a+b)ⁿ</text>
  <text x="80" y="284" font-size="20" font-weight="800" fill="#b83246">项、系数、幂次</text>
"""
    if variant == "probability:table":
        rows = []
        for row, values in enumerate([("x", "0", "1", "2"), ("P", ".2", ".5", ".3")]):
            y = 150 + row * 50
            rows.append(f'<text x="96" y="{y}" font-size="20" font-weight="800" fill="#1354a5">{values[0]}</text>')
            for col, value in enumerate(values[1:]):
                rows.append(f'<text x="{158 + col * 62}" y="{y}" font-size="20" font-weight="800">{value}</text>')
        return f"""
  <rect x="72" y="112" width="270" height="122" rx="14" fill="#ffffff" stroke="#d7deea" stroke-width="4"/>
  <path d="M72 170h270M134 112v122" stroke="#d7deea" stroke-width="3"/>
  {''.join(rows)}
  <text x="96" y="286" font-size="21" font-weight="800" fill="#b83246">E(X), Var(X)</text>
"""
    if variant == "probability:tree":
        return """
  <circle cx="92" cy="176" r="8" fill="#b83246"/>
  <path d="M100 176L196 128M100 176L196 224M204 128L312 104M204 128L312 152M204 224L312 200M204 224L312 248" stroke="#172033" stroke-width="4"/>
  <g fill="#1354a5"><circle cx="196" cy="128" r="8"/><circle cx="196" cy="224" r="8"/></g>
  <g fill="#1f7a5b"><circle cx="312" cy="104" r="8"/><circle cx="312" cy="152" r="8"/><circle cx="312" cy="200" r="8"/><circle cx="312" cy="248" r="8"/></g>
  <text x="104" y="112" font-size="20" font-weight="800" fill="#b83246">乘法 / 条件</text>
"""
    if variant == "probability:binomial":
        bars = []
        for pos, height in enumerate([36, 76, 112, 76, 36]):
            x = 86 + pos * 48
            bars.append(f'<rect x="{x}" y="{254 - height}" width="28" height="{height}" fill="#1354a5"/>')
        return f"""
  <path d="M72 270V118M72 270h292" stroke="#172033" stroke-width="4"/>
  {''.join(bars)}
  <text x="96" y="104" font-size="23" font-weight="800" fill="#b83246">X ~ B(n,p)</text>
  <text x="112" y="306" font-size="19" font-weight="800" fill="#1f7a5b">公式或表格求概率</text>
"""
    if variant == "mechanics:kinematics":
        return """
  <path d="M82 272V112M82 272h280" stroke="#172033" stroke-width="4"/>
  <path d="M104 250L190 210L276 166L344 122" fill="none" stroke="#1354a5" stroke-width="6"/>
  <path d="M190 210h86" stroke="#d99a24" stroke-width="5" stroke-dasharray="7 6"/>
  <text x="106" y="104" font-size="22" font-weight="800" fill="#b83246">速度-时间图与位移-时间图</text>
  <text x="112" y="306" font-size="19" font-weight="800" fill="#1f7a5b">斜率与面积</text>
"""
    if variant == "mechanics:newton":
        return f"""
  <rect x="152" y="172" width="110" height="70" rx="12" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <path d="M142 206h-64" stroke="#b83246" stroke-width="7" marker-end="url(#newton-left-{index})"/>
  <path d="M272 206h84" stroke="#1f7a5b" stroke-width="9" marker-end="url(#newton-right-{index})"/>
  <text x="88" y="126" font-size="24" font-weight="800" fill="#1354a5">ΣF = ma</text>
  <text x="112" y="288" font-size="19" font-weight="800" fill="#b83246">方向先定正</text>
  <defs>
    <marker id="newton-left-{index}" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M10 0 0 5 10 10z" fill="#b83246"/></marker>
    <marker id="newton-right-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#1f7a5b"/></marker>
  </defs>
"""
    if variant == "mechanics:momentum":
        return """
  <circle cx="132" cy="196" r="30" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <circle cx="286" cy="196" r="24" fill="#fffaf1" stroke="#d99a24" stroke-width="4"/>
  <path d="M166 196h86" stroke="#b83246" stroke-width="7" marker-end="url(#mom-arrow)"/>
  <text x="94" y="126" font-size="24" font-weight="800" fill="#1354a5">mv</text>
  <text x="118" y="282" font-size="20" font-weight="800" fill="#1f7a5b">冲量 = 动量变化</text>
  <defs><marker id="mom-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#b83246"/></marker></defs>
"""
    if variant == "coordinate:circle":
        return """
  <path d="M80 272V96M80 272h282" stroke="#172033" stroke-width="4"/>
  <circle cx="212" cy="180" r="74" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="5"/>
  <path d="M212 180h74" stroke="#b83246" stroke-width="4"/>
  <text x="112" y="104" font-size="22" font-weight="800" fill="#1354a5">(x-a)²+(y-b)²=r²</text>
"""
    if variant == "coordinate:intersection":
        return """
  <path d="M80 272V106M80 272h282" stroke="#172033" stroke-width="4"/>
  <path d="M102 250C160 132 260 132 338 250" fill="none" stroke="#1354a5" stroke-width="5"/>
  <path d="M104 232L336 126" stroke="#b83246" stroke-width="5"/>
  <circle cx="186" cy="194" r="8" fill="#d99a24"/><circle cx="286" cy="150" r="8" fill="#d99a24"/>
  <text x="106" y="104" font-size="22" font-weight="800" fill="#1f7a5b">联立找交点</text>
"""
    if variant.startswith("calculus"):
        return """
  <path d="M78 274V104M78 274h288" stroke="#172033" stroke-width="4"/>
  <path d="M104 246C150 174 196 128 258 150C300 164 326 218 352 246" fill="none" stroke="#1354a5" stroke-width="6"/>
  <path d="M132 218L324 156" stroke="#b83246" stroke-width="5"/>
  <circle cx="226" cy="164" r="8" fill="#d99a24"/>
  <text x="108" y="104" font-size="22" font-weight="800" fill="#b83246">切线斜率</text>
  <text x="118" y="310" font-size="20" font-weight="800" fill="#1f7a5b">dy/dx</text>
"""
    if variant.startswith("integral"):
        return """
  <path d="M80 274V126M80 274h282" stroke="#172033" stroke-width="4"/>
  <path d="M108 250C160 218 204 166 270 148C306 138 332 134 354 130L354 274L108 274Z" fill="#d99a24" fill-opacity=".28"/>
  <path d="M108 250C160 218 204 166 270 148C306 138 332 134 354 130" fill="none" stroke="#1354a5" stroke-width="6"/>
  <path d="M108 274V250M354 274V130" stroke="#b83246" stroke-width="4" stroke-dasharray="7 6"/>
  <text x="132" y="164" font-size="20" font-weight="800" fill="#9b6a10">面积</text>
  <text x="116" y="306" font-size="22" font-weight="800" fill="#1354a5">∫ f(x) dx</text>
"""
    if variant.startswith("series"):
        bars = []
        for pos, height in enumerate([52, 74, 96, 118]):
            x = 88 + pos * 58
            bars.append(f'<rect x="{x}" y="{258 - height}" width="34" height="{height}" fill="#1354a5"/>')
        return f"""
  <path d="M70 274h286" stroke="#172033" stroke-width="4"/>
  {''.join(bars)}
  <path d="M284 136h52" stroke="#b83246" stroke-width="5" marker-end="url(#series-arrow-{index})"/>
  <defs><marker id="series-arrow-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#b83246"/></marker></defs>
  <text x="92" y="120" font-size="22" font-weight="800" fill="#b83246">a, r</text>
  <text x="248" y="196" font-size="22" font-weight="800" fill="#1f7a5b">Sₙ</text>
"""
    if variant == "trig":
        return """
  <circle cx="204" cy="194" r="88" fill="#fffaf1" stroke="#d99a24" stroke-width="4"/>
  <path d="M204 194h118M204 194l74-65M278 129v65" stroke="#172033" stroke-width="4"/>
  <path d="M238 194A34 34 0 0 0 230 171" fill="none" stroke="#b83246" stroke-width="4"/>
  <text x="286" y="186" font-size="18" font-weight="800" fill="#1354a5">cos</text>
  <text x="286" y="156" font-size="18" font-weight="800" fill="#1f7a5b">sin</text>
  <text x="146" y="314" font-size="21" font-weight="800" fill="#b83246">sin, cos, tan</text>
"""
    if variant.startswith("probability"):
        return """
  <path d="M74 270V134M74 270h148" stroke="#172033" stroke-width="4"/>
  <rect x="98" y="218" width="28" height="52" fill="#1354a5"/>
  <rect x="138" y="174" width="28" height="96" fill="#1f7a5b"/>
  <rect x="178" y="202" width="28" height="68" fill="#d99a24"/>
  <path d="M270 160h44M314 160l42-38M314 160l42 38" stroke="#172033" stroke-width="4" fill="none"/>
  <circle cx="270" cy="160" r="8" fill="#b83246"/><circle cx="356" cy="122" r="8" fill="#1354a5"/><circle cx="356" cy="198" r="8" fill="#1f7a5b"/>
  <text x="96" y="116" font-size="20" font-weight="800" fill="#b83246">P(X=x)</text>
"""
    if variant.startswith("mechanics"):
        return f"""
  <rect x="162" y="174" width="96" height="64" rx="12" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <path d="M150 206h-70" stroke="#b83246" stroke-width="7" marker-end="url(#mech-left-{index})"/>
  <path d="M270 206h88" stroke="#1f7a5b" stroke-width="8" marker-end="url(#mech-right-{index})"/>
  <path d="M210 166v-64" stroke="#d99a24" stroke-width="6" marker-end="url(#mech-up-{index})"/>
  <defs>
    <marker id="mech-left-{index}" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M10 0 0 5 10 10z" fill="#b83246"/></marker>
    <marker id="mech-right-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#1f7a5b"/></marker>
    <marker id="mech-up-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#d99a24"/></marker>
  </defs>
  <text x="158" y="284" font-size="24" font-weight="800" fill="#1354a5">F=ma</text>
"""
    if variant.startswith("coordinate"):
        return """
  <path d="M78 276V92M78 276h292" stroke="#172033" stroke-width="4"/>
  <circle cx="214" cy="184" r="72" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="4"/>
  <path d="M104 248L344 112" stroke="#b83246" stroke-width="5"/>
  <circle cx="214" cy="184" r="6" fill="#1354a5"/>
  <text x="230" y="180" font-size="17" font-weight="800" fill="#1354a5">(a,b)</text>
  <text x="116" y="118" font-size="20" font-weight="800" fill="#b83246">y=mx+c</text>
"""
    return """
  <path d="M80 274V126M80 274h282" stroke="#172033" stroke-width="4"/>
  <path d="M106 246C150 172 202 130 260 150C300 164 324 218 350 246" fill="none" stroke="#1354a5" stroke-width="6"/>
  <path d="M122 220h204" stroke="#d99a24" stroke-width="4" stroke-dasharray="7 6"/>
  <text x="120" y="126" font-size="22" font-weight="800" fill="#b83246">x²</text>
  <text x="238" y="306" font-size="20" font-weight="800" fill="#1f7a5b">解后代回检查</text>
"""


def render_zh_visual_svg(visual: VisualBrief, index: int) -> str:
    title = visual.visual_type or "图文结合学习图"
    focus = visual.focus_point or title
    text = " ".join([title, focus, *visual.source_points]).lower()
    if any(word in text for word in ["会计记录", "原始", "分类账", "初始记录"]):
        return render_accounting_flow_svg(index, "zh-CN")
    if any(word in text for word in ["核对", "银行对账", "试算平衡"]):
        return render_reconciliation_svg(index, "zh-CN")
    if any(word in text for word in ["财务报表", "比率"]):
        return render_financial_statement_svg(index, "zh-CN")
    if any(word in text for word in ["会计调整", "影响"]):
        return render_accounting_flow_svg(index, "zh-CN")
    if any(word in text for word in ["市场", "供需", "需求", "供给", "demand", "supply"]):
        return render_market_svg(index, "zh-CN")
    if any(word in text for word in ["生产要素", "机会成本", "经济选择"]):
        return render_economic_flow_svg(index, "zh-CN")
    if any(word in text for word in ["集合", "韦恩"]):
        return render_venn_svg(index, "zh-CN")
    if any(word in text for word in ["力与运动", "合力"]):
        return render_force_svg(index, "zh-CN")
    if any(word in text for word in ["色谱", "层析", "分离", "纯度", "chromatography", "separation", "purity"]):
        return render_analysis_svg(index)
    if any(word in text for word in ["有机", "烃", "原油", "聚合物", "organic", "hydrocarbon", "crude", "polymer"]):
        return render_organic_svg(index)
    if any(word in text for word in ["键", "离子", "共价", "金属键", "结构", "bond", "bonding", "ionic", "covalent", "metallic", "structure"]):
        return render_bonding_svg(index)
    if any(word in text for word in ["粒子", "固体", "液体", "气态", "solid", "liquid", "particles", "states of matter"]):
        return render_particles_svg(index)
    if (
        "气体检验" in text
        or "gas test" in text
        or any(word in text for word in ["limewater", "splint", "hydrogen", "oxygen", "carbon dioxide", "chlorine"])
    ):
        return render_gas_tests_svg(index, "zh-CN")
    if "酸碱" in text or re.search(r"\bph\b", text):
        return render_ph_svg(index)
    if any(word in text for word in ["速率", "平衡", "rate", "equilibrium", "haber"]):
        return render_rate_svg(index)
    if any(word in text for word in ["放热", "吸热", "能量", "exothermic", "endothermic", "energy"]):
        return render_energy_svg(index)
    if any(word in text for word in ["三角函数", "正弦", "余弦", "正切", "弧度", "周期", "sine", "cosine", "trigonometric"]):
        return render_zh_math_topic_svg(index, "三角函数图", focus, "trig")
    if any(word in text for word in ["牛顿", "力学", "重力", "速度", "位移", "加速度", "动量", "冲量", "碰撞", "张力", "法向", "阻力", "运动学", "newton", "velocity", "acceleration", "momentum", "impulse"]):
        return render_zh_math_topic_svg(index, "力学关系图", focus, zh_math_variant("mechanics", text))
    if any(word in text for word in ["坐标", "直线", "圆", "斜率", "交点", "coordinate", "straight line", "circle"]):
        return render_zh_math_topic_svg(index, "坐标几何图", focus, zh_math_variant("coordinate", text))
    if any(word in text for word in ["积分", "面积", "梯形", "integral", "integration", "area", "trapezium"]):
        return render_zh_math_topic_svg(index, "积分面积图", focus, zh_math_variant("integral", text))
    if any(word in text for word in ["导数", "微分", "切线", "法线", "驻点", "derivative", "differentiation", "tangent", "gradient"]):
        return render_zh_math_topic_svg(index, "微分与切线图", focus, zh_math_variant("calculus", text))
    if any(word in text for word in ["数列", "级数", "等差", "等比", "二项式", "sequence", "series", "binomial expansion"]):
        return render_zh_math_topic_svg(index, "数列与级数图", focus, zh_math_variant("series", text))
    if any(word in text for word in ["概率", "随机变量", "二项分布", "伯努利", "均值", "方差", "标准差", "统计", "probability", "distribution", "variance"]):
        return render_zh_math_topic_svg(index, "概率与分布图", focus, zh_math_variant("probability", text))
    if any(word in text for word in ["代数", "二次", "方程", "不等式", "多项式", "函数", "根式", "指数", "因式", "余式", "配方", "algebra", "quadratic", "equation", "function", "polynomial", "surd"]):
        return render_zh_math_topic_svg(index, "代数关系图", focus, zh_math_variant("algebra", text))
    if any(word in text for word in ["几何"]):
        return render_triangle_svg(index)
    fallback_title = title if title != "图文结合学习图" else focus
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(fallback_title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <rect x="54" y="58" width="210" height="244" rx="18" fill="#edf4ff" stroke="#9cbce8" stroke-width="3"/>
  <rect x="292" y="58" width="170" height="104" rx="16" fill="#ecf8f3" stroke="#a7d5c3" stroke-width="3"/>
  <rect x="292" y="198" width="170" height="104" rx="16" fill="#fff3d8" stroke="#e6c36d" stroke-width="3"/>
  <rect x="492" y="58" width="174" height="244" rx="18" fill="#fff1f3" stroke="#e5aab4" stroke-width="3"/>
  <path d="M264 180h28M462 110h30M462 250h30" stroke="#172033" stroke-width="4" marker-end="url(#arrow-zh-{index})"/>
  <defs><marker id="arrow-zh-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
  <text x="92" y="106" font-size="25" font-weight="800" fill="#1354a5">图解</text>
  {svg_multiline_text(title, 92, 148, 10, 28, 24, 800, "#172033")}
  <text x="326" y="106" font-size="22" font-weight="800" fill="#1f7a5b">观察</text>
  <text x="326" y="246" font-size="22" font-weight="800" fill="#8a5f11">方法</text>
  <text x="530" y="108" font-size="22" font-weight="800" fill="#b83246">检查</text>
  <text x="326" y="136" font-size="16" fill="#5b677a">先看图中关系</text>
  <text x="326" y="276" font-size="16" fill="#5b677a">再写解题步骤</text>
  <text x="530" y="144" font-size="16" fill="#5b677a">最后回到题问</text>
  <text x="530" y="176" font-size="16" fill="#5b677a">术语、单位、结论</text>
</svg>
"""


def svg_multiline_text(
    value: str,
    x: int,
    y: int,
    max_chars: int,
    line_height: int,
    size: int = 12,
    weight: int = 700,
    fill: str = "#172033",
) -> str:
    lines = wrap_words(value, max_chars=max_chars)[:3]
    tspans = []
    for index, line in enumerate(lines):
        dy = 0 if index == 0 else line_height
        tspans.append(f'<tspan x="{x}" dy="{dy}">{html_escape(line)}</tspan>')
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
        f'font-weight="{weight}">{"".join(tspans)}</text>'
    )


def wrap_words(value: str, max_chars: int) -> list[str]:
    words = value.replace("/", " / ").split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word[:max_chars]
    if current:
        lines.append(current)
    return lines or [value[:max_chars]]

def html_escape(value: str) -> str:
    return html.escape(value, quote=True)
