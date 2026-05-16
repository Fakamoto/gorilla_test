# Changelog

## 0.1.0 - 2026-05-16

- Packaged the assistant as an installable Typer CLI named `gorilla-test`.
- Added `--model`, `--max-tokens`, and `--api-key-env` CLI options.
- Switched answer generation from `dspy.Predict` to `dspy.ChainOfThought`.
- Removed the manual `reasoning` field from the structured Pydantic answer.
- Set reasoning effort to `high`.
- Increased the default max token budget from `4096` to `8192`.
- Documented `uv` and `pip` installation, provider API key environment variables,
  and PyPI publishing.
