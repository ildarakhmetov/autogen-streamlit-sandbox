# Streamlit + Autogen + OpenAI Demo

In this demo, two personas chat with each other using the OpenAI API. The personas can be changed in the `app.py` file.

> Based on tutorial: (https://medium.com/p/efaf34f7477b) by 01coder.

## Installation

Follow the steps below to run the project:

1. Clone this repository

2. Set up the virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```
   
3. Install the dependencies

```bash
pip install -r requirements.txt
```

4. Run the project

```bash
streamlit run app.py
``` 

## OpenAI API Key

You may add the OpenAI API key in the `.streamlit/secrets.toml` file as follows:

```bash
openai_api_key = "YOUR_API_KEY"
```

Or simply paste it in the text box in the app.