#!/usr/bin/env python
import argparse
import json
from slides import load_vector_database, generate_slides_from_headings, generate_grant_proposal_from_headings

def main():
    parser = argparse.ArgumentParser(description="Generate content using GPU resources from tmux.")
    parser.add_argument("--mode", type=str, required=True, choices=["slides", "grant"], 
                        help="Generation mode: 'slides' or 'grant'")
    parser.add_argument("--headings", type=str, default="", 
                        help="Slide headings (with newline separation). Required for slides mode.")
    parser.add_argument("--template_type", type=str, choices=["proposal", "rfp"], 
                        help="Grant template type: 'proposal' or 'rfp'. Required for grant mode.")
    parser.add_argument("--json_data", type=str, default="", 
                        help="JSON data for grant generation. Required for grant mode.")
    
    args = parser.parse_args()
    
    # Load resources for generation
    db, docs_retrieval_model, all_images, pipe, processor = load_vector_database()

    if args.mode == "slides":
        if not args.headings:
            raise ValueError("Slide headings are required for slides mode.")
        
        # Generate the presentation
        ppt_path = generate_slides_from_headings(db, docs_retrieval_model, all_images, pipe, processor, args.headings)
        print(f"Presentation generated at: {ppt_path}")
        
    elif args.mode == "grant":
        if not args.template_type or not args.json_data:
            raise ValueError("Template type and JSON data are required for grant mode.")
        
        # Parse the JSON data
        try:
            json_data = json.loads(args.json_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data: {e}")
        
        # Generate the grant document
        print("Generating grant document...")
        pdf_path = generate_grant_proposal_from_headings(db, docs_retrieval_model, all_images, pipe, processor, json_data, args.template_type)
        print(f"Grant document generated at: {pdf_path}")
    
    else:
        raise ValueError(f"Unknown mode: {args.mode}")

if __name__ == "__main__":
    main()