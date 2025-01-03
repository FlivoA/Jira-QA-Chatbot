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
        task = {
            "id": issue.get("id"),
            "summary": issue["fields"].get("summary", "N/A"),
            "status": issue["fields"]["status"].get("name", "N/A"),
            "assignee": issue["fields"].get("assignee", {}).get("displayName", "Unassigned"),
            "duedate": issue["fields"].get("duedate", "N/A"),
            "startdate": issue["fields"].get("created", "N/A"),
            "reporter": issue["fields"].get("reporter", {}).get("displayName", "N/A"),
            "priority": issue["fields"]["priority"].get("name", "N/A")
        }
        tasks.append(task)
    return tasks

# Function to dynamically answer queries about Jira project using a QA model
def get_dynamic_jira_answer(query, project_key):
    issues = get_project_issues(project_key)

    if not issues:
        return "No issues found for this project."

    tasks = parse_task_details(issues)
    context = "Here are the tasks in the project:\n"
    for task in tasks:
        context += f"\nTask ID: {task['id']} | Summary: {task['summary']} | Status: {task['status']} | Assignee: {task['assignee']} | Due Date: {task['duedate']} | Start Date: {task['startdate']} | Reporter: {task['reporter']} | Priority: {task['priority']}"

    response = qa_pipeline(question=query, context=context)
    return response['answer']

# Streamlit UI for interacting with the app
st.title('Jira QA Chatbot')

project_key = st.text_input("Enter your Jira project key:")
query = st.text_input("Ask a question about your Jira tasks:")

if project_key and query:
    answer = get_dynamic_jira_answer(query, project_key)
    st.write(f"Answer: {answer}")
