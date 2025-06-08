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
    4. Upload CSV data in 📁 Upload CSV tab.
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

tab1, tab2, tab3, tab4 = st.tabs(["📝 Input", "📊 Column", "📄 Export", "📁 Upload CSV"])

with tab1:
    st.subheader("Add or Edit a Stratigraphic Layer")
    selected_index = st.selectbox("Select a layer to edit or delete", options=["None"] + [f"Layer {i+1}: {l['Lithology']} ({l['Thickness']}m)" for i, l in enumerate(st.session_state.layers)])
    selected_layer = None
    if selected_index != "None":
        idx = int(selected_index.split()[1][:-1]) - 1
        selected_layer = st.session_state.layers[idx]
        st.session_state['selected_index'] = idx
    else:
        st.session_state['selected_index'] = None

    with st.form("layer_form"):
        col1, col2 = st.columns(2)
        with col1:
            lithology = st.selectbox("Lithology", list(lithology_patterns.keys()), index=list(lithology_patterns.keys()).index(selected_layer['Lithology']) if selected_layer else 0)
            color = st.color_picker("Color", value=selected_layer['Color'] if selected_layer else "#c2c2c2")
            grain_size = st.selectbox("Grain Size", ["Fine", "Medium", "Coarse"], index=["Fine", "Medium", "Coarse"].index(selected_layer['Grain Size']) if selected_layer else 0)
        with col2:
            thickness = st.number_input("Thickness (m)", min_value=0.1, step=0.1, value=selected_layer['Thickness'] if selected_layer else 1.0)
            fossils = st.text_input("Fossils", value=selected_layer['Fossils'] if selected_layer else "")
            notes = st.text_area("Notes", value=selected_layer['Notes'] if selected_layer else "")

        if st.form_submit_button("💾 Save Layer"):
            environment = "Marine" if lithology in ["Shale", "Limestone"] else "Fluvial/Deltaic"
            new_layer = {
                'Lithology': lithology,
                'Color': color,
                'Grain Size': grain_size,
                'Thickness': thickness,
                'Fossils': fossils,
                'Environment': environment,
                'Notes': notes
            }
            if st.session_state['selected_index'] is not None:
                st.session_state.layers[st.session_state['selected_index']] = new_layer
                st.success("✅ Layer updated successfully!")
            else:
                st.session_state.layers.append(new_layer)
                st.success("✅ Layer added successfully!")

    if st.session_state['selected_index'] is not None:
        if st.button("🗑️ Delete Selected Layer"):
            del st.session_state.layers[st.session_state['selected_index']]
            st.session_state['selected_index'] = None
            st.success("❌ Layer deleted.")

    if st.button("🧹 Clear All Layers"):
        st.session_state.layers = []
        st.session_state['selected_index'] = None
        st.warning("All layers have been cleared.")

with tab2:
    st.subheader("Visualized Stratigraphic Column")
    if not st.session_state.layers:
        st.info("No layers to display.")
    else:
        df = pd.DataFrame(st.session_state.layers)
        st.dataframe(df)

        st.markdown("### 🧱 Drag to Reorder Layers")
        moved_layer = st.selectbox("Select layer to move", options=[f"Layer {i+1}: {l['Lithology']}" for i, l in enumerate(st.session_state.layers)])
        move_direction = st.radio("Move Layer", ["Up", "Down"])
        if st.button("🔄 Apply Move"):
            index = int(moved_layer.split()[1][:-1]) - 1
            if move_direction == "Up" and index > 0:
                st.session_state.layers[index], st.session_state.layers[index - 1] = st.session_state.layers[index - 1], st.session_state.layers[index]
            elif move_direction == "Down" and index < len(st.session_state.layers) - 1:
                st.session_state.layers[index], st.session_state.layers[index + 1] = st.session_state.layers[index + 1], st.session_state.layers[index]
            st.experimental_rerun()

        col1, col2 = st.columns([3, 1])
        with col1:
            fig, ax = plt.subplots(figsize=(4, 10))
            y = 0
            for i, row in df[::-1].iterrows():
                rect = Rectangle((0, y), 1, row['Thickness'], facecolor=row['Color'], edgecolor='black', hatch=lithology_patterns.get(row['Lithology'], ''))
                ax.add_patch(rect)
                ax.text(0.5, y + row['Thickness']/2, row['Lithology'], ha='center', va='center', fontsize=8)
                y += row['Thickness']
            ax.set_xlim(0, 1)
            ax.set_ylim(0, y)
            ax.axis('off')
            st.pyplot(fig)

        with col2:
            for i, layer in enumerate(df[::-1].to_dict(orient="records")):
                st.markdown(f"**Layer {len(df)-i}:** {layer['Lithology']} ({layer['Thickness']}m)")
                if st.button(f"❌ Delete Layer {len(df)-i}"):
                    del st.session_state.layers[len(df)-i-1]
                    st.experimental_rerun()

        # Mini column preview (smaller size)
        fig_small, ax_small = plt.subplots(figsize=(1, 2))
        y = 0
        for _, row in df[::-1].iterrows():
            ax_small.add_patch(Rectangle((0, y), 1, row['Thickness'], facecolor=row['Color'], edgecolor='black', hatch=lithology_patterns.get(row['Lithology'], '')))
            y += row['Thickness']
        ax_small.set_xlim(0, 1)
        ax_small.set_ylim(0, y)
        ax_small.axis('off')
        st.markdown("### 🔍 Mini Column Preview")
        st.pyplot(fig_small)

        # Facies legend
        st.markdown("### 🧭 Facies Key")
        for facies, desc in facies_legend.items():
            st.markdown(f"**{facies}:** {desc}")
