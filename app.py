"""
Commission Design Promo 2K20 — Application multi-agents (v13 - Final Stable + Vert/Jaune)
Agents : LK (DA, bleu) · Junior (Planning, vert)
Utilisateurs : Designer (violet) · Candidat (bleu clair)
Charte graphique Studio LK v2.2
"""
import streamlit as st
import pandas as pd
import os, json, uuid, base64, zipfile, io, re
from datetime import datetime
from groq import Groq
from pathlib import Path

# ══════════════════════════════════════════
# CHEMINS & CONFIG
# ══════════════════════════════════════════
BASE_DIR   = Path(__file__).parent
DATA_DIR   = BASE_DIR / "data"
PHOTOS_DIR = DATA_DIR / "photos"
BRIEFS_DIR = DATA_DIR / "briefs"
DOCS_DIR   = DATA_DIR / "documents_designers"
IDEAS_FILE = DATA_DIR / "idees_designers.json"
CHARTE_FILE= DATA_DIR / "charte.md"
SUIVI_FILE = DATA_DIR / "suivi_livrables.json"
LIVRABLES_LIST = [
    "charte_graphique", "backdrop", "affiche_bienvenue",
    "fond_salle", "cadre_photo", "template_candidat", "motion_affiches"
]

def get_secret_value(name, default=None):
    try:    return st.secrets.get(name, os.environ.get(name, default))
    except: return os.environ.get(name, default)

st.set_page_config(
    page_title="Commission Design — Promo 2K20",
    page_icon="🎓", layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════
# AVATARS
# ══════════════════════════════════════════
def _b64svg(svg: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

def avatar_lk():
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">'
        '<rect x="2" y="2" width="36" height="36" rx="8" fill="#0c4a6e" stroke="#0ea5e9" stroke-width="2"/>'
        '<line x1="10" y1="30" x2="30" y2="30" stroke="#38bdf8" stroke-width="2" stroke-linecap="round"/>'
        '<text x="20" y="21" text-anchor="middle" dominant-baseline="middle" '
        'font-family="Georgia,serif" font-size="14" font-weight="800" fill="#38bdf8">LK</text>'
        '</svg>'
    )
    return _b64svg(svg)

def avatar_junior():
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">'
        '<rect x="2" y="2" width="36" height="36" rx="8" fill="#065f46" stroke="#6ee7b7" stroke-width="2"/>'
        '<line x1="10" y1="30" x2="30" y2="30" stroke="#6ee7b7" stroke-width="2" stroke-linecap="round"/>'
        '<text x="20" y="21" text-anchor="middle" dominant-baseline="middle" '
        'font-family="Georgia,serif" font-size="14" font-weight="800" fill="#6ee7b7">Jr</text>'
        '</svg>'
    )
    return _b64svg(svg)

def avatar_designer():
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">'
        '<rect x="2" y="2" width="36" height="36" rx="8" fill="#7c3aed" stroke="#a78bfa" stroke-width="2"/>'
        '<line x1="10" y1="30" x2="30" y2="30" stroke="#a78bfa" stroke-width="2" stroke-linecap="round"/>'
        '<text x="20" y="21" text-anchor="middle" dominant-baseline="middle" '
        'font-family="Georgia,serif" font-size="14" font-weight="800" fill="#c4b5fd">DS</text>'
        '</svg>'
    )
    return _b64svg(svg)

def avatar_candidat():
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">'
        '<rect x="2" y="2" width="36" height="36" rx="8" fill="#0284c7" stroke="#7dd3fc" stroke-width="2"/>'
        '<line x1="10" y1="30" x2="30" y2="30" stroke="#7dd3fc" stroke-width="2" stroke-linecap="round"/>'
        '<text x="20" y="21" text-anchor="middle" dominant-baseline="middle" '
        'font-family="Georgia,serif" font-size="14" font-weight="800" fill="#bae6fd">C</text>'
        '</svg>'
    )
    return _b64svg(svg)

AVT_LK   = avatar_lk()
AVT_JR   = avatar_junior()
AVT_DSGN = avatar_designer()
AVT_CAND = avatar_candidat()

