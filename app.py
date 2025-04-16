import streamlit as st
import json
from pathlib import Path
import subprocess
import shlex
import os
import time

# Fixed JSON path for payload
temp_path = "edit the path of the temp_path created through streamlit for grant_proposal."
temp_slide_path = "edit the path of the temp_slide_path created through streamlit for slide_generation."


# Function to trigger generation
def trigger_generation_in_tmux(headings="", mode="slides", template_type=None, json_file=None):
    if mode == "slides":
        if json_file:  # New flow: structured input via JSON file
            escaped_file = shlex.quote(json_file)
            cmd = f'tmux send-keys -t 2 "python run_generation.py --mode slides --json_file {escaped_file}" Enter'
        elif headings:
            escaped_headings = shlex.quote(headings)
            cmd = f'tmux send-keys -t 2 "python run_generation.py --mode slides --headings {escaped_headings}" Enter'
        else:
            st.error("For slides mode, either slide headings or a JSON file must be provided.")
            return False
    elif mode == "grant":
        if not json_file or not template_type:
            st.error("For grant mode, both --template_type and --json_file must be provided.")
            return False
        escaped_file = shlex.quote(json_file)
        escaped_template = shlex.quote(template_type)
        cmd = (
            f'tmux send-keys -t 2 "python run_generation.py --mode grant '
            f'--template_type {escaped_template} --json_file {escaped_file}" Enter'
        )
    else:
        st.error("Invalid mode. Must be 'slides' or 'grant'.")
        return False

    try:
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        st.error(f"Error triggering generation in tmux: {e}")
        return False



# Load template fields
template_fields_path = Path("template_fields.json")
if template_fields_path.exists():
    with open(template_fields_path, "r") as f:
        loaded_template_fields = json.load(f)
else:
    st.error("template_fields.json not found.")
    st.stop()

# UI Start
st.title("Multimodal Content Generator")
tab_slides, tab_grant = st.tabs(["Generate Slides", "Grant Proposal"])

