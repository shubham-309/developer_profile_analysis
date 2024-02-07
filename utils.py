from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import requests
import base64
import os
from datetime import datetime, timedelta
from langchain.chains.summarize import load_summarize_chain

load_dotenv()

def get_user_changed_files_in_commits(owner, repo, username, token):
    print(f"Fetching changed files for {username} in {owner}/{repo}")
    base_url = "https://api.github.com"
    commits_url = f"{base_url}/repos/{owner}/{repo}/commits"

    headers = {"Authorization": f"token {token}"}

    one_week_ago = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

    commits_params = {
        "author": username,
        "since": one_week_ago,
    }

    commits_response = requests.get(commits_url, headers=headers, params=commits_params)
    commits_response.raise_for_status()

    commits_data = commits_response.json()

    user_changed_files = []

    for commit in commits_data:
        commit_details = {
            'sha': commit['sha'],
            'message': commit['commit']['message'],
            'changed_files': []
        }

        files_url = f"{base_url}/repos/{owner}/{repo}/commits/{commit['sha']}?diff=unified&w=0"
        files_response = requests.get(files_url, headers=headers)

        files_response.raise_for_status()

        files_data = files_response.json()

        for file_info in files_data.get('files', []):
            if 'changes' in file_info and file_info['changes'] > 0:
                file_details = {
                    'status': file_info['status'],
                    'path': file_info['filename'],
                    'content': ""
                }

                raw_url = f"{base_url}/repos/{owner}/{repo}/contents/{file_info['filename']}?ref={commit['sha']}"
                file_response = requests.get(raw_url, headers=headers)

                file_response.raise_for_status()

                file_data = file_response.json()

                if 'content' in file_data:
                    content = base64.b64decode(file_data['content']).decode('utf-8')
                    file_details['content'] = content

                commit_details['changed_files'].append(file_details)

        user_changed_files.append(commit_details)

    return user_changed_files


def get_user_pull_requests(owner, repo, username, token):
    print(f"Fetching pull requests for {username} in {owner}/{repo}")
    base_url = "https://api.github.com"
    pulls_url = f"{base_url}/repos/{owner}/{repo}/pulls"

    headers = {"Authorization": f"token {token}"}

    # Calculate the date 1 week ago
    one_week_ago = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Get user pull requests
    pulls_params = {
        "state": "all",
        "sort": "updated",
        "direction": "desc",
        "since": one_week_ago,
        "creator": username  # Filter by the creator (user)
    }

    pulls_response = requests.get(pulls_url, headers=headers, params=pulls_params)
    pulls_response.raise_for_status()
    pulls_data = pulls_response.json()

    user_pull_requests = []
    for pull_request in pulls_data:
        pull_request_details = {
            'number': pull_request['number'],
            'title': pull_request['title'],
            'state': pull_request['state'],
            'comments': []
        }

        # Get comments for the pull request
        comments_url = f"{base_url}/repos/{owner}/{repo}/issues/{pull_request['number']}/comments"
        comments_response = requests.get(comments_url, headers=headers)
        comments_response.raise_for_status()
        comments_data = comments_response.json()

        for comment in comments_data:
            comment_details = {
                'user': comment['user']['login'],
                'body': comment['body']
            }
            pull_request_details['comments'].append(comment_details)

        user_pull_requests.append(pull_request_details)

    return user_pull_requests

def get_summary(doc):
    llm_g = ChatGoogleGenerativeAI(model="gemini-pro")
    chain = load_summarize_chain(llm_g, chain_type="stuff")
    summary = chain.run([doc])
    return summary


def generate(filename, content_variables):
    llm_g = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.9)
    Developer_Performance_Analysis_Prompt = """
    Task: Evaluate the developer's performance by analyzing code quality in their recent commits.

    Instructions:
    1. Retrieve the last few commits made by the developer in the specified repository.
    2. Assess the code quality, considering factors such as adherence to coding standards, maintainability, and efficiency.
    3. Provide a rating on a scale of 1 to 5 stars, where 1 represents poor performance and 5 represents excellent performance.
    4. Include a detailed summary of the analysis, highlighting strengths and areas for improvement.
    5. If there are specific criteria or coding standards to adhere to, mention them in your analysis.

    Input:
    File Name: {filename}
    Code : {code}

    Output Structure:
    Developer Performance Rating: [1-5 stars (display ⭐)]
    
    Summary:
    - Code Quality Strengths: [Identify strong points]
    - Areas for Improvement: [Highlight areas that need improvement]

    Recommendations:
    - Suggest specific actions to enhance code quality.
    - Provide guidance on adopting best practices.

    Note: The rating should reflect the overall code quality, and the summary should offer constructive feedback for improvement. Please do not include any code or code suggestion in the output.
    """
    Developer_Performance_Analysis_Prompt = Developer_Performance_Analysis_Prompt.format(code=content_variables,
                                                                                         filename=filename)
    response = llm_g.invoke(Developer_Performance_Analysis_Prompt)
    response = response.content
    performance = response
    return performance


def generateres(user, comment):
    llm_g = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.9)
    Pull_Request_Analysis_Prompt = """
    Task: Evaluate the developer's performance by analyzing comment quality in their pull requests.

    Do an analysis on {user}'s {comment} on an repository and give him an rating from 1-5 based on the comments on Pull request.
    
    1. Positive comments : like +1, bravo, nice,this code looks very good etc.
    2. Code suggestions in comments: Some alternate implementation of current code, this should be considered as neutral.
    3. Change Request: This could be considered as negative or if reviewer says there is a change in requirement then neutral.

    input:
    user - {user}
    comment - {comment}

    Output Structure:
    Developer Performance Rating: [1-5 (display ⭐)]
    

    Note: The rating should reflect the overall comment quality.
    """

    Pull_Request_Analysis_Prompt = Pull_Request_Analysis_Prompt.format(user=user, comment=comment)
    response = llm_g.invoke(Pull_Request_Analysis_Prompt)
    response = response.content
    pranalysis = response
    return pranalysis


def get_jira_issue_info(url, issue_key, email, api_token):
    url = f"{url}/rest/api/2/issue/{issue_key}"

    headers = {
        "Accept": "application/json",
    }

    response = requests.get(url, headers=headers, auth=(email, api_token))

    if response.status_code == 200:
        data = response.json()

        issue_key = data['key']
        issue_type = data['fields']['issuetype']['name']
        project_name = data['fields']['project']['name']
        priority_name = data['fields']['priority']['name']
        status_name = data['fields']['status']['name']
        summary = data['fields']['summary']
        creator_name = data['fields']['creator']['displayName']

        assignee_info = data['fields']['assignee']
        if assignee_info:
            assignee_name = assignee_info['displayName']
        else:
            assignee_name = "Unassigned"

        result = {
            "Issue Key": issue_key,
            "Issue Type": issue_type,
            "Project": project_name,
            "Priority": priority_name,
            "Status": status_name,
            "Summary": summary,
            "Creator": creator_name,
            "Assignee": assignee_name,
        }

        return result
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def get_file_content(file_url):
    response = requests.get(file_url)
    if response.status_code == 200:
        return response.text
    else:
        return None
