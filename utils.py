from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import requests
import base64  # Add this import
from datetime import datetime, timedelta
from langchain.chains.summarize import load_summarize_chain


load_dotenv()

def get_user_changed_files_in_commits(owner, repo, username, token):
    print(f"Fetching changed files for {username} in {owner}/{repo}")
    base_url = "https://api.github.com"
    commits_url = f"{base_url}/repos/{owner}/{repo}/commits"

    headers = {"Authorization": f"token {token}"}

    # Calculate the date 1 week ago
    one_week_ago = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Get user commits
    commits_params = {
        "author": username,
        "since": one_week_ago,
    }

    commits_response = requests.get(commits_url, headers=headers, params=commits_params)
    
    # Raise an exception if the request was unsuccessful
    commits_response.raise_for_status()

    # Parse JSON response
    commits_data = commits_response.json()

    user_changed_files = []

    for commit in commits_data:
        commit_details = {
            'sha': commit['sha'],
            'message': commit['commit']['message'],
            'changed_files': []
        }

        # Get file changes
        files_url = f"{base_url}/repos/{owner}/{repo}/commits/{commit['sha']}?diff=unified&w=0"
        files_response = requests.get(files_url, headers=headers)
        
        # Raise an exception if the request was unsuccessful
        files_response.raise_for_status()

        # Parse JSON response
        files_data = files_response.json()

        for file_info in files_data.get('files', []):
            # Check if file_info is a dictionary
            if 'changes' in file_info and file_info['changes'] > 0:
                file_details = {
                    'status': file_info['status'],
                    'path': file_info['filename'],
                    'content': ""
                }

                # Get file content
                raw_url = f"{base_url}/repos/{owner}/{repo}/contents/{file_info['filename']}?ref={commit['sha']}"
                file_response = requests.get(raw_url, headers=headers)
                
                # Raise an exception if the request was unsuccessful
                file_response.raise_for_status()

                # Parse JSON response
                file_data = file_response.json()

                if 'content' in file_data:
                    # Decode content from base64 and convert to UTF-8
                    content = base64.b64decode(file_data['content']).decode('utf-8')
                    file_details['content'] = content

                commit_details['changed_files'].append(file_details)

        user_changed_files.append(commit_details)

    return user_changed_files


# def get_user_changed_files_in_commits(owner, repo, username, token):
#     print(f"Fetching changed files for {username} in {owner}/{repo}")
#     base_url = "https://api.github.com"
#     commits_url = f"{base_url}/repos/{owner}/{repo}/commits"

#     headers = {"Authorization": f"token {token}"}

#     # Calculate the date 1 week ago
#     one_week_ago = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

#     # Get user commits
#     commits_params = {
#         "author": username,
#         "since": one_week_ago,
#     }

#     commits_response = requests.get(commits_url, headers=headers, params=commits_params)
#     commits_response.raise_for_status()
#     commits_data = commits_response.json()

#     user_changed_files = []

#     for commit in commits_data:
#         commit_details = {
#             'sha': commit['sha'],
#             'message': commit['commit']['message'],
#             'changed_files': []
#         }

#         # Get file changes directly from commit details
#         changes = commit.get('files', [])

#         for file_info in changes:
#             file_details = {
#                 'status': file_info['status'],
#                 'path': file_info['filename'],
#                 'content': ""
#             }

#             # Get file content
#             raw_url = f"{base_url}/repos/{owner}/{repo}/contents/{file_info['filename']}?ref={commit['sha']/'?diff=unified&w=0'}"
#             file_response = requests.get(raw_url, headers=headers)
#             file_response.raise_for_status()
#             file_data = file_response.json()

#             if 'content' in file_data:
#                 content = base64.b64decode(file_data['content']).decode('utf-8')
#                 file_details['content'] = content

#             commit_details['changed_files'].append(file_details)

#         user_changed_files.append(commit_details)

#     return user_changed_files



