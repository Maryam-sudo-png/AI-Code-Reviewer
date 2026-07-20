# AICodeReviewer

A CLI tool that reviews source code using an LLM under a locked "Senior Code QA Engineer" persona. It ingests a raw `.py` / `.js` / `.java` file, forces a structured two-part response (bug report + refactored code), validates the response before showing it, and renders the result in the terminal with syntax highlighting.

## Features

- **File ingestion** with graceful handling of missing files, permission errors, and bad encodings
- **Locked system persona** that forces a consistent, non-conversational output format
- **Output validation** — malformed responses (missing/misordered headers) are rejected instead of shown
- **Rich terminal rendering** with Markdown + syntax-highlighted code blocks
- Uses Groq's free-tier API (Llama 3.3 70B)

## How it works

```
raw file  -->  capture_payload()  -->  get_review()  -->  validate_response()  -->  render_output()
```

1. `capture_payload()` reads the target file into memory
2. `get_review()` sends the code to the model with a strict system instruction
3. `validate_response()` checks that both `## BUG_REPORT` and `## REFACTORED_CODE` are present and in order
4. `render_output()` pretty-prints the validated Markdown to the terminal

## Setup

```bash
git clone https://github.com/Maryam-sudo-png/AICodeReviewer.git
cd AICodeReviewer
pip install -r requirements.txt
```

Get a free Groq API key from [console.groq.com/keys](https://console.groq.com/keys), then set it as an environment variable:

```bash
# Windows PowerShell
$env:GROQ_API_KEY="your_key_here"

# macOS/Linux
export GROQ_API_KEY="your_key_here"
```

## Usage

```bash
python code_reviewer.py path/to/file.py
```

## Example output

```
## BUG_REPORT
- The print statement is trying to concatenate a string with an integer, which will cause a TypeError.
- The function does not include any error handling or input validation.

## REFACTORED_CODE
def add_numbers(a, b):
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both inputs must be numbers")
    result = a + b
    print(f"Sum is: {result}")
    return result
```

## Tech stack

- Python
- Groq API (Llama 3.3 70B)
- Rich (terminal rendering)

## License

MIT
