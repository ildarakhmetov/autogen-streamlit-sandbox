import streamlit as st
import asyncio
from autogen import AssistantAgent, UserProxyAgent

#### PERSONAS ####
# You can change the personas to whatever you want.
assistant_persona = "You are a sarcastic computer science professor. You speak English very well. You often make sarcastic comments about your students' homework assignments. You may not always be polite to your students."
user_proxy_persona = "You are a student who is struggling with a homework assignment. You speak English very poorly. You are a native speaker of Russian, so occasionally you will use Russian words in your English sentences."


st.write("""# AutoGen Chat Agents""")

class TrackableAssistantAgent(AssistantAgent):
    # override constructor to add system_message parameter
    def __init__(self, *args, system_message=None, **kwargs):
        super().__init__(*args, system_message=system_message, **kwargs)

    def _process_received_message(self, message, sender, silent):
        with st.chat_message(sender.name):
            st.markdown(message)
        return super()._process_received_message(message, sender, silent)


class TrackableUserProxyAgent(UserProxyAgent):
    # override constructor to add system_message parameter
    def __init__(self, *args, system_message=None, **kwargs):
        super().__init__(*args, system_message=system_message, **kwargs)

    def _process_received_message(self, message, sender, silent):
        with st.chat_message(sender.name):
            st.markdown(message)
        return super()._process_received_message(message, sender, silent)


selected_model = None

# try to get selected_key from the .streamlit/secrets.toml file
try:
    selected_key = st.secrets["openai_api_key"]
except:
    selected_key = None


with st.sidebar:
    st.header("OpenAI Configuration")
    selected_model = st.selectbox("Model", ['gpt-3.5-turbo', 'gpt-4'], index=1)
    if not selected_key:
        selected_key = st.text_input("API Key", type="password")

with st.container():
    # for message in st.session_state["messages"]:
    #    st.markdown(message)

    user_input = st.chat_input("Type something...")
    if user_input:
        if not selected_key or not selected_model:
            st.warning(
                'You must provide valid OpenAI API key and choose preferred model', icon="⚠️")
            st.stop()

        llm_config = {
            "request_timeout": 600,
            "config_list": [
                {
                    "model": selected_model,
                    "api_key": selected_key
                }
            ]
        }
        # create an AssistantAgent instance named "assistant"
        assistant = TrackableAssistantAgent(
            name="assistant", llm_config=llm_config, system_message=assistant_persona)

        # create a UserProxyAgent instance named "user"
        user_proxy = TrackableUserProxyAgent(
            name="user", human_input_mode="NEVER", llm_config=llm_config, system_message=user_proxy_persona)

        # Create an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Define an asynchronous function
        async def initiate_chat():
            await user_proxy.a_initiate_chat(
                assistant,
                message=user_input,
            )

        # Run the asynchronous function within the event loop
        loop.run_until_complete(initiate_chat())
