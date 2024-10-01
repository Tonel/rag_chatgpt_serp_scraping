# Python RAG Chatbot with GPT4-o

## Prerequisites

- Linux, macOS, or WSL
- Python 3+
- A [Bright Data](https://brightdata.com/) account with the [SERP API](https://brightdata.com/products/serp-api) product enabled
- An [OpenAI API key](https://platform.openai.com/api-keys)

## Instructions

### #1: Project Setup

Clone the current GitHub repository with:

```bash
git clone https://github.com/Tonel/rag_gpt_serp_scraping
```

Enter the project folder:

```bash
cd rag_gpt_serp_scraping
```

Create a Python virtual environment and activate it:

```bash
python3 -m venv env
source ./env/bin/activate
```

### #2: Install the Project's Dependencies

In an activated Python virtual environment, launch the command below to install the project's dependencies:

```bash
pip install -r requirenments.txt
```

This may take a while, so be patient.

### #3: Configure the Environment Variables

Define the following environment variables in a `.env` file or in the system:

```text
BRIGHT_DATA_SERP_API_HOST="<YOUR_BD_HOST>"
BRIGHT_DATA_SERP_API_PORT=<YOUR_BD_PORT>
BRIGHT_DATA_SERP_API_USERNAME="<YOUR_BD_USERNAME>"
BRIGHT_DATA_SERP_API_PASSWORD="<YOUR_BD_PASSOWRD>"

OPENAI_API_KEY="<YOUR_OPENAI_API_KEY>"
```

- You can configure SERP API and retrieve the required credentials as explained in the [official docs](https://docs.brightdata.com/scraping-automation/serp-api/introduction).
- You can create an Open AI API key as explained in the [official quickstart tutorial](https://platform.openai.com/docs/quickstart).

### #4: Run the Application
In an activated Python virtual environment, execute the following command to launch the application:
```bash
streamlit run app.py
```
