# Gorilla Test Assistant 🦍

This project is a small macOS proof of concept for screenshot-based multiple-choice analysis. It was built to show how traditional assessment formats can break down in the age of multimodal AI.

## Background

For context on why this project was created, read the blog post: [Pass any TestGorilla Assessment 🦍](https://blog.fgoiriz.com/posts/testgorilla/).

## Features

- Captures the screen on a left Alt keypress
- Analyzes visible multiple-choice questions with DSPy and `gpt-5.4-mini`
- Returns structured answers with concise reasoning
- Sends macOS notifications with `pync`
- Uses inline `uv` script dependencies in `main.py`

## Setup

1. Install `uv`.

   On macOS, Homebrew is the simplest option:

   ```bash
   brew install uv
   ```

2. Clone the repository:

   ```bash
   git clone git@github.com:Fakamoto/gorilla_test.git
   cd gorilla_test
   ```

3. Set your OpenAI API key:

   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

## Usage

Run the script with `uv`:

```bash
uv run main.py
```

When a multiple-choice question is visible, press the left Alt key and wait for the notification with the suggested answer.

## Notes

- This is designed for macOS.
- `uv` reads the dependencies directly from `main.py`, so there is no `requirements.txt`.
- The model is configured in `main.py` as `openai/gpt-5.4-mini`.
- Use responsibly and respect the terms of service for any platform involved.

## Disclaimer

This project is meant to highlight the need for more advanced and relevant assessment methods in tech hiring. It should not be used to gain unfair advantages in actual assessments.
