import boto3
import json
import os
from dotenv import load_dotenv
import botocore.config
import re

def sanitize_claude_output(output_str: str) -> str:
    output_str = output_str.strip().split("```")[0].strip()
    output_str = re.sub(r'(?<!\\)\\n', '\\\\n', output_str)
    output_str = re.sub(r'[\x00-\x1F\x7F]', '', output_str)
    return output_str

load_dotenv()

bedrock_config = botocore.config.Config(
    connect_timeout=10,
    read_timeout=300,
    retries={"max_attempts": 3}
)

bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1", config=bedrock_config)

def call_claude(
    query_or_answers,
    context=None,
    image_context=None,
    mode="default",
    template_name=None,
    template_fields=None,
    debug=False
):

    if mode == "slides":
        
        system_prompt = """
You are generating content for a PowerPoint slide deck. You will receive structured input and relevant context retrieved from documents.

Your task is to return a valid **JSON array** of slides that will be directly rendered into a presentation.

---

Output Format:

Title Slide (only once, first slide):
{
  "id": "slide-0",
  "type": "title",
  "title_text": "<Main Title>",
  "subtitle_text": "<Short Subtitle or Tagline>"
}

Section Header Slide (if applicable):
{
  "id": "slide-<number>",
  "type": "section",
  "section_title": "<Name of the Section>"
}

Regular Content Slide:
{
  "id": "slide-<number>",
  "type": "content",
  "title_text": "<Heading>",
  "text": [
    "<Bullet 1 (≤10 words)>",
    "<Bullet 2>",
    "... (up to 5 total)"
  ],
  "image_index": <optional image index from image_context>
}

---

Guidelines:
- Output only valid, parseable JSON (no markdown or explanation).
- Use the `"text"` key (not "bullets") for bullet points.
- Use the `image_index` field only if an image clearly matches the slide.
- Use the provided context and image summaries.
- Avoid long paragraphs—keep bullets ≤10 words, focused and readable.

Begin with slide-0 and increment IDs per slide. Output only the final JSON array.
"""


    elif mode == "grant":
        field_list = template_fields.get(template_name, [])
        system_prompt = f"""
You are a professional grant-writing assistant.

Your task is to generate a well-structured grant proposal in **valid JSON format** using the template '{template_name}'.

Instructions:
- **Return ONLY valid JSON** — no markdown, explanations, or commentary.
- JSON **must be parseable by `json.loads()`** in Python. All strings must be properly quoted and escaped.
- Ensure **every newline character is escaped as `\\n`**.
- Use the following top-level keys **exactly**: {field_list}
- Prioritize completeness and correctness. If the prompt is too long to complete all fields:
    - **Only fill as many fields as will safely fit within the token limit.**
    - Do **not truncate** in the middle of a field or value.
    - Wrap up cleanly with a valid closing brace (`}}`).

Style:
- Use clear, structured paragraphs.
- Expand on user context using realistic examples, numbers, and timelines.
- Be concise and informative — avoid fluff, but keep tone formal and persuasive.

Example JSON structure:
{{
  "introduction": "...",
  "statement_of_need": "...",
  ...
}}

Begin now.
"""
    else:
        system_prompt = "You are a helpful assistant. Respond clearly and concisely."

    # Merge text + image context
    context_text = "\n\n".join([doc.page_content for doc in context]) if context else ""
    if image_context:
        context_text = image_context + "\n\n" + context_text

    input_text = (
        system_prompt.strip() +
        "\n\nContext:\n" + context_text.strip() +
        "\n\nRequest:\n" + json.dumps(query_or_answers, indent=2) +
        "\n\nBot:"
    )

    if debug:
        print("\n================== FULL PROMPT ==================\n")
        print(input_text)
        print("\n=================================================\n")

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4000,
        "messages": [{"role": "user", "content": input_text}]
    }

    response = bedrock_client.invoke_model(
        body=json.dumps(payload),
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        contentType="application/json",
        accept="application/json"
    )

    response_body = json.loads(response["body"].read())
    raw_text = response_body['content'][0]['text']

    # Save raw output to file
    with open("claude_raw_output.txt", "w", encoding="utf-8") as f:
        f.write(raw_text)

    clean_output = sanitize_claude_output(raw_text)

    if debug:
        print("\n================ SANITIZED OUTPUT ================\n")
        print(clean_output)
        print("\n==================================================\n")

    return clean_output
