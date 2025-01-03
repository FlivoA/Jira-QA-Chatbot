import streamlit as st
from transformers import pipeline
import torch
import requests

# Install dependencies if not already installed
# Uncomment the following lines if you're running this locally and need to install the packages
# !pip install transformers
# !pip install datasets
# !pip install torch
# !pip install requests

# Set up Jira credentials (Secure your credentials properly in real scenarios)
JIRA_URL = "https://pavannekkanti1234.atlassian.net/"
JIRA_EMAIL = "pavannekkanti1234@gmail.com"
JIRA_API_TOKEN = "Your_Jira_API_Token"

# Function to fetch Jira issues (dummy function for illustration)
def get_project_issues(project_key):
    # Example Jira API call, replace with actual code
    response = requests.get(
        f"{JIRA_URL}/rest/api/2/search?jql=project={project_key}",
        auth=(JIRA_EMAIL, JIRA_API_TOKEN)
    )
    if response.status_code == 200:
        return response.json()['issues']
    else:
        return []

# Function to parse task details (dummy function for illustration)
def parse_task_details(issues):
    tasks = []
    for issue in issues:
        task = {
            'id': issue['id'],
            'summary': issue['fields']['summary'],
            'status': issue['fields']['status']['name'],
            'assignee': issue['fields'].get('assignee', {}).get('displayName', 'Unassigned'),
            'duedate': issue['fields'].get('duedate', 'No due date'),
            'startdate': issue['fields'].get('created', 'No start date'),
            'reporter': issue['fields']['reporter']['displayName'],
            'priority': issue['fields']['priority']['name']
        }
        tasks.append(task)
    return tasks

# Load the QA pipeline only once to avoid reloading during every function call
@st.cache_resource
def load_qa_pipeline():
    return pipeline("question-answering", model="deepset/roberta-base-squad2")

qa_pipeline = load_qa_pipeline()

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

    # Debugging: Print the context
    st.write(f"Context:\n{context}\n")

    # Pass the query and context to the QA pipeline
    response = qa_pipeline(question=query, context=context)

    # Debugging: Print raw model response to understand the output
    st.write(f"Raw Model Response:\n{response}")

    # Return the answer
    return response['answer']

# Streamlit UI
st.title("Jira Project Query Answering")
project_key = st.text_input("Enter Jira Project Key:", "FLIV")  # Replace with your Jira project key

# Example Query
query = st.text_input("Enter your query about the project:", "Who is the reporter for Task 10002?")

if query and project_key:
    response = get_dynamic_jira_answer(query, project_key)
    st.write("Response:")
    st.write(response)
