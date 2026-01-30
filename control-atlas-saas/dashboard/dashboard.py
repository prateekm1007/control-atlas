import streamlit as st
import requests, base64, json, os
import streamlit.components.v1 as components

st.set_page_config(page_title="Toscanini", layout="wide")
backend_url = os.getenv("BACKEND_URL", "http://brain:8000")

if "inspect" not in st.session_state: st.session_state.inspect = None

st.title("🛡️ TOSCANINI // FORENSIC STATION")

with st.sidebar:
    st.header("📉 NKG Intelligence")
    try:
        s = requests.get(f"{backend_url}/stats", timeout=3).json()
        st.metric("Forbidden Motifs", s.get("unique_pius", 0))
    except: pass
    st.info("Brain: ONLINE")
    gen_choice = st.selectbox("Generator", ["AlphaFold3", "RFdiffusion", "Chai-1", "ESMFold"])

uploaded_file = st.file_uploader("Upload Structure (PDB or CIF)")

if uploaded_file:
    with st.spinner("Executing Audit..."):
        try:
            res = requests.post(f"{backend_url}/audit", files={"file": (uploaded_file.name, uploaded_file.getvalue())}, data={"generator": gen_choice}).json()
            
            if res.get("verdict") != "ERROR":
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric("PHYSICAL SCORE", f"{res['score']}%", delta=res['verdict'])
                    if res.get("pdf_b64"):
                        st.download_button("📄 Download Notary Certificate", base64.b64decode(res["pdf_b64"]), file_name="certificate.pdf")
                    st.download_button("📂 Download Sealed PDB/CIF", base64.b64decode(res["pdb_b64"]), file_name=f"sealed.{res['ext']}")
                    
                    st.info(f"**{res['routing'].get('banner')}**")
                    st.subheader("Causal Rationale")
                    st.write(res.get("narrative"))
                    
                    st.subheader("Diagnostic Ledger")
                    for l in res['laws']:
                        icon = "❌" if l['status'] == 'FAIL' else "✅"
                        with st.expander(f"{icon} {l['law_id']} - {l['title']}"):
                            st.write(f"Observed: {l['measurement']}")
                            st.caption(f"Rationale: {l['rationale']}")
                            if l.get("anchor") and st.button("🔍 Inspect", key=f"btn_{l['law_id']}"):
                                st.session_state.inspect = l['anchor']
                
                with col2:
                    struct_data = base64.b64decode(res["pdb_b64"]).decode()
                    fmt = res.get("ext", "pdb") # Dynamic Format (cif or pdb)
                    style = "{cartoon:{color:'spectrum'}}" if res['verdict'] == 'PASS' else "{stick:{radius:0.2}, sphere:{radius:0.6, color:'spectrum'}}"
                    
                    inspect_js = ""
                    if st.session_state.inspect:
                        c = st.session_state.inspect
                        p = c.get('pos', [0,0,0])
                        inspect_js = f"v.addSphere({{center:{{x:{p[0]}, y:{p[1]}, z:{p[2]}}}, radius:3, color:'red', wireframe:true}}); v.zoomTo({{resi:{c.get('res_seq',1)}}});"

                    components.html(f"""
                        <div id='v' style='height:600px;width:100%;background:#070b14;border-radius:10px;'></div>
                        <script src='https://3Dmol.org/build/3Dmol-min.js'></script>
                        <script>
                            var v = $3Dmol.createViewer('v', {{backgroundColor: '#070b14'}});
                            v.addModel(`{struct_data}`, '{fmt}');
                            v.setStyle({{}}, {style});
                            v.zoomTo(); {inspect_js} v.render(); v.spin(true);
                        </script>
                    """, height=620)
            else: st.error(res.get("details"))
        except Exception as e: st.error(f"Failed: {e}")
