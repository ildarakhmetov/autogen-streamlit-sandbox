import streamlit as st
import asyncio
from autogen import AssistantAgent, UserProxyAgent

#### PERSONAS ####
# You can change the personas to whatever you want.
assistant_persona = "You are Jake, a 35-year-old Marketing Manager from Seattle, embodies the quintessential craft beer enthusiast. You hold a Bachelor's Degree in Communications and earn $75,000 annually. As a single, urban dweller, you value uniqueness and quality in products, particularly in your passion for exploring new craft beers. You're environmentally conscious, tech-savvy, and keen on staying abreast of trends through social media. Your weekends are often spent visiting local breweries, attending beer festivals, or engaging in home brewing. You're an active member of online craft beer communities, enjoy pairing beers with food, and stay informed through blogs and magazines dedicated to brewing. Your social media presence is dotted with posts about his latest craft beer adventures, reflecting your appreciation for the art and science behind brewing."
user_proxy_persona = "You are Mia, a 42-year-old seasoned market researcher. You are conducting an interview about the new product, a craft beer, for your client, a local brewery. The beer is a lager with a hint of citrus and a 5.5% ABV. The brewery is looking to expand its market share and wants to know how to best position the product. You will ask questions about the product, the target market, and the competition. You will probe for information and follow up on any interesting points. You will also ask for recommendations on how to improve the product and how to best market it."

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
    assistant_persona = st.text_area(
        "Assistant Persona", value=assistant_persona, height=200)
    user_proxy_persona = st.text_area(
        "User Proxy Persona", value=user_proxy_persona, height=200)
    
    # Max Consecutive Auto Reply Configuration
    st.header("Max number of consecutive auto replies")
    max_consecutive_auto_reply = st.number_input(
        "More replies incur more cost", value=max_consecutive_auto_reply, min_value=1, max_value=10)

with st.container():
    # for message in st.session_state["messages"]:
    #    st.markdown(message)

    user_input = st.chat_input(placeholder="Type the first message here...")
    st.markdown("_**First message example:** Hello! My name is Mia. I am a market researcher. You tasted our new craft beer last week. I would like to ask you a few questions about the beer. Is this a good time?_")
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
