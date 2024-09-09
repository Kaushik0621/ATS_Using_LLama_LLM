from llama_index.readers.file import PDFReader
from llama_index.core import VectorStoreIndex
import json
import re
import os
import openai

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Set OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    openai.api_key = api_key
else:
    raise ValueError("OpenAI API key is not set. Check your .env file.")

def process_pdf(pdf_path: str):
    """
    Process the PDF and extract information as a JSON object directly from the LLM.
    
    Args:
        pdf_path (str): The path to the PDF file.
        
    Returns:
        dict: A dictionary containing extracted details such as personal info, education, work experience, and skills.
    """
    document = PDFReader().load_data(file=pdf_path)
    index = VectorStoreIndex.from_documents(documents=document)
    query_engine = index.as_query_engine()

    # Define the questions we want to ask the model, instructing it to return answers in JSON format
    questions = {
        "name": """
            What is the full name of the applicant? The name should not contain any special characters like '@', '/'. 
            If not found or improperly formatted, return "N/A". Please return the answer in the following JSON format:
            {"name": "Applicant's full name"}. If the name is not found, use {"name": "N/A"}.
        """,
        "phone": """
            What is the phone number of the applicant? If you cannot find a valid phone number, return "N/A". 
            Please return the answer in the following JSON format: {"phone": "Applicant's phone number"}.
            If no phone number is found, use {"phone": "N/A"}.
        """,
        "education": """
            Extract the applicant's educational background. For each degree, only include the degree name without any additional details such as honors, distinctions, or classifications. 
            For each entry, also include institution, start date, and end date.
            If no date is provided or is in an incorrect format, return "N/A" for that date. 
            Please return the answer in the following JSON format:
            {
                "education": [
                    {
                        "degree": "Degree Name",
                        "institution": "Institution Name",
                        "start_date": "mm/yyyy or N/A",
                        "end_date": "mm/yyyy or N/A"
                    },
                    ...
                ]
            }. If no education is found, return {"education": []}.
        """,

        "work_experience": """
            Extract the applicant's work experience. For each position, include role, company, start and end dates, and key responsibilities.
            If no date is provided or is in an incorrect format, return "N/A" for that date.
            Please return the answer in the following JSON format:
            {
                "work_experience": [
                    {
                        "role": "Job Role",
                        "company": "Company Name",
                        "start_date": "mm/yyyy or N/A",
                        "end_date": "mm/yyyy or N/A",
                        "responsibilities": ["Responsibility 1", "Responsibility 2", "Responsibility 3"]
                    }
                ]
            }. If no work experience is found, return {"work_experience": []}.
        """,
        "skills": """
            Extract the technical skills of the applicant. If no skills are found, return "N/A".
            Please return the answer in the following JSON format: {"skills": ["Skill 1", "Skill 2"]}.
            If no skills are found, use {"skills": []}.
        """
    }

    # Collect answers from the query engine
    results = {}
    for key, question in questions.items():
        response = query_engine.query(question)
        print(f"Response for {key}:\n{response.response}\n")  # Debug print to check raw response
        try:
            # Try to parse the response directly as JSON
            results[key] = json.loads(response.response)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON for {key}: {response.response}")
            results[key] = None

    # Structure the output by merging all the JSON parts
    structured_output = {
        "personal_info": {
            "name": results.get("name", {}).get("name", "N/A"),
            "phone": results.get("phone", {}).get("phone", "N/A")
        },
        "education": results.get("education", {}).get("education", []),
        "work_experience": results.get("work_experience", {}).get("work_experience", []),
        "skills": results.get("skills", {}).get("skills", [])
    }

    # Fallback in case education or work experience has improperly formatted dates
    for entry in structured_output["education"]:
        if not re.match(r"\d{2}/\d{4}", entry.get("start_date", "")):
            entry["start_date"] = "N/A"
        if not re.match(r"\d{2}/\d{4}", entry.get("end_date", "")):
            entry["end_date"] = "N/A"

    for entry in structured_output["work_experience"]:
        if not re.match(r"\d{2}/\d{4}", entry.get("start_date", "")):
            entry["start_date"] = "N/A"
        if not re.match(r"\d{2}/\d{4}", entry.get("end_date", "")):
            entry["end_date"] = "N/A"

    return structured_output
