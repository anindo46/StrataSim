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
tab1, tab2, tab3, tab4 = st.tabs(["📝 Input", "📊 Column", "📄 Export", "📁 Upload CSV"])

with tab1:
    st.subheader("📝 Add Stratigraphic Layer")
    with st.form("add_layer_form"):
        col1, col2 = st.columns(2)
        with col1:
            lithology = st.selectbox("Lithology", list(lithology_patterns.keys()))
            color = st.color_picker("Color")
            grain_size = st.selectbox("Grain Size", ["Fine", "Medium", "Coarse"])
        with col2:
            thickness = st.number_input("Thickness (m)", min_value=0.1, step=0.1)
            fossils = st.text_input("Fossils")
            notes = st.text_area("Notes")

        if st.form_submit_button("➕ Add Layer"):
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
            st.success("Layer added successfully.")

with tab2:
    st.subheader("📊 Stratigraphic Column")
    if st.button("🧹 Clear All Layers"):
        st.session_state.layers = []
        st.success("All layers cleared.")
    if not st.session_state.layers:
        st.warning("No layers added yet.")
    else:
        df = pd.DataFrame(st.session_state.layers)
        st.dataframe(df)
        selected_row = st.selectbox("Select a row to delete", df.index.tolist(), format_func=lambda i: f"{df.loc[i, 'Lithology']} ({df.loc[i, 'Thickness']}m)")
        if st.button("❌ Delete Selected Row"):
            st.session_state.layers.pop(selected_row)
            st.success("Selected layer deleted.")
            # Removed deprecated rerun function
        fig, ax = plt.subplots(figsize=(4, 10))
        y = 0
        for i in range(len(df) - 1, -1, -1):
            row = df.iloc[i]
            rect = Rectangle((0, y), 1, row['Thickness'], facecolor=row['Color'], edgecolor='black', hatch=lithology_patterns.get(row['Lithology'], ''))
            ax.add_patch(rect)
            ax.text(0.5, y + row['Thickness']/2, row['Lithology'], ha='center', va='center', fontsize=8)
            y += row['Thickness']
        ax.set_xlim(0, 1)
        ax.set_ylim(0, y)
        ax.axis('off')
        st.pyplot(fig)

with tab3:
    st.subheader("📄 Export Options")
    if not st.session_state.layers:
        st.warning("Add layers to enable export.")
    else:
        df = pd.DataFrame(st.session_state.layers)
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

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv, "strat_data.csv", mime="text/csv")

# Show redirect button if just uploaded
# Removed auto-switch (deprecated). Use message below instead.
if st.session_state.get('uploaded'):
    st.info("✅ Layers added! Use the 📊 Column tab above to view your stratigraphy.")

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

st.markdown("**Developed by Anindo Paul Sourav – Student, Geology and Mining, University of Barishal**")
