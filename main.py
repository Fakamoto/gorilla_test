import io
from typing import List
import marvin
import pynput
from PIL import ImageGrab
import pydantic
import pync

class MultipleChoiceResponse(pydantic.BaseModel):
    """
    Model containing the explanation of the question, reasoning behind the answer, and the answer itself.
    """

    explanation_of_question: str = pydantic.Field(
        ..., description="Explanation of the test question."
    )
    reasoning: str = pydantic.Field(..., description="Reasoning behind the answer.")
    is_single_answer: bool = pydantic.Field(
        ..., description="True if the question requires a single answer."
    )
    is_multiple_answer: bool = pydantic.Field(
        ..., description="True if multiple answers are allowed."
    )
    answer: list[int] = pydantic.Field(
        ...,
        description="Answer(s) to the question, depending on its requirements. The number of checkboxes may vary. If the question requires selecting a single checkbox, provide a single value (e.g., [3]). If the question allows selecting multiple checkboxes, provide a list of the selected values (e.g., [2, 4, 5]).",
    )

    @pydantic.model_validator(mode="after")
    def validate_answer_conditions(self):
        self.answer = sorted(self.answer)
        if self.is_single_answer:
            if len(self.answer) != 1:
                raise ValueError("If 'is_single_answer' is True, 'answer' must contain exactly one item.")
            if self.is_multiple_answer:
                raise ValueError("'is_multiple_answer' must be False when 'is_single_answer' is True.")
        return self

def get_multiple_choice_response(image) -> MultipleChoiceResponse:
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img = marvin.Image(data=img_bytes.getvalue())
    return marvin.cast(img, target=MultipleChoiceResponse)

def notify(message: str, title: str = "Gorilla Test 🦍"):
    pync.Notifier.notify(message, title=title)

def on_press(key):
    if key == pynput.keyboard.Key.alt_l:
        notify("Processing question... 🤔")
        try:
            image = ImageGrab.grab()
            response = get_multiple_choice_response(image)
            print(response)
            answer = response.answer[0] if response.is_single_answer else ", ".join(map(str, response.answer))
            notify(f"Answer: {answer}")
        except Exception as e:
            print(f"Error: {e}")
            notify("An error occurred")

def main():
    print("Listening for keypresses...")
    notify("Script started")
    with pynput.keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    main()
