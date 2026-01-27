import streamlit as st
import requests, base64, json, os
import streamlit.components.v1 as components

st.set_page_config(page_title="Toscanini", layout="wide")
backend_url = os.getenv("BACKEND_URL", "http://brain:8000")

st.title("🛡️ TOSCANINI // FORENSIC STATION")
st.caption("v13.16.1 Cloud-Safe JSON Guard")

if "audit_result" not in st.session_state:
    st.session_state.audit_result = None

with st.sidebar:
    st.header("📉 NKG Intelligence")
    try:
        s = requests.get(f"{backend_url}/stats", timeout=5)
        st.metric("Forbidden Motifs", s.json().get("unique_pius", 0))
        st.success("Brain: ONLINE")
    except:
        st.error("Brain unreachable")

uploaded_file = st.file_uploader("Upload Structure", type=["pdb","cif"])

if uploaded_file:
    with st.spinner("Compiling Forensic Decision..."):
        try:
            r = requests.post(
                f"{backend_url}/audit",
                files={"file": (uploaded_file.name, uploaded_file.getvalue())},
                data={"generator": "AF3"},
                timeout=60
            )
            if not r.text.strip():
                st.error("Empty response from Brain")
            else:
                st.session_state.audit_result = r.json()
        except Exception as e:
            st.error(f"Handshake Failed: {e}")

res = st.session_state.audit_result
if res and res.get("verdict") == "PASS":
    col1, col2 = st.columns([1,2])
    with col1:
        st.metric("SCORE", f"{res.get('score')}%")
        st.write(res.get("narrative"))
        if res.get("pdf_b64"):
            st.download_button(
                "📄 Download Certificate",
                base64.b64decode(res["pdf_b64"]),
                file_name="certificate.pdf"
            )
    with col2:
        if res.get("pdb_b64"):
            html = f"<div id='v' style='height:520px;width:100%;background:#070b14'></div><script src='https://3Dmol.org/build/3Dmol-min.js'></script><script>const v=$3Dmol.createViewer(document.getElementById('v'),{{backgroundColor:'#070b14'}});v.addModel(atob('{res['pdb_b64']}'),'pdb');v.setStyle({{}},{{cartoon:{{colorscheme:'spectrum'}}}});v.zoomTo();v.render();</script>"
            components.html(html, height=620)
