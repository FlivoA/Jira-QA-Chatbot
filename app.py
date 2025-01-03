import streamlit as st
from transformers import pipeline
import requests
from requests.auth import HTTPBasicAuth

# Set up Jira credentials
JIRA_URL = "https://pavannekkanti1234.atlassian.net/"
JIRA_EMAIL = "pavannekkanti1234@gmail.com"
JIRA_API_TOKEN = "ATATT3xFfGF0aeWOqF2UwCy2t_uMnrTEWE5GAsK1BqJv5kzxs0GvOc8SCQd_-dvHSIzFbAiaIXP1wmcM7v1zEswqRdVZ8k-pHFhXosjHLYqz5OXj3ZDW10RPOArtU8eNIkDt9pyf8C80zj_y4Rb91SqkGSVj4hKqbkhHjuzYahIprgxPA6ovjt4=0E989D9E"

# Load the QA pipeline with a model suited for Question-Answering
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

# Function to fetch Jira project issues
def get_project_issues(project_key):
    url = f"{JIRA_URL}/rest/api/3/search"
    query = {"jql": f"project={project_key}"}
    response = requests.get(url, headers={"Content-Type": "application/json"},
                            params=query, auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN))
    if response.status_code == 200:
        return response.json().get("issues", [])
    else:
        st.error(f"Failed to fetch issues: {response.status_code} {response.reason}")
        return []

# Function to parse task details from Jira issues
def parse_task_details(issues):
    tasks = []
    for issue in issues:
        tasks.append({
            "id": issue["id"],
            "summary": issue["fields"].get("summary", "No Summary"),
            "status": issue["fields"]["status"]["name"],
            "assignee": issue["fields"].get("assignee", {}).get("displayName", "Unassigned"),
            "duedate": issue["fields"].get("duedate", "None"),
            "startdate": issue["fields"].get("created", "None"),
            "reporter": issue["fields"]["reporter"]["displayName"],
            "priority": issue["fields"]["priority"]["name"]
        })
    return tasks

# Function to dynamically answer queries about Jira project using a QA model
def get_dynamic_jira_answer(query, context):
    response = qa_pipeline(question=query, context=context)
    return response['answer']

# Streamlit UI for interacting with the app
st.title('Jira QA Chatbot')

# Step 1: Enter project key and fetch context
project_key = st.text_input("Enter your Jira project key:")

if project_key:
    issues = get_project_issues(project_key)
    if not issues:
        st.write("No issues found for this project.")
    else:
        tasks = parse_task_details(issues)
        # Generate a well-formatted context
        context = "Here are the tasks in the project:\n\n"
        for task in tasks:
            context += (
                f"Task ID: {task['id']}\n"
                f"Summary: {task['summary']}\n"
                f"Status: {task['status']}\n"
                f"Assignee: {task['assignee']}\n"
                f"Due Date: {task['duedate']}\n"
                f"Start Date: {task['startdate']}\n"
                f"Reporter: {task['reporter']}\n"
                f"Priority: {task['priority']}\n"
                f"{'-'*40}\n"
            )
        st.text(context)

        # Step 2: Ask a query based on the context
        query = st.text_input("Ask a question about the tasks above:")
        if query:
            answer = get_dynamic_jira_answer(query, context)
            st.write(f"Answer: {answer}")
