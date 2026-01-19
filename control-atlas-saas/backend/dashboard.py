import streamlit as st
import requests
import pandas as pd
import time
import plotly.express as px
import streamlit.components.v1 as components

st.set_page_config(page_title="Sovereign Sieve Forensic Lab", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: #e0e0e0; } .narrative-spine { background-color: #16191f; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b; font-style: italic; line-height: 1.6; margin-bottom: 25px; } .verdict-card { padding: 20px; border-radius: 10px; text-align: center; font-weight: bold; } .verdict-VETO { border: 2px solid #ff4b4b; background: #1a0d0d; } .verdict-PASS { border: 2px solid #00ff7f; background: #0a110d; }</style>", unsafe_allow_html=True)

with st.sidebar:
    st.title("🛡️ Sovereign Sieve")
    if 'token' not in st.session_state:
        email = st.text_input("Email", value="conductor@falsify.bio")
        pw = st.text_input("Password", type="password", value="physics_is_law")
        if st.button("Login"):
            res = requests.post("http://api:8000/auth/login", data={"username": email, "password": pw})
            if res.status_code == 200:
                st.session_state['token'] = res.json()['access_token']; st.rerun()
    else:
        st.success("Session Active")
        if st.button("Logout"): del st.session_state['token']; st.rerun()

if 'token' not in st.session_state: st.stop()
headers = {"Authorization": f"Bearer {st.session_state['token']}"}

def render_3d(job_id, metrics):
    res = requests.get(f"http://api:8000/jobs/file/{job_id}", headers=headers)
    if res.status_code == 200:
        fmt = res.headers.get("X-File-Format", "pdb")
        data = res.text.replace("\n", "\\n").replace("'", "\\'")
        vec = metrics.get('clash_coords', {})
        overlay = f"var p1={{x:{vec['atom1'][0]},y:{vec['atom1'][1]},z:{vec['atom1'][2]}}}; var p2={{x:{vec['atom2'][0]},y:{vec['atom2'][1]},z:{vec['atom2'][2]}}}; v.addCylinder({{start:p1,end:p2,radius:0.05,color:'red',dashed:true}}); v.addLabel('Observed: {vec['dist']}A',{{position:p1,backgroundColor:'#ff4b4b',fontColor:'white'}});" if vec and 'atom1' in vec else ""
        html = f"""<div id="v" style="height:500px;width:100%;border-radius:15px;border:1px solid #444;"></div><script src="https://3Dmol.org/build/3Dmol-min.js"></script><script>var v=$3Dmol.createViewer("v",{{backgroundColor:"#000"}}); v.addModel(`{data}`,"{fmt}"); v.setStyle({{chain:'A'}},{{cartoon:{{color:'spectrum',opacity:0.8}}}}); v.setStyle({{chain:'B'}},{{stick:{{radius:0.2,color:'white'}}}}); {overlay} v.zoomTo({{chain:'B'}}); v.render();</script>"""
        components.html(html, height=520)

tab1, tab2 = st.tabs(["🧬 Audit Case File", "📈 NKG Matrix"])

with tab1:
    if 'last_job' not in st.session_state:
        file = st.file_uploader("Upload Structure (CIF/PDB)", type=["cif", "pdb"])
        if st.button("Engage Sieve") and file:
            res = requests.post("http://api:8000/jobs/upload", files={"file": (file.name, file.getvalue())}, data={"target_chain": "A", "binder_chain": "B"}, headers=headers)
            st.session_state['last_job'] = res.json()['job_id']; st.rerun()
    else:
        job_id = st.session_state['last_job']
        status = requests.get(f"http://api:8000/jobs/status/{job_id}", headers=headers).json()
        if status['status'] == 'completed':
            render_3d(job_id, status['metrics']) # RESTORED TRIGGER
            st.markdown(f"<div class='verdict-card verdict-{'PASS' if 'PASS' in status['verdict'] else 'VETO'}'><h2>{status['verdict']}</h2></div>", unsafe_allow_html=True)
            if st.button("← New Audit"): del st.session_state['last_job']; st.rerun()
        else:
            st.info(f"Physics Engine: {status.get('current_stage', 'QUEUED')}...")
            time.sleep(3); st.rerun()

with tab2:
    st.header("Negative Knowledge Graph")
    nkg_res = requests.get("http://api:8000/nkg/analytics/matrix", headers=headers).json()
    if nkg_res and len(nkg_res) > 0:
        df = pd.DataFrame.from_dict(nkg_res, orient='index').fillna(0)
        st.plotly_chart(px.imshow(df, color_continuous_scale="Reds"))
    else:
        st.info("Accumulating failure data...")
