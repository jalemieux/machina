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
load_dotenv("development.config.env")
from machina import Machina, WebSearchTool, WebCrawlerTool, PolygonApiTool
import os 

web_search_tool = WebSearchTool(api_key=os.getenv("TAVILY_API_KEY"))
polygon_api_tool = PolygonApiTool(api_key=os.getenv("POLYGON_API_KEY"))
web_crawler_tool = WebCrawlerTool()


question_to_machinas = """
Based on the initial prompt and the tools available to you, please provide a detailed response covering the following points:
	1.	Purpose:
	•	What is your overall purpose as a language model?
	•	What are the primary goals you are designed to achieve?
	2.	Capabilities:
	•	What tasks or operations can you perform using the available tools?
	•	How can these tools assist in executing your functions?
	•	Please give examples if applicable.
	3.	Limitations:
	•	What actions or tasks are outside your scope or beyond what you are allowed to do?
	•	Are there any specific constraints or rules that restrict your functionality?

	Provide your explanation in a clear and structured manner.
    """
    
agent = Machina(api_key=os.getenv("GEMINI_API_KEY"), model="gemini-1.5-flash",
                          prompt="""
                          You are a news agent that reasearches news of a given topic.
                          You will be given a topic and you will fetch the latest news on that topic, analyze it, and provide a summary of the key points.
                          Your output should be easy to read,should be in markdown format.
                          """,
                          tools=[web_search_tool])

ret = agent.ask(question_to_machinas)
print(ret.parts[0].text)


