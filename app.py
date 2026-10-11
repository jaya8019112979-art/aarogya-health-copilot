import json
import re
from datetime import datetime
from io import BytesIO

import streamlit as st


st.set_page_config(
    page_title="Aarogya | Personal Health Copilot",
    page_icon="✳️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
    :root {
        --ink:#18352f; --muted:#70817a; --green:#286c55; --green-dark:#19483a;
        --mint:#eaf4ed; --paper:#f6f8f5; --line:#e4ebe5; --white:#fff;
    }
    html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
    .stApp { background:var(--paper); color:var(--ink); }
    [data-testid="stSidebar"], [data-testid="collapsedControl"],
    [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] { display:none; }
    [data-testid="stHeader"] { background:transparent; }
    [data-testid="stMainBlockContainer"] {
        max-width:1160px; padding:1.1rem 2.3rem 3.5rem !important;
    }
    h1,h2,h3,h4 { font-family:'Manrope',sans-serif; color:var(--ink); letter-spacing:-.035em; }
    h1 { font-size:2rem; font-weight:750; }
    h2 { font-size:1.5rem; }
    p, li { color:#50645c; }
    a { color:var(--green); }
    .site-header {
        display:flex; align-items:center; justify-content:space-between; gap:1rem;
        padding:.35rem 0 1.05rem; border-bottom:1px solid var(--line); margin-bottom:.55rem;
    }
    .brand { display:flex; align-items:center; gap:.7rem; }
    .brand-mark {
        width:40px; height:40px; display:grid; place-items:center; border-radius:14px;
        color:#fff; background:var(--green); font-size:1.35rem; font-weight:700;
    }
    .brand-name { color:var(--ink); font:800 1.22rem 'Manrope',sans-serif; letter-spacing:-.05em; }
    .brand-sub { color:var(--muted); font-size:.73rem; margin-top:-.1rem; }
    .privacy-badge {
        color:#426859; background:#eaf3ec; border:1px solid #dce9de;
        border-radius:999px; padding:.42rem .75rem; font-size:.75rem; font-weight:600;
    }
    [data-testid="stRadio"] { margin:.25rem 0 1.3rem; }
    [data-testid="stRadio"] > label { display:none; }
    [data-testid="stRadio"] [role="radiogroup"] {
        gap:.4rem; border-bottom:1px solid var(--line); padding-bottom:.8rem;
    }
    [data-testid="stRadio"] [role="radiogroup"] label {
        border:1px solid transparent; border-radius:10px; padding:.48rem .82rem;
        color:#62746c; transition:all .15s ease;
    }
    [data-testid="stRadio"] [role="radiogroup"] label:hover {
        background:#edf3ee; color:var(--green-dark);
    }
    [data-testid="stRadio"] [role="radiogroup"] label[data-selected="true"] {
        background:#e8f2e9; border-color:#dceade; color:var(--green-dark); font-weight:700;
    }
    [data-testid="stRadio"] [role="radiogroup"] label > div > div:first-child { display:none; }
    [data-testid="stRadio"] [role="radiogroup"] label > div { display:block; }
    .hero {
        position:relative; overflow:hidden; padding:2.3rem 2.5rem; border-radius:24px;
        color:#f7fbf6; background:linear-gradient(115deg,#183e35 0%,#286b53 64%,#77a687 100%);
        box-shadow:0 16px 36px rgba(27,71,56,.12);
    }
    .hero:after {
        content:""; position:absolute; width:260px; height:260px; right:-70px; top:-110px;
        border:1px solid rgba(255,255,255,.16); border-radius:50%;
        box-shadow:0 0 0 32px rgba(255,255,255,.035),0 0 0 68px rgba(255,255,255,.025);
    }
    .hero h1 { position:relative; z-index:1; color:#fff; font-size:2.55rem; line-height:1.12; margin:.42rem 0; }
    .hero p { position:relative; z-index:1; color:#e0eee3; max-width:560px; margin:.55rem 0 0; font-size:1.02rem; line-height:1.6; }
    .eyebrow { color:#c8e0cc; font-size:.72rem; font-weight:700; letter-spacing:.13em; text-transform:uppercase; }
    .section-label { color:var(--green); font-size:.75rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; }
    .soft-card {
        background:var(--white); padding:1.1rem 1.2rem; border:1px solid var(--line);
        border-radius:16px; min-height:100px; box-shadow:0 4px 14px rgba(31,64,49,.025);
    }
    .soft-card small { color:var(--muted); font-size:.78rem; }
    .soft-card strong { display:block; color:var(--ink); font:750 1.65rem 'Manrope',sans-serif; margin-top:.25rem; }
    .panel {
        background:white; border:1px solid var(--line); border-radius:18px; padding:1.25rem 1.4rem;
        box-shadow:0 4px 14px rgba(31,64,49,.025);
    }
    .empty-state {
        text-align:center; padding:2rem 1rem; border:1px dashed #cbd9ce; border-radius:18px;
        background:rgba(255,255,255,.7);
    }
    .empty-icon { font-size:2rem; margin-bottom:.35rem; }
    .empty-title { color:var(--ink); font:700 1.05rem 'Manrope',sans-serif; }
    .empty-copy { color:var(--muted); font-size:.9rem; max-width:440px; margin:.35rem auto 0; }
    .stButton > button, .stDownloadButton > button {
        min-height:2.65rem; border-radius:10px; font-weight:650;
        transition:transform .15s ease, box-shadow .15s ease;
    }
    .stButton > button[kind="primary"], .stDownloadButton > button {
        background:var(--green); border-color:var(--green); color:#fff;
    }
    .stButton > button[kind="primary"]:hover, .stDownloadButton > button:hover {
        background:var(--green-dark); border-color:var(--green-dark); color:#fff;
        transform:translateY(-1px); box-shadow:0 6px 14px rgba(31,89,66,.18);
    }
    .stButton > button[kind="primary"] *, .stDownloadButton > button * { color:#fff !important; }
    [data-testid="stFileUploader"] section {
        border-radius:14px; border-color:#bdd1c1; background:#fbfdfb;
    }
    [data-testid="stFileUploader"] section:hover { border-color:var(--green); }
    [data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input,
    [data-testid="stSelectbox"] > div > div {
        border-radius:10px; border-color:#dce5dd; background:#fff;
    }
    [data-testid="stAlert"] { border-radius:12px; }
    [data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
    .timeline-date { color:var(--green); font-size:.8rem; font-weight:700; }
    .site-footer {
        border-top:1px solid var(--line); margin-top:2rem; padding-top:1rem;
        color:var(--muted); font-size:.75rem; display:flex; justify-content:space-between; gap:1rem;
    }
    .hero {
        display:grid; grid-template-columns:minmax(0,1.3fr) minmax(230px,.7fr);
        align-items:center; gap:2rem; padding:2.55rem 2.7rem;
    }
    .hero h1 { max-width:600px; font-size:2.7rem; }
    .hero p { max-width:510px; }
    .hero-action-note { position:relative; z-index:1; margin-top:1.15rem; color:#d6e8da; font-size:.8rem; }
    .hero-aside {
        position:relative; z-index:1; padding:1.2rem 1.3rem; border:1px solid rgba(255,255,255,.2);
        border-radius:18px; background:rgba(255,255,255,.09); backdrop-filter:blur(6px);
    }
    .hero-aside-title { color:#fff; font:700 1rem 'Manrope',sans-serif; margin-bottom:.8rem; }
    .hero-step { display:flex; align-items:center; gap:.7rem; padding:.58rem 0; color:#e0eee3; font-size:.82rem; }
    .hero-step + .hero-step { border-top:1px solid rgba(255,255,255,.13); }
    .hero-step-icon {
        width:28px; height:28px; display:grid; place-items:center; flex:0 0 28px;
        border-radius:9px; color:#e8f4e9; background:rgba(255,255,255,.13); font-size:.85rem;
    }
    .overview-heading { display:flex; align-items:end; justify-content:space-between; gap:1rem; margin:.4rem 0 .8rem; }
    .overview-heading h2 { margin:.15rem 0 0; font-size:1.25rem; }
    .overview-heading p { margin:0; color:var(--muted); font-size:.8rem; }
    .overview-panel {
        height:100%; padding:1.25rem 1.35rem; border:1px solid var(--line);
        border-radius:16px; background:#fff;
    }
    .overview-panel h3 { margin:.35rem 0; font-size:1.12rem; }
    .overview-panel p { margin:.3rem 0 .9rem; font-size:.88rem; line-height:1.55; }
    .overview-tag {
        display:inline-flex; align-items:center; gap:.35rem; padding:.32rem .6rem;
        border-radius:999px; background:#eef5ef; color:#426859; font-size:.7rem; font-weight:700;
    }
    .workflow-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.85rem; margin-top:.7rem; }
    .workflow-card {
        padding:1rem 1.05rem; border:1px solid var(--line); border-radius:14px;
        background:rgba(255,255,255,.72);
    }
    .workflow-card-icon { font-size:1.1rem; }
    .workflow-card strong { display:block; color:var(--ink); font:700 .87rem 'Manrope',sans-serif; margin:.48rem 0 .24rem; }
    .workflow-card span { color:var(--muted); font-size:.77rem; line-height:1.45; }
    .privacy-note {
        display:flex; align-items:flex-start; gap:.55rem; padding:.8rem .95rem;
        border:1px solid #e3eadf; border-radius:12px; background:#f0f5ed;
        color:#526b5b; font-size:.76rem; line-height:1.5;
    }
    @media (max-width:720px) {
        [data-testid="stAppViewContainer"] .main .block-container { padding:.8rem 1rem 2rem; }
        .site-header { align-items:flex-start; }
        .privacy-badge { font-size:.68rem; padding:.35rem .55rem; }
        .hero { padding:1.65rem 1.35rem; border-radius:18px; }
        .hero h1 { font-size:2rem; }
        .hero { grid-template-columns:1fr; gap:1rem; }
        .hero-aside { max-width:100%; }
        .workflow-grid { grid-template-columns:1fr; }
        .overview-heading { align-items:flex-start; flex-direction:column; }
        [data-testid="stRadio"] [role="radiogroup"] { gap:.15rem; flex-wrap:wrap; }
        [data-testid="stRadio"] [role="radiogroup"] label { padding:.42rem .58rem; font-size:.83rem; }
        .site-footer { flex-direction:column; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "records" not in st.session_state:
    st.session_state.records = []


def extract_document_text(uploaded_file):
    """Extract searchable PDF text, falling back to local Tesseract OCR."""
    content = uploaded_file.getvalue()
    suffix = uploaded_file.name.rsplit(".", 1)[-1].lower()

    if suffix == "pdf":
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages).strip()
        if text:
            return text

        try:
            import fitz
            import pytesseract
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError(
                "This looks like a scanned PDF. Install the OCR packages and "
                "Tesseract (see README.md), then try again."
            ) from exc

        document = fitz.open(stream=content, filetype="pdf")
        ocr_pages = []
        for page in document:
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image = Image.open(BytesIO(pixmap.tobytes("png")))
            ocr_pages.append(pytesseract.image_to_string(image))
        text = "\n".join(ocr_pages).strip()
        if not text:
            raise RuntimeError("No readable text was found in this PDF.")
        return text

    try:
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError(
            "Image OCR packages are not installed. Follow the setup instructions in README.md."
        ) from exc

    image = Image.open(BytesIO(content))
    text = pytesseract.image_to_string(image).strip()
    if not text:
        raise RuntimeError("No readable text was found in this image.")
    return text


def extract_health_data(text):
    """Extract only explicit values and labels; avoid guessing clinical meaning."""
    observations = []
    medications = []
    dates = []
    diagnoses = []
    date_pattern = re.compile(
        r"\b(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b"
    )
    lab_pattern = re.compile(
        r"^\s*([A-Za-z][A-Za-z0-9 /().%-]{1,45}?)\s*[:\-]\s*"
        r"([<>]?\s*-?\d+(?:\.\d+)?)\s*"
        r"([A-Za-zµμ/%°][A-Za-zµμ/%°0-9.^-]*)?"
        r"(?:\s*\((?:ref(?:erence)?\s*)?([<>]?\s*-?\d+(?:\.\d+)?)"
        r"\s*(?:-|–|to)\s*([<>]?\s*-?\d+(?:\.\d+)?)(?:\s*([^)]+))?\))?",
        re.IGNORECASE,
    )
    medication_pattern = re.compile(
        r"^\s*([A-Za-z][A-Za-z0-9 /().-]{1,45}?)\s+"
        r"(\d+(?:\.\d+)?\s*(?:mg|mcg|µg|g|ml|mL|IU|units?))\b(.*)$",
        re.IGNORECASE,
    )

    for line in text.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        for found_date in date_pattern.findall(cleaned):
            if found_date not in dates:
                dates.append(found_date)

        lab_match = lab_pattern.match(cleaned)
        if lab_match and (lab_match.group(4) or lab_match.group(5)):
            name = lab_match.group(1).strip()
            raw_value = lab_match.group(2).replace(" ", "")
            value = float(raw_value.lstrip("<>"))
            low = float(lab_match.group(4).replace(" ", "").lstrip("<>"))
            high = float(lab_match.group(5).replace(" ", "").lstrip("<>"))
            if raw_value.startswith(("<", ">")):
                status = "Not compared (qualified result)"
            else:
                status = "Low" if value < low else "High" if value > high else "Within provided range"
            observations.append(
                {
                    "name": name,
                    "value": raw_value,
                    "unit": (lab_match.group(3) or "").strip(),
                    "reference_low": lab_match.group(4).strip(),
                    "reference_high": lab_match.group(5).strip(),
                    "reference_unit": (lab_match.group(6) or "").strip(),
                    "status": status,
                }
            )
            continue

        medication_match = medication_pattern.match(cleaned)
        if medication_match and not re.search(
            r"\b(?:reference|normal|range|result|level)\b", cleaned, re.IGNORECASE
        ):
            medications.append(
                {
                    "name": medication_match.group(1).strip(),
                    "dose": medication_match.group(2).strip(),
                    "instructions": medication_match.group(3).strip(" ,;:-"),
                }
            )

    for match in re.finditer(
        r"(?im)^\s*(?:diagnosis|impression)\s*:\s*(.+)$", text
    ):
        value = match.group(1).strip()
        if value:
            diagnoses.append(value)

    return {
        "observations": observations,
        "medications": medications,
        "dates": dates,
        "diagnoses": diagnoses,
    }


def create_summary(health_data, language):
    """Produce a cautious, rule-based recap; no diagnosis or treatment advice."""
    phrases = {
        "English": {
            "title": "Record overview",
            "empty": "No structured lab values, medicines, or dates were recognized. Review the original report.",
            "abnormal": "The report lists {name} as {value} {unit} (reference {low}–{high}); this is outside the range printed on that report.",
            "normal": "{name}: {value} {unit} (within the range printed on the report: {low}–{high}).",
            "qualified": "{name}: {value} {unit}. The report uses a qualified value, so it was not automatically compared with the stated range ({low}–{high}).",
            "medicine": "Medicine text found: {name}, {dose}{instructions}. Confirm the directions with your prescription and care team.",
            "diagnosis": "Diagnosis/impression text on the document: {value}",
            "date": "Date(s) found in the document: {value}",
            "disclaimer": "This is a text extraction, not a diagnosis. Reference intervals vary by lab and person. Ask a qualified clinician to interpret results, especially if you have symptoms.",
        },
        "Hindi": {
            "title": "रिकॉर्ड का सार",
            "empty": "कोई संरचित लैब मान, दवा या तारीख़ नहीं मिली। मूल रिपोर्ट की जाँच करें।",
            "abnormal": "रिपोर्ट में {name}: {value} {unit} (दर्ज संदर्भ सीमा {low}–{high}) है; यह रिपोर्ट में दी गई सीमा से बाहर है।",
            "normal": "{name}: {value} {unit} (रिपोर्ट में दी गई सीमा {low}–{high} के भीतर)।",
            "qualified": "{name}: {value} {unit}। रिपोर्ट में विशेष चिह्न वाला मान है, इसलिए इसकी तुलना दर्ज सीमा ({low}–{high}) से स्वचालित रूप से नहीं की गई।",
            "medicine": "दवा का पाठ मिला: {name}, {dose}{instructions}। निर्देशों की पुष्टि प्रिस्क्रिप्शन और स्वास्थ्य टीम से करें।",
            "diagnosis": "दस्तावेज़ में निदान/इम्प्रेशन का पाठ: {value}",
            "date": "दस्तावेज़ में मिली तारीख़ें: {value}",
            "disclaimer": "यह पाठ से निकाला गया सार है, निदान नहीं। संदर्भ सीमाएँ लैब और व्यक्ति के अनुसार बदलती हैं। परिणामों की व्याख्या योग्य चिकित्सक से कराएँ।",
        },
        "Telugu": {
            "title": "రికార్డు సారాంశం",
            "empty": "నిర్మిత ల్యాబ్ విలువలు, మందులు లేదా తేదీలు గుర్తించబడలేదు. అసలు నివేదికను పరిశీలించండి.",
            "abnormal": "నివేదికలో {name}: {value} {unit} (నివేదిక పరిధి {low}–{high})గా ఉంది; ఇది నివేదికలో ఇచ్చిన పరిధికి వెలుపల ఉంది.",
            "normal": "{name}: {value} {unit} (నివేదికలో ఇచ్చిన పరిధి {low}–{high}లో ఉంది).",
            "qualified": "{name}: {value} {unit}. నివేదికలో పరిమితి సూచించే విలువ ఉంది; అందువల్ల పేర్కొన్న పరిధి ({low}–{high})తో స్వయంచాలకంగా పోల్చలేదు.",
            "medicine": "మందు వివరాలు గుర్తించబడ్డాయి: {name}, {dose}{instructions}. ప్రిస్క్రిప్షన్ మరియు వైద్య బృందంతో సూచనలను నిర్ధారించండి.",
            "diagnosis": "పత్రంలోని నిర్ధారణ/ఇంప్రెషన్ వచనం: {value}",
            "date": "పత్రంలో గుర్తించిన తేదీలు: {value}",
            "disclaimer": "ఇది పాఠ్య సంగ్రహణ మాత్రమే, నిర్ధారణ కాదు. ఫలితాలను అర్హత కలిగిన వైద్య నిపుణులతో చర్చించండి.",
        },
    }[language]
    lines = [f"### {phrases['title']}"]

    for item in health_data["observations"]:
        key = (
            "abnormal"
            if item["status"] in ("High", "Low")
            else "qualified"
            if item["status"] == "Not compared (qualified result)"
            else "normal"
        )
        lines.append(
            "- "
            + phrases[key].format(
                name=item["name"],
                value=item["value"],
                unit=item["unit"],
                low=item["reference_low"],
                high=item["reference_high"],
            )
        )
    for item in health_data["medications"]:
        suffix = f" {item['instructions']}" if item["instructions"] else ""
        lines.append(
            "- "
            + phrases["medicine"].format(
                name=item["name"], dose=item["dose"], instructions=suffix
            )
        )
    for diagnosis in health_data["diagnoses"]:
        lines.append("- " + phrases["diagnosis"].format(value=diagnosis))
    if health_data["dates"]:
        lines.append("- " + phrases["date"].format(value=", ".join(health_data["dates"])))
    if not any(health_data[key] for key in ("observations", "medications", "diagnoses", "dates")):
        lines.append(phrases["empty"])

    return "\n\n".join(lines), phrases["disclaimer"]


def make_fhir_bundle(patient_name, demo_id, records):
    """Create a lightweight FHIR-style demo bundle, not a validated FHIR export."""
    resources = [
        {
            "resourceType": "Patient",
            "id": "demo-patient",
            "identifier": [{"system": "urn:demo:abha", "value": demo_id}],
            "name": [{"text": patient_name}],
            "extension": [{"url": "urn:demo:mock-abha", "valueBoolean": True}],
        }
    ]
    for index, record in enumerate(records, start=1):
        resources.append(
            {
                "resourceType": "DocumentReference",
                "id": f"document-{index}",
                "status": "current",
                "subject": {"reference": "Patient/demo-patient"},
                "description": record["name"],
                "date": record["created_at"],
                "content": [
                    {
                        "attachment": {
                            "contentType": record["content_type"],
                            "title": record["name"],
                        }
                    }
                ],
            }
        )
        for observation_index, observation in enumerate(
            record["health_data"]["observations"], start=1
        ):
            value = observation["value"]
            if value.startswith(("<", ">")):
                result_value = {"valueString": f"{value} {observation['unit']}".strip()}
            else:
                result_value = {
                    "valueQuantity": {
                        "value": float(value),
                        "unit": observation["unit"],
                    }
                }
            resources.append(
                {
                    "resourceType": "Observation",
                    "id": f"observation-{index}-{observation_index}",
                    "status": "preliminary",
                    "subject": {"reference": "Patient/demo-patient"},
                    "code": {"text": observation["name"]},
                    **result_value,
                    "note": [
                        {
                            "text": (
                                f"Document-stated reference: {observation['reference_low']}"
                                f"–{observation['reference_high']} "
                                f"{observation['reference_unit']}".strip()
                            )
                        }
                    ],
                }
            )
    return {
        "resourceType": "Bundle",
        "type": "collection",
        "meta": {"tag": [{"code": "demo", "display": "Not for clinical use"}]},
        "entry": [{"resource": item} for item in resources],
    }


def add_record(name, content_type, text):
    health_data = extract_health_data(text)
    st.session_state.records.insert(
        0,
        {
            "name": name,
            "content_type": content_type,
            "text": text,
            "health_data": health_data,
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "record_date": health_data["dates"][0] if health_data["dates"] else "Date not found",
        },
    )


if st.session_state.pop("navigate_to_add", False):
    st.session_state.page_navigation = "Add a record"

st.markdown(
    """
    <header class="site-header">
      <div class="brand">
        <div class="brand-mark">✳</div>
        <div>
          <div class="brand-name">aarogya</div>
          <div class="brand-sub">PERSONAL HEALTH COPILOT</div>
        </div>
      </div>
      <div class="privacy-badge">Session-only prototype</div>
    </header>
    """,
    unsafe_allow_html=True,
)
page = st.radio(
    "Workspace",
    ["Overview", "Add a record", "Health summary", "Timeline", "FHIR / ABHA demo", "How it works"],
    label_visibility="collapsed",
    horizontal=True,
    key="page_navigation",
)

if page == "Overview":
    st.markdown(
        """
        <div class="hero">
          <div>
            <div class="eyebrow">A calmer view of your care</div>
            <h1>Your health, all in one place.</h1>
            <p>Bring your reports together, understand what they contain, and keep your care journey organized — one record at a time.</p>
            <div class="hero-action-note">Your records stay in this browser session. You stay in control.</div>
          </div>
          <div class="hero-aside">
            <div class="hero-aside-title">A clearer picture, step by step</div>
            <div class="hero-step"><span class="hero-step-icon">↥</span><span>Add a report or prescription</span></div>
            <div class="hero-step"><span class="hero-step-icon">⌕</span><span>Review extracted details</span></div>
            <div class="hero-step"><span class="hero-step-icon">◎</span><span>Explore your health timeline</span></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    records = st.session_state.records
    observation_count = sum(len(item["health_data"]["observations"]) for item in records)
    medication_count = sum(len(item["health_data"]["medications"]) for item in records)
    st.markdown(
        """
        <div class="overview-heading">
          <div><div class="section-label">Your health library</div><h2>A little more organized, every day.</h2></div>
          <p>Everything here is linked to the record it came from.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    columns = st.columns(3)
    for column, icon, label, value in zip(
        columns,
        ["▤", "⌁", "＋"],
        ["Records collected", "Lab values found", "Medicine mentions"],
        [len(records), observation_count, medication_count],
    ):
        column.markdown(
            f'<div class="soft-card"><small>{icon} &nbsp; {label}</small><strong>{value}</strong></div>',
            unsafe_allow_html=True,
        )
    st.write("")
    left, right = st.columns([1.15, 1], gap="large")
    with left:
        st.markdown(
            """
            <div class="overview-panel">
              <span class="overview-tag">✦ &nbsp; GET STARTED</span>
              <h3>Start with a report</h3>
              <p>Upload a PDF or image, or paste text from a prescription, lab result, or discharge summary.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Add your first record" if not records else "Add another record", type="primary"):
            st.session_state.navigate_to_add = True
            st.rerun()
    with right:
        st.markdown(
            """
            <div class="overview-panel">
              <span class="overview-tag">✓ &nbsp; SOURCE-LINKED</span>
              <h3>Keep the context</h3>
              <p>Extracted details stay connected to their source. Lab values are compared only with ranges printed on that report.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown(
        """
        <div class="workflow-grid">
          <div class="workflow-card"><div class="workflow-card-icon">▧</div><strong>Bring it together</strong><span>PDF, image, or pasted text from your health documents.</span></div>
          <div class="workflow-card"><div class="workflow-card-icon">⌕</div><strong>Understand the details</strong><span>Review detected dates, medicine mentions, and reported lab ranges.</span></div>
          <div class="workflow-card"><div class="workflow-card-icon">◷</div><strong>See the bigger picture</strong><span>Browse a simple timeline and export a mock FHIR-style bundle.</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if records:
        st.write("")
        st.markdown('<div class="section-label">Your records</div>', unsafe_allow_html=True)
        st.subheader("Recently added")
        for record in records[:3]:
            with st.container(border=True):
                entry, count = st.columns([3, 1])
                entry.markdown(f"**{record['name']}**")
                entry.caption(f"{record['record_date']} · Added {record['created_at']}")
                count.metric("Findings", len(record["health_data"]["observations"]) + len(record["health_data"]["medications"]))
    else:
        st.markdown(
            """
            <div class="empty-state">
              <div class="empty-icon">🗂️</div>
              <div class="empty-title">Your health library starts here</div>
              <div class="empty-copy">Add a report to see its extracted details and build a timeline for this session.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.write("")
    st.markdown(
        '<div class="privacy-note"><span>ⓘ</span><span>Informational use only — this prototype does not diagnose or replace professional care. Review extracted text against the original and discuss health decisions with a qualified clinician.</span></div>',
        unsafe_allow_html=True,
    )

elif page == "Add a record":
    st.title("Add a health record")
    st.write("Bring a report into your session. Review extracted text carefully before using it.")
    st.info("Files and pasted text are held in this active app session only; they are not added to a persistent health record.")
    upload_tab, paste_tab = st.tabs(["Upload a file", "Paste report text"])

    with upload_tab:
        uploaded_file = st.file_uploader(
            "Choose a PDF, PNG, or JPEG",
            type=["pdf", "png", "jpg", "jpeg"],
            help="Text PDFs are extracted directly. Scanned PDFs and images use local Tesseract OCR.",
        )
        if uploaded_file:
            st.caption(f"Selected: {uploaded_file.name} · {uploaded_file.size:,} bytes")
            if st.button("Extract and add record", type="primary"):
                try:
                    extracted_text = extract_document_text(uploaded_file)
                except Exception as exc:
                    st.error(f"Could not extract this file: {exc}")
                else:
                    add_record(uploaded_file.name, uploaded_file.type or "application/octet-stream", extracted_text)
                    st.success("Record added to this session.")
                    st.text_area("Extracted text — review OCR before relying on it", extracted_text, height=220)
                    st.caption("OCR can misread names, values, units, and handwriting. Verify every detail against the original.")

    with paste_tab:
        pasted_text = st.text_area(
            "Paste text from a report",
            height=220,
            placeholder="Example:\nReport date: 2025-05-14\nHemoglobin: 13.2 g/dL (12-16)\nMedicine: Metformin 500 mg twice daily",
        )
        record_name = st.text_input("Record name", "Pasted health record")
        if st.button("Add pasted record", type="primary"):
            if not pasted_text.strip():
                st.error("Paste some report text first.")
            else:
                add_record(record_name.strip() or "Pasted health record", "text/plain", pasted_text.strip())
                st.success("Record added to this session.")

elif page == "Health summary":
    st.title("Health summary")
    st.caption("A plain-language recap of text found in your records — not a medical interpretation.")
    if not st.session_state.records:
        st.info("Add a report first to see its extracted details.")
    else:
        labels = [
            f"{record['name']} · {record['record_date']}"
            for record in st.session_state.records
        ]
        selector, language_selector = st.columns([2, 1])
        selection = selector.selectbox("Choose a source record", range(len(labels)), format_func=lambda item: labels[item])
        language = language_selector.selectbox("Summary language", ["English", "Hindi", "Telugu"])
        record = st.session_state.records[selection]
        summary, disclaimer = create_summary(record["health_data"], language)
        with st.container(border=True):
            st.markdown('<div class="section-label">Based on the selected source</div>', unsafe_allow_html=True)
            st.markdown(summary)
        st.warning(disclaimer)
        observations = record["health_data"]["observations"]
        if observations:
            st.subheader("Values extracted from this report")
            st.dataframe(observations, use_container_width=True, hide_index=True)
        if record["health_data"]["medications"]:
            st.subheader("Medicine mentions")
            st.dataframe(record["health_data"]["medications"], use_container_width=True, hide_index=True)
        with st.expander("View source text"):
            st.text(record["text"])

elif page == "Timeline":
    st.title("Health timeline")
    st.caption("A session-level index of your records. Dates and details come from the source text.")
    if not st.session_state.records:
        st.info("Your timeline is empty. Add a record to get started.")
    else:
        for record in st.session_state.records:
            with st.container(border=True):
                top, detail = st.columns([1, 4])
                top.markdown(f'<div class="timeline-date">{record["record_date"]}</div>', unsafe_allow_html=True)
                detail.markdown(f"### {record['name']}")
                detail.caption(
                    f"{len(record['health_data']['observations'])} lab values · "
                    f"{len(record['health_data']['medications'])} medicine mentions · "
                    f"Added {record['created_at']}"
                )
                if record["health_data"]["observations"]:
                    for observation in record["health_data"]["observations"]:
                        status_label = observation["status"]
                        detail.write(
                            f"• {observation['name']}: {observation['value']} "
                            f"{observation['unit']} — {status_label} vs. stated range"
                        )
                else:
                    detail.caption("No lab values with stated reference ranges were found.")

elif page == "FHIR / ABHA demo":
    st.title("FHIR-style export")
    st.caption("Mock interoperability preview. No ABHA account is connected and no real identifier is verified.")
    patient_name = st.text_input("Demo patient name", "Demo Patient")
    demo_id = st.text_input("Mock ABHA/demo ID", "DEMO-ABHA-0001")
    st.info("Use a dummy identifier only. This export is a lightweight FHIR-style demonstration, not a validated clinical FHIR resource.")
    bundle = make_fhir_bundle(patient_name, demo_id, st.session_state.records)
    st.json(bundle, expanded=False)
    st.download_button(
        "Download FHIR-style JSON",
        data=json.dumps(bundle, indent=2, ensure_ascii=False),
        file_name="health-records-demo.json",
        mime="application/json",
    )

else:
    st.title("How it works")
    st.caption("A privacy-conscious prototype pipeline")
    st.markdown(
        """
        ```
        PDF / image / pasted text
                  │
          PDF text extraction ── scanned PDF or image → local Tesseract OCR
                  │
          Rule-based field extraction (dates, medicines, lab values + stated ranges)
                  │
          Plain-language, multilingual recap (English · Hindi · Telugu)
                  │
          Session-only timeline ──→ FHIR-style JSON demo export
        ```
        """
    )
    st.markdown("#### What this prototype does")
    st.write(
        "Extracts searchable PDF text with pypdf, and uses local Tesseract OCR for images "
        "and scanned PDFs. A transparent set of patterns identifies likely dates, medicine "
        "mentions, diagnosis/impression labels, and lab values only when the report itself "
        "includes a reference interval. No generative AI service is connected."
    )
    st.markdown("#### What it does not do")
    st.write(
        "It is not a medical device, does not diagnose, does not infer a normal range, "
        "does not recommend treatment, and does not connect to ABDM. Data exists only "
        "in the active Streamlit session and may be lost when the session ends."
    )
    st.markdown("#### Data model")
    st.write(
        "The demo export contains a Patient, DocumentReference entries, and Observation "
        "entries for extracted lab values. It uses a dummy ABHA identifier and is not "
        "a validated ABDM/FHIR implementation."
    )
    st.markdown("#### OCR and language limitations")
    st.write(
        "OCR quality depends on image quality and the local Tesseract language packs. "
        "Hindi and Telugu support applies to fixed summary wording only; OCR currently "
        "uses the installed Tesseract default language and is not optimized for handwriting."
    )

st.markdown(
    """
    <footer class="site-footer">
      <span>✳ &nbsp; Aarogya · Your health information, made easier to navigate.</span>
      <span>Session-only prototype &nbsp;·&nbsp; Not medical advice</span>
    </footer>
    """,
    unsafe_allow_html=True,
)
