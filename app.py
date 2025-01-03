import streamlit as st
from transformers import pipeline

# Set up Jira credentials
JIRA_URL = "https://pavannekkanti1234.atlassian.net/"
JIRA_EMAIL = "pavannekkanti1234@gmail.com"
JIRA_API_TOKEN = "ATATT3xFfGF0aeWOqF2UwCy2t_uMnrTEWE5GAsK1BqJv5kzxs0GvOc8SCQd_-dvHSIzFbAiaIXP1wmcM7v1zEswqRdVZ8k-pHFhXosjHLYqz5OXj3ZDW10RPOArtU8eNIkDt9pyf8C80zj_y4Rb91SqkGSVj4hKqbkhHjuzYahIprgxPA6ovjt4=0E989D9E"

# Load the QA pipeline with a model suited for Question-Answering
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

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
