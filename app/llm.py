import os
import json
from openai import OpenAI
from .schemes import SummarizeResponse

# MODEL = "meta-llama/Meta-Llama-3.1-8B-Instruct"
# MODEL = "Qwen/Qwen3-30B-A3B-Instruct-2507"
MODEL = "meta-llama/Llama-3.3-70B-Instruct"

client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=os.environ.get("NEBIUS_API_KEY"),
)


def call_llm(context: str):
    prompt = f"""
    You are analyzing a GitHub repository and giving a structured summary. 
    Return ONLY a valid JSON object. 
    Do not include any introductory text, markdown formatting, or code blocks.

    Follow the below JSON schema strictly, ensuring all fields are present and correctly formatted:

    {{
    "summary": "A human-readable description of what the project does.",
    "technologies": ["List of main technologies, languages, and frameworks used.],
    "structure": "Brief description of the project structure."
    }}

    Constraints:
    1. Valid JSON is mandatory.
    2. summary:
        - Ensure the summary captures the project's unique value proposition and how it works in a human-readable way. 
        - Avoid marketing language or subjective adjectives.
        - Exactly ONE sentence is sufficient.
    3. technologies:
        - Prioritize primary runtime technologies over dev-dependencies.
        - List ONLY the 6 most important technologies (core languages, frameworks, and critical dependencies) without duplicates.
        - Avoid listing build tools or linters unless central to the project.
        - DO NOT list the project name.
        - DO NOT infer low-level technologies unless explicitly declared.
        - Avoid generic terms like "Engine", "Framework", or "LLMs".
    4. structure:
        - Specifically, a technical description of the file layout. 
        - You MUST mention at least 3 specific top-level directory names and what they contain. 
        - Keep the structure description UP TO 2 concise sentences.

    Repository Context:
    {context}
    """

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You produce human-readable and structured repository summaries."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.0,
    )

    text = response.choices[0].message.content

    # Validate JSON before returning
    try:
        parsed = SummarizeResponse(**json.loads(text))
    except json.JSONDecodeError:
        raise ValueError("LLM returned invalid JSON")

    return parsed
