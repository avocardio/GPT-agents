import requests
from bs4 import BeautifulSoup
import json

from utils.utils import get_response

def scrape_text(url):
    """Scrape text from a webpage"""
    # Most basic check if the URL is valid:
    if not url.startswith('http'):
        return "Error: Invalid URL"
    
    try:
        response = requests.get(url, headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"})
    except requests.exceptions.RequestException as e:
        return None

    # Check if the response contains an HTTP error
    if response.status_code >= 400:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    # Find all 'p' and 'li' tags
    text_tags = soup.find_all(['p', 'li'])

    relevant_text = []
    for tag in text_tags:
        text = tag.get_text(strip=True)
        if len(text) > 100:  # Only add text with a reasonable length
            relevant_text.append(text)

    # Join the relevant text chunks
    text = '\n'.join(relevant_text)

    #text = soup.get_text()
    #lines = (line.strip() for line in text.splitlines())
    #chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    #text = '\n'.join(chunk for chunk in chunks if len(chunk) > 1000)

    return text

def extract_hyperlinks(soup):
    """Extract hyperlinks from a BeautifulSoup object"""
    hyperlinks = []
    for link in soup.find_all('a', href=True):
        hyperlinks.append((link.text, link['href']))
    return hyperlinks

def format_hyperlinks(hyperlinks):
    """Format hyperlinks into a list of strings"""
    formatted_links = []
    for link_text, link_url in hyperlinks:
        formatted_links.append(f"{link_text} ({link_url})")
    return formatted_links

def scrape_links(url):
    """Scrape links from a webpage"""
    response = requests.get(url, headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"})

    # Check if the response contains an HTTP error
    if response.status_code >= 400:
        return "error"

    soup = BeautifulSoup(response.text, "html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    hyperlinks = extract_hyperlinks(soup)

    return format_hyperlinks(hyperlinks)

def split_text(text, max_length=3500):
    """Split text into chunks of a maximum length"""
    paragraphs = text.split("\n")
    current_length = 0
    current_chunk = []

    for paragraph in paragraphs:
        if current_length + len(paragraph) + 1 <= max_length:
            current_chunk.append(paragraph)
            current_length += len(paragraph) + 1
        else:
            yield "\n".join(current_chunk)
            current_chunk = [paragraph]
            current_length = len(paragraph) + 1

    if current_chunk:
        yield "\n".join(current_chunk)

def summarize_text(text, question, debug = False):
    """Summarize text using the LLM model"""
    if not text:
        return None

    text_length = len(text)
    if debug:
        print("\n"+f"Text length: {text_length} characters")

    summaries = []
    chunks = list(split_text(text))

    for i, chunk in enumerate(chunks):
        if debug:
            print(f"Summarizing chunk {i + 1} / {len(chunks)}")
        summary = get_response([{"role": "user","content": f"\n\n\n{chunk}\n\n\n Using the above text, please answer the following question: \"{question}\" -- if the question cannot be answered using the text, please summarize the text. Do not comment on the text. Do not start with 'The text talks about' or 'The text provides'. Just summarize according to the question!"}], max_tokens=300)
        summaries.append(summary)

    if debug:
        print(f"Summarized {len(chunks)} chunks.")

    combined_summary = "\n".join(summaries)

    final_summary = get_response([{"role": "user","content": f"\n\n\n{combined_summary}\n\n\n Using the above text, please answer the following question: \"{question}\" -- if the question cannot be answered using the text, please summarize the text. Do not comment on the text. Do not start with 'The text talks about' or 'The text provides'. Just summarize according to the question!"}], max_tokens=300)

    return final_summary

def search(user_input):
    query = get_response([{"role": "user", "content": f"Given the user input: {user_input}. What would you search on Google to help the user? Respond with a search query starting with \" and ending with \"."}], max_tokens=100)
    query = query.split("\"")[1]
    url = f"https://www.google.com/search?q={query}"
    links = scrape_links(url)[0:20]
    links = [link for link in links if not link.__contains__("/search?") and not link.__contains__(".google.com") and not link.__contains__("youtube")]
    links = [link.split("(")[1] for link in links]
    links = [link.replace(")","") for link in links if link.__contains__("https://")]

    with open("config.json", "r") as config:
        config = json.load(config)

    num_sources = config["NUM_BROWSING_SOUCES"]

    # Only use 3 links or less
    if len(links) > num_sources:
        links = links[0:num_sources]
    summaries = []

    for n, link in enumerate(links):
        print(f"Reading link {n + 1} / {len(links)}")
        text = scrape_text(link)
        if text is not None:
            summary = summarize_text(text, query)
            if summary is None:
                links.remove(link)
                continue
            summaries.append(summary)

    combined_summary = "\n".join(summaries)
    final_summary = summarize_text(combined_summary, query)

    return {"role": "user", "content": user_input + f"\n\n(You searched for {query} on google, and found this information: {final_summary}. The sources are: {links}. Please respond with a message to the user.)"}