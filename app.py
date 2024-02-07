import streamlit as st
from dotenv import load_dotenv
from utils import *
from langchain.docstore.document import Document
from langchain.callbacks import get_openai_callback
import pandas as pd
import os
import time

load_dotenv()

st.set_page_config("Impressico's Developer Performance Analysis Tool", page_icon="https://media.licdn.com/dms/image/C4E0BAQErzHJr7lA-uQ/company-logo_200_200/0/1631356294168?e=1714608000&v=beta&t=lbeplkUBiGsPGvObCIUmLk5qRA9X8NvoJGHWBZEC6so", layout="wide")

api_token = os.getenv("JIRA_TOKEN")
token = os.getenv('GITHUB_API_TOKEN')

st.title(" Developer Performance Analysis 🥇 ")
st.subheader("Analysing your Developer's Performance 🤖")

tabs = st.tabs(["GitHub Analysis", "Jira Issue Details :bug:"])

with tabs[0]:
    st.image("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMwAAADACAMAAAB/Pny7AAAAaVBMVEX///8XFRUAAAD6+vr19fUUEhIPDQ2lpaUqKioFAAAMCQnu7u7y8vLT09Pb29sIBQV8e3vi4uKsrKzo6OjLy8txcXFGRUWNjY22tbVRUFA8Ozuampq+vr4mJSVdXFwyMjJmZWUdHByEg4Mg1T6LAAAJz0lEQVR4nO1d67ayKhT9XAomXjOveUl9/4c8WntXGhAh2B5nOH82GuKExWJd8d+/HTt27NixY8eOHTt27NixY8eOHb8wLc91j0ldxFcUdXJ0Xc8yzW+/2IfwTkFS5OkZXnDp8jgJTt6331AQ3shjKPvpzR1kLICc6XejHIok+POE3CTOy+l9yQuPJ+DpH+W4RKdvvy8bXmJHk2TxeDww/vGc2snfXJ+jnWYAoRiTm8yFVz7Bt9/8BX40bpNPmPzwIdCXafLtt58h6S7g4E+Z3Nfn0v0dOn5pgCSTG7CDyr9BJ2hFtzxveUbt9v29cxoUULkCID1+lYpbNIqoXOmg+HsHj+l3ECqjMoJAm3zJcjvZBqikMgGc6iuy5qdAVHOZFucLatqKM4W75QkIzvbGJo47NMpF7BfQR+6WXI4lXnVK8oHxlmfOsdcjYr9AQPytuNRqFTINBOJtuBR6l+UGBPYGVMxqCy4jINd+fnoV2oaLgXCuWUVbVa9Rjc2BkV42ln3QcOqzQJpKIxszPmjXY3M2tqWNTH1xtuRiGOGh0KUFAn0mDAtOo+n0dC+bcxkVdKPFXzPLL3AZ2Zx1CNpA44IxVnXuIISp1iuk6rnUNC7kcrk0yJENmT2AHcD9+DAqm0I1F5cWGQvPdVLHeVo2q0I0yJnCmrk9PowmyggUe9JWR1uYX9P2WORlKBsHRNeEQHDbGQl1mFbt2Um1yBA8BgniFMnQGal09pP6pT1jtNJUcvHPtJMfsuf/nOoUf6zvwOmKmRBRJSC8KAxyWBHVioFq/je3bpcBG0ScpxzgMgOFISsWx0hMnQ9I1UUFYoMqQPByOrtxf3+Z2/v356zt0hFdm52b22+/lIBU7vIQcalkEFbmqh1buvgAxQp0u3FxwumVs6hKgqPrWXd4U97WjrIbIwTl6fU8NOkbT11YvaJzIT31bE4ADulSeubw6ildSD0+TNbEVWoMAfrunzQm/fmmkDXl0tWtSTU0Jm9AiQ6wGAtjQKTDamKOpsTt9FkOmZ6IA12dTUKtYGmsnHV46CFTMIeL1nudx57l9W9MBpPVCs1kybAuMjZ7vGHteC5zYTZWAOPShGudTtZ+NNiqeRVYqvk64FozgGMJY9BBhuOcY1j37CPPDtZChuflwTrtzDAufp5dK2LwhIA7YLnm0dx50hJqYJ5qE569wc/BVPpXOCtlmIYzd8RVKoArZWjpnKmATXi+t7NCzixq6Oc+TZE6Dg9wc1n4IO9xFj1PtbRaAqdexJEGZMinOumu/w0EaaqkCDIOm1Ba51glhwxUulInvARwWMrqM//MTpNBpi1Tf0o5RsBZVh5szpbRmacv2LFrhGQ1KGeGtBYhuryBJTcNPb58myAdR8wDscEUCejklHNQMjOYRFp0144cSopEfWH7Zam+LPAE9lmDD3LZGvb+R6HSsPxHQxty5lnO1Pf4osH4f4afsYVCah45DmxYaq4KtdgWrlxYg6MgtXj/M0RMDQCpjEkYsGcn1GIvPyPHLBGHVkad+Uz9qDgtRwNbAziljB2VMC0z1Guv0qsPLIuGnGWUT9Gwnoca5Zn5JXymW4h7mcFjZg8cOmjWzDwyyJExcdlB36+SkQtqcMg0/ysyX9wzysn02iuokw3JbKCa2R6NYjKGVtdsQtFsRka/BVBxfE21ZL5qmykn43TarWZOkEuGDNsCMBzF1WwvMDumC4CIjCpl22YGyTR3HrnsiAaWOuQSRsmMsYXbzI6lhlKBIbY/M6ozzbo5ZkuFnD/D8TQ1pWYe4CQD5TxNbpC009qEbHHjszIhTV55AdG7aZKMnUuRLDrhrPX3Ys2ScbN/Nu+ROuWMlwmUjWhyYs2jJ65RzjiHgrSAB9wsYK4vdM4ubJLPAnjs/Mx0dmlLAwa8Rh3oJC0pXhJb39KYNrcWSPaE4+U0DXLQtDQBZ8escHJ52WZtCSeTWwpEpKXbYltn0yTpSTjXbLfMmCwz6RlMuW2ZmGjI0ngGt63Vka8K49bOTPfEKGTxA377JJIKNN/gcquaprZDhTSueNM+iS8r+mi4m2ZiIy/CNJi8k23CmnqzN5WAE5tW4UUk7jsu67ocLfSmJw5B6SuK1Jh++64/EqNVgvB2rsZ9YytZHDfm1Zn9jNWtGsJ/39/noEhB7UkSCVz89Nrk9hkOcxVw7SZbjIrhPKwcxR8ygSZP57BulEVcEy6DbU8XZc7tnBCyNXSSkYrIDRCrewFc9PTe0AWWaVpukPeL1QmdSyu3d052exG7lIegtZtzZvfB/Uao4/I+MIQddGjtDw2cY1U2WLRnXUG/zulJX6KnBsOiX04nut7C2lb+SycpBaab3O515dqVs8fD+rDDrOcMQX5f6prqIKCrgsha3h1lnt1m+LmVVnBhFFgbQfP80lDeb+1jBzwIHLja2r983qBOGhXB+kU7IID9y4ZZgPy2XI8X+GFAkZu+6KDFj/JsRswTwfBmYDP/9JpaR1EAZXlv1iOc6dEv1REoR/Wzz67jQY6i3uaXfABGvw4z9ZYIoQjK8NnSyMX+qbAXV2eF99p5WvRBKLfFqVqgACusPHgJB95bNGkuCMlETmpeuPQF0qE/GpZBp0fR1/HV0RVrc+OkYF6nR234dFho4UfZ5+nFsIFB5Imx+E1Cgk8Ux2IBnoJmpn1wwh+jBCEcglicPuFHfmYzt6qjkYJjM59/GB4bI0izhlwdnbC/lJGY3nHZ1TELkEZ5fC6eC9r8GohTnKdd16VDJex0WsyS0gW0RE4Xx/3SvDDNzz6SYYqSUb1hrliUtJOVd8KZguYZtFri84sk0Erdb4qdmtpaqJLZnYArFaYYGVBzQwsNhfEsGuvYCIkZMTSWttozpwqtaTsXIYP13qZbzV1EkM8Fmu/vSsV6SycmM3nGxoE0kHM03pPBksUYHyAPZy+BANri6Hq3Q8Y0PfcktlhvyRDdjW0TcrI0LIFkURXXdV3Y1VAekNBSvSNDyAZcJi2wdEXw7BtTBxVkwk1u0h5hc++gJSrIQLMRl3//al4qRQUZyLT3gTzgd+xopDAZdms5dJvdpD/hFDE/pLGaDIFo4y+3mDFiiBoWI8P0ZwDF23+2JWB8GWQdGQS6C8AZyKlfoVhDBkG/yelCQ5Lh1+gXPgh5UzQyIc6++FEtM89eFIE0GQKZ/o80cOFH50WuRZIMhnO0qUKmwayjZkZHigyGJqr/wldD3TrCT5pAggwCHNWbfg2IAzcZ4G594kaMzL0RgwAMyV+hMsELquanckM0mPoT6wFoqj/30VPTLW53F4ter368/TsrRDLtX8CpKjPxL2G5UVZWf/jDrTt27NixY8eOHTt27NixY8eOv4r/AGS5jKsfz6j5AAAAAElFTkSuQmCC", width=100, use_column_width= 40)
    st.title("GitHub Developer Performance Analysis")

    owner = st.text_input("Enter your GitHub's Owner name")
    repo = st.text_input("Enter your Repository ")
    username = st.text_input("Enter your username ")

    submit = st.button("Analyse")

    if submit and owner and repo and token:
        with get_openai_callback() as cb:
            analysis_results = []

            changed_files_info = get_user_changed_files_in_commits(owner, repo, username, token)
            user_pull_requests = get_user_pull_requests(owner, repo, username, token)
            st.header("\nUser Commits in the Last Week:")
            st.toast("Getting Commit Info")

            commit_analysis = None
            pr_analysis = None

            for commit_info in changed_files_info:
                st.write(f"\nCommit SHA: {commit_info['sha']}")
                st.write(f"Commit Message: {commit_info['message']}")

                if commit_info['changed_files']:
                    st.subheader("\nChanged Files:")
                    for file_info in commit_info['changed_files']:
                        with st.expander("Code"):
                            st.write(f"\nFile Status: {file_info['status']}")
                            st.write(f"File Path: {file_info['path']}")
                            
                            if file_info['content']:
                                st.write("File Content:")
                                st.code(file_info['content'])
                                commit_analysis = generate(file_info['path'], file_info['content'])
                                time.sleep(10)

                            else:
                                st.warning("No file changed in this commit 🚨")
                else:
                    st.warning("No changed files in this commit.") 

                analysis_results.append({
                'type': 'commit',
                'sha': commit_info['sha'],
                'analysis': commit_analysis
                })
            
            st.toast("Getting Pull request info")

            st.header("\nUser Pull Requests in the Last Week:")
            for pull_request in user_pull_requests:
                    with st.expander("pull requestes info"):
                        st.write(f"\nPull Request Number: {pull_request['number']}")
                        st.write(f"Pull Request Title: {pull_request['title']}")
                        st.write(f"State: {pull_request['state']}")
                        
                        if pull_request['comments']:
                            st.write(f"\nComments:")
                            for comment in pull_request['comments']:
                                st.write(f"Comment by {comment['user']}: {comment['body']}")
                                pr_analysis = generateres(comment['user'], comment['body'])
                                time.sleep(10)
                        else:
                            st.warning("No comments on this pull request.")

                        
                        analysis_results.append({
                        'type': 'pull_request',
                        'number': pull_request['number'],
                        'analysis': pr_analysis
                        })
            
            all_analyses = []

            st.toast("Doing an analysis on your code")
                    
            st.header("Developer Performance Analysis Results:")
            for result in analysis_results:
                if result['type'] == 'commit':
                    st.subheader(f"Commit SHA: {result['sha']}")
                elif result['type'] == 'pull_request':
                    st.subheader(f"Pull Request Number: {result['number']}")
                st.write(result['analysis'])

                all_analyses.append(str(result['analysis']))
            all_analyses_content = "\n".join(all_analyses)

            doc =  Document(page_content=all_analyses_content)


            overall_summary = get_summary(doc)
            
            st.header("\nOverall Summary:")
            st.write(overall_summary)
            st.toast("Here is your summary")  


            data = [line.split(": ") for line in str(cb).strip().split("\n")]
            df = pd.DataFrame(data, columns=["Metric", "Value"])

            
            st.subheader("Cost")
            st.table(df)



with tabs[1]:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Jira_Logo.svg/2560px-Jira_Logo.svg.png", width=100, use_column_width= 40)
    st.title("Jira Issue Details")

    url = st.text_input("Enter your project URL")
    email = st.text_input("Enter your email id")
    key = st.text_input("Enter Issue Key to fetch")

    submit = st.button("Fetch Issue Details")

    if submit and url and email and api_token and key:
        issue_info = get_jira_issue_info(url, key, email, api_token)

        if issue_info:
            for key, value in issue_info.items():
                st.write(f"{key}: {value}")
        else:
            st.warning("Issue not found or insufficient permissions.")