# Slides Tab
with tab_slides:
    st.header("Smart Slide Deck Generator")

    # Purpose & Subtype
    purpose_category = st.selectbox("Presentation Purpose", [
        "Program Reporting", "Strategic Planning", "Fundraising & Outreach",
        "Partnership Engagement", "Food Access & Hunger Relief",
        "Health Equity & Wellness", "Youth & Education Outreach"
    ])

    subtype_options = {
        "Program Reporting": ["Impact Report", "Annual Outcomes", "Evaluation Summary"],
        "Strategic Planning": ["Vision & Mission Review", "Roadmap Presentation"],
        "Fundraising & Outreach": ["Donor Pitch", "Awareness Campaign", "Community Outreach"],
        "Partnership Engagement": ["Joint Initiatives", "Stakeholder Update"],
        "Food Access & Hunger Relief": ["Hunger Landscape Report", "Regional Network Strategy", "Advocacy & Public Policy"],
        "Health Equity & Wellness": ["Nutrition + Health Services Integration", "Mental Health & Trauma Support"],
        "Youth & Education Outreach": ["School Nutrition Program", "Community Learning Initiatives"]
    }
    subtype = st.selectbox("Subtype", subtype_options.get(purpose_category, []))
    guided_questions = {
    "Impact Report": [
        "What program or initiative are you reporting on?",
        "What are the key outcomes or impact metrics?",
        "Who is the target audience for this presentation?",
        "What success stories or highlights would you like to include?",
        "What challenges or lessons should be addressed?"
    ],
    "Annual Outcomes": [
        "What were your organization's key accomplishments this year?",
        "What data or KPIs do you want to showcase?",
        "Who is the audience (e.g., board, public)?",
        "Are there any standout achievements to emphasize?",
        "Any improvements or goals for next year?"
    ],
    "Evaluation Summary": [
        "What was the scope of the evaluation?",
        "What methodologies or tools were used?",
        "What key findings or trends emerged?",
        "How are you using these insights?",
        "What are the next steps?"
    ],
    "Donor Pitch": [
        "What cause or program are you raising funds for?",
        "What problem does your initiative solve?",
        "Who benefits from your work?",
        "What has been your impact so far?",
        "What do you need support for next?"
    ],
    "Awareness Campaign": [
        "What is the central theme or cause?",
        "Who is the target audience for outreach?",
        "What types of media or channels will be used?",
        "What outcomes are you aiming for?",
        "How are you measuring engagement or success?"
    ],
    "Community Outreach": [
        "What neighborhood or community are you engaging?",
        "What are the primary needs or concerns there?",
        "How will your team connect with them?",
        "What activities or materials will you include?",
        "How will feedback or participation be captured?"
    ],
    "Vision & Mission Review": [
        "What is your current mission and vision?",
        "Why is there a need to revise or realign them?",
        "What are your long-term goals?",
        "Who are your core stakeholders?",
        "How does this presentation fit into your strategic planning?"
    ],
    "Roadmap Presentation": [
        "What major initiatives are on the horizon?",
        "What milestones or phases are planned?",
        "Who is responsible for what?",
        "What risks or challenges are anticipated?",
        "How will you track progress?"
    ],
    "Joint Initiatives": [
        "Who are your partners or collaborators?",
        "What shared goals are driving this initiative?",
        "What resources or responsibilities are being shared?",
        "What timelines or deliverables are expected?",
        "How will success be evaluated collaboratively?"
    ],
    "Stakeholder Update": [
        "Who is the stakeholder group you are updating?",
        "What initiatives or progress should they know about?",
        "What decisions or support do you need from them?",
        "What risks or concerns should be surfaced?",
        "What next steps or calls to action will you include?"
    ],
    "Hunger Landscape Report": [
        "What regions or populations are covered in your report?",
        "What are the most critical hunger metrics?",
        "What are the root causes or contributing factors?",
        "What stories or case studies illustrate the impact?",
        "What policy or programmatic recommendations are included?"
    ],
    "Regional Network Strategy": [
        "What is the scope of your regional food bank network?",
        "What are the shared strategic priorities?",
        "What infrastructure, logistics, or gaps are being addressed?",
        "How are local agencies contributing to this vision?",
        "What goals and metrics are being tracked collectively?"
    ],
    "Advocacy & Public Policy": [
        "What issue or legislation are you advocating for?",
        "How does it relate to food security or health equity?",
        "Who are your coalition partners?",
        "What outreach efforts or lobbying are underway?",
        "What outcome or impact do you seek?"
    ],
    "Nutrition + Health Services Integration": [
        "What health partners are involved?",
        "What nutrition programs are being embedded or expanded?",
        "How is patient screening or referral handled?",
        "What are your health outcome goals?",
        "How is data being collected and shared?"
    ],
    "Mental Health & Trauma Support": [
        "What populations are affected by trauma or instability?",
        "What services are being offered?",
        "Who delivers these services and how are they trained?",
        "What outcomes are expected for individuals served?",
        "How is follow-up care or case management structured?"
    ],
    "School Nutrition Program": [
        "What student group is being served?",
        "What meals or resources are provided?",
        "How does this fit within broader school services?",
        "What are your nutritional or wellness benchmarks?",
        "How is family engagement incorporated?"
    ],
    "Community Learning Initiatives": [
        "What topics or skills are covered in the curriculum?",
        "Who are the facilitators or educators?",
        "What population is the initiative targeting?",
        "How are workshops or sessions structured?",
        "What success metrics are you using?"
    ]
}

    questions = guided_questions.get(subtype, [])
    user_answers = {}

    if questions:
        st.subheader("Please answer the following questions:")
        for idx, question in enumerate(questions):
            user_answers[question] = st.text_area(f"{idx+1}. {question}", key=f"slide_q_{idx}")

    if st.button("Generate Slide Deck"):
        structured_input = {
            "category": purpose_category,
            "subtype": subtype,
            "answers": user_answers
        }

        with open(temp_slide_path, "w") as f:
            json.dump(structured_input, f, indent=2)

        triggered = trigger_generation_in_tmux(mode="slides", json_file=temp_slide_path)

        countdown_placeholder = st.empty()
        download_placeholder = st.empty()

        if triggered:
            st.success("The Presentation has began to cook!")
            pptx_output_path = "assign an output path"

            for remaining in range(300, 0, -1):  # 5-minute timeout
                minutes, seconds = divmod(remaining, 60)
                countdown_placeholder.info(f"⏳ Waiting for presentation... {minutes}:{seconds:02d} remaining")
                time.sleep(1)

                if os.path.exists(pptx_output_path):
                    countdown_placeholder.success("✅ Presentation is ready!")
                    with open(pptx_output_path, "rb") as file:
                        download_placeholder.download_button(
                            label="📊 Download Your Slide Deck (.pptx)",
                            data=file,
                            file_name="Generated_Presentation.pptx",
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                        )
                    break
            else:
                countdown_placeholder.error("⚠️ Timeout: Presentation was not generated in 5 minutes.")
        else:
            st.error("❌ Failed to send generation command to tmux.")



