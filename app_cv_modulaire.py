"""Application Streamlit de génération et de personnalisation de CV."""

# -*- coding: utf-8 -*-
import io
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from copy import deepcopy
from uuid import uuid4

import streamlit as st

# ====== THEME & CSS ======
PAGE_TITLE = "CV – Générateur & Déclinaisons"
st.set_page_config(page_title=PAGE_TITLE, page_icon="🧰", layout="wide")

CSS = """
<style>
:root {
  --accent: #0E7490;
  --accent-soft: #f0f9ff;
  --ink: #0f172a;
}
html, body, [class*="css"]  {
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif !important;
  color: var(--ink);
  background: #f8fafc;
}
.block-container {
  padding-top: 2.5rem;
  padding-bottom: 2.5rem;
  max-width: 1100px;
}
.cv-card {
  background: white;
  border-radius: 24px;
  padding: 28px 32px;
  box-shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
  border: 1px solid rgba(15, 116, 144, 0.08);
}
.badge {
  display:inline-flex;
  padding: 4px 12px;
  border-radius:999px;
  background: rgba(14, 116, 144, 0.1);
  color: #0f172a;
  font-weight: 500;
  font-size: 12px;
  margin: 0 6px 6px 0;
}
.h1 { font-size: 34px; font-weight: 800; margin-bottom: 4px; }
.h2 { font-size: 15px; color:#0f172a; font-weight: 700; text-transform: uppercase; letter-spacing: .18em; margin: 18px 0 12px 0;}
.h3 { font-size: 16px; font-weight:700; margin: 2px 0 2px 0; color:#0f172a; }
.muted { color:#475569; }
.rule { height:1px; background:linear-gradient(90deg,var(--accent),transparent); margin: 18px 0 14px 0;}
.header-band {
  background: linear-gradient(135deg, rgba(14, 116, 144, 0.92), rgba(56, 189, 248, 0.88));
  color: white;
  border-radius: 28px;
  padding: 26px 32px;
  margin-bottom: 22px;
  position: relative;
  overflow: hidden;
}
.header-band::after {
  content:"";
  position:absolute;
  inset:20px;
  border:1px solid rgba(255,255,255,0.25);
  border-radius:20px;
  opacity:0.6;
}
.header-band .title { font-size: 30px; font-weight: 800; margin:0; }
.header-band .subtitle { opacity:.9; margin-top:10px; font-size: 16px; }
.grid-preview {
  display:grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(220px, 0.8fr);
  gap: 36px;
}
.side-card {
  background: var(--accent-soft);
  border-radius: 20px;
  padding: 22px 24px;
  border: 1px solid rgba(14, 116, 144, 0.18);
}
.small { font-size: 13px; }
.footer { border-top:1px dashed #e2e8f0; margin-top:18px; padding-top:12px; font-size:12px; color:#64748b;}
.sign-line { margin-top: 18px; }
ul.clean-list { padding-left: 0; }
ul.clean-list li { list-style: none; margin-bottom: 12px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ====== DATA MODELS ======
@dataclass
class Experience:
    role: str
    org: str
    dates: str
    bullets: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class EducationItem:
    title: str
    school: str
    dates: str
    details: str = ""


@dataclass
class CVData:
    name: str
    headline: str
    location: str
    phone: str
    email: str
    linkedin: str = ""
    websites: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    softskills: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    summary: str = ""
    experiences: List[Experience] = field(default_factory=list)
    education: List[EducationItem] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)


# ====== SEED PROFILE (pré-rempli à partir de ton CV) ======
seed = CVData(
    name="Ibrahim BITAR",
    headline="Chef de projet senior – Management d’équipes & conduite de projets complexes (12 ans) | Génie civil / Nucléaire",
    location="Île-de-France (mobilité prioritaire)",
    phone="+33 6 95 75 83 09",
    email="ibrahim.bitar@live.com",
    linkedin="linkedin.com/in/bitaribrahim",
    websites=["egis-group.com", "irsn.fr", "gem.ec-nantes.fr"],
    languages=["Français (bilingue)", "Anglais (courant)", "Arabe (bilingue)"],
    softskills=["Communication", "Management", "Planification", "Encadrement", "Autonomie", "Pédagogie", "Pensée innovante"],
    tools=["MS Project", "Python", "Matlab", "ANSYS", "Cast3m", "LS-DYNA", "Git", "LaTeX", "Linux", "Inkscape"],
    interests=["Philosophie", "Culture scientifique", "Basket-ball", "Rédaction d’essais", "Méditations", "Activités sociales"],
    summary="Chef de projet en ingénierie nucléaire, pilotage de production et qualité, coordination multi-acteurs, et capitalisation REX.",
    experiences=[
        Experience(
            role="Chef de projets – Production, coordination & planification",
            org="EGIS Industrie (Énergie & Villes durables) – Nucléaire",
            dates="Oct. 2023 – Aujourd’hui",
            bullets=[
                "Coordination des études de production pour les nouvelles centrales EPR2 à Penly",
                "Responsable livraisons (qualité, délais), découpage projet, planning, ressources, budget",
                "Animation comité technique, gestion des risques, capitalisation des retours d’expérience"
            ],
            tags=["EPR2", "SSI", "Qualité", "Planification", "Pilotage"]
        ),
        Experience(
            role="Responsable des outils de calcul scientifique",
            org="EGIS Industrie – Nucléaire",
            dates="Mai 2024 – Aujourd’hui",
            bullets=[
                "Coordination du développement et recettage des outils internes",
                "Préparation audits, appui aux démarches de certification ISO",
                "Définition des bonnes pratiques, standardisation"
            ],
            tags=["Outils", "Qualif/ISO", "Dev interne"]
        ),
        Experience(
            role="Chef de projets techniques & scientifiques",
            org="IRSN",
            dates="2019 – 2023",
            bullets=[
                "Benchmarks & workshops internationaux sur la modélisation des structures",
                "Gestion prestations d’étude (délais/ressources/objectifs)",
                "Programmes pluriannuels R&D, encadrement stagiaires/doctorants/post-docs"
            ],
            tags=["R&D", "Struct.", "International"]
        ),
        Experience(
            role="Ingénieur chercheur (R&D)",
            org="CEA",
            dates="2018 – 2019",
            bullets=[
                "Comportement des liaisons BA (renforcement parasismique, projet Ilisbar)",
                "Modèles plaques & publications scientifiques"
            ],
            tags=["Parasismique", "BA", "Publications"]
        ),
        Experience(
            role="Doctorant & ingénieur de recherche (GéM)",
            org="École Centrale de Nantes / GeM",
            dates="2014 – 2017",
            bullets=[
                "Modèles EF pour structures en BA & plateforme Matlab",
                "Rapports SINAPS@, publications & conférences"
            ],
            tags=["EF", "BA", "SINAPS@"]
        ),
    ],
    education=[
        EducationItem(
            title="Doctorat en Génie Civil",
            school="École Centrale de Nantes",
            dates="2013 – 2017",
            details="Rupture dans le BA par éléments finis poutre généralisés & multifibres"
        ),
        EducationItem(
            title="Double diplôme Ingénieur–Master en Génie Civil (Majore de promo)",
            school="École Centrale de Nantes / Université Libanaise (FG III)",
            dates="2008 – 2013",
            details=""
        ),
    ],
    keywords=[
        "Engineering project manager", "Team leader", "Problem solving", "Modélisation", "Appels d’offres",
        "Chef de service", "Organisation", "Team work"
    ]
)


# ====== PRESETS DE DÉCLINAISON ======
PRESETS: Dict[str, Dict[str, Any]] = {
    "Chef de projet – Ingénierie nucléaire (EPR2/SSI)": {
        "keep_tags": ["EPR2", "SSI", "Qualité", "Planification", "Pilotage"],
        "hide_sections": [],
        "extra_keywords": ["RCC-CW", "ESPN", "Eurocodes", "Coordination partenaires", "Gestion des risques"],
        "headline_addon": " | Ingénierie nucléaire – EPR2 / SSI"
    },
    "R&D / Académique (structures)": {
        "keep_tags": ["R&D", "Struct.", "Publications", "Parasismique", "BA", "EF", "SINAPS@"],
        "hide_sections": [],
        "extra_keywords": ["Publications", "Confs", "Direction scientifique", "Encadrement"],
        "headline_addon": " | R&D – Modélisation des structures"
    },
    "Data / ML pour l’ingénierie": {
        "keep_tags": ["Outils", "Qualif/ISO", "Dev interne", "R&D"],
        "hide_sections": ["Intérêts"],
        "extra_keywords": ["Python", "Pipelines scikit-learn", "Data viz", "Automatisation"],
        "headline_addon": " | Data/ML appliqué à l’ingénierie"
    },
    "Consultant / PMO": {
        "keep_tags": ["Qualité", "Planification", "Pilotage", "International"],
        "hide_sections": [],
        "extra_keywords": ["PMO", "Tableaux de bord", "Audit", "Standardisation"],
        "headline_addon": " | Conseil – PMO & Excellence opérationnelle"
    },
}


# ====== HELPERS ======
def experience_to_dict(exp: Experience) -> Dict[str, Any]:
    return {
        "uid": str(uuid4()),
        "role": exp.role,
        "org": exp.org,
        "dates": exp.dates,
        "bullets": exp.bullets.copy(),
        "tags": exp.tags.copy(),
        "enabled": True,
    }


def education_to_dict(ed: EducationItem) -> Dict[str, Any]:
    return {
        "uid": str(uuid4()),
        "title": ed.title,
        "school": ed.school,
        "dates": ed.dates,
        "details": ed.details,
        "enabled": True,
    }


def parse_free_list(text: str) -> List[str]:
    if not text:
        return []
    tokens: List[str] = []
    for chunk in text.replace(";", ",").splitlines():
        tokens.extend([item.strip() for item in chunk.split(",") if item.strip()])
    return tokens


def format_list(values: List[str]) -> str:
    return ", ".join(values)


def delist(items: List[str]) -> str:
    return " · ".join([item for item in items if item]) if items else ""


def download_button_bytes(bin_bytes: bytes, filename: str, label: str) -> None:
    st.download_button(label, data=bin_bytes, file_name=filename, mime="application/pdf")


def init_state() -> None:
    if "cv_general" not in st.session_state:
        st.session_state["cv_general"] = {
            "name": seed.name,
            "headline_base": seed.headline,
            "headline": seed.headline,
            "use_preset_headline": True,
            "summary": seed.summary,
            "location": seed.location,
            "phone": seed.phone,
            "email": seed.email,
            "linkedin": seed.linkedin,
            "websites": seed.websites.copy(),
            "languages": seed.languages.copy(),
            "softskills": seed.softskills.copy(),
            "tools": seed.tools.copy(),
            "interests": seed.interests.copy(),
            "keywords": seed.keywords.copy(),
            "use_preset_keywords": True,
        }
    if "experiences" not in st.session_state:
        st.session_state["experiences"] = [experience_to_dict(exp) for exp in seed.experiences]
    if "education" not in st.session_state:
        st.session_state["education"] = [education_to_dict(ed) for ed in seed.education]


def reset_state() -> None:
    st.session_state["experiences"] = [experience_to_dict(exp) for exp in seed.experiences]
    st.session_state["education"] = [education_to_dict(ed) for ed in seed.education]
    st.session_state["cv_general"] = {
        "name": seed.name,
        "headline_base": seed.headline,
        "headline": seed.headline,
        "use_preset_headline": True,
        "summary": seed.summary,
        "location": seed.location,
        "phone": seed.phone,
        "email": seed.email,
        "linkedin": seed.linkedin,
        "websites": seed.websites.copy(),
        "languages": seed.languages.copy(),
        "softskills": seed.softskills.copy(),
        "tools": seed.tools.copy(),
        "interests": seed.interests.copy(),
        "keywords": seed.keywords.copy(),
        "use_preset_keywords": True,
    }


def apply_preset_to_state(preset: Dict[str, Any]) -> None:
    experiences = st.session_state.get("experiences", [])
    keep_tags = set(preset.get("keep_tags", []))
    indexed = list(enumerate(experiences))
    if keep_tags:
        indexed.sort(key=lambda item: (0 if keep_tags.intersection(set(map(str.strip, item[1]["tags"]))) else 1, item[0]))
    st.session_state["experiences"] = [deepcopy(item[1]) for item in indexed]
    for exp in st.session_state["experiences"]:
        exp["enabled"] = True if not keep_tags else bool(keep_tags.intersection(set(map(str.strip, exp["tags"]))))


def merge_keywords(base: List[str], extra: List[str]) -> List[str]:
    seen: set[str] = set()
    merged: List[str] = []
    for value in base + extra:
        clean = value.strip()
        if clean and clean.lower() not in seen:
            merged.append(clean)
            seen.add(clean.lower())
    return merged


# ====== PDF (ReportLab) ======
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor


def cv_to_pdf_bytes(cv: CVData, show_sections: Dict[str, bool], signature_image: Optional[bytes], theme_color: str) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    margin = 1.9 * cm
    inner_width = width - 2 * margin
    side_width = 6.2 * cm
    gutter = 0.8 * cm
    main_width = inner_width - side_width - gutter

    c.setTitle(f"CV - {cv.name}")
    accent = HexColor(theme_color) if theme_color else HexColor("#0E7490")
    neutral = HexColor("#0f172a")
    muted = HexColor("#475569")

    def wrap_by_width(text: str, font_name: str, font_size: float, max_width: float) -> List[str]:
        lines: List[str] = []
        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()
            if not words:
                lines.append("")
                continue
            current = words[0]
            for word in words[1:]:
                test = f"{current} {word}"
                if c.stringWidth(test, font_name, font_size) <= max_width:
                    current = test
                else:
                    lines.append(current)
                    current = word
            lines.append(current)
        return lines or [""]

    def draw_lines(lines: List[str], *, x: float, y: float, font_name: str, font_size: float, leading: float, color: HexColor) -> float:
        c.setFont(font_name, font_size)
        c.setFillColor(color)
        for line in lines:
            c.drawString(x, y, line)
            y -= leading
        return y

    def draw_section_label(label: str, *, x: float, y: float) -> float:
        badge_height = 16
        badge_width = c.stringWidth(label.upper(), "Helvetica-Bold", 8) + 14
        c.setFillColor(accent)
        c.roundRect(x, y - badge_height + 4, badge_width, badge_height, 6, fill=1, stroke=0)
        c.setFillColor(HexColor("#ffffff"))
        c.setFont("Helvetica-Bold", 8)
        c.drawString(x + 7, y - 4, label.upper())
        return y - badge_height - 6

    def ensure_column_space(current_y: float, needed: float) -> bool:
        return current_y - needed >= margin + 1.2 * cm

    def draw_badges(values: List[str], *, x: float, y: float, max_width: float) -> float:
        if not values:
            return y
        current_x = x
        current_y = y
        pad_x = 4
        pad_y = 2
        height_badge = 12
        c.setFont("Helvetica", 7)
        for value in values:
            text_width = c.stringWidth(value, "Helvetica", 7) + pad_x * 2
            if current_x + text_width > x + max_width:
                current_x = x
                current_y -= height_badge + 4
            c.setFillColor(accent)
            c.roundRect(current_x, current_y - height_badge + pad_y, text_width, height_badge, 5, fill=1, stroke=0)
            c.setFillColor(HexColor("#ffffff"))
            c.drawString(current_x + pad_x, current_y - 4, value)
            current_x += text_width + 6
        return current_y - height_badge - 6

    header_height = 92
    c.setFillColor(accent)
    c.roundRect(margin, height - margin - header_height, inner_width, header_height, 18, fill=1, stroke=0)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 20)
    c.drawString(margin + 18, height - margin - 28, cv.name)
    c.setFont("Helvetica", 11)
    c.drawString(margin + 18, height - margin - 46, cv.headline[:150])

    contact_lines = wrap_by_width(delist([cv.location, cv.phone, cv.email, cv.linkedin] + cv.websites), "Helvetica", 9, inner_width - 36)
    contact_y = height - margin - 62
    contact_y = draw_lines(contact_lines, x=margin + 18, y=contact_y, font_name="Helvetica", font_size=9, leading=11, color=HexColor("#e0f2fe"))

    body_top = contact_y - 16
    main_x = margin
    side_x = margin + main_width + gutter
    y_main = body_top
    y_side = body_top

    side_bg_top = body_top + 10
    c.setFillColor(HexColor("#f0f9ff"))
    c.roundRect(side_x - 10, margin, side_width + 20, side_bg_top - margin, 16, fill=1, stroke=0)

    truncated = False

    if show_sections.get("Résumé", True) and cv.summary and not truncated:
        lines = wrap_by_width(cv.summary, "Helvetica", 10, main_width)
        needed = 26 + len(lines) * 13
        if ensure_column_space(y_main, needed):
            y_main = draw_section_label("Résumé", x=main_x, y=y_main)
            y_main = draw_lines(lines, x=main_x, y=y_main, font_name="Helvetica", font_size=10, leading=13, color=neutral)
            y_main -= 4
        else:
            truncated = True

    if show_sections.get("Expériences", True) and cv.experiences and not truncated:
        y_main = draw_section_label("Expériences", x=main_x, y=y_main)
        y_main -= 4
        for exp in cv.experiences:
            title = f"{exp.role} — {exp.org}".strip(" —")
            title_lines = wrap_by_width(title, "Helvetica-Bold", 10.5, main_width)
            date_lines = wrap_by_width(exp.dates, "Helvetica", 9, main_width)
            bullets_lines = sum(len(wrap_by_width(bullet, "Helvetica", 9.5, main_width - 16)) for bullet in exp.bullets)
            needed = (len(title_lines) * 12) + (len(date_lines) * 11) + max(bullets_lines, 1) * 12 + 14
            if exp.tags:
                needed += 16
            if not ensure_column_space(y_main, needed):
                truncated = True
                break
            y_main = draw_lines(title_lines, x=main_x, y=y_main, font_name="Helvetica-Bold", font_size=10.5, leading=12.5, color=neutral)
            y_main = draw_lines(date_lines, x=main_x, y=y_main, font_name="Helvetica", font_size=9, leading=11, color=muted)
            for bullet in exp.bullets:
                bullet_lines = wrap_by_width(bullet, "Helvetica", 9.5, main_width - 16)
                c.setFont("Helvetica", 9.5)
                c.setFillColor(neutral)
                for idx, line in enumerate(bullet_lines):
                    if idx == 0:
                        c.drawString(main_x + 4, y_main, "•")
                        c.drawString(main_x + 14, y_main, line)
                    else:
                        c.drawString(main_x + 14, y_main, line)
                    y_main -= 12
            y_main -= 2
            if exp.tags:
                y_main = draw_badges(exp.tags, x=main_x, y=y_main + 6, max_width=main_width)
            y_main -= 6

    if show_sections.get("Éducation", True) and cv.education and not truncated:
        y_main = draw_section_label("Éducation", x=main_x, y=y_main)
        y_main -= 2
        for edu in cv.education:
            title = f"{edu.title} — {edu.school}".strip(" —")
            title_lines = wrap_by_width(title, "Helvetica-Bold", 10.5, main_width)
            date_lines = wrap_by_width(edu.dates, "Helvetica", 9, main_width)
            details_lines: List[str] = []
            if edu.details:
                details_lines = wrap_by_width(edu.details, "Helvetica", 9.5, main_width)
            needed = len(title_lines) * 12 + len(date_lines) * 11 + len(details_lines) * 12 + 18
            if not ensure_column_space(y_main, needed):
                truncated = True
                break
            y_main = draw_lines(title_lines, x=main_x, y=y_main, font_name="Helvetica-Bold", font_size=10.5, leading=12, color=neutral)
            y_main = draw_lines(date_lines, x=main_x, y=y_main, font_name="Helvetica", font_size=9, leading=11, color=muted)
            if details_lines:
                y_main = draw_lines(details_lines, x=main_x, y=y_main, font_name="Helvetica", font_size=9.5, leading=12, color=neutral)
            y_main -= 6

    def render_side_block(title: str, content_lines: List[str], *, font_size: float = 9.5, leading: float = 12) -> None:
        nonlocal y_side, truncated
        if truncated or not content_lines:
            return
        needed = 28 + len(content_lines) * leading
        if not ensure_column_space(y_side, needed):
            truncated = True
            return
        y_side = draw_section_label(title, x=side_x, y=y_side)
        y_side = draw_lines(content_lines, x=side_x, y=y_side, font_name="Helvetica", font_size=font_size, leading=leading, color=neutral)
        y_side -= 8

    if show_sections.get("Compétences", True):
        blocks = [
            ("Langues", delist(cv.languages)),
            ("Soft skills", delist(cv.softskills)),
            ("Outils", delist(cv.tools)),
        ]
        content: List[str] = []
        for label, values in blocks:
            if values:
                content.extend(wrap_by_width(f"{label} : {values}", "Helvetica", 9.5, side_width))
        render_side_block("Compétences", content)

    if show_sections.get("Intérêts", False) and cv.interests:
        render_side_block("Centres d’intérêt", wrap_by_width(delist(cv.interests), "Helvetica", 9.5, side_width))

    if show_sections.get("Mots-clés", False) and cv.keywords:
        if not truncated:
            needed = 30
            if not ensure_column_space(y_side, needed):
                truncated = True
            else:
                y_side = draw_section_label("Mots-clés", x=side_x, y=y_side)
                y_side = draw_badges(cv.keywords, x=side_x, y=y_side + 10, max_width=side_width)

    if truncated:
        c.setFillColor(HexColor("#dc2626"))
        c.setFont("Helvetica", 8.5)
        c.drawString(margin, margin + 0.5 * cm, "Contenu réduit pour conserver une seule page. Ajuste les sections ou retire des expériences.")

    if signature_image:
        try:
            img = ImageReader(io.BytesIO(signature_image))
            img_w = 4.6 * cm
            img_h = 1.8 * cm
            c.drawImage(img, width - margin - img_w, margin + 1.4 * cm, img_w, img_h, mask="auto")
            c.setFillColor(muted)
            c.setFont("Helvetica", 8)
            c.drawString(width - margin - img_w, margin + 1.1 * cm, "Signé électroniquement")
        except Exception:
            pass

    c.setFillColor(muted)
    c.setFont("Helvetica", 8)
    c.drawString(margin, margin, f"Exporté le {datetime.now().strftime('%d/%m/%Y %H:%M')} – Généré avec Streamlit")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


# ====== UI BUILDERS ======
SECTION_DEFAULTS = [
    ("Résumé", True),
    ("Expériences", True),
    ("Éducation", True),
    ("Compétences", True),
    ("Intérêts", False),
    ("Mots-clés", False),
]


def render_sidebar() -> Dict[str, Any]:
    st.sidebar.title("⚙️ Options du CV")
    preset_name = st.sidebar.selectbox("Déclinaison (destinataire / usage)", list(PRESETS.keys()), index=0)
    preset = PRESETS[preset_name]

    if st.sidebar.button("Réordonner selon le preset"):
        apply_preset_to_state(preset)
        st.experimental_rerun()

    if st.sidebar.button("Réinitialiser le CV complet"):
        reset_state()
        st.experimental_rerun()

    theme_color = st.sidebar.color_picker("Couleur d’accent (PDF)", value="#0F766E")
    hide_sections = set(preset.get("hide_sections", []))
    show_sections: Dict[str, bool] = {}
    for label, default in SECTION_DEFAULTS:
        show_sections[label] = st.sidebar.checkbox(label, value=(label not in hide_sections and default))

    uploaded_signature = st.sidebar.file_uploader(
        "Signature (PNG/JPG sur fond transparent de préférence)", type=["png", "jpg", "jpeg"]
    )
    signature_bytes = uploaded_signature.read() if uploaded_signature else None

    st.sidebar.write("---")
    st.sidebar.caption("Astuce : coche/décoche les sections à inclure dans l’export PDF.")

    return {
        "preset_name": preset_name,
        "preset": preset,
        "theme_color": theme_color,
        "show_sections": show_sections,
        "signature": signature_bytes,
    }


def render_general_information(preset: Dict[str, Any]) -> None:
    general = st.session_state["cv_general"]
    colA, colB = st.columns([1.25, 1])

    with colA:
        st.subheader("📝 Infos générales")
        general["name"] = st.text_input("Nom complet", general["name"])
        general["headline_base"] = st.text_input("Accroche (headline)", general["headline_base"])
        use_suffix = st.checkbox(
            "Appliquer automatiquement le suffixe du preset",
            value=general.get("use_preset_headline", True),
            help="Le suffixe varie selon la déclinaison ciblée.",
        )
        general["use_preset_headline"] = use_suffix
        if use_suffix:
            suffix = preset.get("headline_addon", "")
            general["headline"] = general["headline_base"] + suffix
            if suffix:
                st.caption(f"Suffixe appliqué : {suffix}")
        else:
            general["headline"] = st.text_input("Accroche finale", general.get("headline", general["headline_base"]))
        general["summary"] = st.text_area("Résumé (profil)", general["summary"], height=130)

        c1, c2, c3 = st.columns(3)
        with c1:
            general["location"] = st.text_input("Localisation", general["location"])
        with c2:
            general["phone"] = st.text_input("Téléphone", general["phone"])
        with c3:
            general["email"] = st.text_input("Email", general["email"])

        general["linkedin"] = st.text_input("LinkedIn", general["linkedin"])
        websites_input = st.text_input("Sites (séparés par virgule ou retour)", format_list(general["websites"]))
        general["websites"] = parse_free_list(websites_input)

    with colB:
        st.subheader("🧩 Compétences & plus")
        general["languages"] = parse_free_list(
            st.text_area("Langues", format_list(general["languages"]), height=70, help="Utilise virgules ou retours à la ligne.")
        )
        general["softskills"] = parse_free_list(
            st.text_area("Soft skills", format_list(general["softskills"]), height=90)
        )
        general["tools"] = parse_free_list(
            st.text_area("Outils", format_list(general["tools"]), height=90)
        )
        general["interests"] = parse_free_list(
            st.text_area("Centres d’intérêt", format_list(general["interests"]), height=70)
        )
        general["keywords"] = parse_free_list(
            st.text_area("Mots-clés principaux", format_list(general["keywords"]), height=90)
        )
        general["use_preset_keywords"] = st.checkbox(
            "Ajouter les mots-clés suggérés par le preset",
            value=general.get("use_preset_keywords", True),
            help="Fusionne tes mots-clés avec ceux recommandés pour la cible.",
        )
        if preset.get("extra_keywords"):
            st.caption("Suggestions du preset : " + ", ".join(preset["extra_keywords"]))


def render_experience_manager() -> None:
    st.markdown('<div class="rule"></div>', unsafe_allow_html=True)
    st.subheader("🏗️ Expériences")
    experiences = st.session_state["experiences"]
    if not experiences:
        st.info("Ajoute ta première expérience professionnelle.")
    to_delete: List[int] = []
    for idx, exp in enumerate(experiences):
        header_parts = [exp.get("role", ""), exp.get("org", "")]
        header = " — ".join([part for part in header_parts if part]) or f"Expérience #{idx + 1}"
        dates = exp.get("dates", "")
        if dates:
            header += f" ({dates})"
        with st.expander(header, expanded=(idx == 0)):
            col_ctrl = st.columns([3, 1, 1, 1])
            exp["enabled"] = col_ctrl[0].checkbox(
                "Inclure dans le CV",
                value=exp.get("enabled", True),
                key=f"{exp['uid']}_enabled",
            )
            if col_ctrl[1].button("⬆️", key=f"{exp['uid']}_up") and idx > 0:
                experiences[idx - 1], experiences[idx] = experiences[idx], experiences[idx - 1]
                st.experimental_rerun()
            if col_ctrl[2].button("⬇️", key=f"{exp['uid']}_down") and idx < len(experiences) - 1:
                experiences[idx + 1], experiences[idx] = experiences[idx], experiences[idx + 1]
                st.experimental_rerun()
            if col_ctrl[3].button("🗑️", key=f"{exp['uid']}_delete"):
                to_delete.append(idx)

            exp["role"] = st.text_input("Intitulé du poste", exp["role"], key=f"{exp['uid']}_role")
            exp["org"] = st.text_input("Organisation", exp["org"], key=f"{exp['uid']}_org")
            exp["dates"] = st.text_input("Période", exp["dates"], key=f"{exp['uid']}_dates")
            bullets_text = st.text_area(
                "Points clés (une ligne = un point)",
                "\n".join(exp.get("bullets", [])),
                key=f"{exp['uid']}_bullets",
                height=140,
            )
            exp["bullets"] = [b.strip() for b in bullets_text.splitlines() if b.strip()]
            tags_text = st.text_input(
                "Tags (virgule ou retour)",
                format_list(exp.get("tags", [])),
                key=f"{exp['uid']}_tags",
            )
            exp["tags"] = parse_free_list(tags_text)
    if to_delete:
        for index in sorted(to_delete, reverse=True):
            experiences.pop(index)
        st.experimental_rerun()

    with st.expander("➕ Ajouter une expérience"):
        with st.form("add_experience_form"):
            new_role = st.text_input("Intitulé du poste", key="new_exp_role")
            new_org = st.text_input("Organisation", key="new_exp_org")
            new_dates = st.text_input("Période", key="new_exp_dates")
            new_bullets = st.text_area(
                "Points clés (une ligne = un point)",
                key="new_exp_bullets",
                height=120,
            )
            new_tags = st.text_input("Tags", key="new_exp_tags")
            if st.form_submit_button("Ajouter"):
                st.session_state["experiences"].append(
                    {
                        "uid": str(uuid4()),
                        "role": new_role.strip(),
                        "org": new_org.strip(),
                        "dates": new_dates.strip(),
                        "bullets": [b.strip() for b in new_bullets.splitlines() if b.strip()],
                        "tags": parse_free_list(new_tags),
                        "enabled": True,
                    }
                )
                for key in ["new_exp_role", "new_exp_org", "new_exp_dates", "new_exp_bullets", "new_exp_tags"]:
                    st.session_state.pop(key, None)
                st.success("Expérience ajoutée.")
                st.experimental_rerun()


def render_education_manager() -> None:
    st.markdown('<div class="rule"></div>', unsafe_allow_html=True)
    st.subheader("🎓 Éducation")
    education = st.session_state["education"]
    if not education:
        st.info("Ajoute ton parcours académique.")
    to_delete: List[int] = []
    for idx, edu in enumerate(education):
        header = edu.get("title") or f"Formation #{idx + 1}"
        school = edu.get("school")
        dates = edu.get("dates")
        subtitle = " — ".join([part for part in [school, dates] if part])
        if subtitle:
            header += f" ({subtitle})"
        with st.expander(header, expanded=(idx == 0)):
            col_ctrl = st.columns([3, 1, 1, 1])
            edu["enabled"] = col_ctrl[0].checkbox(
                "Inclure dans le CV",
                value=edu.get("enabled", True),
                key=f"{edu['uid']}_edu_enabled",
            )
            if col_ctrl[1].button("⬆️", key=f"{edu['uid']}_edu_up") and idx > 0:
                education[idx - 1], education[idx] = education[idx], education[idx - 1]
                st.experimental_rerun()
            if col_ctrl[2].button("⬇️", key=f"{edu['uid']}_edu_down") and idx < len(education) - 1:
                education[idx + 1], education[idx] = education[idx], education[idx + 1]
                st.experimental_rerun()
            if col_ctrl[3].button("🗑️", key=f"{edu['uid']}_edu_delete"):
                to_delete.append(idx)

            edu["title"] = st.text_input("Intitulé", edu["title"], key=f"{edu['uid']}_title")
            edu["school"] = st.text_input("Établissement", edu["school"], key=f"{edu['uid']}_school")
            edu["dates"] = st.text_input("Période", edu["dates"], key=f"{edu['uid']}_dates")
            edu["details"] = st.text_area("Détails", edu.get("details", ""), key=f"{edu['uid']}_details", height=120)
    if to_delete:
        for index in sorted(to_delete, reverse=True):
            education.pop(index)
        st.experimental_rerun()

    with st.expander("➕ Ajouter une formation"):
        with st.form("add_education_form"):
            new_title = st.text_input("Intitulé", key="new_edu_title")
            new_school = st.text_input("Établissement", key="new_edu_school")
            new_dates = st.text_input("Période", key="new_edu_dates")
            new_details = st.text_area("Détails", key="new_edu_details", height=120)
            if st.form_submit_button("Ajouter"):
                st.session_state["education"].append(
                    {
                        "uid": str(uuid4()),
                        "title": new_title.strip(),
                        "school": new_school.strip(),
                        "dates": new_dates.strip(),
                        "details": new_details.strip(),
                        "enabled": True,
                    }
                )
                for key in ["new_edu_title", "new_edu_school", "new_edu_dates", "new_edu_details"]:
                    st.session_state.pop(key, None)
                st.success("Formation ajoutée.")
                st.experimental_rerun()


def build_cv(preset: Dict[str, Any]) -> CVData:
    general = st.session_state["cv_general"]
    keywords = general["keywords"]
    if general.get("use_preset_keywords", True):
        keywords = merge_keywords(keywords, preset.get("extra_keywords", []))

    experiences = [
        Experience(
            role=exp.get("role", ""),
            org=exp.get("org", ""),
            dates=exp.get("dates", ""),
            bullets=exp.get("bullets", []),
            tags=exp.get("tags", []),
        )
        for exp in st.session_state["experiences"]
        if exp.get("enabled", True)
    ]

    education = [
        EducationItem(
            title=edu.get("title", ""),
            school=edu.get("school", ""),
            dates=edu.get("dates", ""),
            details=edu.get("details", ""),
        )
        for edu in st.session_state["education"]
        if edu.get("enabled", True)
    ]

    return CVData(
        name=general["name"],
        headline=general["headline"],
        location=general["location"],
        phone=general["phone"],
        email=general["email"],
        linkedin=general["linkedin"],
        websites=general["websites"],
        languages=general["languages"],
        softskills=general["softskills"],
        tools=general["tools"],
        interests=general["interests"],
        summary=general["summary"],
        experiences=experiences,
        education=education,
        keywords=keywords,
    )


def render_preview(cv: CVData, show_sections: Dict[str, bool]) -> None:
    st.markdown('<div class="rule"></div>', unsafe_allow_html=True)
    st.subheader("👀 Aperçu web")
    with st.container():
        contact_line = delist([cv.location, cv.phone, cv.email, cv.linkedin] + cv.websites)

        main_blocks: List[str] = []
        if show_sections.get("Résumé", True) and cv.summary:
            main_blocks.append(
                f"""
                <section>
                    <div class=\"h2\">Résumé</div>
                    <p class=\"muted\">{cv.summary}</p>
                </section>
                """
            )

        if show_sections.get("Expériences", True) and cv.experiences:
            exp_html = ["<div class=\"h2\">Expériences</div>"]
            for exp in cv.experiences:
                bullets = "".join([f"<li>{bullet}</li>" for bullet in exp.bullets])
                tags = "".join([f'<span class="badge">{tag}</span>' for tag in exp.tags]) if exp.tags else ""
                exp_html.append(
                    f"""
                    <article>
                        <div class=\"h3\">{exp.role} — {exp.org}</div>
                        <div class=\"small muted\">{exp.dates}</div>
                        <ul class=\"clean-list\">{bullets}</ul>
                        <div>{tags}</div>
                    </article>
                    """
                )
            main_blocks.append("".join(exp_html))

        if show_sections.get("Éducation", True) and cv.education:
            edu_html = ["<div class=\"h2\">Éducation</div>"]
            for edu in cv.education:
                details = f"<p class=\"small muted\">{edu.details}</p>" if edu.details else ""
                edu_html.append(
                    f"""
                    <article>
                        <div class=\"h3\">{edu.title}</div>
                        <div class=\"small muted\">{edu.school} — {edu.dates}</div>
                        {details}
                    </article>
                    """
                )
            main_blocks.append("".join(edu_html))

        side_blocks: List[str] = []
        if show_sections.get("Compétences", True):
            side_blocks.append(
                f"""
                <section>
                    <div class=\"h2\">Compétences</div>
                    <p><strong>Langues :</strong><br>{delist(cv.languages)}</p>
                    <p><strong>Soft skills :</strong><br>{delist(cv.softskills)}</p>
                    <p><strong>Outils :</strong><br>{delist(cv.tools)}</p>
                </section>
                """
            )
        if show_sections.get("Intérêts", False) and cv.interests:
            side_blocks.append(
                f"""
                <section>
                    <div class=\"h2\">Centres d’intérêt</div>
                    <p>{delist(cv.interests)}</p>
                </section>
                """
            )
        if show_sections.get("Mots-clés", False) and cv.keywords:
            side_blocks.append(
                f"""
                <section>
                    <div class=\"h2\">Mots-clés</div>
                    <div>{"".join([f'<span class="badge">{keyword}</span>' for keyword in cv.keywords])}</div>
                </section>
                """
            )

        preview_html = f"""
        <div class=\"cv-card\">
            <header>
                <div class=\"h1\">{cv.name}</div>
                <div class=\"muted\">{cv.headline}</div>
                <div class=\"small muted\">{contact_line}</div>
                <div class=\"rule\"></div>
            </header>
            <div class=\"grid-preview\">
                <div>{"".join(main_blocks) if main_blocks else ""}</div>
                <aside class=\"side-card\">{"".join(side_blocks) if side_blocks else ""}</aside>
            </div>
            <div class=\"footer\">Astuce : adapte l’accroche et les tags selon la cible. Les déclinaisons sont gérées dans la barre latérale.</div>
        </div>
        """

        st.markdown(preview_html, unsafe_allow_html=True)


def render_export(cv: CVData, show_sections: Dict[str, bool], signature: Optional[bytes], theme_color: str) -> None:
    st.markdown('<div class="rule"></div>', unsafe_allow_html=True)
    st.subheader("📄 Export PDF & Signature")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.write("Vérifie le contenu dans l’aperçu, puis exporte ton PDF aux couleurs choisies. Le générateur garantit une seule page en cas de contenu dense.")
    with col2:
        if st.button("Générer le PDF"):
            pdf_bytes = cv_to_pdf_bytes(cv, show_sections, signature, theme_color)
            fname = f"CV_{cv.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            download_button_bytes(pdf_bytes, fname, "⬇️ Télécharger le PDF")


# ====== MAIN APP ======
def main() -> None:
    init_state()
    sidebar_state = render_sidebar()
    preset = sidebar_state["preset"]

    st.title(PAGE_TITLE)
    with st.container():
        st.markdown(
            '<div class="cv-card header-band"><div class="title">Génère, édite et exporte ton CV en un clic</div><div class="subtitle">Déclinaisons par cible, contrôle du contenu, export PDF et signature.</div></div>',
            unsafe_allow_html=True,
        )

    render_general_information(preset)
    render_experience_manager()
    render_education_manager()

    cv = build_cv(preset)
    render_preview(cv, sidebar_state["show_sections"])
    render_export(cv, sidebar_state["show_sections"], sidebar_state["signature"], sidebar_state["theme_color"])

    st.caption("© Toi. Ce script est 100% local. Tu peux enrichir les presets/sections selon les candidatures.")


if __name__ == "__main__":
    main()
