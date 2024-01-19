import streamlit as st
from utils import *
from dotenv import load_dotenv

load_dotenv()
 
st.set_page_config(page_title="Developer Performance Analysis APP")
st.title(" Analysing your Developer's Performance 🤖 📑")
st.subheader("Helping you with your work 📝")

owner = st.text_input("Enter your GitHub Username ", key= "shubham-309")
repo = st.text_input("Emter your Repository ")
token = st.text_input("Enter token")
branch = st.text_input("Enter the branch you are working on :-")

submit = st.button("Analyse")

if submit and owner and repo and branch and token:

    count_commits = get_commits_count(owner, repo, token)
    count_pull_requests = get_pull_requests_count(owner, repo, token)
    file_contents = get_commit_file_contents(owner, repo, token, branch)

    if count_commits == 0:
        st.warning("No commit found in last 7 days.")
    else:
        st.write("Total Commits by "+ owner + " into " + repo +" is "+ str(count_commits)+".")
    if count_pull_requests == 0:
        st.warning("No Pull Requests found in last 7 days.")
    else:    
        st.write("Total Pull Requests by "+ owner + " into " + repo +" is "+ str(count_pull_requests)+".")

    # Display file contents
    for file_path, content in file_contents.items():
        st.write("File Name : "+ file_path)
        st.code(content)

    response = generate(count_commits, count_pull_requests, content)
    st.write(response)
