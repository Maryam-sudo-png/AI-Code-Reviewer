"""
Intelligent Code Reviewer & Explainer
--------------------------------------
A CLI tool that ingests a raw source file, sends it to a model under a
locked "Senior Code QA Engineer" persona, validates the structured
response, and renders it with syntax-highlighted Markdown in the
terminal.

Usage:
    python code_reviewer.py path/to/file.py

Setup:
    pip install -r requirements.txt
    set GROQ_API_KEY=your_key_here   (Windows PowerShell: $env:GROQ_API_KEY="...")
"""

import os
import sys
import argparse

from groq import Groq
from rich.console import Console
from rich.markdown import Markdown

# ----------------------------------------------------------------------
# Config — single place to swap the model if the free-tier lineup shifts
# ----------------------------------------------------------------------
MODEL_NAME = "llama-3.3-70b-versatile"

SYSTEM_INSTRUCTION = """You are a cold, analytical Senior Code QA Engineer.

You review the code you are given and respond with EXACTLY two sections,
in this order, using these exact Markdown headers:

## BUG_REPORT
- Direct, concise bullet points only.
- Cover syntax anomalies, logic bugs, and performance issues.
- No praise, no filler, no conversational language.

## REFACTORED_CODE
- A single fenced code block containing the corrected, compilable code.
- Nothing outside the fenced block in this section.

Do not write greetings, summaries, or any text outside these two sections.
Do not say "Sure" or "Here is your code" or similar conversational filler.
"""

REQUIRED_HEADERS = ["## BUG_REPORT", "## REFACTORED_CODE"]


# ----------------------------------------------------------------------
# Phase 1: Input & Payload Capture
# ----------------------------------------------------------------------
def capture_payload(filepath: str) -> str:
    """Read a source file into a string, preserving it exactly as-is.
    Exits cleanly (no raw traceback) on the three expected failure modes.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: file not found -> {filepath}")
        sys.exit(1)
    except PermissionError:
        print(f"Error: permission denied reading -> {filepath}")
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"Error: could not decode file (unexpected encoding) -> {filepath}")
        sys.exit(1)


# ----------------------------------------------------------------------
# Phase 2: Context Orchestration
# ----------------------------------------------------------------------
def get_review(code: str, filename: str) -> str:
    """Send the code to the model under the locked system instruction."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY environment variable is not set.")
        sys.exit(1)

    client = Groq(api_key=api_key)

    user_prompt = f"Review the following file: {filename}\n\n```\n{code}\n```"

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content or ""


def validate_response(response_text: str) -> bool:
    """Reject the response if both required headers aren't present in order."""
    if not response_text:
        return False
    idx_bug = response_text.find(REQUIRED_HEADERS[0])
    idx_refactor = response_text.find(REQUIRED_HEADERS[1])
    if idx_bug == -1 or idx_refactor == -1:
        return False
    return idx_bug < idx_refactor


# ----------------------------------------------------------------------
# Phase 3: Rich Terminal Rendering
# ----------------------------------------------------------------------
def render_output(response_text: str) -> None:
    """Pretty-print the validated Markdown with syntax highlighting."""
    console = Console()
    console.print(Markdown(response_text))


# ----------------------------------------------------------------------
# CLI wiring
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Analyze a source file and get a structured bug report + refactored code."
    )
    parser.add_argument("filepath", help="Path to the .py/.js/.java file to review")
    args = parser.parse_args()

    console = Console()

    code = capture_payload(args.filepath)

    with console.status("[bold cyan]Sending code to the model for review..."):
        review = get_review(code, args.filepath)

    if not validate_response(review):
        console.print(
            "[bold red]Validation failed:[/bold red] the model response was "
            "malformed (missing or misordered ## BUG_REPORT / ## REFACTORED_CODE headers). "
            "No output was rendered."
        )
        sys.exit(1)

    render_output(review)


if __name__ == "__main__":
    main()
