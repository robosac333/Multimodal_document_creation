import argparse
import json
import os
from create_documents import (
    generate_slides_from_headings,
    generate_grant_from_inputs
)

def main():
    parser = argparse.ArgumentParser(description="Generate content using GPU resources from tmux.")
    parser.add_argument("--mode", type=str, required=True, choices=["slides", "grant"],
                        help="Generation mode: 'slides' or 'grant'")
    parser.add_argument("--template_type", type=str, required=False,
                        help="Template name (e.g., 'IC-Grant-Application', 'Generic-Grant-Proposal')")
    parser.add_argument("--json_data", type=str, help="JSON string containing input")
    parser.add_argument("--json_file", type=str, help="Path to JSON file containing input")

    args = parser.parse_args()

    if args.mode == "slides":
        if not args.json_file:
            raise ValueError("--json_file is required for slides mode.")
        if not os.path.exists(args.json_file):
            raise FileNotFoundError(f"JSON file not found: {args.json_file}")

        with open(args.json_file, "r") as f:
            user_json = json.load(f)

        ppt_path = generate_slides_from_headings(user_json)
        print(f"[slides] Presentation generated at: {ppt_path}")


    elif args.mode == "grant":
        if not args.template_type:
            raise ValueError("Template type is required for grant mode.")

        if args.json_file:
            if not os.path.exists(args.json_file):
                raise FileNotFoundError(f"JSON file not found: {args.json_file}")
            with open(args.json_file, "r") as f:
                json_data = json.load(f)
        elif args.json_data:
            try:
                json_data = json.loads(args.json_data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON string: {e}")
        else:
            raise ValueError("Either --json_file or --json_data must be provided for grant mode.")

        print(f"[grant] Generating DOCX using template: {args.template_type}")
        docx_path = generate_grant_from_inputs(json_data)
        print(f"[grant] DOCX generated at: {docx_path}")

if __name__ == "__main__":
    main()
