# Gorilla Test Assistant 🦍

This project provides an automated assistant for TestGorilla assessments, demonstrating the potential limitations of traditional multiple-choice testing in the age of AI. This tool is specifically designed for macOS users.

## Background

For context on why this project was created, check out the blog post: [Pass any TestGorilla Assessment 🦍](https://your-blog-url-here.com)

## Features

- Captures screen content on keypress using Pillow (PIL)
- Analyzes multiple-choice questions using GPT-4 Vision via the Marvin library
- Provides discreet answer notifications using pync
- Monitors keyboard input with pynput

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-username/gorilla-test-assistant.git
   cd gorilla-test-assistant
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Ensure you have a valid OpenAI API key and set it as an environment variable:
   ```
   export OPENAI_API_KEY='your-api-key-here'
   ```

## Usage

1. Run the script:
   ```
   python main.py
   ```

2. When you encounter a multiple-choice question:
   - Press the left Alt key
   - Wait for the notification with the suggested answer

## Important Notes

- This tool is for educational and demonstration purposes only.
- Use responsibly and ethically.
- Be aware of the terms of service for any platforms you're using.
- This tool is designed specifically for macOS and may not work on other operating systems.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This project is meant to highlight the need for more advanced and relevant assessment methods in tech hiring. It should not be used to gain unfair advantages in actual assessments. It is specifically designed for macOS users and may not function on other operating systems.
