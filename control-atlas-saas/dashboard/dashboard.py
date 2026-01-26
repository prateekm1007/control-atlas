import streamlit as st
import requests, base64, json, os
import streamlit.components.v1 as components

st.set_page_config(page_title="Toscanini Forensic Pad", layout="wide")
# WELD: Pointing to the hard-linked name 'brain'
backend_url = "http://brain:8000"

st.title("🛡️ TOSCANINI // FORENSIC STATION")
st.caption("v12.0.4 Network Welded | Handshake: IMMUTABLE")

if "audit_result" not in st.session_state: st.session_state.audit_result = None

with st.sidebar:
    st.header("📉 NKG Intelligence")
    try:
        s_res = requests.get(f"{backend_url}/stats", timeout=3).json()
        st.metric("Forbidden Motifs", s_res.get("unique_pius", 0))
        st.success("Brain Connection: ONLINE")
    except:
        st.error("🔄 Connecting...")

uploaded_file = st.file_uploader("Upload Structure", type=["pdb", "cif"])
if uploaded_file:
    if "audit_result" not in st.session_state or st.session_state.get("file_id") != uploaded_file.name:
        with st.spinner("Executing Physics..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                res = requests.post(f"{backend_url}/audit", files=files, data={"generator": "AF3"}, timeout=20).json()
                st.session_state.audit_result = res
                st.session_state.file_id = uploaded_file.name
            except Exception as e:
                st.error(f"Weld Break: {e}")

res = st.session_state.audit_result
if res:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("SOVEREIGNTY SCORE", f"{res['score']}%")
        for l in res['laws']:
            with st.expander(f"{l['law_id']}"):
                st.write(f"Status: {l['status']}")
                if st.button("ℹ️ Explain", key=l['law_id']):
                    exp = requests.get(f"{backend_url}/explain/{l['law_id']}").json()
                    st.info(f"{exp['title']}: {exp['summary']}")
    with col2:
        if "pdb_b64" in res:
            html = f"<div id='viz' style='height: 520px; width: 100%; background-color: #070b14; border-radius: 12px;'></div><script src='https://3Dmol.org/build/3Dmol-min.js'></script><script>(function() {{ const v = $3Dmol.createViewer(document.getElementById('viz'), {{backgroundColor:'#070b14'}}); v.addModel(atob('{res['pdb_b64']}'), 'pdb'); v.setStyle({{}}, {{cartoon:{{colorscheme:{{prop:'b',gradient:'rwb',min:50,max:90}}}}}}); v.zoomTo(); v.render(); setInterval(()=>v.rotate(0.5,'y'),50); }})();</script>"
            components.html(html, height=620)
