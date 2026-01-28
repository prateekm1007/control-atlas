import streamlit as st
import requests, base64, json, os
import streamlit.components.v1 as components
st.set_page_config(page_title="Toscanini", layout="wide")
backend_url = "http://brain:8000"
st.title("🛡️ TOSCANINI // FORENSIC STATION")
if "audit_result" not in st.session_state: st.session_state.audit_result = None
if "tel_coords" not in st.session_state: st.session_state.tel_coords = None

with st.sidebar:
    st.header("📉 NKG Intelligence")
    try:
        s = requests.get(f"{backend_url}/stats", timeout=3).json()
        st.metric("Forbidden Motifs", s.get("unique_pius", 0))
        st.success("Brain: ONLINE")
    except: st.error("Brain: CONNECTING...")

uploaded_file = st.file_uploader("Upload Structure")
gen_choice = st.sidebar.selectbox("Generator", ["AlphaFold3", "RFdiffusion", "Chai-1"])

if uploaded_file:
    if st.session_state.audit_result is None or st.session_state.get("last") != uploaded_file.name:
        with st.spinner("Compiling Forensic Decision..."):
            try:
                res = requests.post(f"{backend_url}/audit", files={"file": (uploaded_file.name, uploaded_file.getvalue())}, data={"generator": gen_choice}, timeout=30).json()
                st.session_state.audit_result, st.session_state.last = res, uploaded_file.name
            except Exception as e: st.error(f"Handshake Failed: {e}")

res = st.session_state.audit_result
if res and res.get("verdict") != "ERROR":
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("SCORE", f"{res['score']}%")
        st.write(f"Interpretation: {res['narrative']}")
        if res.get("pdf_b64"): st.download_button("📄 Download Certificate", base64.b64decode(res["pdf_b64"]), file_name="cert.pdf")
        st.subheader("Diagnostic Ledger")
        for l in res['laws']:
            with st.expander(f"⚖️ {l['law_id']}"):
                st.write(f"Observed: {l['measurement']}")
                if st.button("ℹ️ Explain", key=f"ex-{l['law_id']}"): st.info(f"**{l['principle']}**\n\n{l['rationale']}")
    with col2:
        if "pdb_b64" in res:
            html = f"<div id='v' style='height:520px;width:100%;background:#070b14'></div><script src='https://3Dmol.org/build/3Dmol-min.js'></script><script>function startViewer() {{ if (typeof $3Dmol === 'undefined') {{ setTimeout(startViewer, 100); return; }} const v = $3Dmol.createViewer(document.getElementById('v'), {{backgroundColor:'#070b14'}}); v.addModel(atob('{res['pdb_b64']}'), '{res['ext']}'); v.setStyle({{}}, {{cartoon:{{colorscheme:{{prop:'b',gradient:'rwb',min:50,max:90}}}}}}); v.render(); setInterval(()=>{{ v.rotate(0.5, 'y'); }}, 50); }} startViewer();</script>"
            components.html(html, height=620)
