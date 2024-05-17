from openai import OpenAI
import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import json

load_dotenv()
# URL of the web page you want to scrape
url = 'https://news.ycombinator.com/'

# Sending an HTTP GET request to the URL
response = requests.get(url)
if response.status_code == 200:
    # Printing the content of the web page
    print("Successfully retrieved the web page.")
else:
    print('Failed to retrieve the web page.')

# Parse the HTML content of the page
soup = BeautifulSoup(response.text, 'html.parser')

# Find the body tag and extract its contents
body_content = soup.body.get_text()

# Create an assistant
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

assistant = client.beta.assistants.create(
  name="Web Scraper",
  response_format={ "type": "json_object" },
  instructions="You are a web scraper that can extract complex data from HTML into JSON format.",
  model="gpt-4o",
)

print(assistant.id)

# Create a thread
thread = client.beta.threads.create()
json_example = {
    "news": [
        {"rank": 1, "title": "News 1", "points": 100, "comments": 50},
        {"rank": 2, "title": "News 2", "points": 80, "comments": 40},
        {"rank": 3, "title": "News 3", "points": 70, "comments": 30},
    ]
}

# Create a message and link it to the thread
message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content=f"I need to extract news from Hacker News, here's the list {body_content}. The information I want is: the rank of the news, the title, the number of points and the number of comments. Here's an example of the expected JSON structure: {json_example}"
)

# Trigger the run
run = client.beta.threads.runs.create_and_poll(
  thread_id=thread.id,
  assistant_id=assistant.id
)

if run.status == 'completed': 
  messages = client.beta.threads.messages.list(
    thread_id=thread.id
  )
else:
  print(run.status)

print(messages.data[0].content[0].text.value)

with open('top_news.json', 'w') as out_file:
    json.dump(messages.data[0].content[0].text.value, out_file)
