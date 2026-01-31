import streamlit as st
import requests, base64, json, os
import streamlit.components.v1 as components
st.set_page_config(page_title="Toscanini", layout="wide")
backend_url = os.getenv("BACKEND_URL", "http://brain:8000")

if "audit_result" not in st.session_state: st.session_state.audit_result = None
if "inspect" not in st.session_state: st.session_state.inspect = None
if "candidates" not in st.session_state: st.session_state.candidates = None

st.title("🛡️ TOSCANINI // FORENSIC STATION")

with st.sidebar:
    st.header("📉 NKG Intelligence")
    path = st.radio("Structure Entry", ["Biological Discovery", "Manual Upload"])
    
    if path == "Manual Upload":
        f = st.file_uploader("Upload Structure")
        # AUTOMATION: Trigger audit if file is uploaded and not already processed
        if f and (not st.session_state.audit_result or st.session_state.get("last_file") != f.name):
            with st.spinner("Processing Upload..."):
                res = requests.post(f"{backend_url}/ingest", files={"file": (f.name, f.getvalue())}, data={"mode": "Upload", "candidate_id": "man"}).json()
                st.session_state.audit_result = res
                st.session_state.last_file = f.name
    else:
        q = st.text_input("🔍 Search Protein, Function or ID", placeholder="e.g. Insulin, P01308...")
        if q and st.button("Discover Targets"):
            st.session_state.candidates = requests.post(f"{backend_url}/search", data={"query": q}).json()
        
        if st.session_state.candidates:
            st.subheader("Results")
            for c in st.session_state.candidates:
                # AUTOMATION: For Evidence, one click triggers acquisition + audit
                if st.button(f"{c['label']}", key=c['id']):
                    if c['type'] == 'Evidence':
                        with st.spinner("Fetching & Auditing..."):
                            res = requests.post(f"{backend_url}/ingest", data={"mode": "Discovery", "candidate_id": c['id']}).json()
                            st.session_state.audit_result = res
                    else:
                        st.session_state.sel_id = c['id']

            if st.session_state.get("sel_id"):
                seq = st.text_area("Enter Sequence", height=100)
                if st.button("🚀 Generate & Notarize"):
                    with st.spinner("Generating..."):
                        res = requests.post(f"{backend_url}/ingest", data={"mode": "Discovery", "candidate_id": st.session_state.sel_id, "sequence": seq}).json()
                        st.session_state.audit_result = res
                        del st.session_state.sel_id

# --- RENDERER (12 Pillars) ---
if st.session_state.audit_result:
    res = st.session_state.audit_result
    if res.get("verdict") == "ERROR": st.error(f"⚠️ {res.get('details')}")
    else:
        col1, col2 = st.columns([1, 2])
        with col1:
            m1, m2 = st.columns([1, 1])
            m1.metric("PHYSICAL SCORE", f"{res['score']}%", help=res['definitions']['PHYSICAL_SCORE']['explanation'])
            m2.metric("ML CONFIDENCE", f"{res['conf']}%", help=res['definitions']['CONFIDENCE_SCORE']['explanation'])
            with st.container(border=True):
                st.caption(f"Source: {res['provenance']['source']} | Audit ID: `{res['sig']}`")
                st.download_button("📂 Download Sealed PDB", base64.b64decode(res["pdb_b64"]), file_name=f"notarized.{res['ext']}", key="dl_p")
                if res.get("pdf_b64"): st.download_button("📄 Download Certificate", base64.b64decode(res["pdf_b64"]), file_name="certificate.pdf")
            
            st.info(f"**{res['routing'].get('banner')}**")
            st.subheader("Forensic Causal Rationale")
            st.write(res.get("narrative"))
            
            st.subheader("Diagnostic Ledger")
            for l in res['laws']:
                icon = "✅" if l['status']=='PASS' else "❌"
                with st.expander(f"{icon} {l['law_id']} - {l['title']}"):
                    st.write(l['measurement']); st.caption(f"Rationale: {l.get('rationale')}")
                    if l.get("anchor") and st.button("🔍 Inspect", key=f"btn_{l['law_id']}"):
                        st.session_state.inspect = l['anchor']; st.rerun()
        with col2:
            data = base64.b64decode(res["pdb_b64"]).decode(); fmt = res.get("ext", "pdb")
            style = "{stick:{radius:0.2}, sphere:{radius:0.6, color:'spectrum'}}" if res['verdict'] == 'VETO' else "{cartoon:{color:'spectrum'}}"
            inspect_js = ""
            if st.session_state.inspect:
                p = st.session_state.inspect['pos']
                inspect_js = "v.addSphere({center:{x:" + str(p[0]) + ", y:" + str(p[1]) + ", z:" + str(p[2]) + "}, radius:3, color:'red', wireframe:true}); v.zoomTo({center:{x:" + str(p[0]) + ", y:" + str(p[1]) + ", z:" + str(p[2]) + "}});"
            components.html(f"<div id='v' style='height:600px;width:100%;background:#070b14;border-radius:10px;'></div><script src='https://3Dmol.org/build/3Dmol-min.js'></script><script>var v = $3Dmol.createViewer('v', {{backgroundColor: '#070b14'}}); v.addModel(`{data}`, '{fmt}'); v.setStyle({{}}, {style}); v.zoomTo(); {inspect_js} v.render(); v.spin(true);</script>", height=620)
