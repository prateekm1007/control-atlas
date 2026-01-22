import streamlit as st
import requests, os, base64, json
import streamlit.components.v1 as components

st.set_page_config(page_title="Toscanini Forensic Pad", layout="wide")
backend_url = os.getenv("BACKEND_URL", "http://api:8000")

LAW_DESC = {"LAW-155": "Atoms cannot overlap overlapping space.", "LAW-160": "Backbone continuity failure.", "LAW-162": "H-Bond saturation failure."}
SCORE_HELP = "### Score Tiers\n- **>85%:** Pristine\n- **70-85%:** Marginal\n- **<30%:** Vetoed"

if "audit_result" not in st.session_state: st.session_state.audit_result = None
if "teleport_coords" not in st.session_state: st.session_state.teleport_coords = None

st.title("🛡️ TOSCANINI // FORENSIC STATION")
st.caption("v10.3.7 Hardened Apex | Full Manifest Restoration COMPLETE")

with st.sidebar:
    st.header("📉 NKG Intelligence")
    try:
        s_res = requests.get(f"{backend_url}/api/v1/nkg/stats").json()
        st.metric("Forbidden PIUs", s_res.get("unique_pius", 0))
        if s_res.get("model_fingerprints"): st.bar_chart(s_res["model_fingerprints"])
    except: st.write("NKG Offline")
    if st.button("🔄 New Audit"):
        st.session_state.audit_result = None; st.rerun()

cola, colb = st.columns([2, 1])
with cola: uploaded_file = st.file_uploader("Upload Structure", type=["pdb", "cif"])
with colb: gen_choice = st.selectbox("Generator", ["AlphaFold3", "RFdiffusion", "Chai-1", "Other"])

if uploaded_file:
    with st.spinner("Compiling Forensic Decision..."):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        res = requests.post(f"{backend_url}/api/v1/audit/upload", files=files, data={"generator": gen_choice}).json()
        st.session_state.audit_result = res

res = st.session_state.audit_result
if res and res.get("verdict") != "ERROR":
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("SOVEREIGNTY SCORE", f"{res.get('score', 0)}%", help=SCORE_HELP)
        v_type = {"PASS":"success", "WARNING":"warning", "VETO":"error"}.get(res['verdict'], "info")
        getattr(st, v_type)(f"VERDICT: {res['verdict']}")
        st.subheader("Causal Rationale")
        st.write(res.get("narrative"))
        st.subheader("Diagnostic Ledger")
        for law in res.get("laws", []):
            lid, lstat = law['law_id'], law['status']
            with st.expander(f"{lid}: {lstat}"):
                st.write(f"Confidence: {law.get('conf')}")
                st.write(f"Observed: {law.get('measurement')}")
                if st.button("ℹ️ Explain Law", key=f"ex-{lid}"): st.info(LAW_DESC.get(lid))
        if res.get("pdf_b64"):
            st.download_button("📄 Download Certificate", base64.b64decode(res["pdf_b64"]), file_name=f"decision_{res['sig']}.pdf", mime="application/pdf")
    with col2:
        if "pdb_b64" in res:
            html_code = f"<div id='viz' style='height: 520px; width: 100%; background-color: #070b14; border-radius: 12px;'></div><script src='https://3Dmol.org/build/3Dmol-min.js'></script><script>(function() {{ const viewer = $3Dmol.createViewer(document.getElementById('viz'), {{backgroundColor: '#070b14'}}); viewer.addModel(atob('{res['pdb_b64']}'), '{res['ext']}'); viewer.setStyle({{}}, {{cartoon: {{colorscheme: {{prop:'b', gradient: 'rwb', min:50, max:90}}}}}}); viewer.render(); setInterval(() => {{ viewer.rotate(0.5, 'y'); }}, 50); }})();</script>"
            components.html(html_code, height=540)
elif res: st.error(f"Brain Error: {res.get('details')}")
