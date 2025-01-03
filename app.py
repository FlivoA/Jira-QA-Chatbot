import os
import subprocess
import streamlit as st

# Check if 'transformers' is installed, if not, install it
try:
    import transformers
except ImportError:
    subprocess.check_call([os.sys.executable, "-m", "pip", "install", "transformers"])

# Now we can safely import transformers
from transformers import pipeline

# Set up Jira credentials
JIRA_URL = "https://pavannekkanti1234.atlassian.net/"
JIRA_EMAIL = "pavannekkanti1234@gmail.com"
JIRA_API_TOKEN = "your-jira-api-token"  # Replace with your actual Jira API token

# Load the QA pipeline with a model suited for Question-Answering
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

# Function to fetch project issues from Jira (Example)
def get_project_issues(project_key):
    # Implement your Jira API call here to fetch issues based on the project key
    # For now, this is a placeholder returning a mock response
    return [
        {
            "id": "10001",
            "summary": "Task 1",
            "status": "In Progress",
            "assignee": "John Doe",
            "duedate": "2025-01-10",
            "startdate": "2025-01-03",
            "reporter": "Jane Smith",
            "priority": "High"
        },
        {
            "id": "10002",
            "summary": "Task 2",
            "status": "To Do",
            "assignee": "Alice Brown",
            "duedate": "2025-01-15",
            "startdate": "2025-01-05",
            "reporter": "Bob White",
            "priority": "Medium"
        }
    ]

# Function to parse task details (Mock)
def parse_task_details(issues):
    # Mocking the parsing of issues
    tasks = []
    for issue in issues:
        tasks.append({
            "id": issue["id"],
            "summary": issue["summary"],
            "status": issue["status"],
            "assignee": issue["assignee"],
            "duedate": issue["duedate"],
            "startdate": issue["startdate"],
            "reporter": issue["reporter"],
            "priority": issue["priority"]
        })
    return tasks

# Function to dynamically answer queries about Jira project using a QA model
def get_dynamic_jira_answer(query, project_key):
    # Fetch Jira issues for the selected project
    issues = get_project_issues(project_key)

    if not issues:
        return "No issues found for this project."

    # Parse and structure task details from issues
    tasks = parse_task_details(issues)

    # Build a detailed context from the task details
    context = "Here are the tasks in the project:\n"
    for task in tasks:
        context += f"\nTask ID: {task['id']} | Summary: {task['summary']} | Status: {task['status']} | Assignee: {task['assignee']} | Due Date: {task['duedate']} | Start Date: {task['startdate']} | Reporter: {task['reporter']} | Priority: {task['priority']}"

    # Pass the query and context to the QA pipeline
    response = qa_pipeline(question=query, context=context)

    # Return the answer
    return response['answer']

# Streamlit UI for interacting with the app
st.title('Jira QA Chatbot')

project_key = st.text_input("Enter your Jira project key:")
query = st.text_input("Ask a question about your Jira tasks:")

if project_key and query:
    answer = get_dynamic_jira_answer(query, project_key)
    st.write(f"Answer: {answer}")
