# Using the pollinations pypi package

import pollinations

model = pollinations.Image(
    model="flux",
    width=1024,
    height=1024,
    seed=42
)

model.Generate(
    prompt="A beautiful landscape",
    save=True
)
# The image will be saved in the current directory with a filename based on the prompt and parameters.