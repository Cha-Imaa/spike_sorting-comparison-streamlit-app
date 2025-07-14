import streamlit as st
from pathlib import Path
import re

# === CONFIGURATION ===
root_dir = Path("interactive_matched_neurons")
unmatched1_dir = root_dir / "unmatched_algo1"
unmatched2_dir = root_dir / "unmatched_algo2"

# === PAGE SETTINGS ===
st.set_page_config(page_title="Neuron Comparison Dashboard", layout="wide")
st.title("Neuron Matching Dashboard")

# === CUSTOM STYLING ===
st.markdown("""
<style>
iframe {
    border: none;
    height: 400px;
    width: 100%;
    overflow: hidden;
}
.stat-card {
    display: inline-block;
    background: #f3f6fa;
    border-radius: 10px;
    padding: 15px 20px;
    margin: 5px 10px;
    font-size: 15px;
    box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
}
.stat-card strong {
    display: block;
    font-size: 17px;
    color: #034694;
}
.slider-label {
    font-size: 18px;
    margin-top: 10px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# === LOAD GLOBAL STATS ===
summary_data = {}
summary_path = root_dir / "global_summary.txt"
if summary_path.exists():
    with open(summary_path) as f:
        for line in f:
            if ':' in line:
                key, val = line.strip().split(":", 1)
                summary_data[key.strip()] = val.strip()

# === LOAD MATCHED PAIRS ===
matched_pairs = {}
for file in root_dir.glob("*_algo1.html"):
    base = file.stem.replace("_algo1", "")
    matched_pairs[base] = {"algo1": file.name}
for file in root_dir.glob("*_algo2.html"):
    base = file.stem.replace("_algo2", "")
    if base in matched_pairs:
        matched_pairs[base]["algo2"] = file.name
for file in root_dir.glob("*_info.txt"):
    base = file.stem.replace("_info", "")
    if base in matched_pairs:
        matched_pairs[base]["info"] = file.name

# === TABS ===
tabs = st.tabs(["\U0001F4CA Global Statistics", "\U0001F517 Matched Neurons", "\U0001F9EC Unmatched Neurons"])

# === TAB 1: GLOBAL STATS ===
with tabs[0]:
    st.subheader("Global Statistics")
    stat_layout = ""
    for label in ["Algo1 neurons", "Algo2 neurons", "Total comparisons", "Matched pairs", "Average match score"]:
        if label in summary_data:
            title = label.replace("Algo1", "Kilosort4").replace("Algo2", "Jim's")
            stat_layout += f"""<div class='stat-card'>
                <strong>{summary_data[label]}</strong>
                {title}
            </div>"""
    st.markdown(stat_layout, unsafe_allow_html=True)

# === TAB 2: MATCHED NEURONS ===
with tabs[1]:
    st.subheader("Matched Neurons (Kilosort4 vs Jim's)")
    if matched_pairs:
        pair_names = list(matched_pairs.keys())
        selected_index = st.slider("Select Matched Neuron Pair", 0, len(pair_names) - 1, 0)
        selected_pair = pair_names[selected_index]
        pair_data = matched_pairs[selected_pair]

        # Parse and render stats
        stat_data = []
        if "info" in pair_data:
            with open(root_dir / pair_data["info"]) as f:
                lines = f.readlines()
                for line in lines:
                    match = re.match(r"^(.*?):\s*(.*)$", line.strip())
                    if match:
                        label, value = match.groups()

                        # Clean labels
                        if label == "Neuron Algo1 ID":
                            label = "Kilosort4 Neuron ID"
                        elif label == "Neuron Algo2 ID":
                            label = "Jim's Neuron ID"
                        elif label == "Algo1 spikes":
                            label = "Kilosort4 Spikes"
                        elif label == "Algo2 spikes":
                            label = "Jim's Spikes"
                        elif label == "Matched spikes":
                            label = "Matched Spikes"
                        elif label == "Match score":
                            label = "Match Score"

                        stat_data.append((label, value))

        # Render stats as Streamlit columns
        cols = st.columns(len(stat_data))
        for col, (label, value) in zip(cols, stat_data):
            with col:
                st.markdown(f"<div class='stat-card'><strong>{value}</strong>{label}</div>", unsafe_allow_html=True)

        # Show matched plots
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Kilosort4")
            st.components.v1.html((root_dir / pair_data["algo1"]).read_text(), height=400)

        with col2:
            st.markdown("#### Jim's")
            st.components.v1.html((root_dir / pair_data["algo2"]).read_text(), height=400)
    else:
        st.info("No matched neuron pairs found.")

# === TAB 3: UNMATCHED NEURONS ===
with tabs[2]:
    col1, col2 = st.columns(2)

    def display_unmatched(title, folder_path, key_prefix):
        files = sorted(folder_path.glob("*.html"))
        if not files:
            return
        idx = st.slider(f"{title} Slider", 0, len(files)-1, 0, key=key_prefix)
        file = files[idx]
        st.markdown(f"<div class='slider-label'>{title} - Neuron {file.stem.split('_')[-1]}</div>", unsafe_allow_html=True)
        st.components.v1.html(file.read_text(), height=300)

    with col1:
        display_unmatched("Kilosort4 Unmatched", unmatched1_dir, "u1")
    with col2:
        display_unmatched("Jim's Unmatched", unmatched2_dir, "u2")
