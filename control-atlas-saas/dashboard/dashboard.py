import streamlit as st
import requests, os, base64, json
import streamlit.components.v1 as components

st.set_page_config(page_title="Toscanini Forensic Pad", layout="wide")
backend_url = os.getenv("BACKEND_URL", "http://api:8000")

# --- LAW CANON REGISTRY (Epistemic Truth) ---
LAW_CANON = {
    "LAW-155": {
        "title": "Steric Clash Prohibition",
        "principle": "Two non-bonded heavy atoms cannot occupy overlapping space.",
        "why": "Violations indicate physically impossible structures that cannot exist."
    },
    "LAW-160": {
        "title": "Backbone Continuity",
        "principle": "Backbones must have fixed geometric spacing (~3.8Å).",
        "why": "Large deviations indicate the AI 'tore' the protein chain to satisfy a motif."
    },
    "LAW-120": {
        "title": "Peptide Bond Sanity",
        "principle": "Covalent peptide bonds have fixed chemical lengths (1.33Å).",
        "why": "Violations mean the backbone itself is chemically impossible."
    }
}

if "teleport_coords" not in st.session_state: st.session_state.teleport_coords = None
if "active_law_id" not in st.session_state: st.session_state.active_law_id = None

st.title("🛡️ TOSCANINI // FORENSIC STATION")
st.caption("v9.5.7 Epistemic Decoupling | Every Law is Explainable")

uploaded_file = st.file_uploader("Upload Protein Design", type=["pdb", "cif"])

if uploaded_file:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
    try:
        res = requests.post(f"{backend_url}/api/v1/audit/upload", files=files).json()
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Diagnostic Ledger")
            for law in res.get("laws", []):
                law_id = law.get('law_id', 'Unknown')
                status = law.get('status', 'ERROR')
                status_emoji = "✅" if status == "PASS" else "❌"
                
                with st.expander(f"{status_emoji} {law_id}: {status}"):
                    st.write(f"**Observed:** {law.get('measurement', 'N/A')} {law.get('units', '')}")
                    
                    # --- DECOUPLED TRIGGER 1: EXPLAIN (Always Available) ---
                    if st.button(f"ℹ️ Explain Law", key=f"exp-{law_id}", use_container_width=True):
                        st.session_state.active_law_id = law_id
                    
                    # --- DECOUPLED TRIGGER 2: TELEPORT (Evidence-Dependent) ---
                    anchor = law.get('anchor')
                    if anchor:
                        if st.button(f"🔍 Teleport to Evidence", key=f"tel-{law_id}", use_container_width=True):
                            st.session_state.teleport_coords = anchor
                            st.session_state.active_law_id = law_id

            # RENDER THE ACTIVE LAW CARD
            if st.session_state.active_law_id:
                card = LAW_CANON.get(st.session_state.active_law_id, {})
                st.write("---")
                st.markdown(f"### 🔹 {st.session_state.active_law_id}")
                st.info(f"**Principle:** {card.get('principle')}")
                st.warning(f"**Forensic Impact:** {card.get('why')}")
                
        with col2:
            if "pdb_b64" in res:
                coords = st.session_state.teleport_coords
                zoom_js = f"viewer.zoomTo({{center: {{x: {coords[0]}, y: {coords[1]}, z: {coords[2]}}}, radius: 8.0}});" if coords else "viewer.zoomTo();"
                html_code = f"""
                <div id='viz' style='height: 600px; width: 100%; background-color: #070b14; border-radius: 12px;'></div>
                <script src='https://3Dmol.org/build/3Dmol-min.js'></script>
                <script>
                (function() {{
                    const viewer = $3Dmol.createViewer(document.getElementById('viz'), {{backgroundColor: '#070b14'}});
                    viewer.addModel(atob('{res['pdb_b64']}'), '{res['ext']}');
                    viewer.setStyle({{}}, {{cartoon: {{colorscheme: {{prop:'b', gradient: 'rwb', min:50, max:90}}}}}});
                    {zoom_js}
                    viewer.render();
                }})();
                </script>"""
                components.html(html_code, height=620)
    except Exception as e:
        st.error(f"Handshake failed: {e}")