# ══════════════════════════════════════════
# ANIMATION CSS PARTICULES (100% fiable) - AVEC VERT & JAUNE
# ══════════════════════════════════════════
def inject_particles_animation():
    st.markdown("""
    <style>
    /* Conteneur principal - commence après la sidebar sur desktop */
    #particles-container {
        position: fixed; top: 0; left: 0;
        width: 100%; height: 100%;
        z-index: -1; pointer-events: none; overflow: hidden;
    }
    @media (min-width: 992px) {
        #particles-container { left: 300px; width: calc(100% - 300px); }
    }
    .particle {
        position: absolute;
        background: radial-gradient(circle, rgba(124,58,237,0.8), rgba(14,165,233,0.4));
        border-radius: 50%; pointer-events: none;
        animation: floatParticle linear infinite;
    }
    /* Tailles et positions (extraites de ton fichier) */
    .particle:nth-child(1) { width: 4px; height: 4px; top: 15%; left: 10%; animation-duration: 28s; animation-delay: 0s; }
    .particle:nth-child(2) { width: 2px; height: 2px; top: 35%; left: 25%; animation-duration: 62s; animation-delay: 4s; }
    .particle:nth-child(3) { width: 5px; height: 5px; top: 55%; left: 45%; animation-duration: 44s; animation-delay: 2s; }
    .particle:nth-child(4) { width: 3px; height: 3px; top: 75%; left: 70%; animation-duration: 50s; animation-delay: s; }
    .particle:nth-child(5) { width: 6px; height: 6px; top: 85%; left: 90%; animation-duration: 36s; animation-delay: 1.5s; }
    .particle:nth-child(6) { width: 2px; height: 2px; top: 25%; left: 80%; animation-duration: 74s; animation-delay: 3s; }
    .particle:nth-child(7) { width: 4px; height: 4px; top: 45%; left: 15%; animation-duration: 62s; animation-delay: 2.8s; }
    .particle:nth-child(8) { width: 3px; height: 3px; top: 65%; left: 35%; animation-duration: 59s; animation-delay: 2.2s; }
    .particle:nth-child(9) { width: 5px; height: 5px; top: 10%; left: 55%; animation-duration: 41s; animation-delay: 4s; }
    .particle:nth-child(10) { width: 2px; height: 2px; top: 30%; left: 95%; animation-duration: 57s; animation-delay: 1.2s; }
    .particle:nth-child(11) { width: 4px; height: 4px; top: 50%; left: 5%; animation-duration: 43s; animation-delay: 2.5s; }
    .particle:nth-child(12) { width: 3px; height: 3px; top: 70%; left: 85%; animation-duration: 65s; animation-delay: 5.3s; }
    .particle:nth-child(13) { width: 6px; height: 6px; top: 90%; left: 20%; animation-duration: 65s; animation-delay: 3.5s; }
    .particle:nth-child(14) { width: 2px; height: 2px; top: 5%; left: 40%; animation-duration: 33s; animation-delay: 3.8s; }
    .particle:nth-child(15) { width: 4px; height: 4px; top: 40%; left: 60%; animation-duration: 38s; animation-delay: 4.2s; }
    .particle:nth-child(16) { width: 3px; height: 3px; top: 60%; left: 75%; animation-duration: 50s; animation-delay: 0.7s; }
    .particle:nth-child(17) { width: 5px; height: 5px; top: 80%; left: 50%; animation-duration: 42s; animation-delay: 2.8s; }
    .particle:nth-child(18) { width: 2px; height: 2px; top: 20%; left: 65%; animation-duration: 66s; animation-delay: 5.1s; }
    .particle:nth-child(19) { width: 4px; height: 4px; top: 95%; left: 8%; animation-duration: 59s; animation-delay: 3.2s; }
    .particle:nth-child(20) { width: 3px; height: 3px; top: 8%; left: 30%; animation-duration: 14s; animation-delay: 4.5s; }
    .particle:nth-child(21) { width: 5px; height: 5px; top: 38%; left: 98%; animation-duration: 44s; animation-delay: 8.4s; }
    .particle:nth-child(22) { width: 2px; height: 2px; top: 58%; left: 12%; animation-duration: 31s; animation-delay: 2.1s; }
    .particle:nth-child(23) { width: 4px; height: 4px; top: 78%; left: 42%; animation-duration: 41s; animation-delay: 3.8s; }
    .particle:nth-child(24) { width: 3px; height: 3px; top: 12%; left: 88%; animation-duration: 67s; animation-delay: 1.4s; }
    .particle:nth-child(25) { width: 6px; height: 6px; top: 32%; left: 22%; animation-duration: 23s; animation-delay: 2.9s; }
    .particle:nth-child(26) { width: 2px; height: 2px; top: 52%; left: 78%; animation-duration: 55s; animation-delay: 0.6s; }
    .particle:nth-child(27) { width: 4px; height: 4px; top: 72%; left: 32%; animation-duration: 68s; animation-delay: 3.1s; }
    .particle:nth-child(28) { width: 3px; height: 3px; top: 92%; left: 55%; animation-duration: 40s; animation-delay: 4.9s; }
    .particle:nth-child(29) { width: 5px; height: 5px; top: 18%; left: 48%; animation-duration: 32s; animation-delay: 4.3s; }
    .particle:nth-child(30) { width: 2px; height: 2px; top: 48%; left: 92%; animation-duration: 22s; animation-delay: 2.9s; }
    .particle:nth-child(31) { width: 4px; height: 4px; top: 68%; left: 8%; animation-duration: 16s; animation-delay: 2.4s; }
    .particle:nth-child(32) { width: 3px; height: 3px; top: 88%; left: 68%; animation-duration: 59s; animation-delay: 3.6s; }
    .particle:nth-child(33) { width: 6px; height: 6px; top: 28%; left: 52%; animation-duration: 64s; animation-delay: 3.7s; }
    .particle:nth-child(34) { width: 2px; height: 2px; top: 42%; left: 3%; animation-duration: 25s; animation-delay: 2.3s; }
    .particle:nth-child(35) { width: 4px; height: 4px; top: 62%; left: 62%; animation-duration: 43s; animation-delay: 4.1s; }
    .particle:nth-child(36) { width: 3px; height: 3px; top: 82%; left: 82%; animation-duration: 51s; animation-delay: 3.2s; }
    .particle:nth-child(37) { width: 5px; height: 5px; top: 22%; left: 18%; animation-duration: 17s; animation-delay: 5.4s; }
    .particle:nth-child(38) { width: 2px; height: 2px; top: 56%; left: 38%; animation-duration: 23s; animation-delay: 1.5s; }
    .particle:nth-child(39) { width: 4px; height: 4px; top: 76%; left: 58%; animation-duration: 55s; animation-delay: 6.7s; }
    .particle:nth-child(40) { width: 3px; height: 3px; top: 96%; left: 14%; animation-duration: 18s; animation-delay: 4.9s; }
    .particle:nth-child(41) { width: 5px; height: 5px; top: 6%; left: 75%; animation-duration: 20s; animation-delay: 8.1s; }
    .particle:nth-child(42) { width: 2px; height: 2px; top: 36%; left: 42%; animation-duration: 81s; animation-delay: 2.6s; }
    .particle:nth-child(43) { width: 4px; height: 4px; top: 66%; left: 28%; animation-duration: 24s; animation-delay: 3.3s; }
    .particle:nth-child(44) { width: 3px; height: 3px; top: 86%; left: 48%; animation-duration: 46s; animation-delay: 3.0s; }
    .particle:nth-child(45) { width: 6px; height: 6px; top: 14%; left: 98%; animation-duration: 59s; animation-delay: 4.7s; }
    .particle:nth-child(46) { width: 2px; height: 2px; top: 44%; left: 72%; animation-duration: 52s; animation-delay: 7.8s; }
    .particle:nth-child(47) { width: 4px; height: 4px; top: 64%; left: 18%; animation-duration: 34s; animation-delay: 5.0s; }
    .particle:nth-child(48) { width: 3px; height: 3px; top: 84%; left: 38%; animation-duration: 25s; animation-delay: 3.3s; }
    .particle:nth-child(49) { width: 5px; height: 5px; top: 26%; left: 82%; animation-duration: 32s; animation-delay: 7s; }
    .particle:nth-child(50) { width: 2px; height: 2px; top: 46%; left: 58%; animation-duration: 18s; animation-delay: 4.6s; }

    @keyframes floatParticle {
        0% { transform: translateY(0px) translateX(0px); opacity: 0; }
        10% { opacity: 0.7; }
        90% { opacity: 0.3; }
        100% { transform: translateY(-500px) translateX(calc(80px * (sin(var(--angle, 1))))); opacity: 0; }
    }
    .aurora-glow {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        z-index: -1; background: radial-gradient(ellipse at 50% 50%, rgba(124,58,237,0.08), rgba(14,165,233,0.04), transparent);
        animation: auroraShift 12s ease-in-out infinite; pointer-events: none;
    }
    @keyframes auroraShift { 0% { opacity: 0.5; transform: scale(1); } 50% { opacity: 0.8; transform: scale(1.05); } 100% { opacity: 0.5; transform: scale(1); } }
    </style>
    <div id="particles-container">
        <div class="aurora-glow"></div>
        <div class="cursor-glow" id="cursorGlow"></div>
        <div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div>
        <div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div>
        <div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div>
        <div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div>
        <div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div>
    </div>
    <script>
    const glow = document.getElementById('cursorGlow');
    if (glow) {
        document.addEventListener('mousemove', (e) => { glow.style.left = e.clientX + 'px'; glow.style.top = e.clientY + 'px'; });
        document.addEventListener('touchmove', (e) => { if(e.touches.length) { glow.style.left = e.touches[0].clientX + 'px'; glow.style.top = e.touches[0].clientY + 'px'; } });
    }
    </script>
    """, unsafe_allow_html=True)
    
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:opsz,wght@14..32,300;400;500;600;700&display=swap');
    html,body,[class*="css"]{font-family:'Inter','Helvetica Neue',Helvetica,Arial,sans-serif;background-color:#07070E;}
    .stApp{background-color:transparent;}
                
                /* ── SIDEBAR : SUPPRESSION DU FOND TROP SOMBRE ── */
[data-testid="stSidebar"] {
    background-color: transparent !important;
    backdrop-filter: none !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
}
[data-testid="stSidebar"] > div:first-child {
    background: transparent !important;
}
/* Expander "Comment utiliser" sans fond noir */
details[open] > summary, details > summary {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}
.streamlit-expanderContent {
    background: transparent !important;
    border: none !important;
}

    /* CORRECTION MOBILE & SIDEBAR : Ne masque pas le header pour préserver le bouton hamburger */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* SIDEBAR */
    [data-testid="stSidebar"]{background-color:#0E0E1D!important;border-right:1px solid rgba(255,255,255,0.06); z-index: 20;}
    [data-testid="stSidebar"]>div:first-child{display:flex!important;flex-direction:column!important;min-height:100vh;padding-bottom:0!important;}
    [data-testid="stSidebar"] *{color:#E2E8F0!important;}
    div[data-testid="stRadio"]>div{background-color:#161628!important;border-radius:.75rem!important;padding:.5rem .75rem!important;border:1px solid rgba(255,255,255,0.06);margin-top:2px;}

    .sb-brand-title{font-family:'Syne',sans-serif;font-size:1.65rem;font-weight:800;letter-spacing:-.03em;line-height:1.1;background:linear-gradient(135deg,#fff 0%,#a78bfa 80%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:2px;}
    .sb-brand-sub{font-size:.68rem;color:#6B6B96!important;font-weight:300;letter-spacing:.12em;text-transform:uppercase;}
    .sb-label{font-size:.55rem;letter-spacing:.2em;text-transform:uppercase;color:#6B6B96!important;font-weight:500;margin:14px 0 5px 0;padding-bottom:3px;border-bottom:1px solid rgba(255,255,255,.05);}
    .sb-livrable{display:flex;align-items:center;gap:7px;padding:2px 0;font-size:.71rem;color:#A0A0C8!important;line-height:1.9;}
    .sb-chk{width:13px;height:13px;border-radius:3px;flex-shrink:0;display:inline-flex;align-items:center;justify-content:center;font-size:.55rem;}
    .sb-chk.done{background:rgba(16,185,129,.18);border:1px solid #10b981;color:#6ee7b7!important;}
    .sb-chk.partial{background:rgba(253,211,77,.12);border:1px solid #fcd34d;color:#fcd34d!important;}
    .sb-chk.todo{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.12);color:transparent!important;}
    .sb-liv-name{font-weight:400;color:#C4B5FD!important;}
    .sb-liv-status{font-size:.6rem;color:#475569!important;margin-left:auto;}
    .sb-spacer{flex:1 1 auto;}
    .sb-footer{padding:6px 0 10px 0;border-top:1px solid rgba(255,255,255,.05);margin-top:auto;}
    .sb-footer-name{font-family:'Syne',sans-serif;font-weight:800;font-size:.60rem;background:linear-gradient(135deg,#fff 0%,#a78bfa 80%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;display:block;margin-bottom:1px;}
    .sb-footer-roles{font-size:.55rem;color:#A0A0C8!important;font-weight:300;line-height:1.5;}

    /* HERO */
    .hero-title{font-family:'Syne',sans-serif;font-size:2.6rem;font-weight:800;letter-spacing:-.04em;background:linear-gradient(135deg,#fff 0%,#a78bfa 80%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;text-align:center;margin-bottom:.25rem;}
    .hero-sub{text-align:center;color:#6B6B96;margin-bottom:1.5rem;font-size:.85rem;font-weight:300;}

    /* INPUTS */
    .stTextInput>div>div>input,.stTextArea>div>div>textarea{background-color:#0E0E1D!important;color:#F0F0FA!important;border:1px solid rgba(255,255,255,.1)!important;border-radius:.75rem!important;}
    .stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{border-color:#7C3AED!important;box-shadow:0 0 0 2px rgba(124,58,237,.35)!important;outline:none!important;}
    div[data-testid="stChatInput"] textarea{background-color:#0E0E1D!important;color:#F0F0FA!important;border:1px solid rgba(255,255,255,.1)!important;border-radius:.75rem!important;}
    div[data-testid="stChatInput"] textarea:focus{border-color:#7C3AED!important;box-shadow:0 0 0 2px rgba(124,58,237,.35)!important;outline:none!important;}
    div[data-testid="stChatInputContainer"]{border:1px solid rgba(255,255,255,.08)!important;border-radius:.9rem!important;background:#0E0E1D!important;}
    div[data-testid="stChatInputContainer"]:focus-within{border-color:#7C3AED!important;box-shadow:0 0 0 2px rgba(124,58,237,.28)!important;}
    div[data-testid="stChatInput"] button{background:linear-gradient(135deg,#7C3AED, #A855F7)!important;border-radius:.5rem!important;border:none!important;}
    div[data-testid="stChatInput"] button:hover{background:linear-gradient(135deg,#A855F7,#EC4899)!important;}
    div[data-testid="stChatInput"] button svg{fill:white!important;}

    /* BOUTONS */
    .stButton>button{background:linear-gradient(135deg,#7C3AED,#A855F7)!important;color:white!important;font-weight:600;border:none;border-radius:.75rem!important;}
    .stButton>button:hover{background:linear-gradient(135deg,#A855F7, #EC4899)!important;box-shadow:0 4px 12px rgba(124,58,237,.3);}

    /* CARTES */
    .idea-card{background:#0E0E1D;border:1px solid rgba(167,139,250,.15);border-left:3px solid #7c3aed;border-radius:12px;padding:12px 16px;margin-bottom:10px;}
    .idea-card.validated{border-left-color:#10b981;}
    .idea-card.rejected{border-left-color:#ef4444;opacity:.55;}
    .idea-meta{font-size:.62rem;color:#6B6B96;margin-bottom:5px;}
    .idea-text{font-size:.8rem;color:#F0F0FA;line-height:1.6;}
    .idea-response{font-size:.76rem;color:#A78BFA;margin-top:6px;font-style:italic;}
    .candidat-card{background:#0E0E1D;border:1px solid rgba(167,139,250,.18);border-radius:14px;padding:12px 16px;margin-bottom:10px;}
    .candidat-name{font-family:'Syne',sans-serif;font-size:.92rem;font-weight:700;background:linear-gradient(135deg,#fff 0%,#a78bfa 80%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
    .candidat-meta{font-size:.7rem;color:#6B6B96;margin-top:3px;line-height:1.7;}
    .candidat-sujet{font-size:.76rem;color:#A78BFA;margin-top:5px;font-style:italic;}
    [data-testid="stFileUploader"]{background:#0E0E1D!important;border:1px dashed rgba(124,58,237,.35)!important;border-radius:12px!important;}
    [data-testid="stFileUploadDropzone"]{background:transparent!important;}
    .gen-block{background:#0a1628;border:1px solid rgba(14,165,233,.25);border-left:3px solid #0ea5e9;border-radius:12px;padding:14px 18px;margin:10px 0;font-size:.8rem;color:#e0f2fe;line-height:1.7;white-space:pre-wrap;}
    .gen-title{font-family:'Syne',sans-serif;font-size:.72rem;font-weight:700;color:#38bdf8;letter-spacing:.1em;text-transform:uppercase;margin-bottom:8px;}
    hr{border-color:rgba(255,255,255,.05);}

    /* AIDE DÉPLIABLE COMPACTE */
    details.help-details { background: rgba(10, 10, 22, 0.75); border: 1px solid rgba(124, 58, 237, 0.2); border-radius: 14px; padding: 14px 18px; margin: 10px 0 20px 0; backdrop-filter: blur(8px); font-size: 0.82rem; color: #cbd5e1; line-height: 1.5; }
    summary.help-summary { cursor: pointer; font-weight: 700; color: #a78bfa; font-size: 0.9rem; list-style: none; display: flex; align-items: center; justify-content: space-between; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 10px; }
    summary.help-summary::-webkit-details-marker { display: none; }
    summary.help-summary::after { content: "▼"; font-size: 0.7rem; transition: transform 0.2s; }
    details[open] summary.help-summary::after { transform: rotate(180deg); }
    .help-role-mini { display: flex; align-items: flex-start; gap: 8px; margin: 6px 0; padding: 6px 8px; background: rgba(255,255,255,0.03); border-radius: 8px; font-size: 0.75rem; }
    .help-role-mini span.icon { font-size: 1rem; flex-shrink: 0; }
    .help-role-mini strong { color: #e2e8f0; }
    .help-steps-mini { margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.06); }
    .help-step-mini { display: flex; align-items: center; gap: 8px; font-size: 0.75rem; color: #94a3b8; margin: 4px 0; }
    .help-step-mini .num { width: 16px; height: 16px; border-radius: 50%; background: linear-gradient(135deg, #7c3aed, #a855f7); color: white; font-size: 0.6rem; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }

    /* BOUTONS */
    .stButton>button{background:linear-gradient(135deg,#7C3AED,#A855F7)!important;color:white!important;font-weight:600;border:none;border-radius:.75rem!important;}
    .stButton>button:hover{background:linear-gradient(135deg,#A855F7,#EC4899)!important;box-shadow:0 4px 12px rgba(124,58,237,.3);}
    
    </style>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════
# TOUTES LES AUTRES FONCTIONS (inchangées du v13)
# ══════════════════════════════════════════
SUJETS_INTERDITS = [
    "crime","criminalité","meurtre","viol","sexuel","pornographie","drogue",
    "trafic","terrorisme","attentat","arme","violence","hacking","fraude",
    "escroquerie","pédophile","inceste","suicide","automutilation"
]
def contenu_interdit(texte: str) -> bool:
    return any(m in texte.lower() for m in SUJETS_INTERDITS)

def init_data_files():
    for d in [DATA_DIR, PHOTOS_DIR, BRIEFS_DIR, DOCS_DIR]: d.mkdir(exist_ok=True)
    if not (DATA_DIR/"candidats.csv").exists():
        pd.DataFrame(columns=["id","nom","prenom","telephone","matricule","sujet_memoire","jour","heure","photo_path","statut"]).to_csv(DATA_DIR/"candidats.csv", index=False)
    if not SUIVI_FILE.exists():
        with open(SUIVI_FILE,"w") as f: json.dump({k:"non commencé" for k in LIVRABLES_LIST}, f)
    if not CHARTE_FILE.exists():
        with open(CHARTE_FILE,"w") as f: f.write("# Charte Graphique\n\n*En attente*")
    if not (DATA_DIR/"planning.csv").exists():
        pd.DataFrame(columns=["nom","prenom","sujet","jour","heure"]).to_csv(DATA_DIR/"planning.csv", index=False)
    if not IDEAS_FILE.exists():
        with open(IDEAS_FILE,"w", encoding="utf-8") as f: json.dump([], f, ensure_ascii=False)

init_data_files()

def lire_suivi() -> dict:
    try:
        with open(SUIVI_FILE) as f: return json.load(f)
    except: return {k:"non commencé" for k in LIVRABLES_LIST}

def ecrire_suivi(suivi: dict):
    with open(SUIVI_FILE,"w") as f: json.dump(suivi, f, indent=2)

def mettre_a_jour_suivi() -> dict:
    suivi = lire_suivi()
    try:
        with open(CHARTE_FILE) as f: txt = f.read()
        suivi["charte_graphique"] = "fait" if len(txt) > 200 else ("en cours" if len(txt) > 30 else "non commencé")
    except: pass
    for liv in ["backdrop","affiche_bienvenue","fond_salle","cadre_photo","template_candidat"]:
        if (BRIEFS_DIR/f"{liv}.md").exists(): suivi[liv] = "brief généré"
        elif suivi.get(liv) not in ["fait","en cours"]: suivi[liv] = "non commencé"
    if (BRIEFS_DIR/"motion_prompt.md").exists(): suivi["motion_affiches"] = "brief généré"
    ecrire_suivi(suivi)
    return suivi

def valider_livrable(nom: str):
    suivi = lire_suivi(); suivi[nom] = "fait"; ecrire_suivi(suivi)

def demarrer_livrable(nom: str):
    suivi = lire_suivi()
    if suivi.get(nom,"non commencé") == "non commencé": suivi[nom] = "en cours"; ecrire_suivi(suivi)

def lire_idees() -> list:
    try:
        with open(IDEAS_FILE, encoding="utf-8") as f: return json.load(f)
    except: return []

def sauver_idee(msg: str, rep: str, fichier: str = "") -> str:
    idees = lire_idees()
    nid = str(uuid.uuid4())[:8]
    idees.append({"id":nid,"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M"),
                  "designer_msg":msg,"lk_response":rep,"fichier_joint":fichier,"statut":"soumis"})
    with open(IDEAS_FILE,"w",encoding="utf-8") as f: json.dump(idees, f, ensure_ascii=False, indent=2)
    return nid

def mettre_a_jour_statut_idee(idea_id: str, statut: str):
    idees = lire_idees()
    for i in idees:
        if i["id"] == idea_id: i["statut"] = statut; break
    with open(IDEAS_FILE,"w",encoding="utf-8") as f: json.dump(idees, f, ensure_ascii=False, indent=2)

def resumer_idees_pour_lead() -> str:
    idees = lire_idees()
    if not idees: return "Aucune idée soumise par les designers pour l'instant."
    lignes = []
    for i in idees: 
        emoji = {"soumis":"🟡","validé":"🟢","rejeté":"🔴"}.get(i["statut"],"⚪")
        fj = f" [Fichier: {i['fichier_joint']}]" if i.get("fichier_joint") else ""
        lignes.append(f"- [{i['timestamp']}] {emoji} ({i['statut'].upper()}) Designer: {i['designer_msg'][:150]}{fj}\n  → LK: {i['lk_response'][:150]}")
    return "\n".join(lignes)

def ajouter_candidat(nom, prenom, telephone, matricule, sujet, photo_bytes=None):
    df = pd.read_csv(DATA_DIR/"candidats.csv")
    nid = str(uuid.uuid4())[:8]
    photo_path = ""
    if photo_bytes:
        photo_path = str(PHOTOS_DIR/f"{nid}.jpg")
        with open(photo_path,"wb") as f: f.write(photo_bytes)
    df = pd.concat([df, pd.DataFrame([{"id":nid,"nom":nom,"prenom":prenom,"telephone":telephone,
                                       "matricule":matricule,"sujet_memoire":sujet,"jour":"","heure":
                                       "","photo_path":photo_path,"statut":"en attente"}])], ignore_index=True)
    df.to_csv(DATA_DIR/"candidats.csv", index=False)
    regenerer_planning()
    return nid

def regenerer_planning():
    df = pd.read_csv(DATA_DIR/"candidats.csv")
    p = DATA_DIR/"planning.csv"
    if df.empty:
        pd.DataFrame(columns=["nom","prenom","sujet","jour","heure"]).to_csv(p, index=False)
        return
    plan = df[["nom","prenom","sujet_memoire","jour","heure"]].copy()
    plan.columns = ["nom","prenom","sujet","jour","heure"]
    plan.to_csv(p, index=False)

def obtenir_planning(): return pd.read_csv(DATA_DIR/"planning.csv")
def candidat_existe(tel): return tel in pd.read_csv(DATA_DIR/"candidats.csv")["telephone"].values
def get_candidat_par_telephone(tel):
    df = pd.read_csv(DATA_DIR/"candidats.csv")
    res = df[df["telephone"]==tel]
    return res.iloc[0] if not res.empty else None

def generer_zip_candidats() -> bytes:
    df = pd.read_csv(DATA_DIR/"candidats.csv")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("candidats_promo2k20.csv", df.to_csv(index=False, encoding="utf-8"))
        for _, row in df.iterrows():
            folder = f"{row.get('prenom','?')} {row.get('nom','?')}/"
            lines = [f"Nom: {row.get('nom','')}", f"Prénom: {row.get('prenom','')}",
                     f"Tél: {row.get('telephone','')}", f"Mat: {row.get('matricule','')}",
                     f"Sujet: {row.get('sujet_memoire','')}", f"Statut: {row.get('statut','')}"]
            zf.writestr(folder+"fiche.txt", "\n".join(lines))
            photo = str(row.get("photo_path",""))
            if photo and Path(photo).exists():
                with open(photo,"rb") as img: zf.writestr(folder+f"portrait{Path(photo).suffix}", img.read())
    buf.seek(0); return buf.getvalue()

def call_groq(messages, model=None):
    api_key = get_secret_value("GROQ_API_KEY")
    if not api_key: return "⚠️ Clé API manquante. Vérifie `secrets.toml`."
    models_to_try = [model] + ["llama-3.1-8b-instant", "llama3-8b-8192"] if model else ["llama-3.1-8b-instant", "llama3-8b-8192"]
    for m in models_to_try:
        try:
            return Groq(api_key=api_key).chat.completions.create(model=m, messages=messages, temperature=0.7, timeout=60, max_tokens=1024).choices[0].message.content
        except Exception as e:
            if "model" in str(e).lower() or "not found" in str(e).lower(): continue
            return f"⚠️ Erreur API : {str(e)}"
    return "⚠️ Aucun modèle disponible."

def sauver_document_designer(f):
    nid = str(uuid.uuid4())[:8]
    path = DOCS_DIR / f"{nid}_{f.name}"
    with open(path,"wb") as fp: fp.write(f.getvalue())
    return str(path), f.name

def generer_charte_via_groq(desc): return call_groq([{"role":"system","content":"Tu es LK. Génère une charte graphique complète en markdown."},{"role":"user","content":desc}])
def generer_brief_via_groq(liv, det): return call_groq([{"role":"system","content":"Tu es LK. Génère un brief créatif précis."},{"role":"user","content":f"Livrable: {liv}\nContexte: {det}"}])
def generer_motion_via_groq(sup): return call_groq([{"role":"system","content":"Tu es LK. Génère un prompt motion détaillé."},{"role":"user","content":sup}])

def afficher_profils_candidats():
    df = pd.read_csv(DATA_DIR/"candidats.csv")
    if df.empty: st.info("Aucun candidat inscrit."); return
    st.caption(f"{len(df)} candidat(s)")
    for _, row in df.iterrows():
        c_img, c_info = st.columns([1,4])
        with c_img:
            ph = str(row.get("photo_path",""))
            if ph and Path(ph).exists(): st.image(ph, width=72)
            else: st.markdown('<div style="width:72px;height:72px;border-radius:10px;background:#161628;border:1px solid rgba(167,139,250,.22);display:flex;align-items:center;justify-content:center;">👤</div>', unsafe_allow_html=True)
        with c_info:
            st.markdown(f'<div class="candidat-card"><div class="candidat-name">{row["prenom"]} {row["nom"]}</div><div class="candidat-meta">📞 {row["telephone"]} · 🎓 {row["matricule"]}</div><div class="candidat-sujet">📝 {row["sujet_memoire"]}</div></div>', unsafe_allow_html=True)

def render_livrables_sidebar(suivi: dict):
    st.markdown('<div class="sb-label">Livrables</div>', unsafe_allow_html=True)
    labels = {"charte_graphique":"Charte","backdrop":"Backdrop","affiche_bienvenue":"Affiche","fond_salle":"Fond salle","cadre_photo":"Cadre","template_candidat":"Template","motion_affiches":"Motion"}
    for k, label in labels.items():
        v = suivi.get(k,"non commencé")
        if v == "fait": cls, ic, txt = "done", "✓", "fait"
        elif v in ("brief généré","en cours"): cls, ic, txt = "partial", "·", v
        else: cls, ic, txt = "todo", "", "à faire"
        st.markdown(f'<div class="sb-livrable"><span class="sb-chk {cls}">{ic}</span><span class="sb-liv-name">{label}</span><span class="sb-liv-status">{txt}</span></div>', unsafe_allow_html=True)

def page_directeur(lead_mode: bool, suivi: dict):
    st.markdown('<div class="hero-title">Design Promo 2K20</div><div class="hero-sub">Directeur Artistique — <strong>LK</strong> · Production visuelle & motion</div>', unsafe_allow_html=True)
    skey = "da_lead" if lead_mode else "da_team"
    resume = resumer_idees_pour_lead()
    
    if lead_mode:
        sys_content = (
            "IDENTITÉ & STATUT\n"
            "Tu es LK, Directeur Artistique de la Commission Design — Promo 2K20 de l'ENSTP de Yaoundé.\n"
            "Tu es un designer et motion designer, choisi pour orchestrer la cohérence visuelle et encadrer l'équipe créative. Tu es un responsable bénévole, pas une IA. Tu assumes un rôle de supervision technique et artistique au sein du comité étudiant.\n\n"
            "MISSION & PÉRIMÈTRE\n"
            "Ta mission est de structurer, enrichir et valider techniquement les propositions des designers. Tu garantis que les livrables (charte, affiches, backdrops, motion, templates) respectent les standards visuels, la charte graphique et les délais de production. Tu es le pont opérationnel entre l'équipe design et Junior Lecco (Le directeur créatif).\n\n"
            "RELATIONS HIÉRARCHIQUES & TONALITÉ\n"
            "Avec Junior Lecco (Lead / Direction Créative) :\n"
            "- Vouvoiement obligatoire. Ton respectueux, factuel, collaboratif.\n"
            "- Tu rends des comptes synthétiques : état d'avancement, idées soumises, points de blocage, recommandations.\n"
            "- Tu reconnais son autorité décisionnelle. Tu ne l'inondes pas de détails inutiles, tu priorises l'information actionnable.\n\n"
            "RÈGLES DE PRODUCTION & LIMITES\n"
            "- Focus 100% visuel & technique : Tu ne donnes aucun conseil académique (rédaction, contenu scientifique, méthodologie de mémoire). Si un designer te sollicite là-dessus, redirige vers la Commission Académique.\n"
            "- Traçabilité : Chaque échange créatif est consigné. Tu es la mémoire du projet.\n"
            "- Cadre étudiant bénévole : Tu rappelles si nécessaire que la commission est un collectif de production visuelle, indépendant de l'administration.\n"
            "- Sécurité & Éthique : Refus catégorique de tout contenu illicite, violent ou inapproprié. Recentrage immédiat sur la production des supports de soutenance.\n\n"
            f"═══ JOURNAL IDÉES ÉQUIPE (temps réel) ═══\n{resume}\n═══ FIN JOURNAL ═══\n\n"
            "Quand Junior Lecco interroge sur les idées des designers, cite les entrées du journal. Si vide, dis-le clairement."
        )
    else:
        sys_content = (
            "IDENTITÉ & STATUT\n"
            "Tu es LK, Directeur Artistique de la Commission Design — Promo 2K20 de l'ENSTP de Yaoundé.\n"
            "Tu es un designer et motion designer, choisi pour orchestrer la cohérence visuelle et encadrer l'équipe créative. Tu es un responsable bénévole, pas une IA. Tu assumes un rôle de supervision technique et artistique au sein du comité étudiant.\n\n"
            "MISSION & PÉRIMÈTRE\n"
            "Ta mission est de structurer, enrichir et valider techniquement les propositions des designers. Tu garantis que les livrables (charte, affiches, backdrops, motion, templates) respectent les standards visuels, la charte graphique et les délais de production. Tu es le pont opérationnel entre l'équipe design et Junior Lecco (Le directeur créatif).\n\n"
            "RELATIONS HIÉRARCHIQUES & TONALITÉ\n"
            "1. Avec les Designers (Équipe Créative) :\n"
            "- Tutoiement obligatoire. Posture de mentor bienveillant et exigeant.\n"
            "- Tu écoutes, tu reformules, tu proposes des ajustements techniques (palette, typo, composition, rythme motion).\n"
            "- Tu encourages la créativité mais tu recadres si une idée s'éloigne des objectifs visuels ou des délais.\n"
            "- Tu ne valides JAMAIS seul. Tu dis systématiquement : 'Je note et je transmets à Junior Lecco pour validation finale.'\n\n"
            "RÈGLES DE PRODUCTION & LIMITES\n"
            "- Focus 100% visuel & technique : Tu ne donnes aucun conseil académique (rédaction, contenu scientifique, méthodologie de mémoire). Si un designer te sollicite là-dessus, redirige vers la Commission Académique.\n"
            "- Traçabilité : Chaque échange créatif est consigné. Tu es la mémoire du projet.\n"
            "- Cadre étudiant bénévole : Tu rappelles si nécessaire que la commission est un collectif de production visuelle, indépendant de l'administration.\n"
            "- Sécurité & Éthique : Refus catégorique de tout contenu illicite, violent ou inapproprié. Recentrage immédiat sur la production des supports de soutenance.\n\n"
            "CONDUITE ATTENDUE\n"
            "- Face à une idée : Tu l'aides à la maturer ('Et si on partait sur un contraste plus fort pour la lisibilité ?'), tu la structures, puis tu l'enregistres pour Junior Lecco.\n"
            "- Tu es un responsable étudiant passionné, rigoureux, et tourné vers l'excellence visuelle de ta promotion."
        )

    if skey not in st.session_state: st.session_state[skey] = [{"role":"system","content":sys_content}]
    else: st.session_state[skey][0] = {"role":"system","content":sys_content}

    if lead_mode:
        idees = lire_idees()
        soumises = [i for i in idees if i["statut"]=="soumis"]
        validees = [i for i in idees if i["statut"]=="validé"]
        if soumises:
            with st.expander(f"📬 Idées en attente ({len(soumises)})", expanded=True):
                for idea in soumises:
                    c_card, c_btns = st.columns([4,1])
                    with c_card:
                        fj = f'<span style="font-size:.6rem;color:#0ea5e9;">📎 {idea["fichier_joint"]}</span>' if idea.get("fichier_joint") else ""
                        st.markdown(f'<div class="idea-card"><div class="idea-meta">🕐 {idea["timestamp"]} · {idea["id"]} {fj}</div><div class="idea-text"><strong>Designer :</strong> {idea["designer_msg"]}</div><div class="idea-response"><strong>LK :</strong> {idea["lk_response"]}</div></div>', unsafe_allow_html=True)
                    with c_btns:
                        st.write("")
                        if st.button("✅", key=f"val_{idea['id']}"): mettre_a_jour_statut_idee(idea["id"],"validé"); st.rerun()
                        if st.button("❌", key=f"rej_{idea['id']}"): mettre_a_jour_statut_idee(idea["id"],"rejeté"); st.rerun()
        if validees:
            with st.expander(f"✅ Idées validées ({len(validees)})", expanded=False):
                for idea in validees: st.markdown(f'<div class="idea-card validated"><div class="idea-meta">🕐 {idea["timestamp"]} · ✅ VALIDÉ</div><div class="idea-text">{idea["designer_msg"]}</div></div>', unsafe_allow_html=True)

        with st.expander("📐 Générer la charte graphique", expanded=False):
            if st.button("⚡ Générer la charte", key="btn_gen_charte", use_container_width=True):
                with st.spinner("LK génère…"): contenu = generer_charte_via_groq(st.session_state.get("desc_charte",""))
                if contenu: 
                    with open(CHARTE_FILE,"w") as f: f.write(contenu)
                    mettre_a_jour_suivi(); st.success("✅"); st.rerun()
        with st.expander("📝 Générer un brief", expanded=False):
            if st.button("⚡ Générer le brief", key="btn_gen_brief", use_container_width=True):
                with st.spinner("LK génère…"): contenu = generer_brief_via_groq(st.session_state.get("sel_livrable",""),"")
                if contenu:
                    with open(BRIEFS_DIR/f"{st.session_state.get('sel_livrable','brief')}.md","w") as f: f.write(contenu)
                    demarrer_livrable(st.session_state.get('sel_livrable','')); mettre_a_jour_suivi(); st.success("✅"); st.rerun()
        with st.expander("🎬 Générer un prompt motion", expanded=False):
            if st.button("⚡ Générer motion", key="btn_gen_motion", use_container_width=True):
                with st.spinner("LK génère…"): contenu = generer_motion_via_groq(st.session_state.get("support_motion",""))
                if contenu:
                    with open(BRIEFS_DIR/"motion_prompt.md","w") as f: f.write(contenu)
                    mettre_a_jour_suivi(); st.success("✅"); st.rerun()

    fichier_nom = ""
    if not lead_mode:
        uploaded = st.file_uploader("📎 Joindre un fichier (optionnel)", type=["jpg","jpeg","png","pdf","docx","txt","md","svg"], key="designer_upload")
        if uploaded:
            st.success(f"📎 **{uploaded.name}** prêt")
            _, fichier_nom = sauver_document_designer(uploaded)

    chat_container = st.container()
    with chat_container:
        for msg in st.session_state[skey]:
            if msg["role"] == "system": continue
            with st.chat_message(msg["role"], avatar=AVT_DSGN if msg["role"]=="user" else AVT_LK): st.markdown(msg["content"])

    if prompt := st.chat_input("Soumets ton idée à LK…" if not lead_mode else "Instruction à LK…", key=f"ci_{skey}"):
        if contenu_interdit(prompt): st.warning("Sujet hors cadre."); st.stop()
        content_user = prompt + (f"\n\n📎 *Fichier joint : {fichier_nom}*" if fichier_nom else "")
        st.session_state[skey].append({"role":"user","content":content_user})
        
        rep = call_groq(st.session_state[skey])
        st.session_state[skey].append({"role":"assistant","content":rep})
        if not lead_mode: sauver_idee(content_user, rep, fichier_nom)
        st.rerun()

    st.markdown("---")
    with st.expander("👥 Profils candidats"): afficher_profils_candidats()

def page_donnees():
    st.markdown('<div class="hero-title">Design Promo 2K20</div><div class="hero-sub">Responsable Inscriptions — <strong>Junior</strong> · Commission Design ESTP Yaoundé</div>', unsafe_allow_html=True)

    if "don_msgs" not in st.session_state:
        st.session_state.don_msgs = [{"role":"system","content":(
            "IDENTITÉ & STATUT\n"
            "Tu es Junior, chargé de l'enregistrement des candidats aux soutenances de la promotion 2020 des filières MARCH et MENG à l'ENSTP de Yaoundé. Tu es l'interlocuteur privilégié pour accompagner les étudiants dans la procédure d'inscription relative à la réalisation des affiches annonçant le passage des candidats.\n"
            "Tu es un visage humain de l'organisation. Tu n'es ni une IA, ni un système automatisé, ni un agent administratif. Tu es un pair qui a accepté des responsabilités au sein du comité étudiant.\n\n"
            "MISSION & PÉRIMÈTRE\n"
            "Ta mission principale est d'accompagner les candidats dans la collecte de leurs données pour la production de leurs supports de soutenance (affiches et motion design).\n"
            "Tu réponds aux questions sur le rôle de la Commission Design : un collectif étudiant de communication visuelle, indépendant de l'administration et du corps académique, travaillant en synergie avec les autres commissions (Logistique, Finance, Académique, Protocole, etc.). \n"
            "Le planning des soutenances est réalisé uniquement par l'administration.\n\n"
            "TON & PERSONNALITÉ\n"
            "- Ton : Chaleureux, pédagogue, professionnel, posture de 'grand frère/mentor étudiant'.\n"
            "- Style : Phrases claires, rythme posé, émojis utilisés avec mesure pour structurer ( ✅ , 📝 , 🎯 ) .\n"
            "- Proximité : Tu tutoies les candidats pour instaurer un climat de confiance étudiante.\n"
            "- Humain : Tu prends le temps de comprendre, tu reformules si besoin, tu ne rushes jamais. Tu ne te présentes JAMAIS comme un chatbot ou une intelligence artificielle.\n\n"
            "PROCÉDURE D'INSCRIPTION (PRIORITÉ ABSOLUE)\n"
            "Tu collectes STRICTEMENT 6 champs, un par un, DANS L'ORDRE :\n"
            "1. Nom de famille → 2. Prénom → 3. Téléphone → 4. Matricule → 5. Sujet de mémoire → 6. Photo portrait\n"
            "Règles de flux :\n"
            "- Tu accompagnes chaque étape : 'Parfait, c'est bien noté. Passons maintenant à ton prénom...'\n"
            "- Tu fais un mini-récapitulatif si la conversation s'étire ou pour rassurer.\n"
            "- Tu ne déduis JAMAIS une information d'un autre message. Tu attends la réponse explicite.\n"
            "- Si un candidat tente de commencer par du chat libre, tu l'accueilles chaleureusement mais tu l'orientes vers le bouton 'Commencer mon inscription' pour structurer la démarche.\n\n"
            "GESTION DES LIMITES & REDIRECTIONS (CRUCIAL)\n"
            "- Questions Académiques (rédaction, contenu mémoire, méthodologie) : 'Je suis spécialisé dans le design et la communication visuelle. Pour cette partie, je te conseille de te rapprocher de la Commission Académique ou de ton encadreur de mémoire. De mon côté, je m'assure que ton affiche soit impeccable !'\n"
            "- Autres Commissions (logistique, finance, protocole) : 'Cette question relève de la Commission [X]. Je t'invite à les contacter directement. Mon focus reste la production visuelle et les inscriptions design.'\n"
            "- Hors sujet / Inapproprié : Refus poli mais ferme, recentrage immédiat sur le cadre de la commission et la préparation des soutenances.\n\n"
            "CONVERSATION POST-INSCRIPTION\n"
            "Une fois les 6 éléments validés, tu bascules en mode 'accompagnement continu'. Tu restes disponible pour répondre aux questions sur le planning, les affiches, ou le rôle de la commission. Tu conserves le contexte, tu ne redemandes jamais les données, et tu maintains ton ton humain et professionnel."
        )}]
        st.session_state.don_etape = None
        st.session_state.don_temp  = {}
        st.session_state.candidat_tel = None
        st.session_state.reg_complete = False
        st.session_state.show_modif = False

    for msg in st.session_state.don_msgs:
        if msg["role"] == "system": continue
        with st.chat_message(msg["role"], avatar=AVT_CAND if msg["role"]=="user" else AVT_JR): st.markdown(msg["content"])

    if st.session_state.don_etape is None and not st.session_state.reg_complete:
        if st.button("📝 Commencer mon inscription", use_container_width=True, key="btn_start_reg"):
            st.session_state.don_etape = "nom"
            st.session_state.don_msgs.append({"role":"assistant","content":"😊 Parfait ! Je suis **Junior**, ton accompagnateur pour la Promo 2K20.\n\n**Étape 1/6 — Ton nom de famille ?**"})
            st.rerun()

    if prompt := st.chat_input("Écris à Junior…", key="ci_junior"):
        if contenu_interdit(prompt):
            with st.chat_message("assistant", avatar=AVT_JR): st.markdown("⚠️ Sujet hors périmètre."); st.stop()
        st.session_state.don_msgs.append({"role":"user","content":prompt})
        etape = st.session_state.don_etape

        if etape:
            if etape == "nom": st.session_state.don_temp["nom"]=prompt.upper(); st.session_state.don_etape="prenom"; rep="Noté ✅\n**Étape 2/6 — Ton prénom ?**"
            elif etape == "prenom": st.session_state.don_temp["prenom"]=prompt.capitalize(); st.session_state.don_etape="telephone"; rep=f"Enchanté **{st.session_state.don_temp['prenom']}** !\n**Étape 3/6 — Téléphone ?**"
            elif etape == "telephone":
                tel=prompt.replace(" ","")
                if candidat_existe(tel): rep="⚠️ Numéro existant. Utilise la modification ou change de numéro."; st.session_state.don_etape=None; st.session_state.don_temp={}
                else: st.session_state.don_temp["telephone"]=tel; st.session_state.don_etape="matricule"; rep="✅\n**Étape 4/6 — Matricule ?**"
            elif etape == "matricule": st.session_state.don_temp["matricule"]=prompt.upper(); st.session_state.don_etape="sujet"; rep="✅\n**Étape 5/6 — Sujet de mémoire ?**"
            elif etape == "sujet": st.session_state.don_temp["sujet"]=prompt; st.session_state.don_etape="photo"; rep="📝\n**Étape 6/6 — Photo portrait**\n👇 Téléverse via le widget ci-dessous, puis clique sur **Enregistrer**."
            elif etape == "photo": rep="📸 Charge ta photo via le widget et clique sur **Enregistrer**."
            st.session_state.don_msgs.append({"role":"assistant","content":rep})
            st.rerun()
        else:
            lower = prompt.lower()
            if any(w in lower for w in ["modifier","corriger","changer","erreur"]):
                st.session_state.show_modif = True
                rep = "✏️ Formulaire de modification ouvert en bas de page. Vérifie ton numéro de téléphone."
            elif any(w in lower for w in ["inscription","commencer"]):
                rep = "Clique sur **📝 Commencer mon inscription** au-dessus du chat."
            else:
                rep = call_groq(st.session_state.don_msgs)
            st.session_state.don_msgs.append({"role":"assistant","content":rep})
            st.rerun()

    if st.session_state.get("don_etape") == "photo":
        st.markdown("---")
        c_up, c_prev = st.columns([2,1])
        with c_up:
            uploaded = st.file_uploader("📸 Photo portrait (JPG/PNG)", type=["jpg","jpeg","png"], key="photo_upload")
            if uploaded: st.session_state.don_photo = uploaded.getvalue(); st.success("✅ Photo chargée")
        with c_prev:
            if st.session_state.get("don_photo"): st.image(st.session_state.don_photo, width=100, caption="Aperçu")
        
        if st.button("💾 Enregistrer mon inscription", use_container_width=True, key="btn_save_reg"):
            if st.session_state.get("don_photo"):
                temp = st.session_state.don_temp
                if all(temp.get(c) for c in ["nom","prenom","telephone","matricule","sujet"]):
                    ajouter_candidat(temp["nom"], temp["prenom"], temp["telephone"], temp["matricule"], temp["sujet"], st.session_state.don_photo)
                    st.session_state.don_etape = None; st.session_state.don_temp = {}; st.session_state.don_photo = None
                    st.session_state.candidat_tel = temp["telephone"]
                    st.session_state.reg_complete = True
                    
                    libre_sys = "Tu es Junior (IDENTITÉ.docx v2). Inscription terminée. Mode accompagnement continu. Ton humain, pas de redemande de données. Réponds aux questions sur la commission, les affiches, l'organisation."
                    st.session_state.don_msgs[0] = {"role":"system","content":libre_sys}
                    st.session_state.don_msgs.append({"role":"assistant","content":f"🎉 **Inscription complète, {temp['prenom']} !**\n\nDonnées enregistrées. Je reste à ta disposition 😊"})
                    st.rerun()
                else: st.error("Données incomplètes.")
            else: st.error("Photo manquante.")

    with st.expander("🗓️ Planning des soutenances", expanded=False):
        pl = obtenir_planning()
        if not pl.empty: st.dataframe(pl, use_container_width=True)
        else: st.info("Planning géré par l'administration.")

    if st.button("✏️ Modifier mes informations", key="btn_toggle_modif", type="secondary"):
        st.session_state.show_modif = not st.session_state.show_modif
    
    with st.expander("❓ Questions fréquentes (FAQ)", expanded=False):
        faqs = [
            ("À quoi sert cette plateforme ?", "Elle permet à la Commission Design de collecter tes informations pour créer ton affiche de présentation personnalisée."),
            ("Qui peut accéder à mes données ?", "Uniquement l'équipe design de la Promo 2K20 et le responsable créatif."),
            ("Je me suis trompé(e) — que faire ?", "Clique sur 'Modifier mes informations', entre ton numéro de téléphone, et corrige les champs."),
            ("Faut-il absolument une photo ?", "Oui, elle sera intégrée à ton affiche. Tu peux l'ajouter plus tard via la modification."),
        ]
        for q, a in faqs:
            st.markdown(f"""
            <div class="faq-item">
                <div class="faq-q">▸ {q}</div>
                <div class="faq-a">{a}</div>
            </div>
            """, unsafe_allow_html=True)

    if st.session_state.show_modif:
        tel_defaut = st.session_state.get("candidat_tel", "")
        tel_modif = st.text_input("📞 Numéro de téléphone d'inscription", value=tel_defaut, key="modif_tel_input")
        
        if tel_modif and tel_modif.strip():
            cand = get_candidat_par_telephone(tel_modif.strip())
            if cand is not None:
                photo_actuelle = str(cand.get("photo_path",""))
                if photo_actuelle and Path(photo_actuelle).exists():
                    st.image(photo_actuelle, width=80, caption="Photo actuelle")
                else:
                    st.caption("📸 Aucune photo enregistrée.")
                
                new_photo = st.file_uploader("📸 Nouvelle photo (optionnel)", type=["jpg","jpeg","png"], key="modif_photo_upload")
                
                with st.form("modif_form"):
                    nn = st.text_input("Nom", cand["nom"])
                    np = st.text_input("Prénom", cand["prenom"])
                    nt = st.text_input("Téléphone", cand["telephone"])
                    nm = st.text_input("Matricule", cand["matricule"])
                    ns = st.text_area("Sujet de mémoire", cand["sujet_memoire"])
                    
                    if st.form_submit_button("✅ Valider la modification"):
                        if nt != tel_modif.strip() and candidat_existe(nt):
                            st.error("⚠️ Ce numéro est déjà utilisé.")
                        else:
                            df = pd.read_csv(DATA_DIR/"candidats.csv")
                            idx = df[df["telephone"]==tel_modif.strip()].index[0]
                            df.at[idx,"nom"]=nn; df.at[idx,"prenom"]=np
                            df.at[idx,"telephone"]=nt; df.at[idx,"matricule"]=nm
                            df.at[idx,"sujet_memoire"]=ns
                            if new_photo is not None:
                                cand_id = str(df.at[idx,"id"])
                                new_path = str(PHOTOS_DIR/f"{cand_id}.jpg")
                                with open(new_path,"wb") as pf: pf.write(new_photo.getvalue())
                                df.at[idx,"photo_path"] = new_path
                            df.to_csv(DATA_DIR/"candidats.csv", index=False)
                            regenerer_planning()
                            st.session_state.candidat_tel = nt
                            st.success("✅ Profil mis à jour !")
                            st.rerun()
            else:
                st.error("Numéro non trouvé.")

def check_access(pwd_key: str, btn_key: str, label: str) -> bool:
    session_key = f"auth_{pwd_key}"
    if st.session_state.get(session_key): return True
    ref = get_secret_value(pwd_key)
    if not ref: st.error(f"Config manquante : {pwd_key}"); return False

    st.markdown(
        '<div style="text-align:center;margin-bottom:1.5rem;">'
        '<div style="font-family:Syne,sans-serif;font-size:2rem;font-weight:800;'
        'background:linear-gradient(135deg,#fff 0%,#a78bfa 80%);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
        'background-clip:text;margin-bottom:.4rem;">Design Promo 2K20</div>'
        '<div style="font-size:.8rem;color:#6B6B96;font-weight:300;">'
        'Commission Design · ENSTP Yaoundé</div>'
        '<div style="display:inline-flex;align-items:center;gap:6px;margin-top:.6rem;'
        'padding:3px 10px;border-radius:100px;background:rgba(16,185,129,.1);'
        'border:1px solid rgba(16,185,129,.25);font-size:.65rem;color:#6ee7b7;">'
        '<span style="width:6px;height:6px;border-radius:50%;background:#10b981;'
        'box-shadow:0 0 0 3px rgba(16,185,129,.2);display:inline-block;"></span>'
        'Plateforme active</div>'
        '</div>',
        unsafe_allow_html=True
    )

    pwd = st.text_input(label, type="password", key=f"inp_{btn_key}")
    if st.button("Accéder", key=f"btn_{btn_key}", use_container_width=True):
        if pwd == ref: st.session_state[session_key] = True; st.rerun()
        else: st.error("Identifiant incorrect")
    return False
def fix_sidebar_visibility():
    st.markdown("""
    <style>
    /* ── Assure que le bouton hamburger (mobile) est toujours visible ── */
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 999999 !important;
        position: fixed !important;
        top: 0.875rem !important;
        left: 0.875rem !important;
    }

    /* ── Assure que la sidebar elle-même passe au-dessus du fond animé ── */
    [data-testid="stSidebar"] {
        z-index: 99999 !important;
        visibility: visible !important;
    }

    /* ── Empêche le fond animé de capturer les clics sur la sidebar ── */
    .particle-bg {
        pointer-events: none !important;
        z-index: -9999 !important;
    }

    /* ── Fix Edge : force le rendu du bouton de toggle ── */
    button[kind="header"] {
        z-index: 999999 !important;
        position: relative !important;
    }

    /* ── Mobile : s'assure que la sidebar ouverte couvre bien l'écran ── */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            width: 80vw !important;
            min-width: 250px !important;
            z-index: 999999 !important;
        }
        /* Overlay sombre derrière la sidebar sur mobile */
        [data-testid="stSidebarContent"] {
            overflow-y: auto !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
def main():
    inject_particles_animation()
    load_css()
    fix_sidebar_visibility()
    suivi = mettre_a_jour_suivi()
    
    with st.sidebar:
        st.markdown('<div style="padding:6px 0 14px 0;"><div class="sb-brand-title">Commission<br>Design</div><div class="sb-brand-sub">Promotion 2K20</div></div>', unsafe_allow_html=True)
        
        with st.expander("ℹ️ Comment utiliser cette application ?", expanded=False):
            st.markdown("""
            <div style='font-size:.78rem;color:#94a3b8;line-height:1.7;'>
            <div style='font-family:Syne,sans-serif;font-size:.88rem;font-weight:700;
            color:#e2e8f0;margin-bottom:10px;'>🎓 Promo 2K20 — ENSTP Yaoundé</div>
            <div style='background:rgba(124,58,237,.08);border-left:3px solid #7c3aed;
            border-radius:0 8px 8px 0;padding:8px 10px;margin-bottom:12px;
            font-size:.74rem;color:#c4b5fd;'>Plateforme pour centraliser les inscriptions
            et la production visuelle des soutenances.</div>
            <div style='margin-bottom:6px;font-size:.64rem;letter-spacing:.15em;
            text-transform:uppercase;color:#475569;font-weight:600;'>Quel est ton rôle ?</div>
            <div style='display:flex;align-items:flex-start;gap:8px;
            background:rgba(14,165,233,.07);border-radius:8px;
            padding:8px 10px;margin-bottom:6px;'>
            <span style='font-size:1.1rem;'>🎓</span>
            <div><strong style='color:#38bdf8;'>Candidat(e)</strong><br>
            Menu <strong>Données et planning</strong>.</div></div>
            <div style='display:flex;align-items:flex-start;gap:8px;
            background:rgba(124,58,237,.07);border-radius:8px;
            padding:8px 10px;margin-bottom:6px;'>
            <span style='font-size:1.1rem;'>✏️</span>
            <div><strong style='color:#a78bfa;'>Designer</strong><br>
            Menu <strong>Direction artistique → Équipe design</strong>.</div></div>
            <div style='display:flex;align-items:flex-start;gap:8px;
            background:rgba(253,211,77,.06);border-radius:8px;
            padding:8px 10px;margin-bottom:10px;'>
            <span style='font-size:1.1rem;'>👑</span>
            <div><strong style='color:#fcd34d;'>Responsable créatif</strong><br>
            Menu <strong>Direction artistique → Direction créative</strong>.</div></div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="sb-label">Navigation</div>', unsafe_allow_html=True)
        page = st.radio("", ["Direction artistique","Données et planning"], label_visibility="collapsed", key="nav_radio")
        access_type = None
        if page == "Direction artistique":
            st.markdown('<div class="sb-label">Accès</div>', unsafe_allow_html=True)
            access_type = st.radio("", ["Équipe design","Direction créative"], label_visibility="collapsed", key="access_radio")
        if page == "Direction artistique": render_livrables_sidebar(suivi)
        if page == "Direction artistique":
            df_c = pd.read_csv(DATA_DIR/"candidats.csv"); nb = len(df_c)
            st.markdown('<div class="sb-label">Export</div>', unsafe_allow_html=True)
            if nb > 0: st.download_button(label=f"📦 Package candidats ({nb})", data=generer_zip_candidats(), file_name=f"promo2k20_{datetime.now().strftime('%Y%m%d')}.zip", mime="application/zip", use_container_width=True)
            else: st.markdown('<div class="sb-info">Aucun candidat.</div>', unsafe_allow_html=True)
        st.markdown('<div class="sb-spacer"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sb-footer"><span class="sb-footer-name">Junior Lecco</span><div class="sb-footer-roles">Graphic Designer · Motion Designer<br>UXP Developer · 3D Artist</div></div>', unsafe_allow_html=True)

    if page == "Direction artistique":
        if access_type == "Direction créative":
            if check_access("LEAD_PASSWORD","lead","Mot de passe — Direction créative"): page_directeur(lead_mode=True, suivi=suivi)
            else: st.stop()
        else:
            if check_access("TEAM_PASSWORD","team","Mot de passe — Équipe design"): page_directeur(lead_mode=False, suivi=suivi)
            else: st.stop()
    else:
        if check_access("PUBLIC_ACCESS_CODE","public","Code d'accès candidats"): page_donnees()
        else: st.stop()

if __name__ == "__main__":
    main()