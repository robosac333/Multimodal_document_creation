import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")

def call_claude(query, context, image_context=None, mode="default"):
    """
    Generate responses from AWS Bedrock and Claude based on the provided mode.
    mode options: 'slides', 'grant', 'report', 'default'
    """

    if mode == "slides":
        system_prompt = """
You will receive a list of slide headings defined by the user. For each heading, generate a JSON object containing the slide content using the retrieved context provided. Structure each slide strictly following this format:

For the title slide (first slide only):
{
  "id": "slide-0",
  "title_text": "<Title Slide Heading>",
  "subtitle_text": "<Concise subtitle based on overall context>",
  "is_title_slide": "yes",
  "source_doc": "<source document name>",
  "page_num": <source page number>
}

For all subsequent slides:
{
  "id": "slide-<slide_number>",
  "title_text": "<User-defined heading>",
  "text": ["<Bullet 1 (max 10 words)>", "<Bullet 2>", ... (up to 5 bullets total)],
  "source_doc": "<source document name>",
  "page_num": <source page number>
}

Guidelines:
- Generate exactly one JSON object per slide heading provided.
- Bullet points must summarize relevant content concisely (≤ 10 words each).
- Maximum 5 bullets per slide.
- Use only the provided retrieved context from the RAG pipeline.
- Return only a valid JSON array of slide objects. No markdown or explanations.

Begin generating slides now.
"""
    elif mode == "report":
        # System prompt for improving the grant content
        system_prompt = """
        Based on your knowledge, please improve this grant proposal JSON. 
        Modify the values to better represent the user's idea while maintaining the same JSON structure.
        Make the content more compelling, clear, and aligned with successful grant proposals.
        """
    else:
        system_prompt = "You are a helpful assistant. Respond clearly and concisely."

    context_text = "\n\n".join([doc.page_content for doc in context])
    if image_context:
        context_text = image_context + "\n\n" + context_text

    input_text = (
        system_prompt +
        "\n\nContext:\n" + context_text +
        "\n\nUser-defined Headings:\n" + query +
        "\n\nBot:"
    )

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2500,
        "messages": [{"role": "user", "content": input_text}]
    }

    response = bedrock_client.invoke_model(
        body=json.dumps(payload),
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        contentType="application/json",
        accept="application/json"
    )

    response_body = json.loads(response['body'].read())
    answer = response_body['content'][0]['text']

    return answer.strip().split("\nBot:")[-1].strip()