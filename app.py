import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from io import BytesIO
from PIL import Image
import base64
import os

st.set_page_config(page_title="StrataSim", layout="wide", page_icon="🪨")

# Sidebar settings
st.sidebar.title("⚙️ Settings")
st.sidebar.info("StrataSim helps create, visualize, and export stratigraphic columns.")
st.sidebar.markdown("---")
theme = st.sidebar.selectbox("Theme Mode", ["Light", "Dark"])
st.sidebar.markdown("---")
st.sidebar.markdown("📘 Need help? Click below")
with st.sidebar.expander("ℹ️ How to Use"):
    st.markdown("""
    1. Add or edit layers in the 📝 Input tab.
    2. View and manage them in 📊 Column tab.
    3. Export results from 📄 Export tab.
    4. Upload CSV or Excel data in 📁 Upload CSV tab.
    Drag layers in 📊 Column tab to reorder.
    """)

if theme == "Dark":
    st.markdown("""
        <style>
        body { background-color: #1e1e1e; color: #eeeeee; }
        .stTextInput > div > div > input {
            background-color: #333333;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

st.title("🪨 StrataSim – Professional Stratigraphic Column Tool")
st.caption("Build, interpret, and export stratigraphic sections with accuracy and ease.")

if 'layers' not in st.session_state:
    st.session_state['layers'] = []
if 'selected_index' not in st.session_state:
    st.session_state['selected_index'] = None

lithology_patterns = {
    "Sandstone": "////",
    "Shale": "....",
    "Limestone": "----",
    "Conglomerate": "xxxx",
    "Siltstone": "\\\\"
}

facies_legend = {
    "Marine": "Shale, Limestone",
    "Fluvial/Deltaic": "Sandstone, Conglomerate, Siltstone"
}

# Tabs
tab_names = ["📝 Input", "📊 Column", "📄 Export", "📁 Upload CSV"]
tabs = st.tabs(tab_names)
tab1, tab2, tab3, tab4 = tabs

# Show redirect button if just uploaded
if st.session_state.get('uploaded'):
    st.toast("Click '📊 Column' tab to view your data.", icon="✅")
    if st.button("➡️ Go to Column Tab"):
        st.switch_page("Column")

# Manual tab-switch button
if 'uploaded' not in st.session_state:
    st.session_state.uploaded = False

with tab4:
    st.subheader("📁 Upload Stratigraphy Data (CSV or Excel)")
    uploaded_file = st.file_uploader("Choose a file to upload", type=["csv", "xlsx"])

    # Sample template download
    sample_data = pd.DataFrame({
        "Lithology": ["Sandstone", "Shale"],
        "Color": ["#c2b280", "#5f5f5f"],
        "Grain Size": ["Coarse", "Fine"],
        "Thickness": [2.5, 1.2],
        "Fossils": ["Plant fragments", "Fish scales"],
        "Notes": ["Base layer", "Dark shale"]
    })
    csv_bytes = sample_data.to_csv(index=False).encode('utf-8')
    st.download_button("📄 Download CSV Template", data=csv_bytes, file_name="strata_template.csv", mime="text/csv")

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df_uploaded = pd.read_csv(uploaded_file)
            else:
                df_uploaded = pd.read_excel(uploaded_file)

            required_columns = {"Lithology", "Color", "Grain Size", "Thickness"}
            if required_columns.issubset(df_uploaded.columns):
                st.dataframe(df_uploaded)
                if st.button("📥 Add Uploaded Layers"):
                    for _, row in df_uploaded.iterrows():
                        environment = "Marine" if row['Lithology'] in ["Shale", "Limestone"] else "Fluvial/Deltaic"
                        st.session_state.layers.append({
                            'Lithology': row['Lithology'],
                            'Color': row['Color'],
                            'Grain Size': row['Grain Size'],
                            'Thickness': row['Thickness'],
                            'Fossils': row.get('Fossils', ''),
                            'Environment': environment,
                            'Notes': row.get('Notes', '')
                        })
                    st.success("✅ Layers successfully added from uploaded file!")
st.session_state.uploaded = True
            else:
                st.error(f"❌ Missing required columns. Please include: {required_columns}")
        except Exception as e:
            st.error(f"Error reading file: {e}")

# Footer credits
st.markdown("""
---
**Developed by Anindo Paul Sourav**  
_Student, Geology and Mining, University of Barishal_  
📧 Email: [anindo.glm@gmail.com](mailto:anindo.glm@gmail.com)  
🌐 [Portfolio](https://anindo.netlify.app)  
🐙 [GitHub](https://github.com/anindosourav)
""")
