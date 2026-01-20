import streamlit as st
import requests, os, base64, json
import streamlit.components.v1 as components

st.set_page_config(page_title="Toscanini Forensic Pad", layout="wide")
backend_url = os.getenv("BACKEND_URL", "http://api:8000")

LAW_CANON = {
    "LAW-155": {"title": "Steric Clash Prohibition", "principle": "Two non-bonded atoms cannot overlap.", "why": "Physical impossibility."},
    "LAW-160": {"title": "Backbone Continuity", "principle": "Cα–Cα distance must maintain ~3.8Å.", "why": "Prevents 'tearing' the protein string."},
    "NKG-001": {"title": "Historical Refusal", "principle": "Forbidden motif match in NKG.", "why": "Known failure pattern."}
}

if "audit_result" not in st.session_state: st.session_state.audit_result = None
if "teleport_coords" not in st.session_state: st.session_state.teleport_coords = None
if "active_law_id" not in st.session_state: st.session_state.active_law_id = None

st.title("🛡️ TOSCANINI // FORENSIC STATION")
st.caption("v9.6.8 Calibration Lock | Constitutional Integrity: AIRTIGHT")

with st.sidebar:
    st.header("📉 Negative Knowledge Graph")
    try:
        stats = requests.get(f"{backend_url}/api/v1/nkg/stats").json()
        u_pius = stats.get("unique_pius", 0)
        st.metric("Distinct Forbidden Motifs", u_pius)
        
        if u_pius == 0:
            st.caption("No constitutional violations recorded yet.")
        else:
            st.caption(f"Learned from {stats.get('total_obs', 0)} design failures.")
            clusters = stats.get("clusters", {})
            if clusters:
                st.write("---")
                st.caption("Hallucination Clusters (Unique PIUs)")
                st.bar_chart(dict(sorted(clusters.items(), key=lambda x: x[1], reverse=True)[:5]))
    except: st.write("NKG Offline")
    if st.button("🔄 New Audit", use_container_width=True):
        st.session_state.audit_result = None; st.session_state.active_law_id = None; st.rerun()

uploaded_file = st.file_uploader("Upload Protein Design", type=["pdb", "cif"])
if uploaded_file:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
    res = requests.post(f"{backend_url}/api/v1/audit/upload", files=files).json()
    st.session_state.audit_result = res

res = st.session_state.audit_result
if res:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("SOVEREIGNTY SCORE", f"{res.get('score', 0)}%")
        if res.get("mode") == "REFUSAL_VETO": st.warning("⚡ IMMUNE RESPONSE: PIU Match")
        
        st.subheader("Diagnostic Ledger")
        for law in res.get("laws", []):
            l_id, status = law.get('law_id'), law.get('status')
            with st.expander(f"{'✅' if status == 'PASS' else '❌'} {l_id}"):
                st.write(f"Observed: {law.get('measurement')} {law.get('units', '')}")
                if st.button("ℹ️ Explain Law", key=f"ex-{l_id}", use_container_width=True):
                    st.session_state.active_law_id = l_id
                if law.get("anchor"):
                    if st.button("🔍 Teleport", key=f"tel-{l_id}", use_container_width=True):
                        st.session_state.teleport_coords, st.session_state.active_law_id = law["anchor"], l_id

        if st.session_state.active_law_id:
            card = LAW_CANON.get(st.session_state.active_law_id, {})
            st.write("---")
            st.markdown(f"### 🔹 {st.session_state.active_law_id}")
            st.info(card.get('principle'))
            st.warning(card.get('why'))

    with col2:
        if "pdb_b64" in res:
            container_id = f"viz-{res['sig']}"
            coords = st.session_state.teleport_coords
            zoom_js = f"viewer.zoomTo({{center: {{x: {coords[0]}, y: {coords[1]}, z: {coords[2]}}}, radius: 8.0}});" if coords else "viewer.zoomTo();"
            html_code = f"""
            <div id='{container_id}' style='height: 500px; width: 100%; background-color: #070b14; border-radius: 12px;'></div>
            <script src='https://3Dmol.org/build/3Dmol-min.js'></script>
            <script>
            (function() {{
                const container = document.getElementById('{container_id}');
                const viewer = $3Dmol.createViewer(container, {{backgroundColor: '#070b14'}});
                viewer.addModel(atob('{res['pdb_b64']}'), '{res['ext']}');
                viewer.setStyle({{}}, {{cartoon: {{colorscheme: {{prop:'b', gradient: 'rwb', min:50, max:90}}}}}});
                {zoom_js}
                viewer.render();
                setInterval(() => {{ viewer.rotate(0.5, 'y'); }}, 50);
            }})();
            </script>"""
            components.html(html_code, height=620)
