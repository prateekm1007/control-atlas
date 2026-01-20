import streamlit as st
import requests
import os
import base64
import streamlit.components.v1 as components

st.set_page_config(page_title="Toscanini Forensic Pad", layout="wide")

st.markdown("""<style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stMetric { background-color: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155; }
    .risk-box { background-color: #450a0a; padding: 20px; border-radius: 10px; border: 1px solid #ef4444; color: #fecaca; margin-bottom: 20px;}
    </style>""", unsafe_allow_html=True)

backend_url = os.getenv("BACKEND_URL", "http://api:8000")

# --- v9.4.7 STATE HANDSHAKE ---
if "audit_result" not in st.session_state: st.session_state.audit_result = None
if "current_file_id" not in st.session_state: st.session_state.current_file_id = None

st.title("🛡️ TOSCANINI // FORENSIC STATION")
st.caption("v9.4.7 Stable Beta-Lite | State-Sync: ACTIVE")

with st.sidebar:
    st.header("📉 Negative Knowledge Graph")
    try:
        stats = requests.get(f"{backend_url}/api/v1/nkg/stats").json()
        st.metric("Unique Physical Vetoes", stats.get("total_vetoes", 0))
    except: st.write("NKG Offline")
    
    # MANUAL RESET
    if st.button("🔄 New Audit", use_container_width=True):
        st.session_state.audit_result = None
        st.session_state.current_file_id = None
        st.rerun()

uploaded_file = st.file_uploader("Upload Protein Design (.pdb / .cif)", type=["pdb", "cif"])

if uploaded_file:
    # Identify the file based on name and size
    file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    
    # TRIGGER: If the file ID changed, clear old result and run new audit
    if st.session_state.current_file_id != file_id:
        with st.spinner("Executing Physics Sieve..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            try:
                response = requests.post(f"{backend_url}/api/v1/audit/upload", files=files)
                st.session_state.audit_result = response.json()
                st.session_state.current_file_id = file_id
            except Exception as e:
                st.error(f"Brain Offline: {e}")

# RENDER
res = st.session_state.audit_result
if res:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("SOVEREIGNTY SCORE", f"{res.get('score', 0)}%")
        verdict = res.get('verdict', 'ERROR')
        if verdict == "PASS": st.success("VERDICT: PASS")
        elif verdict == "VETO": st.error("VERDICT: VETO")
        else: st.warning(f"VERDICT: {verdict}")
        
        st.info(res.get("details", "No forensic details available."))
        
        if res.get("pdf_b64") and verdict != "ERROR":
            st.download_button("📄 Download Official Certificate", 
                               base64.b64decode(res["pdf_b64"]), 
                               file_name=f"verdict_{res.get('sig', 'job')}.pdf",
                               mime="application/pdf",
                               use_container_width=True)

    with col2:
        if res.get("pdb_b64"):
            container_id = f"viz-{res.get('sig', 'main')}"
            clash_js = ""
            if res.get('clash_metadata'):
                c1, c2 = res['clash_metadata']['c1'], res['clash_metadata']['c2']
                clash_js = f"viewer.setStyle({{chain:'{c1['chain']}',resi:{c1['res']}}},{{sphere:{{color:'red',radius:1.5}}}}); viewer.setStyle({{chain:'{c2['chain']}',resi:{c2['res']}}},{{sphere:{{color:'red',radius:1.5}}}});"
            
            html_code = f"""
            <div id='{container_id}' style='height: 500px; width: 100%; background-color: #070b14; border-radius: 12px;'></div>
            <script src='https://3Dmol.org/build/3Dmol-min.js'></script>
            <script>
            (function() {{
                const container = document.getElementById('{container_id}');
                const viewer = $3Dmol.createViewer(container, {{backgroundColor: '#070b14'}});
                viewer.addModel(atob('{res['pdb_b64']}'), '{res.get("ext", "pdb")}');
                viewer.setStyle({{}}, {{cartoon: {{color: 'spectrum'}}}});
                {clash_js}
                viewer.zoomTo(); viewer.render();
                setInterval(() => {{ viewer.rotate(0.5, 'y'); }}, 50);
            }})();
            </script>"""
            components.html(html_code, height=520)
