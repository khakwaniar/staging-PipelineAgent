import streamlit as st

import requests

def generate_pipeline_with_ai(project_details, api_key):
    prompt = f"""
    Generate a GitHub Actions YAML pipeline for a software project with these details:
    - Language/Tech: {project_details['language']}
    - Database: {project_details['database']}
    - Other tech: {project_details['other_tech']}
    - Build steps: Auto-detect based on language (e.g., npm install for Node, pip install for Python).
    - Test steps: Run unit tests if applicable.
    - Deploy to staging server: {project_details['staging_server']}. Use {project_details['deploy_method']} for deployment. Assume secure credentials are stored as GitHub secrets (e.g., SSH_KEY, SERVER_USER, SERVER_PASS).
    - Trigger on push to main branch.
    - Make it simple, secure, handle errors, and avoid overwriting other projects' files (e.g., deploy to a project-specific folder like /staging/{project_details['project_name']}/).
    Output ONLY the YAML code, no explanations.
    """
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "xai/grok-code-fast-1",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

st.title("Pipeline AI Agent Chatbot")
st.write("Enter project details to generate a custom GitHub Actions pipeline for deployment to staging.")

with st.form(key="project_form"):
    project_name = st.text_input("Project Name (used for unique folder)")
    language = st.text_input("Main programming language (e.g., Python, Node.js, Java)")
    database = st.text_input("Database (e.g., PostgreSQL, MongoDB, none)")
    other_tech = st.text_input("Other technologies (e.g., React, Docker, none)")
    staging_server = st.text_input("Staging server IP/hostname")
    deploy_method = st.text_input("Deployment method (e.g., SSH with scp, FTP)")
    api_key = st.text_input("Your OpenRouter API Key for Grok (kept private)", type="password")
    submit = st.form_submit_button("Generate Pipeline")

if submit:
    if not all([project_name, language, staging_server, deploy_method, api_key]):
        st.error("Please fill all required fields.")
    else:
        project_details = {
            'project_name': project_name,
            'language': language,
            'database': database,
            'other_tech': other_tech,
            'staging_server': staging_server,
            'deploy_method': deploy_method
        }
        with st.spinner("Generating..."):
            pipeline_yaml = generate_pipeline_with_ai(project_details, api_key)
        
        if "Error" in pipeline_yaml:
            st.error(pipeline_yaml)
        else:
            st.success("Pipeline generated!")
            st.code(pipeline_yaml, language="yaml")
            st.download_button("Download YAML", pipeline_yaml, file_name=f"{project_name}_workflow.yml")
            st.info("Copy to your repo's .github/workflows/ folder. Set GitHub secrets (e.g., SERVER_USER, SSH_KEY) for deployment. Files deploy to a unique folder to avoid conflicts.")
