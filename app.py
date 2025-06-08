import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from io import BytesIO
from PIL import Image
import base64
import os

st.set_page_config(page_title="StrataSim", layout="wide", page_icon="🪨")

# Sidebar and theme settings
st.sidebar.title("⚙️ Settings")
theme = st.sidebar.radio("Theme Mode", ["Light", "Dark"])

# Header
st.title("🪨 StrataSim – Professional Stratigraphic Column Tool")
st.caption("Build, interpret, and export stratigraphic sections with accuracy and ease.")

# Initialize session state for layers
if 'layers' not in st.session_state:
    st.session_state['layers'] = []

# Lithology symbols (simple hatch styles for now)
lithology_patterns = {
    "Sandstone": "////",
    "Shale": "....",
    "Limestone": "----",
    "Conglomerate": "xxxx",
    "Siltstone": "\\\\"
}

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📝 Input", "📊 Column", "📄 Export", "📁 Upload CSV"])

with tab1:
    st.subheader("Add a Stratigraphic Layer")
    with st.form("layer_form"):
        col1, col2 = st.columns(2)
        with col1:
            lithology = st.selectbox("Lithology", list(lithology_patterns.keys()))
            color = st.color_picker("Color")
            grain_size = st.selectbox("Grain Size", ["Fine", "Medium", "Coarse"])
        with col2:
            thickness = st.number_input("Thickness (m)", min_value=0.1, step=0.1)
            fossils = st.text_input("Fossils")
            notes = st.text_area("Notes")

        submitted = st.form_submit_button("Add Layer")

        if submitted:
            environment = "Marine" if lithology in ["Shale", "Limestone"] else "Fluvial/Deltaic"
            st.session_state.layers.append({
                'Lithology': lithology,
                'Color': color,
                'Grain Size': grain_size,
                'Thickness': thickness,
                'Fossils': fossils,
                'Environment': environment,
                'Notes': notes
            })
            st.success("Layer added successfully!")

with tab2:
    st.subheader("Visualized Stratigraphic Column")
    if not st.session_state.layers:
        st.info("No layers to display.")
    else:
        df = pd.DataFrame(st.session_state.layers)
        st.dataframe(df)

        fig, ax = plt.subplots(figsize=(4, 10))
        y = 0
        for _, row in df[::-1].iterrows():
            rect = Rectangle((0, y), 1, row['Thickness'], facecolor=row['Color'], edgecolor='black', hatch=lithology_patterns.get(row['Lithology'], ''))
            ax.add_patch(rect)
            ax.text(0.5, y + row['Thickness']/2, row['Lithology'], ha='center', va='center', fontsize=8)
            y += row['Thickness']
        ax.set_xlim(0, 1)
        ax.set_ylim(0, y)
        ax.axis('off')
        st.pyplot(fig)

        legend_patches = [Patch(facecolor='white', hatch=pat, label=lit) for lit, pat in lithology_patterns.items()]
        st.pyplot(plt.figure(figsize=(4, 1)))

with tab3:
    st.subheader("Export Options")
    if not st.session_state.layers:
        st.warning("Add layers first.")
    else:
        df = pd.DataFrame(st.session_state.layers)
        # Export image
        fig, ax = plt.subplots(figsize=(4, 10))
        y = 0
        for _, row in df[::-1].iterrows():
            rect = Rectangle((0, y), 1, row['Thickness'], facecolor=row['Color'], edgecolor='black', hatch=lithology_patterns.get(row['Lithology'], ''))
            ax.add_patch(rect)
            ax.text(0.5, y + row['Thickness']/2, row['Lithology'], ha='center', va='center', fontsize=8)
            y += row['Thickness']
        ax.set_xlim(0, 1)
        ax.set_ylim(0, y)
        ax.axis('off')
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        st.download_button("📥 Download Column Image", buf, "strat_column.png", mime="image/png")

        # Export CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv, "strat_data.csv", mime="text/csv")

with tab4:
    st.subheader("Upload CSV File")
    uploaded_file = st.file_uploader("Upload a CSV file with stratigraphy data", type="csv")
    if uploaded_file:
        df_uploaded = pd.read_csv(uploaded_file)
        required_cols = {"Lithology", "Color", "Grain Size", "Thickness"}
        if required_cols.issubset(df_uploaded.columns):
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
            st.success("Layers added from uploaded CSV.")
        else:
            st.error(f"CSV must include these columns: {required_cols}")
