from fpdf import FPDF
import os
import json
from typing import Dict, List, Any, Union

def create_rfp_proposal_from_json(json_data):
    """
    Create a PDF document for an RFP (Request for Proposal) based on the JSON data provided
    
    Args:
        json_data: Dictionary or JSON string containing RFP content
        
    Returns:
        Path to the generated PDF file
    """
    # Parse JSON string if provided as string
    if isinstance(json_data, str):
        try:
            rfp_data = json.loads(json_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None
    else:
        rfp_data = json_data
    
    # Initialize PDF object
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Set fonts
    pdf.set_font("Arial", "B", 16)
    
    # Title
    title = rfp_data.get("title", "GRANT RFP TEMPLATE")
    pdf.cell(0, 10, title, 0, 1, "C")
    pdf.ln(5)
    
    # Top metadata section - 2x2 grid
    pdf.set_font("Arial", "B", 11)
    
    # Row 1: Posting Date and Grant Name
    pdf.cell(95, 10, "POSTING DATE", 1, 0)
    pdf.cell(95, 10, "GRANT NAME", 1, 1)
    
    # Row 1 content
    pdf.set_font("Arial", "", 11)
    posting_date = rfp_data.get("metadata", {}).get("dateSubmitted", "")
    grant_name = rfp_data.get("metadata", {}).get("grantName", "")
    pdf.cell(95, 10, posting_date, 1, 0)
    pdf.cell(95, 10, grant_name, 1, 1)
    
    # Row 2: Solicited By and Address
    pdf.set_font("Arial", "B", 11)
    pdf.cell(95, 10, "SOLICITED BY", 1, 0)
    pdf.cell(95, 10, "ADDRESS OF SOLICITING PARTY", 1, 1)
    
    # Row 2 content
    pdf.set_font("Arial", "", 11)
    solicited_by = rfp_data.get("metadata", {}).get("submittedTo", "")
    address = rfp_data.get("metadata", {}).get("addressOfReceivingParty", "")
    pdf.cell(95, 10, solicited_by, 1, 0)
    pdf.cell(95, 10, address, 1, 1)
    
    pdf.ln(10)
    
    # Track section numbers for roman numerals
    section_num = 1
    roman_numerals = ["I", "II", "III", "IV", "V", "VI", "VII", 
                      "VIII", "IX", "X", "XI", "XII", "XIII", "XIV"]
    
    # Process each main section
    
    # I. PURPOSE OF REQUEST FOR PROPOSAL
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"{roman_numerals[0]}. PURPOSE OF REQUEST FOR PROPOSAL", 0, 1)
    
    # Add purpose content
    pdf.set_font("Arial", "", 11)
    purpose = rfp_data.get("projectPurpose", "")
    if purpose:
        pdf.multi_cell(0, 10, purpose)
    else:
        pdf.cell(0, 10, "", 0, 1)  # Empty space
    
    pdf.ln(5)
    
    # II. ORGANIZATION BACKGROUND
    if pdf.get_y() > 250:
        pdf.add_page()
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"{roman_numerals[1]}. ORGANIZATION BACKGROUND", 0, 1)
    
    # Add organization background content
    pdf.set_font("Arial", "", 11)
    org_background = ""
    
    # Check if organization_info exists in the JSON structure
    if "organization_info" in rfp_data:
        org_background = rfp_data["organization_info"].get("background", "")
    else:
        # Look for background information in other possible locations
        background_data = rfp_data.get("background", {})
        if isinstance(background_data, dict):
            # Use scopeOfProblem or another field as organization background
            org_background = background_data.get("scopeOfProblem", "")
            
    if org_background:
        pdf.multi_cell(0, 10, org_background)
    else:
        pdf.cell(0, 10, "", 0, 1)  # Empty space
    
    pdf.ln(5)
    
    # III. TIMELINE FOR SCOPE OF SERVICES
    if pdf.get_y() > 250:
        pdf.add_page()
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"{roman_numerals[2]}. TIMELINE FOR SCOPE OF SERVICES", 0, 1)
    
    # Timeline table
    timeline_data = rfp_data.get("timeline", [])
    if timeline_data:
        # Table header
        pdf.set_font("Arial", "B", 11)
        pdf.cell(95, 10, "ACTIVITY", 1, 0)
        pdf.cell(95, 10, "PROJECTED DATE", 1, 1)
        
        # Define standard activities if not provided in JSON
        standard_activities = [
            "Grant Application Period",
            "Prior to Final Grant Submissions",
            "After Final Grant Submissions",
            "Underwriting Period",
            "Underwriting Review",
            "Revisions and Final Report"
        ]
        
        # Check if we need to use standard activities or the ones from JSON
        if len(timeline_data) == 0:
            # Use standard activities with empty dates
            for activity in standard_activities:
                pdf.set_font("Arial", "", 11)
                pdf.cell(95, 10, activity, 1, 0)
                pdf.cell(95, 10, "", 1, 1)
        else:
            # Use activities from JSON
            pdf.set_font("Arial", "", 11)
            for item in timeline_data:
                activity = item.get("activity", "")
                date = item.get("projectedDate", "")
                
                # Handle multiline text
                lines_activity = len(activity.split('\n'))
                lines_date = len(date.split('\n'))
                max_lines = max(lines_activity, lines_date, 1)
                
                # Set row height based on content
                row_height = max(10, max_lines * 5)
                
                # Print cells with multiline support
                pdf.multi_cell(95, row_height, activity, 1, 'L', False, 0)
                pdf.multi_cell(95, row_height, date, 1, 'L', False, 1)
    else:
        # Create empty timeline with standard activities
        pdf.set_font("Arial", "B", 11)
        pdf.cell(95, 10, "ACTIVITY", 1, 0)
        pdf.cell(95, 10, "PROJECTED DATE", 1, 1)
        
        pdf.set_font("Arial", "", 11)
        standard_activities = [
            "A. Grant Application Period",
            "B. Prior to Final Grant Submissions",
            "C. After Final Grant Submissions",
            "D. Underwriting Period",
            "E. Underwriting Review",
            "F. Revisions and Final Report"
        ]
        
        for activity in standard_activities:
            pdf.cell(95, 10, activity, 1, 0)
            pdf.cell(95, 10, "", 1, 1)
    
    pdf.ln(5)
    
    # Add a page break before Scope of Services
    pdf.add_page()
    
    # IV. SCOPE OF SERVICES
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"{roman_numerals[3]}. SCOPE OF SERVICES", 0, 1)
    
    # Scope of services subsections
    scope_subsections = [
        "A. GRANT APPLICATION PERIOD",
        "B. PRIOR TO FINAL GRANT SUBMISSIONS",
        "C. AFTER FINAL GRANT SUBMISSIONS",
        "D. UNDERWRITING PERIOD",
        "E. UNDERWRITING REVIEW",
        "F. REVISIONS AND FINAL REPORT"
    ]
    
    # Extract methodology data if available
    methodology_data = rfp_data.get("methodology", {})
    
    # Process each subsection
    for subsection_title in scope_subsections:
        # Add page break if needed
        if pdf.get_y() > 250:
            pdf.add_page()
        
        # Add subsection header
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 10, subsection_title, 0, 1)
        
        # Try to find matching content in methodology
        key = subsection_title[3:].strip().lower().replace(" ", "_")
        content = ""
        
        # Look for matching content in methodology
        if key in methodology_data:
            content = methodology_data[key]
        
        # Add content
        pdf.set_font("Arial", "", 11)
        if content:
            pdf.multi_cell(0, 10, content)
        else:
            pdf.cell(0, 10, "", 0, 1)  # Empty space
        
        pdf.ln(5)
    
    # V. SUBMISSION PROCESS
    if pdf.get_y() > 250:
        pdf.add_page()
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"{roman_numerals[4]}. SUBMISSION PROCESS", 0, 1)
    
    # Add submission process content
    pdf.set_font("Arial", "", 11)
    submission_process = ""
    
    # Try to find submission process in different possible locations
    if "submission_process" in rfp_data:
        submission_process = rfp_data["submission_process"]
    elif "methodologysubmission_process" in rfp_data.get("methodology", {}):
        submission_process = rfp_data["methodology"]["submission_process"]
    
    if submission_process:
        pdf.multi_cell(0, 10, submission_process)
    else:
        pdf.cell(0, 10, "", 0, 1)  # Empty space
    
    pdf.ln(5)
    
    # VI. QUESTIONS / INQUIRIES INFORMATION
    if pdf.get_y() > 250:
        pdf.add_page()
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"{roman_numerals[5]}. QUESTIONS / INQUIRIES INFORMATION", 0, 1)
    
    # Add questions/inquiries content
    pdf.set_font("Arial", "", 11)
    inquiries_info = ""
    
    # Try to find inquiries information in different possible locations
    if "inquiries_information" in rfp_data:
        inquiries_info = rfp_data["inquiries_information"]
    elif "contact_information" in rfp_data:
        inquiries_info = rfp_data["contact_information"]
    
    if inquiries_info:
        pdf.multi_cell(0, 10, inquiries_info)
    else:
        pdf.cell(0, 10, "", 0, 1)  # Empty space
    
    # Save the PDF
    output_filename = rfp_data.get("output_filename", "rfp_proposal.pdf")
    if not output_filename.endswith(".pdf"):
        output_filename += ".pdf"
    
    pdf.output(output_filename)
    print(f"RFP proposal created successfully: {os.path.abspath(output_filename)}")
    return os.path.abspath(output_filename)

