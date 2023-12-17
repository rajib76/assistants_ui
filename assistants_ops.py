import os

import pymongo
import streamlit as st
from assistants.langregister.mongo_db_atlas import MongoAtlas
from assistants.llm_assistants.openai_assistants import OpenAIRetrievalAssistant
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') or st.secrets['OPENAI_API_KEY']
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD") or st.secrets['MONGO_PASSWORD']
print(MONGO_PASSWORD)
mongo_client = MongoAtlas()
mongo_client.uri = "mongodb+srv://rajib76:{MONGO_PASSWORD}@cluster0.cp3rxai.mongodb.net/?retryWrites=true&w=majority".format(
    MONGO_PASSWORD=MONGO_PASSWORD)

client = pymongo.MongoClient(mongo_client.uri)
# Access the desired database and collection
db = client.get_database("assistantstore")
collection = db.get_collection("assistants")
cursor = collection.find({})
discovered_assistants=[]
for document in cursor:
    discovered_assistants.append(document["assistant_name"])


with st.sidebar:
    st.header("OpenAI Configuration")
    selected_model = st.selectbox("Model", ['gpt-3.5-turbo-1106', 'gpt-4-1106-preview'], index=1)
    # selected_key = st.text_input("API Key", type="password")


with st.container():
    with st.form(key="chat_form",clear_on_submit=True):
        assistant_name = st.text_input("Enter name of assistant")
        instructions = st.text_area("Enter the instructions")
        uploaded_file = st.file_uploader("Upload a file to OpenAI embeddings", key="file_uploader")
        upload = st.form_submit_button(label="Create Assistant")

        if upload and instructions and uploaded_file:
            with open(f"{uploaded_file.name}", "wb") as f:
                f.write(uploaded_file.getbuffer())
            assistant = OpenAIRetrievalAssistant(instructions=instructions,
                                                 assistant_name=assistant_name,
                                                 files=[uploaded_file.name],
                                                 model=selected_model
                                                 )
            with st.spinner("Creating assistant"):
                deployed = assistant.deploy_assistant(client=mongo_client)
                print("deployed ",deployed)

            if "Error code" in deployed:
                st.write(deployed)
            else:
                st.write("Created assistant : {assistant_name}".format(assistant_name=assistant.assistant_name) )
