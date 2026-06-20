from langchain_community.document_loaders import PyPDFLoader
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def score_resume(resume_path, current_role, target_role):
    try:
        load = PyPDFLoader(resume_path)
        documents = load.load()

        SYSTEM_PROMPT = f"""
        You are an expert ATS Score Agent.
        Your job is to score the resume based on the ATS score criteria.
        The ATS score criteria is as follows:
        - 100% for a resume that is a perfect match for the job description.
        - 0% for a resume that is a perfect mismatch for the job description.
        - 50% for a resume that is a partial match for the job description.
        The current role is {current_role} and the target role is {target_role}.
        Return the score in JSON format only. No Markdown.
        """
        client = OpenAI()
        response = client.responses.create(
            model="gpt-4o-mini",
            input=SYSTEM_PROMPT + "\n\nResume: " + str(documents))
        return response.output_text
    except Exception as e:
        print(e)
        return None
