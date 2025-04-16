import streamlit as st
import json
from pathlib import Path

st.title("Smart Slide Deck Generator")

# Step 1: Purpose Category
purpose_category = st.selectbox(
    "What is the purpose of your presentation?",
    [
        "Program Reporting",
        "Strategic Planning",
        "Fundraising & Outreach",
        "Partnership Engagement",
        "Food Access & Hunger Relief",
        "Health Equity & Wellness",
        "Youth & Education Outreach"
    ]
)

# Step 2: Subtypes
subtype_options = {
    "Program Reporting": ["Impact Report", "Annual Outcomes", "Evaluation Summary"],
    "Strategic Planning": ["Vision & Mission Review", "Roadmap Presentation"],
    "Fundraising & Outreach": ["Donor Pitch", "Awareness Campaign", "Community Outreach"],
    "Partnership Engagement": ["Joint Initiatives", "Stakeholder Update"],
    "Food Access & Hunger Relief": ["Hunger Landscape Report", "Regional Network Strategy", "Advocacy & Public Policy"],
    "Health Equity & Wellness": ["Nutrition + Health Services Integration", "Mental Health & Trauma Support"],
    "Youth & Education Outreach": ["School Nutrition Program", "Community Learning Initiatives"]
}

subtype = st.selectbox("Select a subtype", subtype_options.get(purpose_category, []))

# Step 3: Guided Questions
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
    st.subheader("Please answer the following questions to help us generate your presentation:")
    for idx, question in enumerate(questions):
        answer = st.text_area(f"{idx+1}. {question}", key=f"q_{idx}")
        user_answers[question] = answer

    if st.button("Generate Slide Deck JSON"):
        st.json(user_answers)
else:
    st.info("Please select a subtype to continue.")

structured_input = {
    "category": purpose_category,
    "subtype": subtype,
    "answers": user_answers
}

# Save to file (optional, for tmux trigger)
with open("tmp_slide_prompt.json", "w") as f:
    json.dump(structured_input, f, indent=2)



