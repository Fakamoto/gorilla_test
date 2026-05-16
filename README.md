# Gorilla Test Assistant

Small macOS CLI that listens for a left Alt keypress, captures the current
screen, and asks a multimodal DSPy program to answer the visible multiple-choice
question.

For background on why this project exists, read the included article:
[Pass any TestGorilla Assessment](blog.md).

## Install

The package name is `gorilla-test-assistant` and it installs the `gorilla-test`
command.

With `uv`:

```bash
uv tool install gorilla-test-assistant
```

With `pip`:

```bash
pip install gorilla-test-assistant
```

This project supports Python `>=3.11,<3.12` because the keyboard listener stack
is known to be safest on Python 3.11.

## API Keys

The default model is `openai/gpt-5.4-mini`, so the default setup is:

```bash
export OPENAI_API_KEY="your-api-key"
```

The CLI accepts any DSPy/LiteLLM-style model name through `--model`. Provider
prefixes like `openai/`, `anthropic/`, and `groq/` are passed through as-is. If
you use an unprefixed model name, the CLI does not rewrite it or assume a
provider.

For common provider-prefixed models, set the standard provider environment
variable:

| Provider prefix | Environment variable |
| --- | --- |
| `openai/` | `OPENAI_API_KEY` |
| `anthropic/` | `ANTHROPIC_API_KEY` |
| `gemini/` or `google/` | `GEMINI_API_KEY` or `GOOGLE_API_KEY` |
| `groq/` | `GROQ_API_KEY` |
| `mistral/` | `MISTRAL_API_KEY` |
| `openrouter/` | `OPENROUTER_API_KEY` |
| `together/` | `TOGETHER_API_KEY` |
| `xai/` | `XAI_API_KEY` |

For another provider, point the CLI at the variable name:

```bash
gorilla-test --model provider/model-name --api-key-env PROVIDER_API_KEY
```

For unprefixed model names, use the environment variables expected by
DSPy/LiteLLM for that model.

## Usage

Start the listener:

```bash
gorilla-test
```

When a multiple-choice question is visible, press the left Alt key. The CLI
prints the structured answer and sends a macOS notification with the selected
option number.

Choose a different model:

```bash
gorilla-test --model openai/gpt-5.4
```

Change the output token budget:

```bash
gorilla-test --max-tokens 8192
```

Show all options:

```bash
gorilla-test --help
```

## Local Development

Run the CLI from this checkout without installing it globally:

```bash
uv run --python 3.11.6 --with . gorilla-test --help
```

Build the package:

```bash
uv build
```

Publish to PyPI with a token:

```bash
export UV_PUBLISH_TOKEN="pypi-..."
uv publish
```

## Notes

- The tool is designed for macOS.
- macOS may require Accessibility and Screen Recording permissions for the
  terminal app running the CLI.
- DSPy uses `ChainOfThought`, so reasoning is produced by the program instead of
  being modeled as a manual Pydantic output field.
- Reasoning effort defaults to `high`.
- The default max token budget is `8192`.

## Disclaimer

This project highlights the need for better assessment methods in tech hiring.
Use it responsibly and respect the terms of service for any platform involved.