def get_user_pull_requests(owner, repo, username, token):
    print(f"Fetching pull requests for {username} in {owner}/{repo}")
    base_url = "https://api.github.com"
    pulls_url = f"{base_url}/repos/{owner}/{repo}/pulls"

    headers = {"Authorization": f"token {token}"}

    # Calculate the date 1 week ago
    one_week_ago = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Get user pull requests
    pulls_params = {
        # "state": "open",  # Filter by open pull requests
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

# def get_commits_count(owner, repo, username, token):
#     base_url = "https://api.github.com"
#     url = f"{base_url}/repos/{owner}/{repo}/commits"
#     headers = {"Authorization": f"token {token}"}

#     today = datetime.date.today()
#     last_week = today - datetime.timedelta(days=7)

#     params = {
#         "author": username,
#         "since": last_week.strftime("%Y-%m-%d"),
#         "until": today.strftime("%Y-%m-%d")
#     }

#     response = requests.get(url, headers=headers, params=params)
#     response.raise_for_status()

#     commits = response.json()
#     return len(commits)

# def get_pull_requests_count(owner, repo, username, token):
#     base_url = "https://api.github.com"
#     url = f"{base_url}/repos/{owner}/{repo}/pulls"
#     headers = {"Authorization": f"token {token}"}

#     today = datetime.date.today()
#     last_week = today - datetime.timedelta(days=7)

#     params = {
#         "author": username,
#         "state": "all",
#         "since": last_week.strftime("%Y-%m-%d"),
#         "until": today.strftime("%Y-%m-%d")
#     }

#     response = requests.get(url, headers=headers, params=params)
#     response.raise_for_status()

#     pull_requests = response.json()
#     return len(pull_requests)

# def get_commit_file_contents(owner, repo, username, token, branch):
#     base_url = "https://api.github.com"
#     commits_url = f"{base_url}/repos/{owner}/{repo}/commits?sha={branch}"
#     headers = {"Authorization": f"token {token}"}

#     response = requests.get(commits_url, headers=headers)
#     response.raise_for_status()

#     commits_info = response.json()

#     file_contents = {}
#     for commit_info in commits_info:
#         commit_sha = commit_info.get('sha')
#         commit_files_url = f"{base_url}/repos/{owner}/{repo}/commits/{commit_sha}"
#         commit_response = requests.get(commit_files_url, headers=headers)
#         commit_response.raise_for_status()

#         commit_data = commit_response.json()

#         # Check if 'author' is not None before accessing 'login'
#         author = commit_data.get('author')
#         if author and 'login' in author:
#             author_login = author['login']
#             if author_login == username:
#                 modified_files = commit_data.get('files', {})

#                 for file_info in modified_files:
#                     file_path = file_info.get('filename')
#                     file_url = file_info.get('raw_url')
#                     file_content = get_file_content(file_url)

#                     if file_content is not None:
#                         file_contents[file_path] = file_content

#     return file_contents


# def get_file_content(file_url):
#     response = requests.get(file_url)
#     if response.status_code == 200:
#         return response.text
#     else:
#         return None

# def get_pull_request_comments_by_user(owner, repo, username, token):
#     # Get the current date and time
#     current_datetime = datetime.date.today()

#     # Calculate the date 7 days ago
#     seven_days_ago = current_datetime - timedelta(days=7)

#     # Get the list of pull requests
#     pulls_url = f'https://api.github.com/repos/{owner}/{repo}/pulls'
#     headers = {"Authorization": f"token {token}"}

#     response_pulls = requests.get(pulls_url, headers=headers)

#     pull_requests_info = []

#     if response_pulls.status_code == 200:
#         pull_requests = response_pulls.json()

#         for pull_request in pull_requests:
#             # Check if the pull request is closed
#             if pull_request['state'] == 'closed':
#                 continue

#             pull_number = pull_request['number']
#             comments_url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/comments'

#             # Get comments for the pull request
#             response_comments = requests.get(comments_url, headers=headers)

#             if response_comments.status_code == 200:
#                 comments = response_comments.json()

#                 for comment in comments:
#                     # Check if the comment is made by the specified user and within the last 7 days
#                     comment_datetime = datetime.datetime.strptime(comment['created_at'], "%Y-%m-%dT%H:%M:%SZ")
#                     if comment['user']['login'] == username and seven_days_ago <= comment_datetime <= current_datetime:
#                         pull_requests_info.append({
#                             'pull_request_title': pull_request['title'],
#                             'pull_request_number': pull_number,
#                             'comment_body': comment['body']
#                         })
#             else:
#                 print(f"Failed to retrieve comments for Pull Request #{pull_number}. Status code: {response_comments.status_code}")
#     else:
#         print(f"Failed to retrieve pull requests. Status code: {response_pulls.status_code}")

#     return pull_requests_info





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

    input:
    file name - {filename}
    code - {code}

    Output Structure:
    Developer Performance Rating: [1-5 stars (display stars)]
    
    Summary:
    - Code Quality Strengths: [Identify strong points]
    - Areas for Improvement: [Highlight areas that need improvement]

    Recommendations:
    - Suggest specific actions to enhance code quality.
    - Provide guidance on adopting best practices.

    Note: The rating should reflect the overall code quality, and the summary should offer constructive feedback for improvement also don.t print any code in o/p.
    """

    Developer_Performance_Analysis_Prompt = Developer_Performance_Analysis_Prompt.format(code = content_variables, filename= filename)
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
    Developer Performance Rating: [1-5 (display stars)]
    

    Note: The rating should reflect the overall comment quality.
    """

    Pull_Request_Analysis_Prompt = Pull_Request_Analysis_Prompt.format(user = user, comment = comment)
    response = llm_g.invoke(Pull_Request_Analysis_Prompt)
    response = response.content
    pranalysis = response
    return pranalysis


# def get_github_repo_issues(owner, repo, token):
#     issues_url = f'https://api.github.com/repos/{owner}/{repo}/issues'
#     headers = {"Authorization": f"token {token}"}

#     response = requests.get(issues_url, headers=headers)

#     if response.status_code == 200:
#         issues = response.json()
#         return [issue['number'] for issue in issues]
#     else:
#         print(f"Failed to retrieve issues. Status code: {response.status_code}")
#         return []

# def get_github_issue_comments(owner, repo, issue_number, token):
#     comments_url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments'
#     headers = {"Authorization": f"token {token}"}

#     response = requests.get(comments_url, headers=headers)

#     if response.status_code == 200:
#         comments = response.json()
#         for comment in comments:
#             return comment['body']
#     else:
#         print(f"Failed to retrieve comments for issue #{issue_number}. Status code: {response.status_code}")
#         return None









# url = "https://h49574215.atlassian.net/rest/api/2/issue/TES-1"
# email = "h49574215@gmail.com"
# api_token = "ATATT3xFfGF0p4hZOJ6rJ-sP8ZTLOBicXD07BFeSU47DleIhCkxScxDummtIuEYP6A3NlKfPwzFwG6YMrljTqbSx_58Xs2GfC2dCxI510o3sMK9Rjcf3Q3MflYOA9FZLdZhn4V5mNiilCwHCvNfr9tFHcMII36kcsxkDKBn6liW1T6zTkEZa_8M=6882AEE7"


def get_jira_issue_info(url,issue_key, email, api_token):
    # Jira API endpoint URL
    url = f"{url}/rest/api/2/issue/{issue_key}"

    # HTTP headers
    headers = {
        "Accept": "application/json",
    }

    # Make the API request
    response = requests.get(url, headers=headers, auth=(email, api_token))

    if response.status_code == 200:
        data = response.json()

        # Extract relevant information
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

        # Create a dictionary with the extracted information
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


def get_last_commit_file_contents(owner, repo, username, token, branch):
    base_url = "https://api.github.com"
    commits_url = f"{base_url}/repos/{owner}/{repo}/commits?sha={branch}&author={username}&per_page=1"
    headers = {"Authorization": f"token {token}"}

    response = requests.get(commits_url, headers=headers)
    response.raise_for_status()

    commits_info = response.json()

    if not commits_info:
        print("No commits found.")
        return

    commit_info = commits_info[0] # Assuming there is at least one commit

    commit_sha = commit_info.get('sha')
    commit_files_url = f"{base_url}/repos/{owner}/{repo}/commits/{commit_sha}"
    commit_response = requests.get(commit_files_url, headers=headers)
    commit_response.raise_for_status()

    commit_data = commit_response.json()

    # Check if 'author' is not None before accessing 'login'
    author = commit_data.get('author')
    if author and 'login' in author:
        author_login = author['login']
        if author_login == username:
            modified_files = commit_data.get('files', [])

            files_info = []
            for file_info in modified_files:
                file_path = file_info.get('filename')
                additions = file_info.get('additions', 0)
                deletions = file_info.get('deletions', 0)
                file_url = file_info.get('raw_url')
                file_content = get_file_content(file_url)

                files_info.append({
                    'file_path': file_path,
                    'additions': additions,
                    'deletions': deletions,
                    'content': file_content
                })

            return files_info

    return None

# def get_file_content(file_url):
#     response = requests.get(file_url)
#     if response.status_code == 200:
#         return response.text
#     else:
#         return None