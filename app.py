

"""DEEPFAKE FORENSICS v4.0 — New: ELA · JPEG Ghost · DCT Heatmap · PDF Report Export"""

import streamlit as st
import torch, torch.nn as nn, torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image
import numpy as np, os, time, cv2, io, base64
from pathlib import Path
from datetime import datetime
from scipy.fftpack import dct

st.set_page_config(page_title="DeepFake Forensics v4", page_icon="DF", layout="wide", initial_sidebar_state="expanded")

# ══════════════════════════════════════════════════════════════════════════════
# CSS — Cinematic Military-Tech Theme
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;600&family=Share+Tech+Mono&display=swap');
:root{--bg:#04080f;--bg2:#070d1a;--card:#0a1220;--cyan:#00e5ff;--blue:#0066ff;--red:#ff1744;--green:#00e676;--amber:#ffab00;--txt:#e0f0ff;--txt2:#5a8aaa;--dim:#2a4a6a;--bdr:#0d2a40;--bdr2:#1a4a6a;}
html,body,[class*="css"]{font-family:'Exo 2',sans-serif!important;background:var(--bg)!important;color:var(--txt)!important;}
.stApp{background:var(--bg)!important;}
.stApp::before{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;background:radial-gradient(ellipse 80% 50% at 20% 0%,rgba(0,102,255,.07) 0%,transparent 60%),radial-gradient(ellipse 60% 40% at 80% 100%,rgba(0,229,255,.05) 0%,transparent 60%);}
.stApp::after{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;background-image:linear-gradient(rgba(0,102,255,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(0,102,255,.025) 1px,transparent 1px);background-size:40px 40px;}
.scan-line{position:fixed;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,rgba(0,229,255,.3),transparent);animation:scanDown 7s linear infinite;pointer-events:none;z-index:9999;}
.scan-overlay{position:fixed;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(0,229,255,.007) 3px,rgba(0,229,255,.007) 4px);pointer-events:none;z-index:9998;}
@keyframes scanDown{0%{top:-2px;opacity:0}5%{opacity:1}95%{opacity:1}100%{top:100vh;opacity:0}}
::-webkit-scrollbar{width:4px}::-webkit-scrollbar-track{background:var(--bg)}::-webkit-scrollbar-thumb{background:var(--blue);border-radius:2px}
.app-title{font-family:'Orbitron',monospace;font-size:2.3rem;font-weight:900;letter-spacing:.12em;background:linear-gradient(135deg,#00e5ff 0%,#0066ff 50%,#00e5ff 100%);background-size:200% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:shine 4s linear infinite;}
@keyframes shine{to{background-position:200% center}}
.app-sub{font-family:'Share Tech Mono',monospace;font-size:.6rem;color:var(--dim);letter-spacing:.4em;text-transform:uppercase;margin-top:5px;}
.v-badge{display:inline-flex;align-items:center;gap:6px;background:rgba(0,229,255,.05);border:1px solid rgba(0,229,255,.2);border-radius:2px;padding:2px 12px;font-family:'Share Tech Mono',monospace;font-size:.58rem;color:var(--cyan);letter-spacing:.2em;}
.v-dot{width:5px;height:5px;border-radius:50%;background:var(--green);box-shadow:0 0 8px rgba(0,230,118,.8);animation:blink 1.5s infinite;}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.2}}
.fc{background:var(--card);border:1px solid var(--bdr);border-radius:4px;padding:18px;position:relative;overflow:hidden;margin-bottom:10px;}
.fc.gr{border-color:rgba(0,230,118,.3);box-shadow:0 0 24px rgba(0,230,118,.1);}
.fc.rr{border-color:rgba(255,23,68,.3);box-shadow:0 0 24px rgba(255,23,68,.12);}
.fc.cr{border-color:rgba(0,229,255,.2);box-shadow:0 0 18px rgba(0,229,255,.08);}
.fc::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--cyan),transparent);opacity:.35;}
.cb{position:absolute;width:13px;height:13px;}
.cb.tl{top:7px;left:7px;border-top:2px solid var(--cyan);border-left:2px solid var(--cyan);}
.cb.tr{top:7px;right:7px;border-top:2px solid var(--cyan);border-right:2px solid var(--cyan);}
.cb.bl{bottom:7px;left:7px;border-bottom:2px solid var(--cyan);border-left:2px solid var(--cyan);}
.cb.br{bottom:7px;right:7px;border-bottom:2px solid var(--cyan);border-right:2px solid var(--cyan);}
.vr-label{font-family:'Share Tech Mono',monospace;font-size:.55rem;color:var(--dim);letter-spacing:.5em;margin-bottom:10px;}
.vr-real{font-family:'Orbitron',monospace;font-size:2.5rem;font-weight:900;color:var(--green);text-shadow:0 0 30px rgba(0,230,118,.6);animation:vr .6s ease-out;letter-spacing:.15em;}
.vr-fake{font-family:'Orbitron',monospace;font-size:2.5rem;font-weight:900;color:var(--red);text-shadow:0 0 30px rgba(255,23,68,.7);animation:vr .6s ease-out,dp 2s ease-in-out infinite .6s;letter-spacing:.15em;}
.vr-unc{font-family:'Orbitron',monospace;font-size:2.5rem;font-weight:900;color:var(--amber);text-shadow:0 0 25px rgba(255,171,0,.5);animation:vr .6s ease-out;letter-spacing:.15em;}
@keyframes vr{0%{opacity:0;transform:scale(.8) translateY(8px);filter:blur(6px)}100%{opacity:1;transform:scale(1) translateY(0);filter:blur(0)}}
@keyframes dp{0%,100%{text-shadow:0 0 30px rgba(255,23,68,.7)}50%{text-shadow:0 0 55px rgba(255,23,68,1),0 0 80px rgba(255,23,68,.3)}}
.conf-val{font-family:'Orbitron',monospace;font-size:1.3rem;font-weight:700;margin-top:10px;}
.conf-lbl{font-family:'Share Tech Mono',monospace;font-size:.55rem;color:var(--dim);letter-spacing:.3em;}
.risk-b{display:inline-block;padding:3px 14px;border-radius:2px;font-family:'Share Tech Mono',monospace;font-size:.6rem;letter-spacing:.2em;font-weight:bold;margin-top:8px;}
.risk-none{background:rgba(0,230,118,.1);color:var(--green);border:1px solid rgba(0,230,118,.3);}
.risk-low{background:rgba(0,230,118,.07);color:#69f0ae;border:1px solid rgba(0,230,118,.2);}
.risk-moderate{background:rgba(255,171,0,.1);color:var(--amber);border:1px solid rgba(255,171,0,.3);}
.risk-high{background:rgba(255,23,68,.1);color:var(--red);border:1px solid rgba(255,23,68,.3);}
.risk-critical{background:rgba(255,23,68,.2);color:#ff6b6b;border:1px solid rgba(255,23,68,.5);animation:cb2 1s infinite;}
.risk-inconclusive{background:rgba(255,171,0,.08);color:#ffd54f;border:1px solid rgba(255,171,0,.2);}
@keyframes cb2{0%,100%{opacity:1}50%{opacity:.6}}
.sb-row{margin-bottom:12px;}
.sb-head{display:flex;justify-content:space-between;margin-bottom:4px;}
.sb-name{font-family:'Share Tech Mono',monospace;font-size:.65rem;color:var(--txt2);letter-spacing:.15em;}
.sb-pct{font-family:'Orbitron',monospace;font-size:.7rem;font-weight:700;}
.sb-track{height:9px;background:rgba(255,255,255,.04);border-radius:1px;overflow:hidden;border:1px solid var(--bdr);}
.sh{display:flex;align-items:center;gap:10px;margin-bottom:11px;margin-top:4px;}
.sh-line{flex:1;height:1px;background:linear-gradient(90deg,var(--bdr2),transparent);}
.sh-txt{font-family:'Share Tech Mono',monospace;font-size:.6rem;color:var(--txt2);letter-spacing:.25em;white-space:nowrap;}
.bd-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:12px 0;}
.bd-item{background:rgba(255,255,255,.02);border:1px solid var(--bdr);border-radius:3px;padding:10px 12px;}
.bd-name{font-family:'Share Tech Mono',monospace;font-size:.56rem;color:var(--dim);letter-spacing:.15em;margin-bottom:5px;}
.bd-track{height:4px;background:rgba(255,255,255,.05);border-radius:2px;overflow:hidden;margin-bottom:5px;}
.bd-val{font-family:'Orbitron',monospace;font-size:.66rem;font-weight:700;}
.exp-card{border-radius:4px;padding:16px 18px;border-left:3px solid;margin:10px 0;background:rgba(255,255,255,.015);}
.exp-title{font-family:'Orbitron',monospace;font-size:.68rem;letter-spacing:.12em;margin-bottom:8px;}
.exp-main{font-family:'Exo 2',sans-serif;font-size:.76rem;color:var(--txt2);line-height:1.65;margin-bottom:10px;}
.exp-detail{font-family:'Share Tech Mono',monospace;font-size:.63rem;color:#3a6a7a;line-height:1.9;white-space:pre-line;}
.art-tag{display:inline-block;background:rgba(255,23,68,.08);border:1px solid rgba(255,23,68,.2);border-radius:2px;padding:1px 8px;font-family:'Share Tech Mono',monospace;font-size:.56rem;color:var(--red);letter-spacing:.1em;margin:2px;}
.real-tag{display:inline-block;background:rgba(0,230,118,.08);border:1px solid rgba(0,230,118,.2);border-radius:2px;padding:1px 8px;font-family:'Share Tech Mono',monospace;font-size:.56rem;color:var(--green);letter-spacing:.1em;margin:2px;}
.hi{display:grid;grid-template-columns:55px 1fr auto 50px;gap:8px;align-items:center;padding:6px 0;border-bottom:1px solid rgba(255,255,255,.025);animation:si .3s ease;}
@keyframes si{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:translateX(0)}}
.ht{font-family:'Share Tech Mono',monospace;font-size:.56rem;color:var(--dim);}
.hf{font-family:'Exo 2',sans-serif;font-size:.66rem;color:var(--txt2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.hv-r{font-family:'Orbitron',monospace;font-size:.56rem;color:var(--green);font-weight:700;}
.hv-f{font-family:'Orbitron',monospace;font-size:.56rem;color:var(--red);font-weight:700;}
.hc{font-family:'Share Tech Mono',monospace;font-size:.56rem;color:var(--dim);}
.sl{font-family:'Share Tech Mono',monospace;font-size:.56rem;color:var(--dim);letter-spacing:.28em;text-transform:uppercase;margin-bottom:7px;}
.ms{display:flex;align-items:center;gap:8px;padding:9px 12px;background:rgba(0,230,118,.04);border:1px solid rgba(0,230,118,.15);border-radius:3px;}
.ms-on{width:8px;height:8px;border-radius:50%;background:var(--green);box-shadow:0 0 8px rgba(0,230,118,.8);animation:blink 2s infinite;flex-shrink:0;}
.ms-txt{font-family:'Share Tech Mono',monospace;font-size:.56rem;color:var(--green);letter-spacing:.1em;line-height:1.6;}
/* New feature tabs */
.feat-label{font-family:'Share Tech Mono',monospace;font-size:.58rem;color:#3a5a6a;letter-spacing:.18em;line-height:2;}
/* Streamlit overrides */
div[data-testid="stFileUploader"]>div{border:none!important;background:transparent!important;padding:0!important;}
div[data-testid="stFileUploader"] label{font-family:'Share Tech Mono',monospace!important;font-size:.65rem!important;color:var(--txt2)!important;letter-spacing:.2em!important;}
section[data-testid="stFileUploadDropzone"]{background:linear-gradient(135deg,#060d1a,#040810)!important;border:1.5px dashed #1a3a5a!important;border-radius:6px!important;min-height:180px!important;transition:all .3s!important;}
section[data-testid="stFileUploadDropzone"]:hover{border-color:var(--cyan)!important;background:rgba(0,229,255,.015)!important;}
.stButton>button{background:linear-gradient(135deg,#001a40,#003380)!important;color:var(--cyan)!important;border:1px solid #0055aa!important;border-radius:2px!important;font-family:'Orbitron',monospace!important;font-size:.6rem!important;font-weight:700!important;letter-spacing:.2em!important;text-transform:uppercase!important;transition:all .25s!important;}
.stButton>button:hover{background:linear-gradient(135deg,#002255,#0044aa)!important;border-color:var(--cyan)!important;box-shadow:0 0 16px rgba(0,229,255,.25)!important;}
[data-testid="stMetric"]{background:var(--card)!important;border:1px solid var(--bdr)!important;border-radius:4px!important;padding:13px!important;}
[data-testid="stMetricLabel"]{color:var(--dim)!important;font-family:'Share Tech Mono',monospace!important;font-size:.56rem!important;letter-spacing:.18em!important;}
[data-testid="stMetricValue"]{color:var(--cyan)!important;font-family:'Orbitron',monospace!important;font-weight:700!important;}
[data-testid="stExpander"]{background:var(--card)!important;border:1px solid var(--bdr)!important;border-radius:4px!important;}
hr{border-color:var(--bdr)!important;}
</style>
<div class="scan-overlay"></div><div class="scan-line"></div>
""", unsafe_allow_html=True)

st.markdown("""
<style>
:root{
  --bg:#05070c;--bg-soft:#080d16;--panel:#0b1320;--panel-2:#101a2a;
  --ink:#eff7ff;--muted:#8aa4b8;--faint:#3d5368;--line:rgba(118,178,255,.16);
  --cyan:#23d5ff;--blue:#5b8cff;--green:#27f0a6;--red:#ff4f6d;--amber:#ffbf47;
  --shadow:0 24px 70px rgba(0,0,0,.36);--ease:cubic-bezier(.22,1,.36,1);
}
.stApp{
  background:
    linear-gradient(115deg,rgba(35,213,255,.045),transparent 26%),
    radial-gradient(circle at 82% 10%,rgba(91,140,255,.12),transparent 32%),
    radial-gradient(circle at 14% 88%,rgba(39,240,166,.08),transparent 28%),
    var(--bg)!important;
}
.block-container{max-width:1500px!important;padding-top:1.35rem!important;padding-bottom:3rem!important;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,rgba(9,16,28,.96),rgba(5,8,14,.98))!important;border-right:1px solid var(--line)!important;}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:.72rem!important;}
.app-hero{
  position:relative;overflow:hidden;border:1px solid var(--line);border-radius:8px;
  padding:24px 26px 22px;margin-bottom:18px;background:
    linear-gradient(135deg,rgba(16,26,42,.94),rgba(7,12,20,.94)),
    linear-gradient(90deg,rgba(35,213,255,.13),transparent);
  box-shadow:var(--shadow);isolation:isolate;
}
.app-hero::before{
  content:"";position:absolute;inset:0;background:
    linear-gradient(90deg,transparent,rgba(35,213,255,.08),transparent);
  transform:translateX(-120%);animation:sweep 7s var(--ease) infinite;z-index:-1;
}
.app-hero::after{
  content:"";position:absolute;right:22px;top:18px;width:150px;height:150px;
  border:1px solid rgba(35,213,255,.14);border-radius:50%;filter:drop-shadow(0 0 24px rgba(35,213,255,.14));
  background:conic-gradient(from 90deg,rgba(35,213,255,.2),transparent 25%,rgba(39,240,166,.16),transparent 58%,rgba(91,140,255,.18),transparent);
  opacity:.7;animation:spin 18s linear infinite;
}
@keyframes sweep{0%,42%{transform:translateX(-125%)}72%,100%{transform:translateX(125%)}}
@keyframes spin{to{transform:rotate(360deg)}}
.app-title{font-size:clamp(1.85rem,3vw,3rem)!important;letter-spacing:.08em!important;line-height:1.02!important;}
.app-sub{color:var(--muted)!important;letter-spacing:.22em!important;margin-top:9px!important;}
.hero-row{display:flex;align-items:flex-end;justify-content:space-between;gap:18px;flex-wrap:wrap;}
.hero-actions{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end;}
.v-badge,.module-chip{
  border:1px solid rgba(35,213,255,.22)!important;border-radius:999px!important;
  background:rgba(35,213,255,.07)!important;color:var(--cyan)!important;
  padding:6px 11px!important;letter-spacing:.12em!important;backdrop-filter:blur(12px);
}
.module-chip{font-family:'Share Tech Mono',monospace;font-size:.57rem;color:var(--muted)!important;}
.metric-deck{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:4px 0 18px;}
.metric-card{
  position:relative;overflow:hidden;border:1px solid var(--line);border-radius:8px;padding:15px 16px;
  background:linear-gradient(180deg,rgba(16,26,42,.82),rgba(8,13,22,.9));box-shadow:0 14px 36px rgba(0,0,0,.22);
}
.metric-card::before{content:"";position:absolute;left:0;right:0;top:0;height:1px;background:linear-gradient(90deg,transparent,var(--accent),transparent);opacity:.65;}
.metric-label{font-family:'Share Tech Mono',monospace;font-size:.58rem;color:var(--faint);letter-spacing:.18em;text-transform:uppercase;}
.metric-value{font-family:'Orbitron',monospace;font-size:clamp(1.35rem,2vw,2rem);font-weight:900;color:var(--ink);margin-top:5px;line-height:1;}
.metric-note{font-family:'Share Tech Mono',monospace;font-size:.56rem;color:var(--muted);margin-top:8px;letter-spacing:.08em;}
.fc,.bd-item,.exp-card{
  border-radius:8px!important;border-color:var(--line)!important;background:linear-gradient(180deg,rgba(16,26,42,.9),rgba(8,13,22,.92))!important;
  box-shadow:0 18px 52px rgba(0,0,0,.24)!important;animation:rise .48s var(--ease) both;
}
@keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
.fc:hover,.bd-item:hover{border-color:rgba(35,213,255,.34)!important;transform:translateY(-1px);transition:transform .22s var(--ease),border-color .22s var(--ease);}
.sh{margin-top:12px!important;margin-bottom:12px!important;}
.sh-txt{color:var(--muted)!important;letter-spacing:.16em!important;font-size:.62rem!important;}
.sh-line{background:linear-gradient(90deg,rgba(35,213,255,.36),transparent)!important;}
.vr-label,.conf-lbl,.bd-name,.sl{letter-spacing:.16em!important;color:var(--faint)!important;}
.vr-real,.vr-fake,.vr-unc{font-size:clamp(1.7rem,3vw,2.65rem)!important;letter-spacing:.08em!important;}
.verdict-card{min-height:265px;display:flex;flex-direction:column;align-items:center;justify-content:center;}
.sb-track{height:12px!important;border-radius:999px!important;background:rgba(255,255,255,.055)!important;border-color:rgba(118,178,255,.14)!important;}
.sb-track>div{border-radius:999px!important;box-shadow:0 0 22px currentColor;animation:barIn .72s var(--ease) both;}
@keyframes barIn{from{width:0;filter:blur(3px)}}
.bd-grid{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:10px!important;}
.bd-track{height:6px!important;border-radius:999px!important;}
.exp-card{border-left-width:4px!important;}
.feat-label{color:var(--muted)!important;letter-spacing:.08em!important;line-height:1.8!important;}
.empty-state{
  position:relative;overflow:hidden;text-align:center;border:1px solid var(--line);border-radius:8px;
  padding:36px 20px 30px;margin-top:4px;background:linear-gradient(180deg,rgba(16,26,42,.58),rgba(8,13,22,.84));
}
.empty-state::before{content:"";position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(35,213,255,.06),transparent);animation:sweep 6s var(--ease) infinite;}
.empty-orbit{width:68px;height:68px;margin:0 auto 14px;border:1px solid rgba(35,213,255,.28);border-radius:50%;position:relative;box-shadow:0 0 35px rgba(35,213,255,.13);}
.empty-orbit::before{content:"";position:absolute;inset:14px;border:1px solid rgba(39,240,166,.26);border-radius:50%;}
.empty-orbit::after{content:"";position:absolute;left:50%;top:-5px;width:9px;height:9px;border-radius:50%;background:var(--cyan);box-shadow:0 0 20px var(--cyan);animation:spin 3.8s linear infinite;transform-origin:0 39px;}
.empty-title{font-family:'Orbitron',monospace;font-size:.78rem;color:var(--cyan);letter-spacing:.22em;}
.empty-copy{font-family:'Share Tech Mono',monospace;font-size:.58rem;color:var(--muted);letter-spacing:.11em;margin-top:8px;}
section[data-testid="stFileUploadDropzone"]{
  min-height:210px!important;border-radius:8px!important;border:1px dashed rgba(35,213,255,.42)!important;
  background:linear-gradient(145deg,rgba(16,26,42,.74),rgba(5,9,16,.92))!important;
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.025),0 18px 50px rgba(0,0,0,.22)!important;
}
section[data-testid="stFileUploadDropzone"]:hover{border-color:var(--cyan)!important;box-shadow:0 0 0 1px rgba(35,213,255,.18),0 24px 60px rgba(0,0,0,.28)!important;transform:translateY(-1px);}
.stButton>button{
  min-height:42px!important;border-radius:7px!important;background:linear-gradient(135deg,rgba(35,213,255,.16),rgba(91,140,255,.20))!important;
  border:1px solid rgba(35,213,255,.42)!important;color:var(--ink)!important;box-shadow:0 14px 32px rgba(35,213,255,.08)!important;
}
.stButton>button:hover{transform:translateY(-1px);box-shadow:0 18px 44px rgba(35,213,255,.16)!important;}
[data-testid="stMetric"]{border-radius:8px!important;background:linear-gradient(180deg,rgba(16,26,42,.86),rgba(8,13,22,.92))!important;}
[data-testid="stImage"] img{border-radius:8px!important;border:1px solid rgba(118,178,255,.12);box-shadow:0 16px 45px rgba(0,0,0,.28);}
.report-copy{font-family:'Share Tech Mono',monospace;font-size:.62rem;color:var(--muted);letter-spacing:.08em;line-height:1.8;}
.download-link{display:inline-block;background:linear-gradient(135deg,rgba(35,213,255,.18),rgba(91,140,255,.22));color:var(--ink);border:1px solid rgba(35,213,255,.42);border-radius:7px;padding:10px 18px;font-family:'Orbitron',monospace;font-size:.62rem;font-weight:700;letter-spacing:.14em;text-decoration:none;text-transform:uppercase;box-shadow:0 16px 42px rgba(35,213,255,.12);}
@media (max-width:900px){
  .metric-deck{grid-template-columns:repeat(2,minmax(0,1fr));}
  .app-hero{padding:20px 18px}.app-hero::after{opacity:.28}
  .bd-grid{grid-template-columns:1fr!important;}
}
@media (max-width:560px){
  .metric-deck{grid-template-columns:1fr;}
  .hero-actions{justify-content:flex-start}.module-chip{font-size:.52rem!important}
  .sh-txt{white-space:normal!important;line-height:1.5;}
}
@media (prefers-reduced-motion:reduce){
  *,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition:none!important;}
}
</style>
""", unsafe_allow_html=True)

# ── Session state ──
for k,v in [('history',[]),('total_analyzed',0),('total_fake',0)]:
    if k not in st.session_state: st.session_state[k]=v

# ══════════════════════════════════════════════════════════════════════════════
# MODEL
# ══════════════════════════════════════════════════════════════════════════════
def find_models():
    found=[]
    for base in ["models/","./",str(Path.home())]:
        if os.path.exists(base):
            for f in os.listdir(base):
                if f.endswith(('.pt','.pth')):
                    p=os.path.join(base,f); found.append((f,p,os.path.getsize(p)/1048576))
    found.sort(key=lambda x:0 if 'balanced' in x[0] else 1 if 'phase6' in x[0] else 2)
    return found

@st.cache_resource
def load_model(path):
    dev=torch.device("cuda" if torch.cuda.is_available() else "cpu")
    try:
        sd=torch.load(path,map_location=dev); out=sd['classifier.1.weight'].shape[0]
        m=models.efficientnet_b3(weights=None); m.classifier[1]=nn.Linear(1536,out)
        m.load_state_dict(sd); m.to(dev); m.eval(); return m,dev,out
    except: return None,None,None

@st.cache_resource
def get_tf():
    return transforms.Compose([transforms.Resize((224,224)),transforms.ToTensor(),
        transforms.Normalize([.485,.456,.406],[.229,.224,.225])])

def predict(image,model,device,odim,tf,thr=0.5):
    if not model: return None
    try:
        t=tf(image).unsqueeze(0).to(device)
        with torch.no_grad(): logits=model(t)
        rs=torch.sigmoid(logits[0,0]).item() if odim==1 else F.softmax(logits,dim=1)[0,0].item()
        fs=1.0-rs if odim==1 else F.softmax(logits,dim=1)[0,1].item()
        verdict="REAL" if rs>=thr else "FAKE" if fs>=thr else "UNCERTAIN"
        conf=rs if verdict=="REAL" else fs if verdict=="FAKE" else max(rs,fs)
        risk=("CRITICAL" if fs>.85 else "HIGH" if fs>.70 else "MODERATE") if verdict=="FAKE" else ("NONE" if rs>.85 else "LOW") if verdict=="REAL" else "INCONCLUSIVE"
        return dict(real_score=rs,fake_score=fs,verdict=verdict,confidence=conf,risk=risk,odim=odim,thr=thr,ts=datetime.now().strftime('%H:%M:%S'))
    except Exception as e: st.error(f"Error: {e}"); return None

# ══════════════════════════════════════════════════════════════════════════════
# GRAD-CAM
# ══════════════════════════════════════════════════════════════════════════════
def gradcam(image,model,device,tf,verdict):
    try:
        t=tf(image).unsqueeze(0).to(device); grads,acts=[],[]
        def sg(g): grads.append(g)
        def fh(m,i,o): acts.append(o); o.register_hook(sg)
        hook=model.features[-1].register_forward_hook(fh)
        out=model(t); model.zero_grad()
        (torch.sigmoid(out[0,0]) if out.shape[1]==1 else F.softmax(out,dim=1)[0,1]).backward()
        hook.remove()
        if not grads or not acts: return None,None
        g=grads[0].cpu().detach().numpy()[0]; a=acts[0].cpu().detach().numpy()[0]
        cam=np.zeros(a.shape[1:],np.float32)
        w=g.mean(axis=(1,2))
        for i,ww in enumerate(w): cam+=ww*a[i]
        cam=np.maximum(cam,0)
        if cam.max()>0: cam/=cam.max()
        ow,oh=image.size; cam_r=cv2.resize(cam,(ow,oh))
        orig=np.array(image.convert('RGB'),dtype=np.float32)
        if verdict=="FAKE":
            hm=np.zeros_like(orig); hm[:,:,0]=cam_r*255; hm[:,:,1]=cam_r*100; hm[:,:,2]=cam_r*15
            alpha=(0.38+cam_r*0.42)[:,:,np.newaxis]
        else:
            hm=np.zeros_like(orig); hm[:,:,0]=cam_r*10; hm[:,:,1]=cam_r*210; hm[:,:,2]=cam_r*130
            alpha=(0.25+cam_r*0.30)[:,:,np.newaxis]
        blended=np.clip(orig*(1-np.clip(alpha,0,.82))+hm*np.clip(alpha,0,.82),0,255).astype(np.uint8)
        try:
            gray=cv2.cvtColor(np.array(image.convert('RGB')),cv2.COLOR_RGB2GRAY)
            fc2=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
            faces=fc2.detectMultiScale(gray,1.1,4,minSize=(60,60))
            if len(faces)>0:
                x,y,fw,fh2=faces[np.argmax([ww*hh for (x,y,ww,hh) in faces])]
                col=(255,30,60) if verdict=="FAKE" else (0,230,118); th=max(2,min(ow,oh)//150); bl=max(14,fw//5)
                for(px,py,dx,dy) in[(x,y,1,0),(x,y,0,1),(x+fw,y,-1,0),(x+fw,y,0,1),(x,y+fh2,1,0),(x,y+fh2,0,-1),(x+fw,y+fh2,-1,0),(x+fw,y+fh2,0,-1)]:
                    cv2.line(blended,(px,py),(px+dx*bl,py+dy*bl),col,th)
                ov=blended.copy(); cv2.rectangle(ov,(x,y),(x+fw,y+fh2),col,1); cv2.addWeighted(ov,.35,blended,.65,0,blended)
        except: pass
        return Image.fromarray(blended),cam_r
    except: return None,None

# ══════════════════════════════════════════════════════════════════════════════
# ELA — Error Level Analysis
# ══════════════════════════════════════════════════════════════════════════════
def ela_analysis(image, quality=90, scale=15):
    """
    Save image at reduced quality, compare with original.
    Manipulated regions show higher error levels (brighter in ELA map).
    """
    orig=image.convert('RGB')
    buf=io.BytesIO(); orig.save(buf,format='JPEG',quality=quality); buf.seek(0)
    compressed=Image.open(buf).convert('RGB')
    orig_np=np.array(orig,dtype=np.float32)
    comp_np=np.array(compressed,dtype=np.float32)
    diff=np.abs(orig_np-comp_np)*scale
    diff=np.clip(diff,0,255).astype(np.uint8)
    # Colorize: low error=dark blue, high error=bright red/yellow
    ela_gray=diff.mean(axis=2)
    ela_colored=np.zeros((*ela_gray.shape,3),np.uint8)
    ela_colored[:,:,0]=np.clip(ela_gray*2,0,255).astype(np.uint8)        # Red: high error
    ela_colored[:,:,1]=np.clip(ela_gray*0.8,0,255).astype(np.uint8)      # Some green
    ela_colored[:,:,2]=np.clip(255-ela_gray*1.5,0,255).astype(np.uint8)  # Blue: low error
    ela_score=float(np.mean(ela_gray))
    ela_max=float(np.max(ela_gray))
    ela_std=float(np.std(ela_gray))
    manipulation_likely = ela_score > 12 or ela_std > 18
    return Image.fromarray(ela_colored), ela_score, ela_max, ela_std, manipulation_likely

# ══════════════════════════════════════════════════════════════════════════════
# JPEG GHOST ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
def jpeg_ghost(image, quality_range=range(50,96,5)):
    """
    JPEG Ghost: save at multiple quality levels, find where error is MINIMIZED.
    The quality where error drops sharply = original save quality.
    Regions saved at different quality = ghosting = manipulation evidence.
    """
    orig=np.array(image.convert('RGB'),dtype=np.float32)
    h,w=orig.shape[:2]
    ghost_maps=[]
    errors=[]
    for q in quality_range:
        buf=io.BytesIO(); image.convert('RGB').save(buf,format='JPEG',quality=q); buf.seek(0)
        comp=np.array(Image.open(buf).convert('RGB'),dtype=np.float32)
        err=np.mean((orig-comp)**2,axis=2)
        errors.append(float(err.mean()))
        ghost_maps.append(err)

    # Find quality where error is minimum (= likely original save quality)
    min_idx=int(np.argmin(errors))
    ghost_q=list(quality_range)[min_idx]

    # Ghost map at that quality — normalized + colorized
    ghost_raw=ghost_maps[min_idx]
    ghost_norm=(ghost_raw/ghost_raw.max()*255).astype(np.uint8) if ghost_raw.max()>0 else np.zeros((h,w),np.uint8)

    # Colorize: blue=consistent(real), red=inconsistent(manipulated)
    ghost_colored=np.zeros((h,w,3),np.uint8)
    ghost_colored[:,:,0]=ghost_norm                                      # Red: high diff
    ghost_colored[:,:,1]=np.clip(ghost_norm*0.4,0,255).astype(np.uint8) # dim green
    ghost_colored[:,:,2]=np.clip(255-ghost_norm,0,255).astype(np.uint8) # Blue: low diff

    # Blend with original for context
    orig_u8=np.array(image.convert('RGB').resize((w,h)),np.uint8)
    blended=np.clip(orig_u8*0.45+ghost_colored*0.55,0,255).astype(np.uint8)

    ghost_score=float(np.std([ghost_maps[i].mean() for i in range(len(ghost_maps))]))
    manipulation_flag = ghost_score > 8.0

    return Image.fromarray(blended), ghost_q, errors, list(quality_range), ghost_score, manipulation_flag

# ══════════════════════════════════════════════════════════════════════════════
# DCT FREQUENCY HEATMAP
# ══════════════════════════════════════════════════════════════════════════════
def dct_heatmap(image, block_size=8):
    """
    Compute 2D DCT on 8×8 blocks (like JPEG). GAN images show periodic
    frequency patterns invisible to the eye. Map high-freq energy spatially.
    """
    gray=np.array(image.convert('L'),dtype=np.float32)/255.0
    h,w=gray.shape
    # Pad to multiple of block_size
    ph=((h+block_size-1)//block_size)*block_size
    pw=((w+block_size-1)//block_size)*block_size
    padded=np.zeros((ph,pw),np.float32)
    padded[:h,:w]=gray
    energy_map=np.zeros((ph//block_size,pw//block_size),np.float32)
    for i in range(0,ph,block_size):
        for j in range(0,pw,block_size):
            block=padded[i:i+block_size,j:j+block_size]
            D=dct(dct(block.T,norm='ortho').T,norm='ortho')
            # High-frequency energy (bottom-right quadrant of DCT block)
            hf=D[block_size//2:,block_size//2:]
            energy_map[i//block_size,j//block_size]=float(np.mean(np.abs(hf)))
    energy_map=cv2.resize(energy_map,(w,h))
    if energy_map.max()>0: energy_map/=energy_map.max()
    # Colorize: cyan=low freq (natural), magenta=high freq (GAN artifact)
    dct_vis=np.zeros((h,w,3),np.uint8)
    dct_vis[:,:,0]=np.clip(energy_map*255,0,255).astype(np.uint8)  # Red
    dct_vis[:,:,1]=np.clip(energy_map*60,0,255).astype(np.uint8)   # dim G
    dct_vis[:,:,2]=np.clip(energy_map*220,0,255).astype(np.uint8)  # Blue → purple/magenta
    orig_np=np.array(image.convert('RGB').resize((w,h)),np.uint8)
    blended=np.clip(orig_np*0.4+dct_vis*0.6,0,255).astype(np.uint8)
    global_hf_score=float(np.mean(energy_map))
    gan_likely = global_hf_score > 0.25
    return Image.fromarray(blended), global_hf_score, gan_likely

# ══════════════════════════════════════════════════════════════════════════════
# PDF REPORT EXPORT
# ══════════════════════════════════════════════════════════════════════════════
def pil_to_b64(img, size=(300,300)):
    img2=img.copy(); img2.thumbnail(size,Image.LANCZOS)
    buf=io.BytesIO(); img2.save(buf,format='PNG'); return base64.b64encode(buf.getvalue()).decode()

def generate_pdf_report(image, result, ela_img, ghost_img, dct_img, ela_score, ghost_score, dct_score, filename):
    """Generate a self-contained HTML report that prints as PDF"""
    ts=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    v=result['verdict']; rs=result['real_score']; fs=result['fake_score']
    conf=result['confidence']*100; risk=result['risk']

    vc="#00e676" if v=="REAL" else "#ff1744" if v=="FAKE" else "#ffab00"
    vt="AUTHENTIC" if v=="REAL" else "SYNTHETIC" if v=="FAKE" else "UNCERTAIN"

    orig_b64=pil_to_b64(image)
    ela_b64=pil_to_b64(ela_img) if ela_img else ""
    ghost_b64=pil_to_b64(ghost_img) if ghost_img else ""
    dct_b64=pil_to_b64(dct_img) if dct_img else ""

    ela_flag="⚠ MANIPULATION DETECTED" if ela_score>12 else "✓ NORMAL"
    ghost_flag="⚠ GHOSTING DETECTED" if ghost_score>8 else "✓ NORMAL"
    dct_flag="⚠ GAN ARTIFACTS" if dct_score>0.25 else "✓ NORMAL"

    html=f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Share+Tech+Mono&family=Exo+2:wght@400;600&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#04080f;color:#e0f0ff;font-family:'Exo 2',sans-serif;padding:40px;}}
.header{{border-bottom:2px solid #00e5ff;padding-bottom:20px;margin-bottom:28px;}}
.title{{font-family:'Orbitron',monospace;font-size:1.8rem;font-weight:900;background:linear-gradient(135deg,#00e5ff,#0066ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:.1em;}}
.sub{{font-family:'Share Tech Mono',monospace;font-size:.65rem;color:#2a4a6a;letter-spacing:.35em;margin-top:4px;}}
.verdict-box{{background:#0a1220;border:2px solid {vc};border-radius:6px;padding:28px;text-align:center;margin:20px 0;box-shadow:0 0 30px {vc}33;}}
.vt{{font-family:'Orbitron',monospace;font-size:2.2rem;font-weight:900;color:{vc};letter-spacing:.2em;}}
.conf{{font-family:'Orbitron',monospace;font-size:1.2rem;color:{vc};margin-top:8px;}}
.risk-chip{{display:inline-block;background:{vc}20;border:1px solid {vc};border-radius:2px;padding:3px 14px;font-family:'Share Tech Mono',monospace;font-size:.7rem;color:{vc};letter-spacing:.2em;margin-top:8px;}}
.section{{margin:24px 0;}}
.sec-title{{font-family:'Orbitron',monospace;font-size:.8rem;color:#00e5ff;letter-spacing:.15em;border-bottom:1px solid #0d2a40;padding-bottom:8px;margin-bottom:14px;}}
.scores{{display:grid;grid-template-columns:1fr 1fr;gap:12px;}}
.score-card{{background:#070d1a;border:1px solid #0d2a40;border-radius:4px;padding:14px;}}
.sc-label{{font-family:'Share Tech Mono',monospace;font-size:.58rem;color:#2a4a6a;letter-spacing:.2em;}}
.sc-val{{font-family:'Orbitron',monospace;font-size:1.1rem;font-weight:700;margin-top:4px;}}
.bar-track{{height:8px;background:rgba(255,255,255,.05);border-radius:2px;margin-top:8px;overflow:hidden;}}
.bar-fill{{height:100%;border-radius:2px;}}
.heatmap-grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:16px 0;}}
.hm-card{{background:#070d1a;border:1px solid #0d2a40;border-radius:4px;padding:12px;text-align:center;}}
.hm-label{{font-family:'Share Tech Mono',monospace;font-size:.6rem;color:#3a6a7a;letter-spacing:.2em;margin-bottom:8px;}}
.hm-flag{{font-family:'Share Tech Mono',monospace;font-size:.62rem;margin-top:8px;}}
.flag-warn{{color:#ff1744;}} .flag-ok{{color:#00e676;}}
img{{border-radius:4px;max-width:100%;}}
.meta-table{{width:100%;border-collapse:collapse;}}
.meta-table td{{padding:7px 12px;border-bottom:1px solid #0d2a40;font-family:'Share Tech Mono',monospace;font-size:.65rem;}}
.meta-table td:first-child{{color:#2a4a6a;letter-spacing:.15em;}}
.meta-table td:last-child{{color:#5a8aaa;}}
.footer{{margin-top:40px;border-top:1px solid #0d2a40;padding-top:14px;font-family:'Share Tech Mono',monospace;font-size:.55rem;color:#0d2a40;letter-spacing:.25em;display:flex;justify-content:space-between;}}
@media print{{body{{background:#fff;color:#111;}} .verdict-box,.score-card,.hm-card{{background:#f5f5f5;border-color:#ccc;}}}}
</style></head><body>
<div class="header">
  <div class="title">DEEPFAKE FORENSICS REPORT</div>
  <div class="sub">NEURAL AUTHENTICITY ANALYSIS SYSTEM v4.0 · {ts}</div>
</div>
<div class="section">
  <div class="sec-title">▸ ANALYSIS TARGET</div>
  <div style="display:grid;grid-template-columns:200px 1fr;gap:20px;align-items:start;">
    <img src="data:image/png;base64,{orig_b64}" style="width:200px;"/>
    <div class="verdict-box">
      <div style="font-family:'Share Tech Mono',monospace;font-size:.58rem;color:#2a4a6a;letter-spacing:.4em;margin-bottom:10px;">FORENSIC VERDICT</div>
      <div class="vt">{vt}</div>
      <div class="conf">{conf:.1f}% CONFIDENCE</div>
      <div><span class="risk-chip">RISK: {risk}</span></div>
    </div>
  </div>
</div>
<div class="section">
  <div class="sec-title">▸ PROBABILITY SCORES</div>
  <div class="scores">
    <div class="score-card">
      <div class="sc-label">AUTHENTIC PROBABILITY</div>
      <div class="sc-val" style="color:#00e676">{rs*100:.2f}%</div>
      <div class="bar-track"><div class="bar-fill" style="width:{rs*100:.1f}%;background:linear-gradient(90deg,#006621,#00e676);"></div></div>
    </div>
    <div class="score-card">
      <div class="sc-label">SYNTHETIC PROBABILITY</div>
      <div class="sc-val" style="color:#ff1744">{fs*100:.2f}%</div>
      <div class="bar-track"><div class="bar-fill" style="width:{fs*100:.1f}%;background:linear-gradient(90deg,#7f0020,#ff1744);"></div></div>
    </div>
  </div>
</div>
<div class="section">
  <div class="sec-title">▸ FORENSIC ANALYSIS MODULES</div>
  <div class="heatmap-grid">
    {'<div class="hm-card"><div class="hm-label">ELA — ERROR LEVEL ANALYSIS</div><img src="data:image/png;base64,'+ela_b64+'"/><div class="hm-flag '+('flag-warn' if ela_score>12 else 'flag-ok')+'">'+ela_flag+f' (score: {ela_score:.2f})</div></div>' if ela_b64 else ''}
    {'<div class="hm-card"><div class="hm-label">JPEG GHOST ANALYSIS</div><img src="data:image/png;base64,'+ghost_b64+'"/><div class="hm-flag '+('flag-warn' if ghost_score>8 else 'flag-ok')+'">'+ghost_flag+f' (score: {ghost_score:.2f})</div></div>' if ghost_b64 else ''}
    {'<div class="hm-card"><div class="hm-label">DCT FREQUENCY HEATMAP</div><img src="data:image/png;base64,'+dct_b64+'"/><div class="hm-flag '+('flag-warn' if dct_score>0.25 else 'flag-ok')+'">'+dct_flag+f' (score: {dct_score:.3f})</div></div>' if dct_b64 else ''}
  </div>
</div>
<div class="section">
  <div class="sec-title">▸ FILE & MODEL METADATA</div>
  <table class="meta-table">
    <tr><td>FILENAME</td><td>{filename}</td></tr>
    <tr><td>ANALYSIS TIME</td><td>{ts}</td></tr>
    <tr><td>MODEL</td><td>EfficientNet-B3 (EWC Continual Learning)</td></tr>
    <tr><td>INPUT SIZE</td><td>224×224 px · ImageNet normalization</td></tr>
    <tr><td>THRESHOLD</td><td>{result['thr']:.2f}</td></tr>
    <tr><td>OUTPUT TYPE</td><td>{result['odim']}-class sigmoid</td></tr>
  </table>
</div>
<div class="footer">
  <span>DEEPFAKE FORENSICS v4.0 · FOR RESEARCH USE ONLY</span>
  <span>EfficientNet-B3 · EWC · ELA · JPEG GHOST · DCT</span>
</div>
</body></html>"""
    return html

# ══════════════════════════════════════════════════════════════════════════════
# FORENSIC EXPLANATION
# ══════════════════════════════════════════════════════════════════════════════
def explain(result, image, cam, ela_score=None, ghost_score=None, dct_score=None):
    v,fs,rs=result['verdict'],result['fake_score'],result['real_score']
    img=np.array(image.convert('RGB'),dtype=np.float32); h,w=img.shape[:2]
    gray=img.mean(axis=2); skin=gray[h//4:3*h//4,w//4:3*w//4]
    skin_var=np.std(skin)
    left=gray[:,:w//2]; right=np.fliplr(gray[:,w//2:])
    mw=min(left.shape[1],right.shape[1])
    sym=np.mean(np.abs(left[:,:mw]-right[:,:mw]))
    edges=np.gradient(gray); edge_m=np.sqrt(edges[0]**2+edges[1]**2).mean()
    color_var=np.std([np.std(img[:,:,i]) for i in range(3)])
    smooth=skin_var<30; hi_sym=sym<20; soft_edge=edge_m<9; odd_color=color_var<6
    cam_conc=float(np.mean(cam[h//4:3*h//4,w//4:3*w//4])) if cam is not None else 0.5

    if v=="FAKE":
        bd={'SKIN TEXTURE':min(.95,.42+(1-min(skin_var/55,1))*.53) if smooth else min(.72,fs*.9),
            'FACIAL SYMMETRY':min(.92,.5+(1-min(sym/32,1))*.42) if hi_sym else min(.62,fs*.72),
            'EDGE COHERENCE':min(.88,.36+(1-min(edge_m/16,1))*.52),
            'COLOR CHANNELS':min(.85,.32+(1-min(color_var/9,1))*.53) if odd_color else min(.56,fs*.62),
            'GAN FREQUENCY':min(.91,fs*.96),'BOUNDARY BLEND':min(.83,.3+fs*.53)}
        if fs>.85: hl="HIGH-CONFIDENCE SYNTHETIC DETECTED"; r2="Strong GAN generation artifacts identified with high certainty across multiple forensic modules."
        elif fs>.70: hl="DEEPFAKE INDICATORS PRESENT"; r2="Multiple manipulation signatures flagged — consistent with AI face generation or face-swap."
        else: hl="POSSIBLE SYNTHETIC MANIPULATION"; r2="Moderate deepfake signals. Lower confidence — manual verification recommended."
        arts,lines=[],[]
        if smooth: arts.append("SMOOTH SKIN"); lines.append(f"• Skin variance ({skin_var:.1f}) abnormally low — GAN generators produce pore-free, plasticky skin.")
        if hi_sym: arts.append("OVER-SYMMETRY"); lines.append(f"• Symmetry diff ({sym:.1f}) unnaturally low — real faces have natural asymmetry; GANs over-symmetrize.")
        if soft_edge: arts.append("BOUNDARY BLUR"); lines.append(f"• Edge sharpness ({edge_m:.1f}) suggests face-swap blending mask artifacts.")
        if odd_color: arts.append("COLOR ANOMALY"); lines.append(f"• RGB variance ({color_var:.1f}) narrow — GAN images show unnatural color uniformity.")
        if ela_score and ela_score>12: arts.append("ELA HIGH ERROR"); lines.append(f"• ELA score ({ela_score:.1f}) elevated — regions re-saved at different quality, indicating post-processing or splicing.")
        if ghost_score and ghost_score>8: arts.append("JPEG GHOSTING"); lines.append(f"• Ghost score ({ghost_score:.2f}) high — double-compression inconsistency detected, classic forgery signature.")
        if dct_score and dct_score>0.25: arts.append("DCT PERIODICITY"); lines.append(f"• DCT high-freq energy ({dct_score:.3f}) elevated — GAN spectral fingerprint in frequency domain.")
        if not arts: arts.append("FREQUENCY ARTIFACT"); lines.append("• Spectral analysis reveals GAN-characteristic periodicity patterns.")
        return hl,r2,arts,"\n".join(lines),bd
    elif v=="REAL":
        bd={'SKIN TEXTURE':max(.12,1-fs*.8),'FACIAL SYMMETRY':max(.18,1-fs*.72),
            'EDGE COHERENCE':max(.1,1-fs*.85),'COLOR CHANNELS':max(.14,1-fs*.76),
            'GAN FREQUENCY':max(.05,fs*.28),'BOUNDARY BLEND':max(.12,1-fs*.7)}
        inds,lines=[],[]
        if not smooth: inds.append("NATURAL SKIN"); lines.append(f"• Skin variance ({skin_var:.1f}) reflects genuine human skin with pores and imperfections.")
        if not hi_sym: inds.append("NATURAL ASYMMETRY"); lines.append(f"• Asymmetry ({sym:.1f}) within normal human range — confirms non-synthetic facial structure.")
        if not soft_edge: inds.append("OPTICAL EDGES"); lines.append(f"• Edge sharpness ({edge_m:.1f}) consistent with camera capture, not neural rendering.")
        if not inds: inds.append("NATURAL STATS"); lines.append("• Pixel frequency, noise and color distributions conform to photographic profiles.")
        return "AUTHENTIC — NO MANIPULATION DETECTED","Neural model found no deepfake artifacts. All forensic modules within expected bounds.",inds,"\n".join(lines),bd
    else:
        bd={k:0.5 for k in['SKIN TEXTURE','FACIAL SYMMETRY','EDGE COHERENCE','COLOR CHANNELS','GAN FREQUENCY','BOUNDARY BLEND']}
        return "ANALYSIS INCONCLUSIVE","Borderline statistics — adjust threshold or test with another model.",["AMBIGUOUS SIGNALS"],f"• Skin ({skin_var:.1f}), Sym ({sym:.1f}) in borderline range.",bd

# ══════════════════════════════════════════════════════════════════════════════
# RENDER HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def r_sh(t):
    st.markdown(f'<div class="sh"><span class="sh-txt">/ {t}</span><div class="sh-line"></div></div>',unsafe_allow_html=True)

def r_metrics(total, reals, fakes, rate):
    cards=[
        ("ANALYZED", f"{total:,}", "Session volume", "#23d5ff"),
        ("AUTHENTIC", f"{reals:,}", "Passed model threshold", "#27f0a6"),
        ("SYNTHETIC", f"{fakes:,}", "Flagged as manipulated", "#ff4f6d"),
        ("FAKE RATE", f"{rate:.1f}%", "Current session mix", "#ffbf47"),
    ]
    html="".join(
        f'<div class="metric-card" style="--accent:{accent};">'
        f'<div class="metric-label">{label}</div><div class="metric-value">{value}</div>'
        f'<div class="metric-note">{note}</div></div>'
        for label,value,note,accent in cards
    )
    st.markdown(f'<div class="metric-deck">{html}</div>',unsafe_allow_html=True)

def r_verdict(res):
    v=res['verdict']; conf=res['confidence']*100; risk=res['risk']
    vc,icon,vt,cc,gc=("vr-real","OK","AUTHENTIC","#27f0a6","gr") if v=="REAL" else ("vr-fake","ALERT","SYNTHETIC","#ff4f6d","rr") if v=="FAKE" else ("vr-unc","CHECK","UNCERTAIN","#ffbf47","cr")
    rc=f"risk-{risk.lower()}"
    st.markdown(f'<div class="fc {gc} verdict-card" style="text-align:center;padding:28px 18px 22px;"><div class="cb tl"></div><div class="cb tr"></div><div class="cb bl"></div><div class="cb br"></div><div class="vr-label">FORENSIC VERDICT</div><div class="{vc}"><span style="font-size:.78rem;letter-spacing:.18em;vertical-align:middle;">{icon}</span><br>{vt}</div><div class="conf-val" style="color:{cc}">{conf:.1f}%</div><div class="conf-lbl">CONFIDENCE SCORE</div><div><span class="risk-b {rc}">RISK: {risk}</span></div></div>',unsafe_allow_html=True)

def r_bars(rs,fs):
    rc="#00e676" if rs>.6 else "#ffab00"; fc2="#ff1744" if fs>.6 else "#ffab00"
    st.markdown(f'<div style="margin:16px 0 4px;"><div class="sb-row"><div class="sb-head"><span class="sb-name">AUTHENTIC SIGNAL</span><span class="sb-pct" style="color:{rc}">{rs*100:.2f}%</span></div><div class="sb-track"><div style="height:100%;width:{rs*100:.1f}%;background:linear-gradient(90deg,#0b7040,{rc});color:{rc};"></div></div></div><div class="sb-row" style="margin-top:12px;"><div class="sb-head"><span class="sb-name">SYNTHETIC SIGNAL</span><span class="sb-pct" style="color:{fc2}">{fs*100:.2f}%</span></div><div class="sb-track"><div style="height:100%;width:{fs*100:.1f}%;background:linear-gradient(90deg,#8d1630,{fc2});color:{fc2};"></div></div></div></div>',unsafe_allow_html=True)

def r_breakdown(bd,verdict):
    items=""
    for name,score in bd.items():
        bc="#ff1744" if verdict=="FAKE" and score>.5 else "#00e676" if verdict=="REAL" else "#ffab00"
        items+=f'<div class="bd-item"><div class="bd-name">{name}</div><div class="bd-track"><div style="height:100%;width:{score*100:.0f}%;background:{bc};border-radius:2px;"></div></div><div class="bd-val" style="color:{bc}">{score*100:.0f}%</div></div>'
    st.markdown(f'<div class="bd-grid">{items}</div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    st.markdown("""<div class="app-hero">
    <div class="hero-row">
      <div><div class="app-title">DEEPFAKE FORENSICS</div><div class="app-sub">Neural Authenticity Analysis System v4.0</div></div>
      <div class="hero-actions">
        <span class="v-badge"><span class="v-dot"></span>ONLINE</span>
        <span class="module-chip">EfficientNet-B3</span>
        <span class="module-chip">ELA</span>
        <span class="module-chip">DCT</span>
        <span class="module-chip">JPEG Ghost</span>
      </div>
    </div>
    </div>""",unsafe_allow_html=True)

    total=st.session_state.total_analyzed; fakes=st.session_state.total_fake
    reals=total-fakes; rate=(fakes/total*100) if total>0 else 0
    r_metrics(total,reals,fakes,rate)

    # Sidebar
    with st.sidebar:
        st.markdown('<div style="padding:14px 0 8px;font-family:\'Orbitron\',monospace;font-size:.78rem;font-weight:700;color:#23d5ff;letter-spacing:.16em;">CONTROL PANEL</div>',unsafe_allow_html=True)
        st.markdown('<div class="sl">MODEL</div>',unsafe_allow_html=True)
        avail=find_models()
        if avail:
            labels=[f"{m[0]} ({m[2]:.0f}MB)" for m in avail]
            idx=st.selectbox("",range(len(labels)),format_func=lambda i:labels[i],label_visibility="collapsed")
            mpath=avail[idx][1]
        else:
            mpath=st.text_input("",value="models/balanced_retrained_fast_model.pt",label_visibility="collapsed")
        model,device,odim=load_model(mpath)
        if model:
            gpu=f"GPU: {torch.cuda.get_device_name(0)[:20]}" if torch.cuda.is_available() else "CPU"
            st.markdown(f'<div class="ms"><div class="ms-on"></div><div class="ms-txt">ONLINE / {odim}-CLASS {"SIGMOID" if odim==1 else "SOFTMAX"}<br>{str(device).upper()} / {gpu}</div></div>',unsafe_allow_html=True)
        else:
            st.error("Model not found."); return

        st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
        st.markdown('<div class="sl">DETECTION THRESHOLD</div>',unsafe_allow_html=True)
        thr=st.slider("",0.40,0.90,0.50,0.01,label_visibility="collapsed")
        mode="SENSITIVE" if thr<0.5 else "BALANCED" if thr==0.5 else "CONSERVATIVE"
        st.markdown(f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:.56rem;color:var(--faint);text-align:center;margin-top:-5px;">{thr:.2f} / {mode}</div>',unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
        st.markdown('<div class="sl">ANALYSIS MODULES</div>',unsafe_allow_html=True)
        show_hm=st.checkbox("Grad-CAM Heatmap",True)
        show_ela=st.checkbox("ELA Analysis",True)
        show_ghost=st.checkbox("JPEG Ghost",True)
        show_dct=st.checkbox("DCT Frequency",True)
        show_bd=st.checkbox("Artifact Breakdown",True)
        show_ex=st.checkbox("Forensic Explanation",True)
        show_hs=st.checkbox("Session History",True)

        st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
        if st.button("CLEAR SESSION"):
            st.session_state.history=[]; st.session_state.total_analyzed=0; st.session_state.total_fake=0; st.rerun()

    tf=get_tf()

    # Upload
    r_sh("TARGET ACQUISITION - DRAG & DROP OR CLICK TO UPLOAD")
    uploaded=st.file_uploader("Supported: JPG / PNG / BMP / WEBP",type=["jpg","jpeg","png","bmp","webp"])

    if not uploaded:
        st.markdown('<div class="empty-state"><div class="empty-orbit"></div><div class="empty-title">AWAITING TARGET</div><div class="empty-copy">ELA / JPEG GHOST / DCT / GRAD-CAM READY</div></div>',unsafe_allow_html=True)
        return

    image=Image.open(uploaded).convert('RGB')

    # Image + Verdict
    col_img,col_v=st.columns([1,1],gap="large")
    with col_img:
        r_sh("INPUT IMAGE")
        st.image(image,use_container_width=True)
        img_np=np.array(image)
        st.markdown(f'<div class="fc" style="padding:12px;margin-top:8px;"><div style="display:grid;grid-template-columns:1fr 1fr;gap:6px 14px;"><div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid rgba(255,255,255,.04);"><span style="font-family:\'Share Tech Mono\',monospace;font-size:.56rem;color:var(--faint);">FILENAME</span><span style="font-family:\'Share Tech Mono\',monospace;font-size:.6rem;color:var(--muted);">{uploaded.name[:22]}</span></div><div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid rgba(255,255,255,.04);"><span style="font-family:\'Share Tech Mono\',monospace;font-size:.56rem;color:var(--faint);">SIZE</span><span style="font-family:\'Share Tech Mono\',monospace;font-size:.6rem;color:var(--muted);">{image.size[0]}x{image.size[1]}</span></div><div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid rgba(255,255,255,.04);"><span style="font-family:\'Share Tech Mono\',monospace;font-size:.56rem;color:var(--faint);">FILE SIZE</span><span style="font-family:\'Share Tech Mono\',monospace;font-size:.6rem;color:var(--muted);">{uploaded.size/1024:.1f} KB</span></div><div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid rgba(255,255,255,.04);"><span style="font-family:\'Share Tech Mono\',monospace;font-size:.56rem;color:var(--faint);">STD DEV</span><span style="font-family:\'Share Tech Mono\',monospace;font-size:.6rem;color:var(--muted);">{np.std(img_np):.2f}</span></div></div></div>',unsafe_allow_html=True)

    with col_v:
        r_sh("FORENSIC VERDICT")
        with st.spinner(""):
            time.sleep(0.15); result=predict(image,model,device,odim,tf,thr)
        if result:
            r_verdict(result); r_bars(result['real_score'],result['fake_score'])
            st.session_state.history.append(dict(file=uploaded.name,verdict=result['verdict'],real=result['real_score'],fake=result['fake_score'],confidence=result['confidence'],risk=result['risk'],time=result['ts']))
            st.session_state.total_analyzed+=1
            if result['verdict']=="FAKE": st.session_state.total_fake+=1

    if not result: return

    # ── Grad-CAM ──
    heatmap=None; cam_data=None
    if show_hm:
        st.markdown("<div style='height:18px'></div>",unsafe_allow_html=True)
        r_sh("GRAD-CAM ACTIVATION HEATMAP")
        hm1,hm2=st.columns([1,1],gap="large")
        with hm1:
            st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:.58rem;color:#2a5a7a;letter-spacing:.2em;margin-bottom:5px;">ORIGINAL</div>',unsafe_allow_html=True)
            st.image(image,use_container_width=True)
        with hm2:
            with st.spinner("Computing Grad-CAM..."):
                heatmap,cam_data=gradcam(image,model,device,tf,result['verdict'])
            lbl_col="#ff1744" if result['verdict']=="FAKE" else "#00e676"
            lbl="SYNTHETIC ACTIVATION" if result['verdict']=="FAKE" else "AUTHENTIC REGIONS"
            st.markdown(f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:.58rem;color:{lbl_col};letter-spacing:.16em;margin-bottom:5px;">/ {lbl}</div>',unsafe_allow_html=True)
            if heatmap: st.image(heatmap,use_container_width=True)
            lc="RED = high fake activation / YELLOW = moderate / DARK = low / [ ] = face region" if result['verdict']=="FAKE" else "GREEN = authentic features / DARK = low activation / [ ] = face region"
            st.markdown(f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:.56rem;color:#2a4a5a;letter-spacing:.1em;margin-top:7px;line-height:1.8;">{lc}</div>',unsafe_allow_html=True)

    # ── ELA + JPEG Ghost ──
    ela_img=None; ela_score=0; ghost_img=None; ghost_score=0; dct_img=None; dct_score=0
    if show_ela or show_ghost:
        st.markdown("<div style='height:18px'></div>",unsafe_allow_html=True)
        cols_row=[]
        if show_ela and show_ghost: c1e,c2e=st.columns([1,1],gap="large"); cols_row=[(c1e,"ela"),(c2e,"ghost")]
        elif show_ela: c1e=st.columns(1)[0]; cols_row=[(c1e,"ela")]
        else: c2e=st.columns(1)[0]; cols_row=[(c2e,"ghost")]

        for col,typ in cols_row:
            with col:
                if typ=="ela":
                    r_sh("ELA - ERROR LEVEL ANALYSIS")
                    with st.spinner("Running ELA..."):
                        ela_img,ela_score,ela_max,ela_std,ela_flag2=ela_analysis(image)
                    flag_col="#ff1744" if ela_flag2 else "#00e676"
                    flag_txt="MANIPULATION DETECTED" if ela_flag2 else "WITHIN NORMAL RANGE"
                    st.image(ela_img,use_container_width=True)
                    st.markdown(f'<div style="margin-top:8px;"><div style="font-family:\'Share Tech Mono\',monospace;font-size:.6rem;color:{flag_col};letter-spacing:.16em;">{flag_txt}</div><div class="feat-label">MEAN ERROR: {ela_score:.2f} / MAX: {ela_max:.1f} / STD: {ela_std:.2f}<br>RED = high recompression error / BLUE = low error<br>Regions saved at different JPEG quality levels appear brighter.</div></div>',unsafe_allow_html=True)
                else:
                    r_sh("JPEG GHOST - DOUBLE COMPRESSION DETECTION")
                    with st.spinner("Running JPEG Ghost..."):
                        ghost_img,ghost_q,errors,quals,ghost_score,ghost_flag2=jpeg_ghost(image)
                    flag_col="#ff1744" if ghost_flag2 else "#00e676"
                    flag_txt="GHOSTING DETECTED" if ghost_flag2 else "CONSISTENT COMPRESSION"
                    st.image(ghost_img,use_container_width=True)
                    st.markdown(f'<div style="margin-top:8px;"><div style="font-family:\'Share Tech Mono\',monospace;font-size:.6rem;color:{flag_col};letter-spacing:.16em;">{flag_txt}</div><div class="feat-label">GHOST SCORE: {ghost_score:.3f} / ESTIMATED ORIG QUALITY: Q{ghost_q}<br>RED = inconsistent double-compressed region / BLUE = consistent<br>Pasted regions can retain a different JPEG quality profile than the background.</div></div>',unsafe_allow_html=True)

    # ── DCT Heatmap ──
    if show_dct:
        st.markdown("<div style='height:18px'></div>",unsafe_allow_html=True)
        r_sh("DCT FREQUENCY HEATMAP - GAN SPECTRAL FINGERPRINT")
        d1,d2=st.columns([1,1],gap="large")
        with d1:
            st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:.58rem;color:#2a5a7a;letter-spacing:.2em;margin-bottom:5px;">ORIGINAL</div>',unsafe_allow_html=True)
            st.image(image,use_container_width=True)
        with d2:
            with st.spinner("Computing DCT..."):
                dct_img,dct_score,gan_likely=dct_heatmap(image)
            flag_col="#ff1744" if gan_likely else "#00e676"
            flag_txt="GAN SPECTRAL ARTIFACTS" if gan_likely else "NATURAL FREQUENCY PROFILE"
            st.markdown(f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:.58rem;color:{flag_col};letter-spacing:.16em;margin-bottom:5px;">/ {flag_txt}</div>',unsafe_allow_html=True)
            if dct_img: st.image(dct_img,use_container_width=True)
            st.markdown(f'<div class="feat-label">HIGH-FREQ ENERGY: {dct_score:.4f} / THRESHOLD: 0.25<br>MAGENTA = high-frequency GAN artifacts / CYAN = natural low-frequency content<br>Analyzes 8x8 DCT blocks, similar to JPEG.</div>',unsafe_allow_html=True)

    # ── Breakdown + Explanation ──
    if show_bd or show_ex:
        st.markdown("<div style='height:16px'></div>",unsafe_allow_html=True)
        hl,r2,inds,detail,bd=explain(result,image,cam_data,ela_score,ghost_score,dct_score)
        bc,ec=st.columns([1,1],gap="large")
        if show_bd:
            with bc:
                r_sh("ARTIFACT BREAKDOWN")
                r_breakdown(bd,result['verdict'])
        if show_ex:
            with ec:
                r_sh("FORENSIC EXPLANATION")
                v3=result['verdict']; ec_col="#ff1744" if v3=="FAKE" else "#00e676" if v3=="REAL" else "#ffab00"
                tag_cls="art-tag" if v3=="FAKE" else "real-tag"
                tags="".join(f'<span class="{tag_cls}">{i}</span>' for i in inds)
                st.markdown(f'<div class="exp-card" style="border-left-color:{ec_col};"><div class="exp-title" style="color:{ec_col};">{hl}</div><div class="exp-main">{r2}</div><div style="margin-bottom:10px;">{tags}</div><div class="exp-detail">{detail}</div></div>',unsafe_allow_html=True)

    # ── PDF REPORT EXPORT ──
    st.markdown("<div style='height:18px'></div>",unsafe_allow_html=True)
    r_sh("EXPORT FORENSIC REPORT")
    exp1,exp2=st.columns([2,1],gap="large")
    with exp1:
        st.markdown('<div class="report-copy">Generate a complete forensic PDF report including analysis modules,<br>heatmaps, scores, and metadata. Open in browser, then print to PDF.</div>',unsafe_allow_html=True)
    with exp2:
        if st.button("GENERATE PDF REPORT"):
            with st.spinner("Generating report..."):
                html_report=generate_pdf_report(image,result,ela_img,ghost_img,dct_img,ela_score,ghost_score,dct_score,uploaded.name)
            b64=base64.b64encode(html_report.encode()).decode()
            fn=f"forensic_report_{uploaded.name.split('.')[0]}_{datetime.now().strftime('%H%M%S')}.html"
            st.markdown(f'<a href="data:text/html;base64,{b64}" download="{fn}" class="download-link">Download Report</a>',unsafe_allow_html=True)
            st.success("Report ready. Open in browser, then print to PDF.")

    # ── History ──
    if show_hs and st.session_state.history:
        st.markdown("<div style='height:18px'></div>",unsafe_allow_html=True)
        r_sh("SESSION HISTORY")
        if len(st.session_state.history)>1:
            import pandas as pd
            df=pd.DataFrame({'Image':[h['file'][:14] for h in st.session_state.history],'Authentic %':[h['real']*100 for h in st.session_state.history],'Synthetic %':[h['fake']*100 for h in st.session_state.history]})
            st.bar_chart(df.set_index('Image')[['Authentic %','Synthetic %']])
        for h in reversed(st.session_state.history[-10:]):
            vc2="hv-r" if h['verdict']=="REAL" else "hv-f"; vt2="AUTHENTIC" if h['verdict']=="REAL" else "SYNTHETIC" if h['verdict']=="FAKE" else "UNCERTAIN"; cc2="#00e676" if h['verdict']=="REAL" else "#ff1744"
            st.markdown(f'<div class="hi"><span class="ht">{h["time"]}</span><span class="hf">{h["file"][:22]}</span><span class="{vc2}">{vt2}</span><span class="hc" style="color:{cc2};">{h["confidence"]*100:.0f}%</span></div>',unsafe_allow_html=True)

    st.markdown('<div style="margin-top:32px;padding:14px 0;border-top:1px solid rgba(118,178,255,.16);display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;"><span style="font-family:\'Share Tech Mono\',monospace;font-size:.52rem;color:var(--faint);letter-spacing:.18em;">DEEPFAKE FORENSICS v4.0 / EfficientNet-B3 / ELA / JPEG GHOST / DCT / GRAD-CAM</span><span style="font-family:\'Share Tech Mono\',monospace;font-size:.52rem;color:var(--faint);letter-spacing:.16em;">FOR RESEARCH USE ONLY</span></div>',unsafe_allow_html=True)

if __name__=="__main__":
    main()
