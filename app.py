import streamlit as st
import asyncio
from autogen import AssistantAgent, UserProxyAgent

#### PERSONAS ####
# You can change the personas to whatever you want.
assistant_persona = ""
user_proxy_persona = "You are a seasoned market researcher with many years of experience doing qualitative interviews.  You are conducting an interview with a potential customer to see their interest in your new product, and see what features your company could offer for the person based on their needs and the benefits they seek.  You will probe their responses requesting that they clarify, justify and/or extend their answers as appropriate. The business idea: ENTER YOUR BUSINESS DESCRIPTION HERE"

# You can change the max_consecutive_auto_reply to whatever you want
# but keep in mind that with higher values, the conversation will be more costly :-)
max_consecutive_auto_reply = 5


st.write("""# Market Research Interview with OpenAI's GPT-4""")

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

# Setting up the sidebar
with st.sidebar:
    # OpenAI Configuration
    st.header("OpenAI Configuration")
    selected_model = st.selectbox("Model", ['gpt-3.5-turbo', 'gpt-4'], index=1)
    if not selected_key:
        selected_key = st.text_input("API Key", type="password")

    # Persona Configuration (override default personas)
    st.header("Persona Configuration")
    st.markdown("""### Interviewee persona instructions:

- Enter the most relevant demo- and psychographic elements and/or behaviors that characterize this persona.
- Include elements you think will provide customer insights to inform your product or service features relative to other competitive solutions.  
- Include their needs, pain points and potential benefits they seek relative to what you want to offer.
- NOTE: be careful to avoid elements that might cause hallucinations (e.g., do you want AI searching for info only from a certain gender or occupation or income level? It might seem useful, but note that AI might only search for data about the variables you specify)
- Run this interview a few times with different personas to see the differences that it generates. """)
    assistant_persona = st.text_area(
        "Interviewee persona", value=assistant_persona, height=200)
    st.markdown("""### Interviewer persona instructions:

- Describe your interviewer, including any capabilities you feel are relevant (e.g., experience as a qualitative market researcher as I’ve given in the example)
- Briefly describe your business, and the customer needs that your business seeks to meet.
- Describe the process you want them to undertake (e.g., use probes to clarify, justify and/or expand on the interviewees responses if helpful in generating a good understanding of this person).
- I’ve included a sample, you should change this for your business. """)
    user_proxy_persona = st.text_area(
        "Interviewer persona", value=user_proxy_persona, height=200)
    
    # Max Consecutive Auto Reply Configuration
    st.header("Max number of consecutive auto replies")
    max_consecutive_auto_reply = st.number_input(
        "More replies incur more cost", value=max_consecutive_auto_reply, min_value=1, max_value=5)

with st.container():
    # for message in st.session_state["messages"]:
    #    st.markdown(message)

    user_input = st.chat_input(placeholder="Type the first message here...")
    st.markdown("""## Activity goals:

- Complement the data you compiled from customer interviews with insights using AI
- Experience AI’s capabilities and limitations in generating insights about your target customers
 
## Process:

- Enter a description of a target customer persona in the top box.
- Briefly describe your business in the bottom box, as well as a market researcher representing this business.
- The interview will run for 5 iterations (questions/answers).
- Try this with 2 or 3 different personas to see if you get additional useful insights.""")
    st.markdown("_**First message example:** Hi, my name's Bob. Thanks for taking the time for this interview!_")
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
            name="assistant",
            llm_config=llm_config,
            max_consecutive_auto_reply=max_consecutive_auto_reply,
            system_message=assistant_persona)

        # create a UserProxyAgent instance named "user"
        user_proxy = TrackableUserProxyAgent(
            name="user",
            human_input_mode="NEVER",
            llm_config=llm_config,
            system_message=user_proxy_persona)

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
