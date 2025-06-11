import streamlit as st
import requests
import random
import urllib.parse
from datetime import datetime
import os
from pathlib import Path

# Sidebar with help link (local help.html)
st.sidebar.markdown(
    '[Help & Documentation](help.html)',
    unsafe_allow_html=True
)

st.title("Pollinations Image Generator")

def load_params_from_file(param_file):
    params = {}
    with open(param_file, "r") as f:
        for line in f:
            if ":" in line:
                key, value = line.split(":", 1)
                params[key.strip().lower()] = value.strip()
    return params

# Option to load parameters from a txt file
with st.expander("Load parameters from saved file"):
    default_param_folder = str(Path.home() / "Pictures")
    param_folder = st.text_input(
        "Folder containing parameter .txt files",
        value=default_param_folder  # Default to Pictures folder
    )

    # Add a refresh button
    if "param_files" not in st.session_state:
        st.session_state.param_files = []

    refresh = st.button("Refresh file list")

    if os.path.isdir(param_folder):
        if refresh or not st.session_state.param_files:
            st.session_state.param_files = sorted(
                [f for f in os.listdir(param_folder) if f.endswith(".txt")],
                reverse=True
            )
        param_files = st.session_state.param_files
    else:
        st.warning("Folder does not exist.")
        param_files = []

    selected_file = st.selectbox(
        "Select a parameter .txt file",
        options=param_files if param_files else ["No .txt files found"],
        index=0
    )

    if st.button("Load Parameters from File"):
        if param_files and selected_file != "No .txt files found":
            param_file_path = os.path.join(param_folder, selected_file)
            params = load_params_from_file(param_file_path)
            # Set session state for each parameter if present
            if "prompt" in params:
                st.session_state.prompt = params["prompt"]
            if "width" in params:
                st.session_state.width = int(params["width"])
            if "height" in params:
                st.session_state.height = int(params["height"])
            if "seed" in params:
                st.session_state.seed_input = params["seed"]
            if "model" in params:
                st.session_state.model = params["model"]
            if "remove logo" in params:
                st.session_state.remove_logo = params["remove logo"].lower() == "true"
            st.success("Parameters loaded! Please check and adjust as needed below.")
        else:
            st.error("File not found or invalid path.")

# Streamlit input widgets for parameters, using session_state if available
prompt = st.text_area(
    "Prompt",
    value=st.session_state.get("prompt", "in the style of a 19th century painting, a young woman holding a small bunch of spring flowers, standing in a field of grass")
)
width = st.number_input("Width", min_value=256, max_value=2048, value=int(st.session_state.get("width", 1024)), step=64)
height = st.number_input("Height", min_value=256, max_value=2048, value=int(st.session_state.get("height", 1024)), step=64)
seed_input = st.text_input("Seed (leave blank for random)", value=st.session_state.get("seed_input", ""))  # Accept blank or number

# Model selection: Turbo or Flux
model = st.selectbox(
    "Model",
    options=["flux", "turbo"],
    index=0 if st.session_state.get("model", "flux") == "flux" else 1
)

remove_logo = st.checkbox("Remove logo", value=st.session_state.get("remove_logo", True))

if "image_bytes" not in st.session_state:
    st.session_state.image_bytes = None

if st.button("Generate Image"):
    # Use random seed if blank, else use entered value
    if seed_input.strip() == "":
        seed = random.randint(0, 999999)
    else:
        try:
            seed = int(seed_input)
        except ValueError:
            st.error("Seed must be blank or an integer.")
            st.stop()
    st.session_state.seed = seed
    with st.spinner("Generating image..."):
        encoded_prompt = urllib.parse.quote(prompt)
        image_url = (
            f"https://pollinations.ai/p/{encoded_prompt}"
            f"?width={width}&height={height}&seed={seed}&model={model}&remove_logo={str(remove_logo).lower()}"
        )
        response = requests.get(image_url)
        if response.status_code == 200:
            st.session_state.image_bytes = response.content
            st.image(response.content, caption="Generated Image")
        else:
            st.session_state.image_bytes = None
            st.error("Failed to generate image.")

def save_image_and_params(folder_path):
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"generated_image_{now}.jpg"
    param_filename = f"generated_image_{now}_params.txt"
    image_path = os.path.join(folder_path, filename)
    param_path = os.path.join(folder_path, param_filename)
    with open(image_path, "wb") as f:
        f.write(st.session_state.image_bytes)
    with open(param_path, "w") as f:
        f.write(
            f"Prompt: {prompt}\n"
            f"Width: {width}\n"
            f"Height: {height}\n"
            f"Seed: {st.session_state.seed}\n"
            f"Model: {model}\n"
            f"Remove logo: {remove_logo}\n"
        )
    return filename, param_filename

if st.session_state.image_bytes:
    # Default to Pictures folder
    default_folder = str(Path.home() / "Pictures")
    folder = st.text_input("Folder to save image and parameters", value=default_folder)
    if st.button("Save Image to Selected Folder"):
        if not os.path.isdir(folder):
            st.error("Selected folder does not exist.")
        else:
            filename, param_filename = save_image_and_params(folder)
            st.success(f"Image saved as {filename} and parameters as {param_filename} in {folder}.")

# To run: streamlit run get_image.py


