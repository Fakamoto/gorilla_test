from types import SimpleNamespace
import unittest

import gorilla_test


class PredictionParsingTests(unittest.TestCase):
    def test_parse_prediction_validates_dict_result_and_extracts_reasoning(self) -> None:
        prediction = SimpleNamespace(
            reasoning="  option 2 matches the visible question  ",
            result={
                "explanation_of_question": "Pick the correct statement.",
                "is_single_answer": True,
                "is_multiple_answer": False,
                "answer": [2],
            },
        )

        result = gorilla_test.parse_prediction(prediction)

        self.assertIsInstance(result.answer, gorilla_test.MultipleChoiceAnswer)
        self.assertEqual(result.answer.answer, [2])
        self.assertEqual(result.reasoning, "option 2 matches the visible question")

    def test_parse_prediction_accepts_pydantic_result(self) -> None:
        answer = gorilla_test.MultipleChoiceAnswer(
            explanation_of_question="Select every true option.",
            is_single_answer=False,
            is_multiple_answer=True,
            answer=[3, 1, 3],
        )
        prediction = SimpleNamespace(result=answer, reasoning="select both true options")

        result = gorilla_test.parse_prediction(prediction)

        self.assertEqual(result.answer.answer, [1, 3])
        self.assertEqual(result.reasoning, "select both true options")

    def test_parse_prediction_handles_missing_reasoning(self) -> None:
        prediction = SimpleNamespace(
            result={
                "explanation_of_question": "Pick one.",
                "is_single_answer": True,
                "is_multiple_answer": False,
                "answer": [1],
            },
        )

        result = gorilla_test.parse_prediction(prediction)

        self.assertEqual(result.answer.answer, [1])
        self.assertEqual(result.reasoning, "")

    def test_format_result_only_includes_reasoning_when_present(self) -> None:
        answer = gorilla_test.MultipleChoiceAnswer(
            explanation_of_question="Pick one.",
            is_single_answer=True,
            is_multiple_answer=False,
            answer=[1],
        )

        without_reasoning = gorilla_test.MultipleChoiceResult(answer=answer, reasoning="")
        with_reasoning = gorilla_test.MultipleChoiceResult(
            answer=answer,
            reasoning="option 1 is correct",
        )

        self.assertNotIn("reasoning", gorilla_test.format_result(without_reasoning))
        self.assertIn('"reasoning": "option 1 is correct"', gorilla_test.format_result(with_reasoning))


class ApiKeyEnvTests(unittest.TestCase):
    def test_unprefixed_model_does_not_assume_openai(self) -> None:
        self.assertEqual(gorilla_test.get_api_key_env_names("gpt-5-mini", None), ())

    def test_prefixed_model_uses_provider_env(self) -> None:
        self.assertEqual(
            gorilla_test.get_api_key_env_names("openai/gpt-5-mini", None),
            ("OPENAI_API_KEY",),
        )


if __name__ == "__main__":
    unittest.main()
