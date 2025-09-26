"""Application Streamlit de génération et de personnalisation de CV."""

# -*- coding: utf-8 -*-
import io
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from copy import deepcopy
from uuid import uuid4
import textwrap

import streamlit as st

# ====== THEME & CSS ======
PAGE_TITLE = "CV – Générateur & Déclinaisons"
st.set_page_config(page_title=PAGE_TITLE, page_icon="🧰", layout="wide")

CSS = """
<style>
:root {
  --accent: #0F766E; /* teal-700 */
  --light: #f8fafc;
  --ink: #0f172a;
}
html, body, [class*="css"]  {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, "Helvetica Neue", Arial, "Noto Sans", "Apple Color Emoji","Segoe UI Emoji" !important;
  color: var(--ink);
}
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
.cv-card {
  background: white; border: 1px solid #e5e7eb; border-radius: 18px; padding: 24px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.badge {
  display:inline-block; padding: 2px 10px; border-radius:999px; border:1px solid #e5e7eb; margin: 0 6px 6px 0; font-size: 12px;
}
.h1 { font-size: 32px; font-weight: 800; margin-bottom: 2px; }
.h2 { font-size: 15px; color:#334155; font-weight: 600; text-transform: uppercase; letter-spacing: .12em; margin: 18px 0 8px 0;}
.h3 { font-size: 15px; font-weight:700; margin: 4px 0 2px 0; }
.muted { color:#475569; }
.rule { height:1px; background:linear-gradient(90deg,var(--accent),transparent); margin: 14px 0 10px 0;}
.header-band {
  background: linear-gradient(90deg, var(--accent), #0284c7);
  color: white; border-radius: 18px; padding: 18px; margin-bottom: 16px;
}
.header-band .title { font-size: 28px; font-weight: 800; margin:0; }
.header-band .subtitle { opacity:.95; margin-top:6px; }
.flex { display:flex; gap: 16px; flex-wrap:wrap; }
.col { flex:1; min-width:220px; }
.small { font-size: 12px; }
.footer { border-top:1px dashed #e2e8f0; margin-top:14px; padding-top:10px; font-size:12px; color:#64748b;}
.sign-line { margin-top: 18px; }
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


def wrap_lines(text: str, width: int = 92) -> List[str]:
    lines = textwrap.wrap(text, width=width)
    return lines or [text]


def ensure_space(y: float, margin: float, needed: float) -> bool:
    return (y - needed) > (margin + 36)


def cv_to_pdf_bytes(cv: CVData, show_sections: Dict[str, bool], signature_image: Optional[bytes], theme_color: str) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    margin = 1.8 * cm
    x = margin
    y = height - margin

    c.setTitle(f"CV - {cv.name}")
    accent = HexColor(theme_color) if theme_color else HexColor("#0F766E")

    def write_text(txt: str, size: int = 11, bold: bool = False, color: str = "#0f172a", leading: float = 14.0) -> None:
        nonlocal x, y
        c.setFillColor(HexColor(color))
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        for line in txt.split("\n"):
            c.drawString(x, y, line)
            y -= leading

    def section(title: str) -> None:
        nonlocal y
        y -= 6
        c.setFillColor(accent)
        c.setLineWidth(2)
        c.line(margin, y, margin + 60, y)
        y -= 12
        write_text(title, size=11, bold=True, color="#0f172a")

    # Header band
    c.setFillColor(accent)
    c.roundRect(margin - 6, height - margin - 38, width - 2 * margin + 12, 38, 10, fill=True, stroke=0)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, height - margin - 18, cv.name)
    c.setFont("Helvetica", 10)
    c.drawString(margin, height - margin - 32, cv.headline[:140])

    y = height - margin - 52

    contacts = delist([cv.location, cv.phone, cv.email, cv.linkedin] + cv.websites)
    write_text(contacts, size=9, color="#334155", leading=11)

    truncated = False

    if show_sections.get("Résumé", True) and cv.summary:
        summary_lines = wrap_lines(cv.summary, width=110)
        required = (len(summary_lines) + 3) * 12
        if ensure_space(y, margin, required):
            section("Résumé")
            for line in summary_lines:
                write_text(line, size=10, color="#111827", leading=13)
        else:
            truncated = True

    if show_sections.get("Expériences", True) and cv.experiences and not truncated:
        section("Expériences")
        for exp in cv.experiences:
            bullet_lines = sum(len(wrap_lines(b, width=96)) for b in exp.bullets)
            needed = (bullet_lines + 4) * 12
            if not ensure_space(y, margin, needed):
                truncated = True
                break
            write_text(f"{exp.role} — {exp.org}", size=10.5, bold=True, color="#0f172a")
            write_text(exp.dates, size=9, color="#475569", leading=11)
            for bullet in exp.bullets:
                wrapped = wrap_lines(bullet, width=96)
                for idx, line in enumerate(wrapped):
                    prefix = "• " if idx == 0 else "  "
                    c.setFillColor(HexColor("#111827"))
                    c.setFont("Helvetica", 9.5)
                    c.drawString(x + 8, y, prefix + line)
                    y -= 11
            if exp.tags:
                tags_line = ", ".join(exp.tags)
                write_text(tags_line, size=8.5, color="#0f172a", leading=10)

    if show_sections.get("Éducation", True) and cv.education and not truncated:
        section("Éducation")
        for ed in cv.education:
            needed = 36
            if ed.details:
                needed += len(wrap_lines(ed.details, width=100)) * 11
            if not ensure_space(y, margin, needed):
                truncated = True
                break
            write_text(f"{ed.title} — {ed.school}", size=10.5, bold=True)
            write_text(ed.dates, size=9, color="#475569", leading=11)
            if ed.details:
                for line in wrap_lines(ed.details, width=100):
                    write_text(line, size=9.5, color="#111827", leading=12)

    if show_sections.get("Compétences", True) and not truncated:
        section("Compétences")
        blocks = [
            ("Langues", delist(cv.languages)),
            ("Soft skills", delist(cv.softskills)),
            ("Outils", delist(cv.tools)),
        ]
        for title, content in blocks:
            needed = 16
            if not ensure_space(y, margin, needed):
                truncated = True
                break
            write_text(f"{title} : {content}", size=9.5, color="#111827", leading=12)

    if show_sections.get("Intérêts", False) and cv.interests and not truncated:
        needed = 24
        if ensure_space(y, margin, needed):
            section("Centres d’intérêt")
            write_text(delist(cv.interests), size=9.5, color="#111827", leading=12)
        else:
            truncated = True

    if show_sections.get("Mots-clés", False) and cv.keywords and not truncated:
        needed = 24
        if ensure_space(y, margin, needed):
            section("Mots-clés")
            write_text(delist(cv.keywords), size=9.5, color="#111827", leading=12)
        else:
            truncated = True

    if truncated:
        write_text(
            "Contenu réduit pour maintenir une seule page. Ajuste la sélection des sections ou des expériences.",
            size=8.5,
            color="#dc2626",
            leading=10,
        )

    if signature_image:
        try:
            img = ImageReader(io.BytesIO(signature_image))
            img_w = 4.6 * cm
            img_h = 1.8 * cm
            c.drawImage(img, width - margin - img_w, margin + 1.2 * cm, img_w, img_h, mask="auto")
            c.setFillColor(HexColor("#64748b"))
            c.setFont("Helvetica", 8)
            c.drawString(width - margin - img_w, margin + 1.0 * cm, "Signé électroniquement")
        except Exception:
            pass

    c.setFillColor(HexColor("#64748b"))
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
        st.markdown('<div class="cv-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="h1">{cv.name}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="muted">{cv.headline}</div>', unsafe_allow_html=True)
        contact_line = delist([cv.location, cv.phone, cv.email, cv.linkedin] + cv.websites)
        st.markdown(f'<div class="small muted">{contact_line}</div>', unsafe_allow_html=True)
        st.markdown('<div class="rule"></div>', unsafe_allow_html=True)

        if show_sections.get("Résumé", True) and cv.summary:
            st.markdown('<div class="h2">Résumé</div>', unsafe_allow_html=True)
            st.write(cv.summary)

        col_main, col_side = st.columns([1.75, 1])
        with col_main:
            if show_sections.get("Expériences", True) and cv.experiences:
                st.markdown('<div class="h2">Expériences</div>', unsafe_allow_html=True)
                for exp in cv.experiences:
                    st.markdown(f'<div class="h3">{exp.role} — {exp.org}</div>', unsafe_allow_html=True)
                    st.caption(exp.dates)
                    for bullet in exp.bullets:
                        st.markdown(f"- {bullet}")
                    if exp.tags:
                        st.markdown(
                            "".join([f'<span class="badge">{tag}</span>' for tag in exp.tags]),
                            unsafe_allow_html=True,
                        )
            if show_sections.get("Éducation", True) and cv.education:
                st.markdown('<div class="h2">Éducation</div>', unsafe_allow_html=True)
                for edu in cv.education:
                    st.markdown(f'<div class="h3">{edu.title}</div>', unsafe_allow_html=True)
                    st.caption(f"{edu.school} – {edu.dates}")
                    if edu.details:
                        st.markdown(edu.details)

        with col_side:
            if show_sections.get("Compétences", True):
                st.markdown('<div class="h2">Compétences</div>', unsafe_allow_html=True)
                st.markdown(f"**Langues :** {delist(cv.languages)}")
                st.markdown(f"**Soft skills :** {delist(cv.softskills)}")
                st.markdown(f"**Outils :** {delist(cv.tools)}")
            if show_sections.get("Intérêts", False) and cv.interests:
                st.markdown('<div class="h2">Centres d’intérêt</div>', unsafe_allow_html=True)
                st.markdown(delist(cv.interests))
            if show_sections.get("Mots-clés", False) and cv.keywords:
                st.markdown('<div class="h2">Mots-clés</div>', unsafe_allow_html=True)
                st.markdown(
                    "".join([f'<span class="badge">{keyword}</span>' for keyword in cv.keywords]),
                    unsafe_allow_html=True,
                )

        st.markdown(
            '<div class="footer">Astuce : adapte l’accroche et les tags selon la cible. Les déclinaisons sont gérées dans la barre latérale.</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)


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
