import requests
import datetime
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

def get_commits_count(owner, repo, token):
    base_url = "https://api.github.com"
    url = f"{base_url}/repos/{owner}/{repo}/commits"
    headers = {"Authorization": f"token {token}"}

    today = datetime.date.today()
    last_week = today - datetime.timedelta(days=7)

    params = {
        "author": owner,
        "since": last_week.strftime("%Y-%m-%d"),
        "until": today.strftime("%Y-%m-%d")
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    commits = response.json()
    return len(commits)

def get_pull_requests_count(owner, repo, token):
    base_url = "https://api.github.com"
    url = f"{base_url}/repos/{owner}/{repo}/pulls"
    headers = {"Authorization": f"token {token}"}

    today = datetime.date.today()
    last_week = today - datetime.timedelta(days=7)

    params = {
        "author": owner,
        "state": "all",
        "since": last_week.strftime("%Y-%m-%d"),
        "until": today.strftime("%Y-%m-%d")
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    pull_requests = response.json()
    return len(pull_requests)

def get_commit_file_contents(owner, repo, token, branch='master'):
    base_url = "https://api.github.com"
    code_url = f"{base_url}/repos/{owner}/{repo}/commits/{branch}"
    headers = {"Authorization": f"token {token}"}

    response = requests.get(code_url, headers=headers)
    response.raise_for_status()

    commit_info = response.json()
    modified_files = commit_info.get('files', {})

    file_contents = {}
    for file_info in modified_files:
        file_path = file_info.get('filename')
        file_url = file_info.get('raw_url')
        file_content = get_file_content(file_url)

        if file_content is not None:
            file_contents[file_path] = file_content

    return file_contents

def get_file_content(file_url):
    response = requests.get(file_url)
    if response.status_code == 200:
        return response.text
    else:
        return None
    

owner = "shubham-309"
repo = "AI_RESUME_SCREENING_SYSTEM"
token = "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"

# Replace 'branch' with the desired branch name
branch = "master"

file_contents = get_commit_file_contents(owner, repo, token, branch)

content_variables = {}
for file_path, content in file_contents.items():
    content_variables[file_path] = content

def generate(commit, pr):
    llm_g = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.9)
    Developer_Performance_Analysis_Prompt = """
    Task: Evaluate the developer's performance by analyzing code quality and comments quality in their recent commits.

    Instructions:
    1. Provide the code content from the developer's last commit in the specified repository.
    2. Assess the code quality, looking at factors such as adherence to coding standards, maintainability, and efficiency.
    3. Evaluate the quality of comments in the code, considering clarity, completeness, and relevance.
    4. Provide a rating on a scale of 1 to 5 stars, where 1 represents poor performance and 5 represents excellent performance.
    5. Include a detailed summary of the analysis, highlighting strengths and areas for improvement.
    6. If there are specific criteria or guidelines used for the evaluation, mention them in your analysis.
    7. Offer constructive feedback on how the developer can enhance both code and comment quality.

    Example Input:
    Code from Last Commit: {code}
    number of commit: {commit}
    number of pull requests: {PR}

    Output:
    Rating: 1-5 stars
    Summary:
    - Code Quality: [Comments on code quality]
    - Comments Quality: [Comments on comments quality]
    - Strengths: [Identify strong points]
    - Areas for Improvement: [Highlight areas that need improvement]

    Note: A higher rating should reflect better overall performance in terms of code and comments quality.
    """

    Developer_Performance_Analysis_Prompt = Developer_Performance_Analysis_Prompt.format(code = content_variables, PR = pr, commit = commit)
    response = llm_g.invoke(Developer_Performance_Analysis_Prompt)
    response = response.content
    performance = response
    return performance


