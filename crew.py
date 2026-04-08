from crewai import Agent, Task, Crew
from crewai.llm import LLM
from dotenv import load_dotenv
import os
# Assuming your tools are in a file named tool.py
from tool import read_csv, analyze_csv 

load_dotenv()

def get_llm(temp):
    return LLM(
        model="llama-3.3-70b-versatile",
        temperature=temp,
        api_key=os.getenv("GROQ_API_KEY"),
        api_base="https://api.groq.com/openai/v1"
    )

def run_data_crew(csv_path: str):
    # 1. AGENTS
    dataset_analyzer = Agent(
        role="Senior Data Analyst",
        goal="Extract descriptive stats, key patterns, and anomalies from the CSV.",
        backstory="Expert in exploratory data analysis and statistical reasoning.",
        tools=[read_csv, analyze_csv],
        llm=get_llm(0.2),
        verbose=True
    )

    insight_reporter = Agent(
        role="Data Insights Report Writer",
        goal="Convert analytical findings into a professionally written insight report.",
        backstory="Specialist in translating complex data into actionable narratives.",
        llm=get_llm(0.4),
        verbose=True
    )

    # 2. TASKS
    task_analyze = Task(
    description=f"Analyze the dataset named '{csv_path}'. Pass ONLY the filename to your tools.",
    expected_output="Technical statistical summary.",
    agent=dataset_analyzer
    )

    task_generate = Task(
        description="Using the analysis, write a report with: Overview, Stats Summary, Trends, and Actionable Insights.",
        expected_output="A polished, structured markdown report.",
        agent=insight_reporter,
        context=[task_analyze]
    )

    # 3. CREW
    crew = Crew(
        agents=[dataset_analyzer, insight_reporter],
        tasks=[task_analyze, task_generate],
        verbose=True
    )

    crew.kickoff()

    return {
        "raw_analysis": task_analyze.output.raw,
        "final_report": task_generate.output.raw
    }