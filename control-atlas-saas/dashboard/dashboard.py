import streamlit as st
import requests, os, base64, json
import streamlit.components.v1 as components

st.set_page_config(page_title="Toscanini Forensic Pad", layout="wide")
backend_url = os.getenv("BACKEND_URL", "http://api:8000")

LAW_CANON = {
    "LAW-155": {"title": "Steric Clash Prohibition", "principle": "Atoms cannot occupy overlapping space.", "why": "Physical impossibility."},
    "LAW-162": {"title": "Interface Saturation (Heuristic)", "principle": "Distance-only donor/acceptor proximity check.", "why": "Angular and orientation checks are not yet enforced."},
    "NKG-001": {"title": "Historical Refusal", "principle": "Known forbidden motif match in NKG.", "why": "Causal memory veto."}
}

if "audit_result" not in st.session_state: st.session_state.audit_result = None
if "teleport_coords" not in st.session_state: st.session_state.teleport_coords = None
if "active_law_id" not in st.session_state: st.session_state.active_law_id = None

st.title("🛡️ TOSCANINI // FORENSIC STATION")
st.caption("v9.8.3 Competitive Telemetry | Science-Safe Analytics")

with st.sidebar:
    st.header("📉 Negative Knowledge Graph")
    try:
        stats = requests.get(f"{backend_url}/api/v1/nkg/stats").json()
        st.metric("Distinct Forbidden Motifs", stats.get("unique_pius", 0))
        
        # RESTORED CHARTS: Fallback logic
        fingerprints = stats.get("model_fingerprints", {})
        audit_failures = stats.get("audit_failures", {})
        
        if fingerprints and sum(fingerprints.values()) > 0:
            st.write("---")
            st.caption("Distinct Forbidden Motifs per Generator")
            st.bar_chart(fingerprints)
        elif audit_failures:
            st.write("---")
            st.caption("Failed Audits per Generator (Physics + Heuristics)")
            st.bar_chart(audit_failures)
        else:
            st.caption("No constitutional violations recorded yet.")
    except: st.write("NKG Offline")
    if st.button("🔄 New Audit"):
        st.session_state.audit_result = None; st.session_state.active_law_id = None; st.rerun()

cola, colb = st.columns([2, 1])
with cola: uploaded_file = st.file_uploader("Upload Protein Design", type=["pdb", "cif"])
with colb: gen_choice = st.selectbox("Generator Source", ["AlphaFold3", "RFdiffusion", "Chai-1", "ESM3", "Boltz-1", "Other"])

if uploaded_file:
    with st.spinner(f"Auditing {gen_choice}..."):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        res = requests.post(f"{backend_url}/api/v1/audit/upload", files=files, data={"generator": gen_choice}).json()
        st.session_state.audit_result = res

res = st.session_state.audit_result
if res:
    col1, col2 = st.columns([1, 2])
    with col1:
        score = res.get('score', 0)
        st.metric("SOVEREIGNTY SCORE", f"{score}%")
        if score < 70: st.caption("❌ Vetoed — fatal violation detected.")
        elif score < 85: st.caption("⚠️ Marginal pass — check interface saturation.")
        else: st.caption("✅ Pristine physics and chemistry verified.")

        verdict = res.get('verdict', 'ERROR')
        if verdict == "PASS": st.success("VERDICT: PASS")
        else: st.error("VERDICT: VETO")
        
        st.subheader("Diagnostic Ledger")
        for law in res.get("laws", []):
            l_id, status = law.get('law_id'), law.get('status')
            emoji = {"PASS":"✅", "WARNING":"⚠️", "VETO":"❌"}.get(status, "❓")
            with st.expander(f"{emoji} {l_id}: {status}"):
                st.write(f"Observed: {law.get('measurement')} {law.get('units', '')}")
                if st.button("ℹ️ Explain Law", key=f"ex-{l_id}"): st.session_state.active_law_id = l_id
                if law.get("anchor"):
                    if st.button("🔍 Teleport", key=f"tel-{l_id}"): 
                        st.session_state.teleport_coords, st.session_state.active_law_id = law["anchor"], l_id

        if st.session_state.active_law_id:
            card = LAW_CANON.get(st.session_state.active_law_id, {})
            st.write("---")
            st.markdown(f"### 🔹 {st.session_state.active_law_id}")
            st.info(card.get('principle')); st.warning(card.get('why'))
        
        if res.get("pdf_b64"):
            st.download_button("📄 Download Certificate", base64.b64decode(res["pdf_b64"]), file_name=f"verdict_{res['sig']}.pdf", mime="application/pdf")

    with col2:
        if "pdb_b64" in res:
            container_id = f"viz-{res['sig']}"
            coords = st.session_state.teleport_coords
            zoom_js = f"viewer.zoomTo({{center: {{x: {coords[0]}, y: {coords[1]}, z: {coords[2]}}}, radius: 8.0}});" if coords else "viewer.zoomTo();"
            html_code = f"""
            <div id='{container_id}' style='height: 600px; width: 100%; background-color: #070b14; border-radius: 12px;'></div>
            <script src='https://3Dmol.org/build/3Dmol-min.js'></script>
            <script>
            (function() {{
                const container = document.getElementById('{container_id}');
                const viewer = $3Dmol.createViewer(container, {{backgroundColor: '#070b14'}});
                viewer.addModel(atob('{res['pdb_b64']}'), '{res['ext']}');
                viewer.setStyle({{}}, {{cartoon: {{colorscheme: {{prop:'b', gradient: 'rwb', min:50, max:90}}}}}});
                viewer.render(); {zoom_js}
                setInterval(() => {{ viewer.rotate(0.5, 'y'); }}, 50);
            }})();
            </script>"""
            components.html(html_code, height=620)
