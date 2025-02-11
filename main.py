# from machina.agent_gemini import AgentGemini
# from tools.tools import WebCrawlerTool, WebSearchTool, PolygonApiTool


# # Use case 1: agent that fetches news from the web and summarizes it and key points






# if __name__ == "__main__":
#     # Initialize the object and call the ask_gemini method 
#     #bob = AgentGemini(api_key="", model="gemini-1.5-flash", tools=[WebCrawlerTool(), WebSearchTool(), PolygonApiTool()])
#     #ret1 = bob.ask("Given the tools at your disposition what areyour capabilities and limitations?")
#     #print("### the script got the response: ", ret1.parts[0].text)
#     #ret2 = bob.ask("What is it you do again?")
#    # print("### the script got the response: ", ret2.parts[0].text)
#     llm_tuner_agent = AgentGemini(api_key="", model="gemini-1.5-flash",
#                                   prompt="""
#                                   You are a LLM tuner agent that tunes the prompt of a given LLM.
#                                   You will be given a prompt and user feedback and you will improve the prompt to improve the quality of the response.
#                                   Your output should be the new prompt only. 
#                                   """,
#                                   tools=[])
                                  
                                  
#     ron_burgundy = AgentGemini(api_key="", model="gemini-1.5-flash",
#                          prompt="""
#                          You are a news agent that reasearches news of a given topic.
#                          You will be given a topic and you will fetch the latest news on that topic, analyze it, and provide a summary of the key points.
#                          Your output should be easy to read,should be in markdown format.
#                          """,
#                          tools=[WebSearchTool()])

#     ret = ron_burgundy.ask("AI related news in the last 24 hours?")
#     print("### the script got the response: ", ret.parts[0].text)
#     user_input = input("Any feedback on the response? ")
#     ret = llm_tuner_agent.ask(f"Prompt: {ron_burgundy.system_prompt} \n User feedback: {user_input}.")
#     print("### the improved prompt is: ", ret.parts[0].text)

from dotenv import load_dotenv

from machina.machina_catalog_manager import MachinaCatalogManager

load_dotenv("development.config.env")
from machina import Machina, WebSearchTool, WebCrawlerTool, PolygonApiTool
import os 
import json
from database import initialize_database, insert_machina_instance  # Import the database functions

web_search_tool = WebSearchTool(api_key=os.getenv("TAVILY_API_KEY"))
polygon_api_tool = PolygonApiTool(api_key=os.getenv("POLYGON_API_KEY"))
web_crawler_tool = WebCrawlerTool()

# bob_handle = Machina(api_key=os.getenv("GEMINI_API_KEY"), model="gemini-1.5-flash", name="bob_the_anchor",
#                      tools=[web_search_tool, web_crawler_tool], 
#                      prompt="""
#                      You are a news agent that reasearches news of a given topic.
#                      """,
#                      )

# jim_handle = Machina(api_key=os.getenv("GEMINI_API_KEY"), model="gemini-1.5-flash", name="jim_the_analyst",
#                      tools=[polygon_api_tool],
#                      prompt="""
#                      You are a financial analyst that analyzes the financial data of a given company.
#                      """,
#                      )

cataloger = MachinaCatalogManager()
catalog = cataloger.catalog_machinas([bob_handle, jim_handle])

#cataloger = MachinaCatalogManager()
#catalog = cataloger.get_all_machinas()

print(catalog)


# catalog = catalog_machinas([bob_handle, jim_handle])

# with open("catalog.json", "w") as f:
#     json.dump(catalog, f)
# Load catalog from file
# with open("catalog.json", "r") as f:
#     catalog = json.load(f)

# print("Catalog has been saved to catalog.json")

# # Initialize the database
# initialize_database()

# # Insert Machina instances into the database
# insert_machina_instance(
#     name="bob_the_anchor",
#     tools=str([tool.__class__.__name__ for tool in bob_handle.tools]),
#     prompt=bob_handle.system_prompt,
#     catalog_description=catalog.get("bob_the_anchor", "")
# )

# insert_machina_instance(
#     name="jim_the_analyst",
#     tools=str([tool.__class__.__name__ for tool in jim_handle.tools]),
#     prompt=jim_handle.system_prompt,
#     catalog_description=catalog.get("jim_the_analyst", "")
# )
