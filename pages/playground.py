import os
import streamlit as st
import streamlit.components.v1 as components
import pymongo
from assistants.langregister.mongo_db_atlas import MongoAtlas
from assistants.llm_assistants.openai_assistants import OpenAIRetrievalAssistant
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') or st.secrets['OPENAI_API_KEY']
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD") or st.secrets['MONGO_PASSWORD']
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
    assistants = st.selectbox("Assistants", discovered_assistants, index=1)
    assistant = OpenAIRetrievalAssistant(assistant_name=assistants)
    if "thread" not in st.session_state:
        _, thread, assistant_id = assistant.init_assistant(greeting="Hi", client=mongo_client)
        st.session_state["thread"] = thread
        st.session_state["assistant_id"] = assistant_id

with st.container():
    with st.form(key="chat_form",clear_on_submit=True):
        question = st.text_area("What do you want to ask")
        submit_button = st.form_submit_button("submit")
        if submit_button:
            if question.lower() == "exit":

                answer = "Thanks for using my expertise"
                st.write(answer)
                deleted = assistant.destroy_thread(st.session_state["thread"])
                st.session_state.pop("thread")
                if deleted:
                    st.write("Thread has been deleted")
            else:
                print("thread id", st.session_state["thread"])
                answer = assistant.ask_assistant(question, st.session_state["thread"], st.session_state["assistant_id"])
                # st.components.v1.html(answer,scrolling=True,width=500,height=300)
                st.markdown(answer,unsafe_allow_html=True)