# Grant Tab
with tab_grant:
    st.header("Smart Grant Proposal Generator")

    purpose_category = st.selectbox(
        "What is the primary purpose of your grant proposal?",
        [
            "Health & Wellness",
            "Youth Development & Education",
            "Food & Basic Needs",
            "Community Empowerment & Infrastructure"
        ]
    )

    subtype_options = {
        "Health & Wellness": ["Mobile Clinics", "Public Health Outreach", "Caregiver Lodging", "Trauma-Informed Services"],
        "Youth Development & Education": ["Preschool Programs", "Creative Arts / Media", "Juvenile Reentry", "Youth Transitional Living"],
        "Food & Basic Needs": ["Urban Farming", "Emergency Financial Relief"],
        "Community Empowerment & Infrastructure": ["Facility Upgrade", "Neighborhood Revitalization", "General Operating Support"]
    }

    subtype = st.selectbox(
        "What type of project are you proposing?",
        subtype_options.get(purpose_category, [])
    )

    template_mapping = {
        "Mobile Clinics": "IC-Grant-Application",
        "Public Health Outreach": "IC-Grant-Application",
        "Caregiver Lodging": "Non-Profit-Grant-Proposal",
        "Trauma-Informed Services": "IC-Grant-Application",
        "Preschool Programs": "Non-Profit-Grant-Proposal",
        "Creative Arts / Media": "IC-Technology-Grant-Proposal",
        "Juvenile Reentry": "IC-Grant-Application",
        "Youth Transitional Living": "IC-Grant-Application",
        "Urban Farming": "Generic-Grant-Proposal",
        "Emergency Financial Relief": "Generic-Grant-Proposal",
        "Facility Upgrade": "IC-Technology-Grant-Proposal",
        "Neighborhood Revitalization": "IC-Grant-Application",
        "General Operating Support": "Generic-Grant-Proposal"
    }

    allocated_template = template_mapping.get(subtype, "Generic-Grant-Proposal")

    guided_questions = {
        "IC-Grant-Application": [
            "Summarize your project in 1–2 sentences.",
            "What problem or need does this project address?",
            "Who is the target population or community you will serve?",
            "What are the main goals and measurable objectives?",
            "How will you achieve these goals? Describe your approach.",
            "How will you track progress and evaluate success?",
            "What impact do you expect this project to have?",
            "How will you ensure the project continues after the grant period?"
        ],
        "IC-Technology-Grant-Proposal": [
            "Describe the core idea and vision for this technology project.",
            "What educational or social issue is this project solving?",
            "List the main goals and measurable outcomes for this year.",
            "Who is the intended audience or user of this technology?",
            "What makes this project sustainable and technically feasible?"
        ],
        "Non-Profit-Grant-Proposal": [
            "What specific problem or issue are you addressing?",
            "What are the key goals and expected outcomes?",
            "Who is the target population you aim to serve?",
            "What are the core activities you plan to undertake?",
            "Who are the staff or team members involved, and what are their roles?"
        ],
        "Generic-Grant-Proposal": [
            "Briefly describe your project’s main purpose.",
            "Why is this project important — what need does it address?",
            "What activities will be conducted as part of the project?",
            "What are your main goals or milestones?",
            "How will success be evaluated or measured?"
        ]
    }

    if allocated_template:
        st.subheader("Tell us about your project briefly. It helps us generate what you want in detail")
        questions = guided_questions.get(allocated_template, [])
        user_answers = {}

        for idx, question in enumerate(questions):
            user_input = st.text_area(f"{idx+1}. {question}", height=80, key=f"q_{idx}")
            user_answers[question] = user_input

        if st.button("Generate Draft Proposal"):
            st.session_state["user_answers"] = user_answers
            st.session_state["allocated_template"] = allocated_template

            field_keys = loaded_template_fields.get(allocated_template, [])
            mapped_fields = {field_keys[i]: ans for i, (q, ans) in enumerate(user_answers.items()) if i < len(field_keys)}

            final_payload = {
                "template_name": allocated_template,
                "fields": mapped_fields
            }

            with open(temp_path, "w") as f:
                json.dump(final_payload, f)

            triggered = trigger_generation_in_tmux(
                headings="",
                mode="grant",
                template_type=allocated_template,
                json_file=temp_path
            )

            if triggered:
                st.success("We have started to cook the grant proposal")
                docx_output_path = "assign an output path"
                countdown_placeholder = st.empty()
                download_placeholder = st.empty()

                for remaining in range(300, 0, -1):
                    minutes, seconds = divmod(remaining, 60)
                    countdown_placeholder.info(f"⏳ Waiting for proposal to generate... {minutes}:{seconds:02d} remaining")
                    time.sleep(1)

                    if os.path.exists(docx_output_path):
                        countdown_placeholder.success("✅ Document is ready!")
                        with open(docx_output_path, "rb") as file:
                            download_placeholder.download_button(
                                label="📄 Download Your Grant Proposal (.docx)",
                                data=file,
                                file_name="Final_Grant_Proposal.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                        break
                else:
                    countdown_placeholder.error("⚠️ Timeout: The file was not generated within 2 minutes.")
            else:
                st.error("⚠️ Failed to trigger background process. Check tmux setup.")
    else:
        st.info("Please select a project subtype to begin.")
