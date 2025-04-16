# CAFB RAG-Powered Smart Document Creation Pipeline

## Overview
This repository contains the complete solution for **smart document generation** using Retrieval-Augmented Generation (RAG), multimodal models, and Large Language Models (LLMs). The pipeline automatically creates detailed, structured documents—such as slide presentations and grant proposals—from minimal user input.

---

## Problem Statement

Manually generating documents like presentations or grant proposals is repetitive and time-consuming. Experts waste valuable time formatting and structuring content instead of concentrating on the actual insights and information.

---

## Our Solution

We've developed a sophisticated, intelligent pipeline powered by:

- **Streamlit UI:** For dynamic, user-friendly input collection.
- **Vector Databases (FAISS & ColPali):** For efficient retrieval of relevant textual and image-based context.
- **Multimodal Models (LLaVA):** To intelligently interpret and use visual data.
- **Large Language Models (Claude API & Mistral):** For generating coherent, tailored, structured document content.

This automated pipeline ensures quick, scalable, and accurate document generation.

---

## Features

- **Dynamic User Interface:** Intuitive Streamlit frontend for easy input handling.
- **Intelligent Context Retrieval:** Semantic search using vector databases.
- **Multimodal Capabilities:** Integrated visual understanding using advanced models.
- **Structured Output:** Automatic creation of polished PowerPoint presentations and professionally formatted grant PDFs.
- **Scalable Architecture:** Supports both local GPU clusters and potential cloud-native deployments.

---

## Workflow

### User Interaction
- Users select the document type and template in the Streamlit UI.
- Users input answers through guided, structured forms.

### Backend Processing
- Input validation and structured storage in JSON.
- Background task execution using `tmux`.
- Retrieval of text and image context via FAISS and ColPali.
- Multimodal interpretation through models like LLaVA.
- Structured content generation using Claude API or Mistral LLM.

### Document Generation
- Automatic creation of slide presentations (`pptx`) and grant proposals (`pdf`).
- Instant download of generated documents via Streamlit UI.

---

## Tech Stack

### Frontend
- **Streamlit:** User-friendly, interactive forms and validation.

### Backend
- **tmux:** Asynchronous processing and task execution.
- **Python:** Core programming language.

### Context Retrieval
- **FAISS:** Efficient text-based semantic retrieval.
- **ColPali:** Image-based context retrieval.
- **Sentence Transformers:** Embedding generation for semantic search.

### Multimodal Understanding
- **LLaVA:** Advanced visual-language model integration.

### Generation and Formatting
- **Claude (AWS Bedrock) & Mistral:** Structured LLM-based content generation.
- **python-pptx:** Dynamic PowerPoint generation.
- **FPDF:** Automated PDF document formatting.

### Deployment Infrastructure
- **Nexus GPU Cluster (UMD):** Current deployment.
- **Potential Cloud-Native Enhancements:** Amazon EC2, SageMaker endpoints, Amazon S3 storage, and Canva API integration.

---

## Installation

```bash
git clone https://github.com/robosac333/Multimodal_document_creation.git
cd Multimodal_document_creation
pip install -r requirements.txt
```

---

## Configuration

Update paths in `app.py` and the main Python script (`run_generation.py`):

### In `app.py`:

- `temp_path`: Path to temporary JSON file for grant proposals.
- `temp_slide_path`: Path to temporary JSON file for slide generation.
- `pptx_output_path`: Path for saving generated PowerPoint presentations.
- `docx_output_path`: Path for saving generated grant proposal documents.

Example:
```python
temp_path = "/your/path/to/tmp_grant_payload.json"
temp_slide_path = "/your/path/to/tmp_slide_payload.json"
pptx_output_path = "/your/path/to/Generated_Presentation.pptx"
docx_output_path = "/your/path/to/Final_Grant_Proposal.docx"
```

### In `create_document.py`:

- `DATA_PATH`: Folder containing PDF documents.
- `FAISS_DB_PATH`: Path to FAISS vector database.
- `IMAGES_FOLDER`: Folder for image outputs.
- `OUTPUT_FOLDER`: Path for final document outputs.

Example:
```python
DATA_PATH = "/your/path/to/pdfs"
FAISS_DB_PATH = "/your/path/to/vector_data_base"
IMAGES_FOLDER = "/your/path/to/img_output"
OUTPUT_FOLDER = "/your/path/to/Final_slide"
```

---

## Running the Application

### Starting the UI
```bash
streamlit run app.py
```


## Directory Structure
```
.
├── app.py                       # Streamlit Frontend
├── run_generation.py            # Backend Task Trigger
├── create_documents.py          # Document Generation Logic
├── bedrock_handler.py           # Claude API Integration
├── text_retrieval.py            # FAISS Vector Retrieval
├── image_retrieval.py           # Image Retrieval and Processing
├── template_fields.json         # Document Template Definitions
├── requirements.txt             # Python Dependencies
├── outputs/                     # Generated Documents
└── docs/                        # Documentation and Diagrams
```

---

## Future Enhancements

- Migration to scalable, cloud-native architecture.
- Enhanced multimodal capabilities with improved image filtering.
- Expansion of template flexibility and document types.
- Integration of professional document formatting APIs like Canva.

---

## License

This project is licensed under the MIT License.


