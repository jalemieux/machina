"""
This script demonstrates an AI assistant that uses a reason+act framework to process user questions.
The assistant follows a cycle of thought, action, and observation to generate answers. It utilizes
OpenAI's language model to think and decide on actions, and TavilyClient to perform actions like
searching the internet or retrieving URL content.
"""
import json
import random
from openai import OpenAI
from tavily import TavilyClient

# Initialize clients for Tavily and OpenAI
tavily_client = TavilyClient()
client = OpenAI()

########################################################
# tools
########################################################
# Define a list of tools with their respective functions and parameters
tools=[
    {
      "type": "function",
      "function": {
        "name": "search_internet",
        "description": "Search the internet for information",
        "parameters": {
          "type": "object",
          "properties": {
            "query": {
              "type": "string",
              "description": "The query to search the internet for"
            },
          },
          "required": ["query"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "get_url_content",
        "description": "Get the content of a URL",
        "parameters": {
          "type": "object",
          "properties": {
            "url": {
              "type": "string",
              "description": "The URL to get the content of"    
            },
          },
          "required": ["url"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "final_answer",
        "description": "Provide the final answer to the user's question",
        "parameters": {
          "type": "object",
          "properties": {
            "answer": {
              "type": "string",
              "description": "The final answer to the user's question"
            },
          },
          "required": ["answer"]
        }
      }
    }
]

# Define functions to interact with TavilyClient
def search_internet(query):
    return tavily_client.search(query)

def get_url_content(url):
    return tavily_client.extract(url)

# Map action names to their corresponding functions
actions = { 'search_internet': search_internet, 'get_url_content': get_url_content}

########################################################
# llm
########################################################
# Function to call the language model with a message
def call_llm(messages, iterative_message) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages + [{'role': 'user', 'content': iterative_message}],
    )
    return response.choices[0].message.content

# Function to call the language model with tools
def call_llm_tool(messages, iterative_message) -> tuple[str, list[dict]]:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages + [{'role': 'user', 'content': iterative_message}],
        tools=tools,
    )
    tool_calls = response.choices[0].message.tool_calls
    return response.choices[0].message, tool_calls

########################################################
# utilities
########################################################
# Function to display the response in a pretty format
def display_response_pretty(response):
    if hasattr(response, 'to_dict'):
        response = response.to_dict()
    formatted_response = json.dumps(response, indent=2)
    print(formatted_response)

import requests

# Function to download JSON data from a URL
def download_json(url):
    import os

    local_filename = url.split("/")[-1]
    if os.path.exists(local_filename):
        with open(local_filename, 'r') as file:
            return json.load(file)
    else:
        response = requests.get(url)
        if response.status_code == 200:
            with open(local_filename, 'w') as file:
                json.dump(response.json(), file)
            return response.json()
        else:
            response.raise_for_status()

# Load HotpotQA dataset
hotpot_qs = download_json("http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_fullwiki_v1.json")

# Function to get a random question from the HotpotQA dataset
def random_hotpot_question() -> tuple[str, str, str, list[str]]:
    entry = hotpot_qs[random.randint(0, len(hotpot_qs) - 1)]
    return entry['_id'], entry['question'], entry['answer'], entry['supporting_facts']

# Function to adapt a long answer to a short form
def short_answer_adapter(question: str, answer: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{ 'role': 'system', 'content': f"""
            You are given a long form answer to a question. Distill the answer to its shortest form without losing relevance to the question. 
            question: {question}
            answer: {answer}
            """}        ],
    )
    return response.choices[0].message.content

########################################################
# Initial prompt for the AI assistant
initial_prompt = """
You are an AI assistant uses the reason+act framework.
- **thought**: You think carefully about the user's question or task. Do not assume you already know the answer.
- **action**: You perform an action based on your thought. You have access to various tools.
- **observation**: You read the result of that action
- **thought**: You revise your reasoning based on the observation.
"""

# Main loop to process the question and generate an answer
def run_loop(messages, question):
    counter = 0
    while counter < 10: # don't run more than 3*5 times
        if counter == 0:
            user_message = f"Given this user question \"{question}\", what is your thought?"
        else:
            user_message = f"Given your previous observation, what is your next thought?"

        thought = call_llm(messages, user_message)
        # append thought to messages
        messages.append({'role': 'assistant', 'content': thought})

        display_response_pretty(messages[-1])

        ##

        message, tool_calls = call_llm_tool(
            messages, 
            f"Given your previous thought, what action would you take?")
      
        messages.append(message)

        display_response_pretty(messages[-1])

        for tool_call in tool_calls:
            action_name = tool_call.function.name
            action_args = json.loads(tool_call.function.arguments)
            if action_name == "final_answer":
                messages.append(message)
                return action_args, messages
                
            else:
                result = actions[action_name](**action_args)
                # append observation to messages
                messages.append({                               # append result message
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })

            display_response_pretty(messages[-1])
        if action_name == "final_answer":
            break

        observation = call_llm(messages, "Given the previous action results, what is your observation?")
        messages.append({'role': 'assistant', 'content': observation})
        

        display_response_pretty(messages[-1])

        counter += 1

# Get a random question from the HotpotQA dataset
_id, question, answer, supporting_facts = random_hotpot_question()

# Test questions for point testing mode
test_questions = [
    { "question": "Are San Antonio International Airport and Yakutat Airport in the same country?", "answer": "No", "why": "dual tool call" },
]

# Flag for point testing mode
point_testing_mode = False
if point_testing_mode:
    _question = test_questions[0]["question"]
else:
    _id, _question, _answer, _supporting_facts = random_hotpot_question()

# Print the user question
print("user question: " + _question)

# Initialize messages with the initial prompt
messages = [{'role': 'system', 'content': initial_prompt}]
answer, messages = run_loop(messages, _question)

# Print the question and the final answer
print("question: " + _question)
print("answer: " + answer["answer"])

# Generate and print a short answer
short_answer = short_answer_adapter(_question, answer["answer"])
print("short answer: " + short_answer)
print("hotpot answer: " + _answer)




