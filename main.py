# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "dspy>=3.2.1",
#     "pillow>=10.4.0",
#     "pydantic>=2.9.2",
#     "pync>=2.0.3",
#     "pynput>=1.7.7",
# ]
# ///

import os

import dspy
from dspy.adapters.baml_adapter import BAMLAdapter
from PIL import ImageGrab
from pydantic import BaseModel, Field, model_validator
from pynput import keyboard
import pync


MODEL_NAME = "openai/gpt-5.4-mini"
REASONING_EFFORT = "low"
VERBOSITY = "low"


class MultipleChoiceResponse(BaseModel):
    """Structured answer for a visible multiple-choice question."""

    explanation_of_question: str = Field(
        description="Brief explanation of what the question is asking."
    )
    reasoning: str = Field(description="Concise reasoning behind the selected answer.")
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
    def validate_answer(self):
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
explanation and reasoning short.
"""


class MultipleChoiceSignature(dspy.Signature):
    screenshot: dspy.Image = dspy.InputField(
        desc="Screenshot containing the assessment question and visible answer options."
    )
    result: MultipleChoiceResponse = dspy.OutputField(
        desc="Structured answer for the visible question."
    )


MultipleChoiceSignature = MultipleChoiceSignature.with_instructions(
    QUESTION_INSTRUCTIONS
)
answer_question = dspy.Predict(MultipleChoiceSignature)


def configure_dspy() -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY before running the assistant.")

    lm = dspy.LM(
        MODEL_NAME,
        temperature=1.0,
        max_tokens=4096,
        reasoning_effort=REASONING_EFFORT,
        verbosity=VERBOSITY,
        allowed_openai_params=["reasoning_effort", "verbosity"],
        api_key=api_key,
    )

    dspy.configure(lm=lm, adapter=BAMLAdapter())
    dspy.configure_cache(enable_disk_cache=False, enable_memory_cache=False)


def get_multiple_choice_response(image) -> MultipleChoiceResponse:
    prediction = answer_question(screenshot=dspy.Image(image))
    return prediction.result


def notify(message: str, title: str = "Gorilla Test Assistant") -> None:
    pync.Notifier.notify(message, title=title)


def format_answer(response: MultipleChoiceResponse) -> str:
    if response.is_single_answer:
        return str(response.answer[0])

    return ", ".join(str(option) for option in response.answer)


def on_press(key) -> None:
    if key != keyboard.Key.alt_l:
        return

    notify("Processing question...")

    try:
        response = get_multiple_choice_response(ImageGrab.grab())
        print(response.model_dump_json(indent=2))
        notify(f"Answer: {format_answer(response)}")
    except Exception as exc:
        print(f"Error: {exc}")
        notify("An error occurred")


def main() -> None:
    configure_dspy()
    print("Listening for left Alt keypresses...")
    notify("Script started")

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


if __name__ == "__main__":
    main()
