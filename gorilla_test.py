import json
import os
from dataclasses import dataclass
from typing import Annotated, Any, Final, Self

import dspy
from dspy.adapters.baml_adapter import BAMLAdapter
from PIL import Image, ImageGrab
from pydantic import BaseModel, Field, model_validator
from pynput import keyboard
import pync
import typer


APP_NAME: Final = "Gorilla Test Assistant"
DEFAULT_MODEL: Final = "openai/gpt-5.4-mini"
DEFAULT_MAX_TOKENS: Final = 8192
REASONING_EFFORT: Final = "high"
VERBOSITY: Final = "low"

API_KEY_ENV_BY_PROVIDER: Final[dict[str, tuple[str, ...]]] = {
    "anthropic": ("ANTHROPIC_API_KEY",),
    "deepseek": ("DEEPSEEK_API_KEY",),
    "gemini": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
    "google": ("GOOGLE_API_KEY", "GEMINI_API_KEY"),
    "groq": ("GROQ_API_KEY",),
    "mistral": ("MISTRAL_API_KEY",),
    "openai": ("OPENAI_API_KEY",),
    "openrouter": ("OPENROUTER_API_KEY",),
    "together": ("TOGETHER_API_KEY",),
    "xai": ("XAI_API_KEY",),
}


class MultipleChoiceAnswer(BaseModel):
    """Structured answer for a visible multiple-choice question."""

    explanation_of_question: str = Field(
        description="Brief explanation of what the question is asking."
    )
    is_single_answer: bool = Field(
        description="True when the question requires exactly one selected option."
    )
    is_multiple_answer: bool = Field(
        description="True when the question allows more than one selected option."
    )
    answer: list[int] = Field(
        description=(
            "One-based option number or numbers to select. "
            "Use [3] for the third option, or [2, 4] for multiple choices."
        )
    )

    @model_validator(mode="after")
    def validate_answer(self) -> Self:
        self.answer = sorted(set(self.answer))

        if self.is_single_answer == self.is_multiple_answer:
            raise ValueError("Exactly one answer mode must be true.")

        if self.is_single_answer and len(self.answer) != 1:
            raise ValueError("Single-answer questions must return exactly one option.")

        if not self.answer:
            raise ValueError("At least one answer option is required.")

        return self


QUESTION_INSTRUCTIONS = """
Analyze the screenshot of a multiple-choice assessment question.

Return the answer using one-based option numbers in the order the options appear on
screen. Decide whether the UI asks for one answer or multiple answers. Keep the
explanation short. Chain-of-thought reasoning is handled by DSPy separately.
"""


class MultipleChoiceSignature(dspy.Signature):
    screenshot: dspy.Image = dspy.InputField(
        desc="Screenshot containing the assessment question and visible answer options."
    )
    result: MultipleChoiceAnswer = dspy.OutputField(
        desc="Structured answer for the visible question."
    )


MultipleChoiceSignature = MultipleChoiceSignature.with_instructions(
    QUESTION_INSTRUCTIONS
)
answer_question = dspy.ChainOfThought(MultipleChoiceSignature)


@dataclass(frozen=True)
class MultipleChoiceResult:
    answer: MultipleChoiceAnswer
    reasoning: str


def get_api_key_env_names(model: str, api_key_env: str | None) -> tuple[str, ...]:
    if api_key_env:
        return (api_key_env,)

    if "/" not in model:
        return ()

    provider = model.split("/", maxsplit=1)[0].lower()
    return API_KEY_ENV_BY_PROVIDER.get(provider, ())


def resolve_api_key(model: str, api_key_env: str | None) -> str | None:
    env_names = get_api_key_env_names(model, api_key_env)

    for env_name in env_names:
        api_key = os.getenv(env_name)
        if api_key:
            return api_key

    if env_names:
        expected_env = " or ".join(env_names)
        raise RuntimeError(
            f"Set {expected_env} before running the assistant, "
            "or pass --api-key-env with the environment variable to use."
        )

    return None


def configure_dspy(
    model: str,
    max_tokens: int,
    api_key_env: str | None,
) -> None:
    api_key = resolve_api_key(model, api_key_env)
    lm_kwargs: dict[str, Any] = {
        "temperature": 1.0,
        "max_tokens": max_tokens,
        "reasoning_effort": REASONING_EFFORT,
        "verbosity": VERBOSITY,
        "allowed_openai_params": ["reasoning_effort", "verbosity"],
    }

    if api_key is not None:
        lm_kwargs["api_key"] = api_key

    lm = dspy.LM(
        model,
        **lm_kwargs,
    )

    dspy.configure(lm=lm, adapter=BAMLAdapter())
    dspy.configure_cache(enable_disk_cache=False, enable_memory_cache=False)


def get_multiple_choice_response(image: Image.Image) -> MultipleChoiceResult:
    prediction: Any = answer_question(screenshot=dspy.Image(image))
    answer = MultipleChoiceAnswer.model_validate(prediction.result)
    reasoning = str(getattr(prediction, "reasoning", "")).strip()

    return MultipleChoiceResult(answer=answer, reasoning=reasoning)


def notify(message: str, title: str = APP_NAME) -> None:
    pync.Notifier.notify(message, title=title)


def format_answer(response: MultipleChoiceAnswer) -> str:
    if response.is_single_answer:
        return str(response.answer[0])

    return ", ".join(str(option) for option in response.answer)


def format_result(result: MultipleChoiceResult) -> str:
    payload: dict[str, Any] = result.answer.model_dump()

    if result.reasoning:
        payload["reasoning"] = result.reasoning

    return json.dumps(payload, indent=2)


def on_press(key: keyboard.Key | keyboard.KeyCode | None) -> None:
    if key != keyboard.Key.alt_l:
        return

    notify("Processing question...")

    try:
        result = get_multiple_choice_response(ImageGrab.grab())
        print(format_result(result))
        notify(f"Answer: {format_answer(result.answer)}")
    except Exception as exc:
        print(f"Error: {exc}")
        notify("An error occurred")


def run(
    model: Annotated[
        str,
        typer.Option(
            "--model",
            "-m",
            help="DSPy/LiteLLM model name, such as openai/gpt-5.4-mini.",
        ),
    ] = DEFAULT_MODEL,
    max_tokens: Annotated[
        int,
        typer.Option(
            "--max-tokens",
            min=1,
            help="Maximum output tokens requested from the model.",
        ),
    ] = DEFAULT_MAX_TOKENS,
    api_key_env: Annotated[
        str | None,
        typer.Option(
            "--api-key-env",
            help="Environment variable that contains the selected model API key.",
        ),
    ] = None,
) -> None:
    """Analyze visible multiple-choice questions from a macOS screenshot."""
    try:
        configure_dspy(model=model, max_tokens=max_tokens, api_key_env=api_key_env)
    except RuntimeError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    print("Listening for left Alt keypresses...")
    notify("CLI started")

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


def main() -> None:
    typer.run(run)


if __name__ == "__main__":
    main()