def main():
    # Example usage
    sample_data = {
        "title": "GRANT RFP TEMPLATE",
        "output_filename": "example_rfp.pdf",
        "metadata": {
            "dateSubmitted": "April 13, 2025",
            "grantName": "Innovation Research Grant",
            "submittedTo": "National Science Foundation",
            "addressOfReceivingParty": "2415 Eisenhower Ave, Alexandria, VA 22314"
        },
        "projectPurpose": "This Request for Proposal (RFP) seeks innovative research projects focused on advancing knowledge in the field of sustainable energy technologies.",
        "timeline": [
            {
                "activity": "A. Grant Application Period",
                "projectedDate": "May 1 - June 15, 2025"
            },
            {
                "activity": "B. Prior to Final Grant Submissions",
                "projectedDate": "June 1 - June 15, 2025"
            },
            {
                "activity": "C. After Final Grant Submissions",
                "projectedDate": "June 16 - July 15, 2025"
            },
            {
                "activity": "D. Underwriting Period",
                "projectedDate": "July 16 - August 15, 2025"
            },
            {
                "activity": "E. Underwriting Review",
                "projectedDate": "August 16 - September 15, 2025"
            },
            {
                "activity": "F. Revisions and Final Report",
                "projectedDate": "September 16 - October 15, 2025"
            }
        ],
        "methodology": {
            "grant_application_period": "During this period, potential applicants can submit initial applications through our online portal. Technical assistance will be available.",
            "prior_to_final_grant_submissions": "All applicants will be required to attend a pre-submission webinar to address common questions and clarify requirements.",
            "after_final_grant_submissions": "All applications will undergo an initial screening for completeness and eligibility.",
            "underwriting_period": "Qualified applications will be reviewed by a panel of experts from various fields.",
            "underwriting_review": "Final recommendations will be made based on the evaluation criteria outlined in the RFP.",
            "revisions_and_final_report": "Selected applicants may be asked to revise their proposals based on reviewer feedback."
        },
        "submission_process": "All proposals must be submitted electronically through our online portal at grants.example.org. Paper submissions will not be accepted. Applicants must register for an account before submitting their proposal.",
        "inquiries_information": "Questions regarding this RFP should be directed to grants@example.org. All questions must be received no later than two weeks before the submission deadline. Responses will be posted publicly on our FAQ page."
    }
    
    # Uncomment to test with sample data
    create_rfp_proposal_from_json(sample_data)

if __name__ == "__main__":
    main()