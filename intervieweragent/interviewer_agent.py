from openai import OpenAI
from dotenv import load_dotenv
import json
load_dotenv()

def interviewer_agent(current_role, target_role, resume_data, job_description):
    try:
        SYSTEM_PROMPT = f"""
        You are an expert Technical Interview Question Generator.

        Generate exactly 10 personalized interview questions using:

        * Candidate Resume
        * Candidate Introduction
        * Knowledge Graph Context
        * Target Role
        * Job Description

        Rules:

        * Question 1 must always be: "Tell me about yourself."
        * Prioritize candidate projects, work experience, and skills over generic theory.
        * Align questions with the target role and job description.
        * Gradually increase difficulty from easy to hard.
        * Include experience, project, technical, role-specific, and scenario-based questions.
        * Avoid duplicates and yes/no questions.
        * Make questions realistic and interviewer-like.

        Return ONLY valid JSON in this format:

        
        "questions": [
        
        "id": 1,
        "category": "introduction",
        "difficulty": "easy",
        "question": "Tell me about yourself."
        
        ]
        

        Requirements:

        * Exactly 10 questions.
        * IDs from 1 to 10.
        * Categories: introduction, experience, project, technical, role_specific, scenario.
        * Difficulty: easy, medium, hard.
        * No markdown.
        * No explanations.
        * Return only JSON.


        """
        client = OpenAI()

        response = client.responses.create(
            model="gpt-4o-mini",
            input=SYSTEM_PROMPT + "\n\nResume: " + "\n\nJob Description: " + str(job_description)+"\n\nCurrent Role: " + str(current_role)+"\n\nTarget Role: " + str(target_role))
        return response.output_text
    except Exception as e:
        print(e)
        return None

def generate_results(
    interview_plan,
    job_description,
    questions,
    answers
):
    try:
        client = OpenAI()

        prompt = f"""
            You are an expert Technical Interview Evaluator.

            Evaluate the candidate based on:

            Interview Plan:
            {json.dumps(interview_plan, indent=2)}


            Job Description:
            {job_description}

            Questions:
            {json.dumps(questions, indent=2)}

            Candidate Answers:
            {json.dumps(answers, indent=2)}

            Return ONLY valid JSON in the following schema:

            
                "overall_score": 0,
                "communication_score": 0,
                "technical_score": 0,
                "problem_solving_score": 0,
                "strengths": [],
                "weaknesses": [],
                "recommendations": [],
                "question_wise_feedback": [
                    
                        "question": "",
                        "score": 0,
                        "feedback": ""
                    
                ]
            

            Scoring must be from 0-100.
            Do not return markdown.
            Do not return explanations.
            Return JSON only.
        """

        response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt
        )

        return response.output_text

    except Exception as e:
        print(f"Error generating results: {e}")
        return None