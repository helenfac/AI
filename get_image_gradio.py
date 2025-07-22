import gradio as gr
import requests
import random
import urllib.parse
from datetime import datetime
import os
from pathlib import Path
import platform

# --- Helper functions ---

def load_params_from_file(param_file):
    params = {}
    with open(param_file, "r") as f:
        for line in f:
            if ":" in line:
                key, value = line.split(":", 1)
                params[key.strip().lower()] = value.strip()
    return params

def get_param_files(folder):
    if os.path.isdir(folder):
        return [f for f in os.listdir(folder) if f.endswith(".txt")]
    return []

def generate_image(prompt, width, height, seed_input, model, remove_logo):
    # Use random seed if blank, else use entered value
    if not seed_input.strip():
        seed = random.randint(0, 999999)
    else:
        try:
            seed = int(seed_input)
        except ValueError:
            return None, None, "Seed must be blank or an integer."
    encoded_prompt = urllib.parse.quote(prompt)
    image_url = (
        f"https://pollinations.ai/p/{encoded_prompt}"
        f"?width={width}&height={height}&seed={seed}&model={model}&remove_logo={str(remove_logo).lower()}"
    )
    response = requests.get(image_url)
    if response.status_code == 200:
        return response.content, seed, None
    else:
        return None, None, "Failed to generate image."

def save_image_and_params(image_bytes, prompt, width, height, seed, model, remove_logo, folder_path):
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"generated_image_{now}.jpg"
    param_filename = f"generated_image_{now}_params.txt"
    image_path = os.path.join(folder_path, filename)
    param_path = os.path.join(folder_path, param_filename)
    with open(image_path, "wb") as f:
        f.write(image_bytes)
    with open(param_path, "w") as f:
        f.write(
            f"Prompt: {prompt}\n"
            f"Width: {width}\n"
            f"Height: {height}\n"
            f"Seed: {seed}\n"
            f"Model: {model}\n"
            f"Remove logo: {remove_logo}\n"
        )
    return f"Image saved as {filename} and parameters as {param_filename} in {folder_path}."

# --- Gradio App Logic ---

def main(
    prompt,
    width,
    height,
    seed_input,
    model,
    remove_logo,
    param_folder,
    param_file,
    save_folder,
    load_params,
    save_image
):
    # Load parameters from file if requested
    if load_params and param_file:
        param_path = os.path.join(param_folder, param_file)
        params = load_params_from_file(param_path)
        prompt = params.get("prompt", prompt)
        width = int(params.get("width", width))
        height = int(params.get("height", height))
        seed_input = params.get("seed", seed_input)
        model = params.get("model", model)
        remove_logo = params.get("remove logo", str(remove_logo)).lower() == "true"

    # Generate image
    image_bytes, seed, error = generate_image(prompt, width, height, seed_input, model, remove_logo)
    if error:
        return None, gr.update(value=seed_input), error

    # Save image and params if requested
    msg = ""
    if save_image and image_bytes:
        if not os.path.isdir(save_folder):
            msg = "Selected folder does not exist."
        else:
            msg = save_image_and_params(image_bytes, prompt, width, height, seed, model, remove_logo, save_folder)

    return image_bytes, str(seed), msg

# --- Default folders ---
if platform.system() == "Darwin":
    default_param_folder = str(Path.home() / "Pictures")
else:
    default_param_folder = str(Path.home() / "Pictures")
    if not os.path.isdir(default_param_folder):
        default_param_folder = str(Path.home() / "My Pictures")

# --- Gradio Interface ---

def get_param_file_list(param_folder):
    return gr.Dropdown.update(choices=get_param_files(param_folder))

with gr.Blocks() as demo:
    gr.Markdown("# Image Generator (Gradio Version)")

    with gr.Row():
        with gr.Column():
            prompt = gr.Textbox(
                label="Prompt",
                value="in the style of a 19th century painting, a young woman holding a small bunch of spring flowers, standing in a field of grass",
                lines=3
            )
            width = gr.Number(label="Width", value=1024, minimum=256, maximum=2048, step=64)
            height = gr.Number(label="Height", value=1024, minimum=256, maximum=2048, step=64)
            seed_input = gr.Textbox(label="Seed (leave blank for random)", value="")
            model = gr.Dropdown(["flux", "turbo"], label="Model", value="flux")
            remove_logo = gr.Checkbox(label="Remove logo", value=True)

            gr.Markdown("### Load Parameters from File")
            param_folder = gr.Textbox(label="Parameter Folder", value=default_param_folder)
            param_file = gr.Dropdown(choices=get_param_files(default_param_folder), label="Parameter File")
            refresh_btn = gr.Button("Refresh File List")
            load_params = gr.Checkbox(label="Load Parameters from Selected File", value=False)

            gr.Markdown("### Save Image and Parameters")
            save_folder = gr.Textbox(label="Folder to Save Image", value=default_param_folder)
            save_image = gr.Checkbox(label="Save Image to Selected Folder", value=False)

            generate_btn = gr.Button("Generate Image")

        with gr.Column():
            image_output = gr.Image(label="Generated Image")
            seed_output = gr.Textbox(label="Used Seed")
            msg_output = gr.Textbox(label="Status / Messages")

    # Refresh param file list when folder changes or button pressed
    param_folder.change(
        fn=get_param_file_list,
        inputs=param_folder,
        outputs=param_file
    )
    refresh_btn.click(
        fn=get_param_file_list,
        inputs=param_folder,
        outputs=param_file
    )

    # Generate image and handle parameter loading/saving
    generate_btn.click(
        fn=main,
        inputs=[
            prompt, width, height, seed_input, model, remove_logo,
            param_folder, param_file, save_folder, load_params, save_image
        ],
        outputs=[image_output, seed_output, msg_output]
    )

if __name__ == "__main__":
    demo.launch()