import streamlit as st
from utils import *
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Developer Performance Analysis APP")
st.title(" Analysing your Developer's Performance 🤖 📑")
st.subheader("Helping you with your work 📝")

owner = st.text_input("Enter your GitHub Username ", key= "shubham-309")
repo = st.text_input("Emter your Repository ")
token = "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"
branch = st.text_input("Enter the branch you are working on :-")

submit = st.button("Analyse")

if submit and owner and repo and branch and token:

    count_commits = get_commits_count(owner, repo, token)
    count_pull_requests = get_pull_requests_count(owner, repo, token)

    st.write("Total Commits by "+ owner + " into " + repo +" is "+ str(count_commits)+".")
    st.write("Total Pull Requests by "+ owner + " into " + repo +" is "+ str(count_pull_requests)+".")


    for file_path, content in content_variables.items():
        st.write("File Name : "+ file_path)
        st.code(content)

    response = generate(count_commits, count_pull_requests)
    st.write(response)
