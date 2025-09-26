# app.py
# -*- coding: utf-8 -*-
import io
import base64
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

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
.h2 { font-size: 16px; color:#334155; font-weight: 600; text-transform: uppercase; letter-spacing: .12em; margin: 18px 0 8px 0;}
.h3 { font-size: 15px; font-weight:700; margin: 4px 0 2px 0; }
.muted { color:#475569; }
.rule { height:1px; background:linear-gradient(90deg,var(--accent),transparent); margin: 14px 0 10px 0;}
.header-band {
  background: linear-gradient(90deg, var(--accent), #0284c7);
  color: white; border-radius: 18px; padding: 18px; margin-bottom: 16px;
}
.header-band .title { font-size: 28px; font-weight: 800; margin:0; }
.header-band .subtitle { opacity:.95; margin-top:6px; }
.flex { display:flex; gap: 16px; }
.col { flex:1; }
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
        "hide_sections": [],
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
def filter_experiences(exps: List[Experience], keep_tags: List[str]) -> List[Experience]:
    if not keep_tags:
        return exps
    keep = []
    for e in exps:
        if set(e.tags).intersection(set(keep_tags)):
            keep.append(e)
    # Si rien ne matche, on garde tout (prudence)
    return keep or exps

def delist(items: List[str]) -> str:
    return " · ".join(items) if items else ""

def download_button_bytes(bin_bytes: bytes, filename: str, label: str):
    st.download_button(label, data=bin_bytes, file_name=filename, mime="application/pdf")

# ====== PDF (ReportLab) ======
# ReportLab est pur-Python, fiable localement.
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor

def cv_to_pdf_bytes(cv: CVData, show_sections: Dict[str, bool], signature_image: Optional[bytes], theme_color: str) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    margin = 2.0*cm
    x = margin
    y = height - margin

    c.setTitle(f"CV - {cv.name}")
    accent = HexColor(theme_color) if theme_color else HexColor("#0F766E")

    def write_text(txt, size=11, bold=False, color="#0f172a", leading=14):
        nonlocal x, y
        c.setFillColor(HexColor(color))
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        for line in txt.split("\n"):
            c.drawString(x, y, line)
            y -= leading

    # Header band
    c.setFillColor(accent)
    c.roundRect(margin-6, height-margin-32, width-2*margin+12, 32, 10, fill=True, stroke=0)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, height-margin-20, cv.name)
    c.setFont("Helvetica", 10)
    c.drawString(margin, height-margin-34, cv.headline[:120])

    y = height - margin - 48

    # Coordinates
    small = f"{cv.location}  |  {cv.phone}  |  {cv.email}  |  {cv.linkedin}"
    write_text(small, size=9, color="#334155", leading=12)

    def section(title):
        nonlocal y
        y -= 6
        c.setFillColor(accent); c.setLineWidth(2)
        c.line(margin, y, margin + 60, y)
        y -= 12
        write_text(title, size=11, bold=True, color="#0f172a")

    # Summary
    if show_sections.get("Résumé", True) and cv.summary:
        section("Résumé")
        write_text(cv.summary, size=10, color="#111827", leading=14)

    # Expériences
    if show_sections.get("Expériences", True) and cv.experiences:
        section("Expériences")
        for e in cv.experiences:
            if y < 100:  # nouvelle page si trop bas
                c.showPage(); y = height - margin
            write_text(f"{e.role} — {e.org}", size=10.5, bold=True)
            write_text(e.dates, size=9, color="#475569", leading=12)
            for b in e.bullets:
                if y < 80:
                    c.showPage(); y = height - margin
                c.setFillColor(HexColor("#111827"))
                c.setFont("Helvetica", 10)
                c.drawString(x+10, y, u"• " + b)
                y -= 13

    # Éducation
    if show_sections.get("Éducation", True) and cv.education:
        section("Éducation")
        for ed in cv.education:
            write_text(f"{ed.title} — {ed.school}", size=10.5, bold=True)
            write_text(ed.dates, size=9, color="#475569", leading=12)
            if ed.details:
                write_text(ed.details, size=10, color="#111827", leading=13)

    # Compétences
    if show_sections.get("Compétences", True):
        section("Compétences")
        write_text("Langues : " + delist(cv.languages), size=10)
        write_text("Soft skills : " + delist(cv.softskills), size=10)
        write_text("Outils : " + delist(cv.tools), size=10)

    # Centres d’intérêt
    if show_sections.get("Intérêts", False) and cv.interests:
        section("Centres d’intérêt")
        write_text(delist(cv.interests), size=10)

    # Mots-clés
    if show_sections.get("Mots-clés", False) and cv.keywords:
        section("Mots-clés")
        write_text(delist(cv.keywords), size=10)

    # Signature
    if signature_image:
        try:
            img = ImageReader(io.BytesIO(signature_image))
            img_w = 4.8*cm
            img_h = 2.0*cm
            c.drawImage(img, width - margin - img_w, margin + 1.2*cm, img_w, img_h, mask='auto')
            write_text("\n\nSigné électroniquement", size=8, color="#64748b", leading=10)
        except Exception:
            pass

    # Footer
    c.setFillColor(HexColor("#64748b"))
    c.setFont("Helvetica", 8)
    c.drawString(margin, margin, f"Exporté le {datetime.now().strftime('%d/%m/%Y %H:%M')} – Généré avec Streamlit")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()

# ====== SIDEBAR – OPTIONS ======
st.sidebar.title("⚙️ Options du CV")

preset_name = st.sidebar.selectbox("Déclinaison (destinataire / usage)", list(PRESETS.keys()), index=0)

theme_color = st.sidebar.color_picker("Couleur d’accent (PDF)", value="#0F766E")
show_sections = {
    "Résumé": st.sidebar.checkbox("Résumé", value=True),
    "Expériences": st.sidebar.checkbox("Expériences", value=True),
    "Éducation": st.sidebar.checkbox("Éducation", value=True),
    "Compétences": st.sidebar.checkbox("Compétences", value=True),
    "Intérêts": st.sidebar.checkbox("Centres d’intérêt", value=False),
    "Mots-clés": st.sidebar.checkbox("Mots-clés", value=False),
}

uploaded_signature = st.sidebar.file_uploader("Signature (PNG/JPG sur fond transparent de préférence)", type=["png", "jpg", "jpeg"])
signature_bytes = uploaded_signature.read() if uploaded_signature else None

st.sidebar.write("---")
st.sidebar.caption("Astuce : coche/décoche les sections à inclure dans l’export PDF.")

# ====== MAIN – ÉDITION RAPIDE ======
st.title(PAGE_TITLE)

with st.container():
    st.markdown('<div class="cv-card header-band"><div class="title">Génère, édite et exporte ton CV en un clic</div><div class="subtitle">Déclinaisons par cible, contrôle du contenu, export PDF et signature.</div></div>', unsafe_allow_html=True)

colA, colB = st.columns([1.2, 1])
with colA:
    st.subheader("📝 Infos générales")
    name = st.text_input("Nom complet", seed.name)
    headline_base = st.text_input("Accroche (headline)", seed.headline)
    preset = PRESETS[preset_name]
    headline = headline_base + preset.get("headline_addon", "")

    summary = st.text_area("Résumé (profil)", seed.summary, height=110)

    c1, c2, c3 = st.columns(3)
    with c1:
        location = st.text_input("Localisation", seed.location)
    with c2:
        phone = st.text_input("Téléphone", seed.phone)
    with c3:
        email = st.text_input("Email", seed.email)

    linkedin = st.text_input("LinkedIn", seed.linkedin)
    websites = st.text_input("Sites (séparés par ‘,’)", ", ".join(seed.websites))

with colB:
    st.subheader("🧩 Compétences & plus")
    languages = st.text_input("Langues", ", ".join(seed.languages))
    softskills = st.text_input("Soft skills", ", ".join(seed.softskills))
    tools = st.text_input("Outils", ", ".join(seed.tools))
    interests = st.text_input("Centres d’intérêt", ", ".join(seed.interests))
    keywords = st.text_input("Mots-clés", ", ".join(seed.keywords + preset.get("extra_keywords", [])))

st.markdown('<div class="rule"></div>', unsafe_allow_html=True)

# ====== EXPÉRIENCES – ÉDITION LÉGÈRE ======
st.subheader("🏗️ Expériences")
keep_tags = preset.get("keep_tags", [])
exp_list = filter_experiences(seed.experiences, keep_tags)

edited_exps: List[Experience] = []
for i, e in enumerate(exp_list):
    with st.expander(f"{e.role} — {e.org} ({e.dates})", expanded=(i==0)):
        role = st.text_input(f"Poste {i+1}", e.role, key=f"role_{i}")
        org = st.text_input(f"Organisation {i+1}", e.org, key=f"org_{i}")
        dates = st.text_input(f"Dates {i+1}", e.dates, key=f"dates_{i}")
        bullets = st.text_area(f"Points-clés {i+1} (une ligne = un point)", "\n".join(e.bullets), key=f"bul_{i}").splitlines()
        tags = st.text_input(f"Tags {i+1}", ", ".join(e.tags), key=f"tags_{i}").split(",")
        edited_exps.append(Experience(role=role, org=org, dates=dates, bullets=[b.strip() for b in bullets if b.strip()], tags=[t.strip() for t in tags if t.strip()]))

# ====== ÉDUCATION ======
st.subheader("🎓 Éducation")
edited_edu: List[EducationItem] = []
for i, ed in enumerate(seed.education):
    with st.expander(f"{ed.title} — {ed.school} ({ed.dates})", expanded=(i==0)):
        title = st.text_input(f"Titre {i+1}", ed.title, key=f"ed_title_{i}")
        school = st.text_input(f"École {i+1}", ed.school, key=f"ed_school_{i}")
        dates = st.text_input(f"Dates {i+1}", ed.dates, key=f"ed_dates_{i}")
        details = st.text_area(f"Détails {i+1}", ed.details, key=f"ed_det_{i}")
        edited_edu.append(EducationItem(title=title, school=school, dates=dates, details=details))

# ====== OBJET FINAL ======
cv = CVData(
    name=name, headline=headline, location=location, phone=phone, email=email, linkedin=linkedin,
    websites=[w.strip() for w in websites.split(",") if w.strip()],
    languages=[l.strip() for l in languages.split(",") if l.strip()],
    softskills=[s.strip() for s in softskills.split(",") if s.strip()],
    tools=[t.strip() for t in tools.split(",") if t.strip()],
    interests=[i.strip() for i in interests.split(",") if i.strip()],
    summary=summary, experiences=edited_exps, education=edited_edu,
    keywords=[k.strip() for k in keywords.split(",") if k.strip()]
)

# ====== APERCU WEB (carte élégante) ======
st.subheader("👀 Aperçu web")
with st.container():
    st.markdown('<div class="cv-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="h1">{cv.name}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="muted">{cv.headline}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="small muted">{cv.location} · {cv.phone} · {cv.email} · {cv.linkedin}</div>', unsafe_allow_html=True)
    st.markdown('<div class="rule"></div>', unsafe_allow_html=True)

    if show_sections.get("Résumé", True) and cv.summary:
        st.markdown('<div class="h2">Résumé</div>', unsafe_allow_html=True)
        st.write(cv.summary)

    if show_sections.get("Expériences", True):
        st.markdown('<div class="h2">Expériences</div>', unsafe_allow_html=True)
        for e in cv.experiences:
            st.markdown(f'<div class="h3">{e.role} — {e.org}</div>', unsafe_allow_html=True)
            st.caption(e.dates)
            for b in e.bullets:
                st.markdown(f"- {b}")
            if e.tags:
                st.markdown("".join([f'<span class="badge">{t}</span>' for t in e.tags]), unsafe_allow_html=True)

    if show_sections.get("Éducation", True):
        st.markdown('<div class="h2">Éducation</div>', unsafe_allow_html=True)
        for ed in cv.education:
            st.markdown(f'<div class="h3">{ed.title} — {ed.school}</div>', unsafe_allow_html=True)
            st.caption(ed.dates)
            if ed.details:
                st.markdown(ed.details)

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
        st.markdown("".join([f'<span class="badge">{k}</span>' for k in cv.keywords]), unsafe_allow_html=True)

    st.markdown('<div class="footer">Astuce : adapte l’accroche et les tags selon la cible. Les déclinaisons sont gérées dans la barre latérale.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ====== EXPORT PDF ======
st.markdown('<div class="rule"></div>', unsafe_allow_html=True)
st.subheader("📄 Export PDF & Signature")

col1, col2 = st.columns([1,1])
with col1:
    st.write("Vérifie le contenu dans l’aperçu, puis exporte ton PDF aux couleurs choisies.")
with col2:
    if st.button("Générer le PDF"):
        pdf_bytes = cv_to_pdf_bytes(cv, show_sections, signature_bytes, theme_color)
        fname = f"CV_{cv.name.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        download_button_bytes(pdf_bytes, fname, "⬇️ Télécharger le PDF")

# ====== FIN ======
st.caption("© Toi. Ce script est 100% local. Tu peux enrichir les presets/sections selon les candidatures.")