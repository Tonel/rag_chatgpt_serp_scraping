from dotenv import load_dotenv
import os
import requests
from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from openai import OpenAI
import streamlit as st

# load the environment variables from the .env file
load_dotenv()

# initialize the OpenAI API client with your API key
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def get_google_serp_urls(query, number_of_urls=5):
    """
    Extracts URLs from Google Search Engine Results Pages (SERPs) for a given query
    using Bright Data's SERP API tool.

    Parameters:
    ----------
    query : str
        The search query for which the URLs need to be extracted from Google SERPs.

    number_of_urls : int, optional
        The maximum number of URLs to return from the search results. Defaults to 5.

    Returns:
    -------
    list of str
        A list containing the URLs of the organic search results from Google.
    """

    # perform a Bright Data's SERP API request
    # with JSON autoparsing
    host = os.environ.get("BRIGHT_DATA_SERP_API_HOST")
    port = os.environ.get("BRIGHT_DATA_SERP_API_PORT")

    username = os.environ.get("BRIGHT_DATA_SERP_API_USERNAME")
    password = os.environ.get("BRIGHT_DATA_SERP_API_PASSWORD")

    proxy_url = f"http://{username}:{password}@{host}:{port}"

    proxies = {"http": proxy_url, "https": proxy_url}

    url = f"https://www.google.com/search?q={query}&brd_json=1"
    response = requests.get(url, proxies=proxies, verify=False)

    # retrieve the parsed JSON response
    response_data = response.json()

    # extract a "number_of_urls" number of
    # Google SERP URLs from the response
    google_serp_urls = []
    if "organic" in response_data:
        for item in response_data["organic"]:
            if "link" in item:
                google_serp_urls.append(item["link"])

    return google_serp_urls[:number_of_urls]


def extract_text_from_urls(urls, number_of_words=600):
    """
    Extracts text content from a list of URLs and retrieves the first
    number_of_words of words from each

    Parameters:
    ----------
    urls : list of str
        A list of URLs from which to extract text content.

    number_of_words : int, optional
        The maximum number of words to extract from each transformed document. Defaults to 600.

    Returns:
    -------
    list of str
        A list containing the extracted text, with each entry corresponding to a URL's content.
    """

    # instruct a headless Chrome instance to visit the provided URLs
    # with the specified user-agent
    loader = AsyncChromiumLoader(
        urls,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    )
    html_documents = loader.load()

    # process the extracted HTML documents to extract text from them
    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(
        html_documents,
        tags_to_extract=["p", "em", "li", "strong", "h1", "h2"],
        unwanted_tags=["a"],
        remove_comments=True,
    )

    # make sure each HTML text document contains only a number
    # number_of_words words
    extracted_text_list = []
    for doc_transformed in docs_transformed:
        # split the text into words and join the first number_of_words
        words = doc_transformed.page_content.split()[:number_of_words]
        extracted_text = " ".join(words)

        # ignore empty text documents
        if len(extracted_text) != 0:
            extracted_text_list.append(extracted_text)

    return extracted_text_list


def get_openai_prompt(request, text_context=[]):
    """
    Constructs a prompt for the OpenAI model based on a request and optional text context.

    Parameters:
    ----------
    request : str
        The request to be answered by the OpenAI model.

    text_context : list of str, optional
        A list of strings providing context for the request. If not empty, the context
        will be included in the generated prompt. Defaults to an empty list.

    Returns:
    -------
    str
        A formatted prompt string for the OpenAI model, either containing just the request
        or including the context as well.
    """

    # default prompt
    prompt = request

    # add the context to the prompt, if present
    if len(text_context) != 0:
        context_string = "\n\n--------\n\n".join(text_context)
        prompt = f"Answer the request using only the context below.\n\nContext:\n{context_string}\n\nRequest: {request}"

    return prompt


def interrogate_openai(prompt, max_tokens=800):
    """
    Sends a prompt to the OpenAI GPT-4 model and retrieves the model's response.

    Parameters:
    ----------
    prompt : str
        The text prompt to be sent to the OpenAI model.

    max_tokens : int, optional
        The maximum number of tokens to generate in the model's response. Defaults to 800.

    Returns:
    -------
    str
        The content of the response generated by the OpenAI model, which answers or
        elaborates on the provided prompt.
    """

    # interrogate the OpenAI model with the given prompt
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
    )

    return response.choices[0].message.content

# create a form in the Streamlit app for user input
with st.form("prompt_form"):
    # intitialize the output results
    result = ""
    final_prompt = ""

    # textarea for user to input their Google search query
    google_search_query = st.text_area("Google Search:", None)
    # textarea for user to input their AI prompt
    request = st.text_area("AI Prompt:", None)

    # button to submit the form
    submitted = st.form_submit_button("Send")

    # if the form is submitted
    if submitted:
        # retrieve the Google SERP URLs from the given search query
        google_serp_urls = get_google_serp_urls(google_search_query)
        # extract the text from the respective HTML pages
        extracted_text_list = extract_text_from_urls(google_serp_urls)
        # generate the AI prompt using the extracted text as context
        final_prompt = get_openai_prompt(request, extracted_text_list)
        # interrogate an OpenAI model with the generated prompt
        result = interrogate_openai(final_prompt)

    # dropdown containing the generated prompt
    final_prompt_expander = st.expander("AI Final Prompt")
    final_prompt_expander.write(final_prompt)

    # write the result from the OpenAI model
    st.write(result)
