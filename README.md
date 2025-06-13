# Image Generator

This project includes `get_image.py`, a Streamlit app for generating images using the [Pollinations API](https://pollinations.ai/). The app allows you to:

- Enter a text prompt describing the image you want to generate.
- Select image width and height.
- Choose a random or specific seed for reproducibility.
- Select the model to use (`flux` or `turbo`).
- Optionally remove the Pollinations logo from the generated image.
- View the generated image directly in the browser.
- Save the generated image and its parameters to a folder of your choice (default is your `Pictures` folder). The parameters are saved in a `.txt` file alongside the image.

## Usage

1. Install dependencies:
    ```
    pip install streamlit requests
    ```

2. Run the app:
    ```
    streamlit run get_image.py
    ```

3. Fill in the prompt and parameters in the web interface, click **Generate Image**, and then use the save option to store the image and parameters.

## Notes

- The generated image and a text file with all parameters used are saved in the selected folder.
- The default save location is your `Pictures` folder, but you can change it in the app.
