import streamlit as st
from transformers import pipeline
import requests

# Set up Jira credentials
JIRA_URL = "https://pavannekkanti1234.atlassian.net/"
JIRA_EMAIL = "pavannekkanti1234@gmail.com"
JIRA_API_TOKEN = "ATATT3xFfGF0aeWOqF2UwCy2t_uMnrTEWE5GAsK1BqJv5kzxs0GvOc8SCQd_-dvHSIzFbAiaIXP1wmcM7v1zEswqRdVZ8k-pHFhXosjHLYqz5OXj3ZDW10RPOArtU8eNIkDt9pyf8C80zj_y4Rb91SqkGSVj4hKqbkhHjuzYahIprgxPA6ovjt4=0E989D9E"

# Load the QA pipeline with a model suited for Question-Answering
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

# Function to fetch Jira project issues
def get_project_issues(project_key):
    url = f"{JIRA_URL}/rest/api/2/search"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    query = {
        "jql": f"project={project_key}",
        "fields": ["id", "summary", "status", "assignee", "duedate", "created", "reporter", "priority"]
    }
    
    response = requests.get(url, headers=headers, auth=auth, params=query)
    if response.status_code == 200:
        return response.json().get("issues", [])
    else:
        st.error(f"Failed to fetch issues. Error: {response.status_code}")
        return []

# Function to parse Jira issues into task details
def parse_task_details(issues):
    tasks = []
    for issue in issues:
        fields = issue.get("fields", {})
        assignee = fields.get("assignee")
        reporter = fields.get("reporter")
        priority = fields.get("priority")
        status = fields.get("status")

        task = {
            "id": issue.get("id", "N/A"),
            "summary": fields.get("summary", "N/A"),
            "status": status.get("name", "N/A") if status else "N/A",
            "assignee": assignee.get("displayName", "Unassigned") if assignee else "Unassigned",
            "duedate": fields.get("duedate", "N/A"),
            "startdate": fields.get("created", "N/A"),
            "reporter": reporter.get("displayName", "N/A") if reporter else "N/A",
            "priority": priority.get("name", "N/A") if priority else "N/A"
        }
        tasks.append(task)
    return tasks

# Function to dynamically answer queries about Jira project using a QA model
def get_dynamic_jira_answer(query, project_key):
    issues = get_project_issues(project_key)

    if not issues:
        return "No issues found for this project."

    tasks = parse_task_details(issues)
    context = "Here are the tasks in the project:\n\n"
    for task in tasks:
        context += (
            f"Task ID: {task['id']} | "
            f"Summary: {task['summary']} | "
            f"Status: {task['status']} | "
            f"Assignee: {task['assignee']} | "
            f"Due Date: {task['duedate']} | "
            f"Start Date: {task['startdate']} | "
            f"Reporter: {task['reporter']} | "
            f"Priority: {task['priority']}\n"
        )
    return context

# Streamlit UI for interacting with the app
st.title('Jira QA Chatbot')

project_key = st.text_input("Enter your Jira project key:")

if project_key:
    # Fetch and display the task context
    context = get_dynamic_jira_answer("", project_key)
    if context != "No issues found for this project.":
        st.text(context)
    
    # Ask a query once the context is displayed
    query = st.text_input("Ask a question about your Jira tasks:")
    if query:
        response = qa_pipeline(question=query, context=context)
        st.write(f"Answer: {response['answer']}")
