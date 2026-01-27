import streamlit as st
import requests, base64, json, os
import streamlit.components.v1 as components

st.set_page_config(page_title="Toscanini Forensic Pad", layout="wide")

# v13.1.5: Using the service name 'brain' but wrapped in a retry-handler
backend_url = os.getenv("BACKEND_URL", "http://brain:8000")

st.title("🛡️ TOSCANINI // FORENSIC STATION")
st.caption("v13.1.5 Cloud Hardened | Handshake: SOVEREIGN")

if "audit_result" not in st.session_state: st.session_state.audit_result = None

with st.sidebar:
    st.header("📉 NKG Intelligence")
    try:
        # HEARTBEAT CHECK
        s_res = requests.get(f"{backend_url}/stats", timeout=5).json()
        st.metric("Forbidden Motifs", s_res.get("unique_pius", 0))
        st.success("Brain Connection: ONLINE")
    except:
        st.error("🔄 Connecting to Brain Engine...")
        st.caption(f"Status: Waiting for internal DNS to resolve '{backend_url}'")

uploaded_file = st.file_uploader("Upload Structure", type=["pdb", "cif"])
gen_choice = st.sidebar.selectbox("Generator", ["AlphaFold3", "RFdiffusion", "Chai-1"])

if uploaded_file:
    if st.session_state.audit_result is None or st.session_state.get("last_file") != uploaded_file.name:
        with st.spinner("Compiling Forensic Decision..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                # RELAXED TIMEOUT FOR CLOUD COLD-START
                res = requests.post(f"{backend_url}/audit", files=files, data={"generator": gen_choice}, timeout=45).json()
                st.session_state.audit_result = res
                st.session_state.last_file = uploaded_file.name
            except Exception as e:
                st.error(f"Handshake Failed: {e}")

res = st.session_state.audit_result
if res and res.get("verdict") != "ERROR":
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("SOVEREIGNTY SCORE", f"{res.get('score', 0)}%", help=">85% Pristine")
        st.write(f"**Interpretation:** {res.get('narrative')}")
        if res.get("pdf_b64"):
            st.download_button("📄 Download Certificate", base64.b64decode(res["pdf_b64"]), file_name="verdict.pdf")
        st.subheader("Ledger")
        for l in res['laws']:
            with st.expander(f"⚖️ {l['law_id']}: {l['status']}"):
                st.write(f"Observed: {l['measurement']}")
                if st.button("ℹ️ Explain", key=f"btn-{l['law_id']}"):
                    exp = requests.get(f"{backend_url}/explain/{l['law_id']}").json()
                    st.info(f"**{l.get('title')}**\n\n{l.get('principle')}\n\n{l.get('rationale')}")
    with col2:
        if "pdb_b64" in res:
            html = f"<div id='viz' style='height: 520px; width: 100%; background-color: #070b14; border-radius: 12px;'></div><script src='https://3Dmol.org/build/3Dmol-min.js'></script><script>function startViewer() {{ const container = document.getElementById('viz'); if (typeof $3Dmol === 'undefined') {{ setTimeout(startViewer, 100); return; }} const viewer = $3Dmol.createViewer(container, {{backgroundColor:'#070b14'}}); viewer.addModel(atob('{res['pdb_b64']}'), '{res['ext']}'); viewer.setStyle({{}}, {{cartoon:{{colorscheme:{{prop:'b',gradient:'rwb',min:50,max:90}}}}}}); viewer.zoomTo(); viewer.render(); setInterval(()=>{{ viewer.rotate(0.5, 'y'); }}, 50); }} startViewer();</script>"
            components.html(html, height=620)
