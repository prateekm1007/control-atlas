import streamlit as st
import requests, os, base64, json
import streamlit.components.v1 as components

st.set_page_config(page_title="Toscanini Forensic Pad", layout="wide")
backend_url = os.getenv("BACKEND_URL", "http://api:8000")

LAW_CANON = {
    "LAW-155": {"title": "Steric Clash Prohibition", "principle": "Atoms cannot occupy overlapping space.", "why": "Physical impossibility."},
    "LAW-162": {"title": "Interface Saturation", "principle": "Binding requires donor-acceptor handshake.", "why": "Chemical failure risk."},
    "NKG-001": {"title": "Historical Refusal", "principle": "Known forbidden motif match in NKG.", "why": "Memory-based veto."}
}

if "audit_result" not in st.session_state: st.session_state.audit_result = None
if "teleport_coords" not in st.session_state: st.session_state.teleport_coords = None
if "active_law_id" not in st.session_state: st.session_state.active_law_id = None

st.title("🛡️ TOSCANINI // FORENSIC STATION")
st.caption("v10.0.5 Standard | Aligned Continuity Lock: ACTIVE")

with st.sidebar:
    st.header("📉 Negative Knowledge Graph")
    try:
        s_res = requests.get(f"{backend_url}/api/v1/nkg/stats").json()
        st.metric("Forbidden PIU Motifs", s_res.get("unique_pius", 0))
        if s_res.get("model_fingerprints"): st.bar_chart(s_res["model_fingerprints"])
    except: st.write("NKG Offline")
    if st.button("🔄 New Audit"):
        st.session_state.audit_result = None; st.session_state.active_law_id = None; st.rerun()

cola, colb = st.columns([2, 1])
with cola: uploaded_file = st.file_uploader("Upload Structure", type=["pdb", "cif"])
with colb: gen_choice = st.selectbox("Generator Source", ["AlphaFold3", "RFdiffusion", "Chai-1", "ESM3", "Boltz-1", "Other"])

if uploaded_file:
    with st.spinner("Executing Forensic Protocol..."):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        res = requests.post(f"{backend_url}/api/v1/audit/upload", files=files, data={"generator": gen_choice}).json()
        st.session_state.audit_result = res

res = st.session_state.audit_result
if res and res.get("verdict") != "ERROR":
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("SOVEREIGNTY SCORE", f"{res.get('score', 0)}%")
        if res.get("mode") == "REFUSAL_VETO": st.warning(f"⚡ IMMUNE RESPONSE: PIU Match")
        
        st.subheader("Diagnostic Ledger")
        for law in res.get("laws", []):
            lid, lstat = law['law_id'], law['status']
            with st.expander(f"{'✅' if lstat=='PASS' else '❌'} {lid}"):
                st.write(f"Observed: {law.get('measurement')} {law.get('units', '')}")
                if st.button("ℹ️ Explain Law", key=f"ex-{lid}"): st.session_state.active_law_id = lid
                if law.get("anchor"):
                    if st.button("🔍 Teleport", key=f"tel-{lid}"): 
                        st.session_state.teleport_coords, st.session_state.active_law_id = law["anchor"], lid

        if st.session_state.active_law_id:
            card = LAW_CANON.get(st.session_state.active_law_id, {})
            st.write("---")
            st.info(card.get('principle')); st.warning(card.get('why'))
        
        if res.get("pdf_b64"):
            st.download_button("📄 Download Governance Certificate v1.0", base64.b64decode(res["pdf_b64"]), file_name=f"decision_{res['sig']}.pdf", mime="application/pdf", use_container_width=True)

    with col2:
        if "pdb_b64" in res:
            html_code = f"""
            <div id='viz' style='height: 500px; width: 100%; background-color: #070b14; border-radius: 12px;'></div>
            <script src='https://3Dmol.org/build/3Dmol-min.js'></script>
            <script>
            (function() {{
                const container = document.getElementById('viz');
                const viewer = $3Dmol.createViewer(container, {{backgroundColor: '#070b14'}});
                viewer.addModel(atob('{res['pdb_b64']}'), '{res['ext']}');
                viewer.setStyle({{}}, {{cartoon: {{colorscheme: {{prop:'b', gradient: 'rwb', min:50, max:90}}}}}});
                {f"viewer.zoomTo({{center:{{x:{st.session_state.teleport_coords[0]},y:{st.session_state.teleport_coords[1]},z:{st.session_state.teleport_coords[2]}}},radius:8}});" if st.session_state.teleport_coords else "viewer.zoomTo();"}
                viewer.render(); setInterval(() => {{ viewer.rotate(0.5, 'y'); }}, 50);
            }})();
            </script>"""
            components.html(html_code, height=620)
elif res:
    st.error(f"Brain Failure: {res.get('details')}")
