from ssl import SSL_ERROR_EOF
from typing_extensions import TypedDict
from openai import OpenAI
from typing import Literal
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langgraph.graph import StateGraph, START, END

load_dotenv()

client = OpenAI()

class State(TypedDict):
    user_id: int #given by the user
    current_role: str #given by the user
    target_role: str #given by the user
    job_description: str #given by the user
    duration: int #given by the user
    hours_per_day: int #given by the user
    user_query: str #given by the user

    skills: list[str] #extracted from the resume
    required_skills: list[str] #extracted from the job description
    market_demand: list[str] #extracted from the web
    roadmap: list[str] #generated roadmap
    project_ideas: list[str] #generated project ideas
    result: str #generated result
    
def extract_skills(state: State):
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
    )
    qdrant_client = QdrantClient(url="http://localhost:6333")
    vectorstore = QdrantVectorStore(
        client=qdrant_client,
        collection_name=f"resume_{state['user_id']}",
        embedding=embeddings,
    )
    res = vectorstore.similarity_search(query="What are the skills that the user has currently in his resume?")
    SYSTEM_PROMPT = f"""
    You are an expert Resume Analysis Agent.

    Your job is to thoroughly analyze the candidate's resume
    and extract the skills that the user has currently in his resume.
    and return the skills in a list of strings.
    """
    openai_response = client.responses.create(
        model="gpt-4o-mini",
        input=f"{SYSTEM_PROMPT} \n\n resume: {res}"
    )
    return {"skills": openai_response.output_text}

def extract_required_skills(state: State):
    SYSTEM_PROMPT = f"""
    You are an expert Job Description Analysis Agent.
    You are given a job description, current role and target role, and you need to extract the required skills for the job.
    and return the required skills in a list of strings only.

    Job Description: {state['job_description']}
    Current Role: {state['current_role']}
    Target Role: {state['target_role']}
    """
    openai_response = client.responses.create(
        model="gpt-4o-mini",
        input=f"{SYSTEM_PROMPT}"
    )
    return {"required_skills": openai_response.output_text}

def extract_market_demand(state: State):
    SYSTEM_PROMPT = f"""
    You are an expert Market Demand Analysis Agent.
    You are given a job description, current role and target role, and you need to extract the market demand for the job.
    and return the market demand in a list of strings only.

    Job Description: {state['job_description']}
    Current Role: {state['current_role']}
    Target Role: {state['target_role']}
    """
    openai_response = client.responses.create(
        model="gpt-4o-mini",
        input=f"{SYSTEM_PROMPT}",
        tools=[{"type": "web_search"}]
    )
    return {"market_demand": openai_response.output_text}

def generate_roadmap(state: State):
    SYSTEM_PROMPT = f"""
    You are an expert Roadmap Generation Agent.
    You are given a job description, current role and target role, and you need to generate a roadmap for the job.
    and return the roadmap in a list of strings only.

    Job Description: {state['job_description']}
    Current Role: {state['current_role']}
    Target Role: {state['target_role']}
    Duration: {state['duration']}
    Hours per Day: {state['hours_per_day']}
    """
    openai_response = client.responses.create(
        model="gpt-5",
        input=f"{SYSTEM_PROMPT}",
        tools=[{"type": "web_search"}]
    )
    return {"roadmap": openai_response.output_text}

def generate_project_ideas(state: State):
    SYSTEM_PROMPT = f"""
    You are an expert Project Ideas Generation Agent.
    You are given a job description, current role and target role, duration, hours per day,
    skills, required skills and market demand, and you need to generate project ideas for the job.
    and return the project ideas in a list of strings only.

    Job Description: {state['job_description']}
    Current Role: {state['current_role']}
    Target Role: {state['target_role']}
    Duration: {state['duration']}
    Hours per Day: {state['hours_per_day']}
    Skills: {state['skills']}
    Required Skills: {state['required_skills']}
    Market Demand: {state['market_demand']}
    """
    openai_response = client.responses.create(
        model="gpt-5",
        input=f"{SYSTEM_PROMPT}",
        tools=[{"type": "web_search"}]
    )
    return {"project_ideas": openai_response.output_text}

def generate_result(state: State):
    SYSTEM_PROMPT = f"""
    You are an expert Result Checker Agent.
    You are given a job description, current role and target role, duration, hours per day,
    skills, required skills and market demand, and you need to check if the  roadmap and project ideas are good
    and is achievable in the given duration and hours per day.
    and return the result in a boolean value only.

    Job Description: {state['job_description']}
    Current Role: {state['current_role']}
    Target Role: {state['target_role']}
    Duration: {state['duration']}
    Hours per Day: {state['hours_per_day']}
    Skills: {state['skills']}
    Required Skills: {state['required_skills']}
    Market Demand: {state['market_demand']}
    Roadmap: {state['roadmap']}
    Project Ideas: {state['project_ideas']}

    Return your response in the form of true if it is good otherwise return false only. and return the reason for the same.
    """
    openai_response = client.responses.create(
        model="gpt-5",
        input=f"{SYSTEM_PROMPT}",
    )
    return {"result": openai_response.output_text}

def check_result(state: State)->Literal["generate_roadmap", "end_node"]: # type: ignore
    if state["result"] == "false":
        return "generate_roadmap"
    else:
        return "end_node"

def end_node(state: State):
    print("\n\nEnding the roadmap generation process. Final state:", state)
    return state

graph_builder = StateGraph(State)

graph_builder.add_node("extract_skills", extract_skills)
graph_builder.add_node("extract_required_skills", extract_required_skills)
graph_builder.add_node("extract_market_demand", extract_market_demand)
graph_builder.add_node("generate_roadmap", generate_roadmap)
graph_builder.add_node("generate_project_ideas", generate_project_ideas)
graph_builder.add_node("generate_result", generate_result)
graph_builder.add_node("end_node", end_node)

graph_builder.add_edge(START, "extract_skills")
graph_builder.add_edge("extract_skills", "extract_required_skills")
graph_builder.add_edge("extract_required_skills", "extract_market_demand")
graph_builder.add_edge("extract_market_demand", "generate_roadmap")
graph_builder.add_edge("generate_roadmap", "generate_project_ideas")
graph_builder.add_edge("generate_project_ideas", "generate_result")
graph_builder.add_conditional_edges("generate_result", check_result,{"generate_roadmap": "generate_roadmap", "end_node": "end_node"})
graph_builder.add_edge("end_node", END)

graph = graph_builder.compile()
