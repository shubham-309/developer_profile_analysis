import requests
from datetime import datetime, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.summarize import load_summarize_chain
from dotenv import load_dotenv
import base64

load_dotenv()

def fetch_user_changed_files_in_commits(owner, repo, username, token):
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
                    'content': "",
                    'patch': file_info['patch']
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


def fetch_user_pull_requests(owner, repo, username, token):
    print(f"Fetching pull requests for {username} in {owner}/{repo}")
    base_url = "https://api.github.com"
    pulls_url = f"{base_url}/repos/{owner}/{repo}/pulls"

    headers = {"Authorization": f"token {token}"}

    one_week_ago = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

    pulls_params = {
        "state": "all",
        "sort": "updated",
        "direction": "desc",
        "since": one_week_ago,
        "creator": username
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

def generate_developer_performance_analysis(filename, code_content, commit_message):
    llm_g = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.9)
    prompt = """
Task: Evaluate the developer's performance by analyzing code quality and commit messages in their recent commits.

Instructions:
1. Retrieve the last few commits made by the developer in the specified repository.
2. Assess the code quality, considering factors such as adherence to coding standards, maintainability, and efficiency, based on the provided unified diff/patch file.
3. Evaluate the clarity and relevance of the commit messages in conveying the changes made.
4. Provide a rating on a scale of 1 to 5 stars for both code quality and commit message quality, where 1 represents poor performance and 5 represents excellent performance.
5. Include a detailed summary of the analysis for both aspects, highlighting strengths and areas for improvement.
6. If there are specific criteria or coding standards to adhere to, mention them in your analysis.

Input:
File Name: {filename}
Code Changes: {code}
Commit Message: {commit_message}

Output Structure:
Code Quality Rating: [1-5 stars (only display number of ⭐)]
Commit Message Quality Rating: [1-5 stars (only display number of ⭐)]

Summary:
- Code Quality Strengths: [Identify strong points]
- Areas for Improvement in Code Quality: [Highlight areas that need improvement]
- Commit Message Clarity: [Evaluate how well the commit message conveys changes]
- Areas for Improvement in Commit Messages: [Highlight areas that need improvement]

Recommendations:
- Suggest specific actions to enhance code quality.
- Provide guidance on writing clear and informative commit messages.
- Offer advice on adopting best practices.

Note: The ratings should reflect the overall code quality and commit message quality, and the summary should offer constructive feedback for improvement.
Special note: Please do not include or print any code file or code in the output.
"""

    prompt = prompt.format(code=code_content, filename=filename, commit_message=commit_message)
    response = llm_g.invoke(prompt)
    return response.content

def generate_pull_request_analysis(user, comment):
    llm_g = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.9)
    prompt = """
    Task: Evaluate the developer's performance by analyzing comment quality in their pull requests.

    Do an analysis on {user}'s {comment} on an repository and give him an rating from 1-5 based on the comments on Pull request.
    
    1. Positive comments : like +1, bravo, nice,this code looks very good etc.
    2. Code suggestions in comments: Some alternate implementation of current code, this should be considered as neutral.
    3. Change Request: This could be considered as negative or if reviewer says there is a change in requirement then neutral.

    input:
    user - {user}
    comment - {comment}

    Output Structure:
    Developer Performance Rating: [1-5 (only display number of ⭐)]
    

    Note: The rating should reflect the overall comment quality.
    """
    prompt = prompt.format(user=user, comment=comment)
    response = llm_g.invoke(prompt)
    return response.content

def fetch_jira_issue_info(url, issue_key, email, api_token):
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
        assignee_name = assignee_info['displayName'] if assignee_info else "Unassigned"

        return {
            "Issue Key": issue_key,
            "Issue Type": issue_type,
            "Project": project_name,
            "Priority": priority_name,
            "Status": status_name,
            "Summary": summary,
            "Creator": creator_name,
            "Assignee": assignee_name,
        }
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def fetch_file_content(file_url):
    response = requests.get(file_url)
    return response.text if response.status_code == 200 else None

def get_summary(doc):
    llm_g = ChatGoogleGenerativeAI(model="gemini-pro")
    chain = load_summarize_chain(llm_g, chain_type="stuff")
    summary = chain.run([doc])
    return summary