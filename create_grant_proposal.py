from fpdf import FPDF
import os
import json
from typing import Dict, List, Any, Union

def create_grant_proposal_from_json(json_data):
    """
    Create a PDF document based on the JSON data provided by the UI
    
    Args:
        json_data: Dictionary or JSON string containing proposal content
        
    Returns:
        Path to the generated PDF file
    """
    # Parse JSON string if provided as string
    if isinstance(json_data, str):
        try:
            proposal_data = json.loads(json_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None
    else:
        proposal_data = json_data
    
    # Initialize PDF object
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Set fonts
    pdf.set_font("Arial", "B", 16)
    
    # Title
    title = proposal_data.get("title", "RESEARCH GRANT PROPOSAL")
    pdf.cell(0, 10, title, 0, 1, "C")
    pdf.ln(5)
    
    # Metadata section
    if "metadata" in proposal_data.get("sections", {}):
        metadata = proposal_data["sections"]["metadata"]
        pdf.set_font("Arial", "B", 11)
        
        # Create metadata fields with content
        metadata_fields = [
            ("DATE SUBMITTED", metadata.get("date_submitted", "")),
            ("GRANT NAME", metadata.get("grant_name", "")),
            ("SUBMITTED TO", metadata.get("submitted_to", "")),
            ("ADDRESS OF RECEIVING PARTY", metadata.get("address_of_receiving_party", "")),
            ("SUBMITTED BY", metadata.get("submitted_by", "")),
            ("ADDRESS OF SUBMITTING PARTY", metadata.get("address_of_submitting_party", ""))
        ]
        
        # Display metadata as a table
        for i in range(0, len(metadata_fields), 2):
            if i+1 < len(metadata_fields):
                # Row label
                pdf.cell(95, 10, metadata_fields[i][0], 1, 0)
                pdf.cell(95, 10, metadata_fields[i+1][0], 1, 1)
                
                # Row content
                pdf.set_font("Arial", "", 11)
                pdf.cell(95, 10, metadata_fields[i][1], 1, 0)
                pdf.cell(95, 10, metadata_fields[i+1][1], 1, 1)
                pdf.set_font("Arial", "B", 11)
    
    pdf.ln(10)
    
    # Track section numbers for roman numerals
    section_num = 1
    roman_numerals = ["I", "II", "III", "IV", "V", "VI", "VII", 
                      "VIII", "IX", "X", "XI", "XII", "XIII", "XIV"]
    
    # Process each section
    sections = proposal_data.get("sections", {})
    for section_id, section_data in sections.items():
        # Skip metadata as it's already handled
        if section_id == "metadata":
            continue
        
        # Check if need to add a page break
        if pdf.get_y() > 250:
            pdf.add_page()
        
        # Format section title
        section_title = section_id.replace("_", " ").upper()
        roman_numeral = roman_numerals[section_num-1] if section_num <= len(roman_numerals) else str(section_num)
        formatted_title = f"{roman_numeral}. {section_title}"
        
        # Add section header
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, formatted_title, 0, 1)
        
        # Process section content based on type
        if section_id == "project_team":
            # Team members table
            if section_data:
                # Table header
                pdf.set_font("Arial", "B", 11)
                pdf.cell(65, 10, "NAME & ROLE", 1, 0)
                pdf.cell(65, 10, "QUALIFICATIONS", 1, 0)
                pdf.cell(60, 10, "RESPONSIBILITIES", 1, 1)
                
                # Table content
                pdf.set_font("Arial", "", 11)
                for member in section_data:
                    name_role = member.get("name_and_role", "")
                    qualifications = member.get("qualifications", "")
                    responsibilities = member.get("responsibilities", "")
                    
                    # Handle multiline text
                    lines_name = len(name_role.split('\n'))
                    lines_qual = len(qualifications.split('\n'))
                    lines_resp = len(responsibilities.split('\n'))
                    max_lines = max(lines_name, lines_qual, lines_resp, 1)
                    
                    # Set row height based on content
                    row_height = max(10, max_lines * 5)
                    
                    # Print cells with multiline support
                    pdf.multi_cell(65, row_height, name_role, 1, 'L', False, 0)
                    pdf.multi_cell(65, row_height, qualifications, 1, 'L', False, 0)
                    pdf.multi_cell(60, row_height, responsibilities, 1, 'L', False, 1)
            
        elif section_id == "background":
            # Background subsections
            subsections = [
                ("SCOPE OF PROBLEM", section_data.get("scope_of_problem", "")),
                ("REVIEW OF RELEVANT LITERATURE", section_data.get("review_of_relevant_literature", "")),
                ("WHY THIS STUDY NEEDS TO BE DONE", section_data.get("why_this_study_needs_to_be_done", "")),
                ("THEORETICAL BASIS", section_data.get("theoretical_basis", "")),
                ("LONG-TERM USES OF RESEARCH", section_data.get("long_term_uses_of_research", ""))
            ]
            
            # Add any custom background fields
            for key, value in section_data.items():
                if key not in ["scope_of_problem", "review_of_relevant_literature", 
                              "why_this_study_needs_to_be_done", "theoretical_basis", 
                              "long_term_uses_of_research"]:
                    formatted_key = key.replace("_", " ").upper()
                    subsections.append((formatted_key, value))
            
            # Process each subsection
            for idx, (subsection_title, content) in enumerate(subsections):
                # Add page break if needed
                if pdf.get_y() > 250:
                    pdf.add_page()
                
                # Add subsection header with alpha index
                pdf.set_font("Arial", "B", 11)
                alpha_idx = chr(65 + idx)  # A, B, C, etc.
                pdf.cell(0, 10, f"{alpha_idx}. {subsection_title}", 0, 1)
                
                # Add content
                pdf.set_font("Arial", "", 11)
                if content:
                    pdf.multi_cell(0, 10, content)
                else:
                    pdf.cell(0, 10, "", 0, 1)  # Empty space
                
                pdf.ln(5)
        
        elif section_id == "methodology":
            # Methodology subsections
            subsections = [
                ("DESIGN OF THE STUDY", section_data.get("design_of_the_study", "")),
                ("DATA COLLECTION PROCEDURES", section_data.get("data_collection_procedures", "")),
                ("TRAINING PROCEDURES", section_data.get("training_procedures", "")),
                ("FACILITY & EQUIPMENT ACCESS", section_data.get("facility_and_equipment_access", "")),
                ("CONFIDENTIALITY PROCEDURES", section_data.get("confidentiality_procedures", "")),
                ("PROCEDURES FOR WORKING WITH SPECIALIZED MATERIALS", 
                 section_data.get("procedures_for_working_with_specialized_materials", "")),
                ("PROCEDURES FOR WORKING WITH HAZARDOUS MATERIALS / SITUATIONS", 
                 section_data.get("procedures_for_working_with_hazardous_materials", "")),
                ("LIMITATIONS", section_data.get("limitations", "")),
                ("ALTERNATIVE METHODOLOGIES", section_data.get("alternative_methodologies", ""))
            ]
            
            # Add any custom methodology fields
            for key, value in section_data.items():
                if key not in ["design_of_the_study", "data_collection_procedures", 
                              "training_procedures", "facility_and_equipment_access", 
                              "confidentiality_procedures", 
                              "procedures_for_working_with_specialized_materials",
                              "procedures_for_working_with_hazardous_materials",
                              "limitations", "alternative_methodologies"]:
                    formatted_key = key.replace("_", " ").upper()
                    subsections.append((formatted_key, value))
            
            # Process each subsection
            for idx, (subsection_title, content) in enumerate(subsections):
                # Add page break if needed
                if pdf.get_y() > 250:
                    pdf.add_page()
                
                # Add subsection header with alpha index
                pdf.set_font("Arial", "B", 11)
                alpha_idx = chr(65 + idx)  # A, B, C, etc.
                pdf.cell(0, 10, f"{alpha_idx}. {subsection_title}", 0, 1)
                
                # Add content
                pdf.set_font("Arial", "", 11)
                if content:
                    pdf.multi_cell(0, 10, content)
                else:
                    pdf.cell(0, 10, "", 0, 1)  # Empty space
                
                pdf.ln(5)
        
        elif section_id == "timeline":
            # Timeline table
            if section_data:
                # Table header
                pdf.set_font("Arial", "B", 11)
                pdf.cell(95, 10, "ACTIVITY", 1, 0)
                pdf.cell(95, 10, "PROJECTED DATE", 1, 1)
                
                # Table content
                pdf.set_font("Arial", "", 11)
                for item in section_data:
                    activity = item.get("activity", "")
                    date = item.get("projected_date", "")
                    
                    # Handle multiline text
                    lines_activity = len(activity.split('\n'))
                    lines_date = len(date.split('\n'))
                    max_lines = max(lines_activity, lines_date, 1)
                    
                    # Set row height based on content
                    row_height = max(10, max_lines * 5)
                    
                    # Print cells with multiline support
                    pdf.multi_cell(95, row_height, activity, 1, 'L', False, 0)
                    pdf.multi_cell(95, row_height, date, 1, 'L', False, 1)
        
        elif section_id == "budget":
            # Budget section
            # Overview
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 10, "BUDGET OVERVIEW", 0, 1)
            
            pdf.set_font("Arial", "", 11)
            overview = section_data.get("overview", "")
            if overview:
                pdf.multi_cell(0, 10, overview)
            else:
                pdf.cell(0, 10, "", 0, 1)  # Empty space
            
            pdf.ln(5)
            
            # Budget items table
            budget_items = section_data.get("items", [])
            if budget_items:
                # Table header
                pdf.set_font("Arial", "B", 11)
                pdf.cell(40, 10, "ITEM", 1, 0)
                pdf.cell(60, 10, "DESCRIPTION", 1, 0)
                pdf.cell(30, 10, "PRICE", 1, 0)
                pdf.cell(30, 10, "QUANTITY", 1, 0)
                pdf.cell(30, 10, "TOTAL", 1, 1)
                
                # Table content
                pdf.set_font("Arial", "", 11)
                total_budget = 0
                
                for item in budget_items:
                    item_name = item.get("item", "")
                    description = item.get("description", "")
                    price = float(item.get("price", 0))
                    quantity = int(item.get("quantity", 0))
                    item_total = price * quantity
                    total_budget += item_total
                    
                    pdf.cell(40, 10, item_name, 1, 0)
                    pdf.cell(60, 10, description, 1, 0)
                    pdf.cell(30, 10, f"${price:.2f}", 1, 0)
                    pdf.cell(30, 10, str(quantity), 1, 0)
                    pdf.cell(30, 10, f"${item_total:.2f}", 1, 1)
                
                # Total row
                pdf.set_font("Arial", "B", 11)
                pdf.cell(160, 10, "TOTAL", 1, 0)
                pdf.cell(30, 10, f"${total_budget:.2f}", 1, 1)
        
        elif section_id == "appendix":
            # Appendix table
            if section_data:
                # Table header
                pdf.set_font("Arial", "B", 11)
                pdf.cell(60, 10, "FILE NAME", 1, 0)
                pdf.cell(80, 10, "DESCRIPTION", 1, 0)
                pdf.cell(50, 10, "LOCATION", 1, 1)
                
                # Table content
                pdf.set_font("Arial", "", 11)
                for item in section_data:
                    file_name = item.get("file_name", "")
                    description = item.get("description", "")
                    location = item.get("location", "")
                    
                    # Handle multiline text
                    lines_file = len(file_name.split('\n'))
                    lines_desc = len(description.split('\n'))
                    lines_loc = len(location.split('\n'))
                    max_lines = max(lines_file, lines_desc, lines_loc, 1)
                    
                    # Set row height based on content
                    row_height = max(10, max_lines * 5)
                    
                    # Print cells with multiline support
                    pdf.multi_cell(60, row_height, file_name, 1, 'L', False, 0)
                    pdf.multi_cell(80, row_height, description, 1, 'L', False, 0)
                    pdf.multi_cell(50, row_height, location, 1, 'L', False, 1)
        
        else:
            # Generic section handling for simple content
            if isinstance(section_data, dict) and "content" in section_data:
                # Single content field
                content = section_data.get("content", "")
                pdf.set_font("Arial", "", 11)
                if content:
                    pdf.multi_cell(0, 10, content)
                else:
                    pdf.cell(0, 10, "", 0, 1)  # Empty space
            elif isinstance(section_data, str):
                # Direct string content
                pdf.set_font("Arial", "", 11)
                if section_data:
                    pdf.multi_cell(0, 10, section_data)
                else:
                    pdf.cell(0, 10, "", 0, 1)  # Empty space
            elif isinstance(section_data, dict):
                # Multiple fields in dictionary
                pdf.set_font("Arial", "", 11)
                for key, value in section_data.items():
                    if isinstance(value, str) and value:
                        field_title = key.replace("_", " ").title()
                        pdf.set_font("Arial", "B", 11)
                        pdf.cell(0, 10, field_title, 0, 1)
                        
                        pdf.set_font("Arial", "", 11)
                        pdf.multi_cell(0, 10, value)
                        pdf.ln(5)
        
        # Increment section counter and add spacing
        section_num += 1
        pdf.ln(10)
    
    # Save the PDF
    output_filename = proposal_data.get("output_filename", "grant_proposal.pdf")
    if not output_filename.endswith(".pdf"):
        output_filename += ".pdf"
    
    pdf.output(output_filename)
    print(f"Grant proposal created successfully: {os.path.abspath(output_filename)}")
    return os.path.abspath(output_filename)

def main():
    # Example usage
    sample_data = {
        "title": "RESEARCH GRANT PROPOSAL",
        "output_filename": "example_proposal.pdf",
        "sections": {
            "metadata": {
                "date_submitted": "April 12, 2025",
                "grant_name": "Innovation Research Grant",
                "submitted_to": "National Science Foundation",
                "submitted_by": "Dr. Jane Smith",
                "address_of_receiving_party": "2415 Eisenhower Ave, Alexandria, VA 22314",
                "address_of_submitting_party": "123 University Ave, Stanford, CA 94305"
            },
            "project_purpose": {
                "content": "This research aims to develop a novel approach to..."
            },
            # Add other sections as needed for testing
        }
    }
    
    # Uncomment to test with sample data
    create_grant_proposal_from_json(sample_data)
    
    # Or create an empty template
    # create_grant_proposal_template()

if __name__ == "__main__":
    main()