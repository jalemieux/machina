from machina.machina import AgentGemini
from machina.tools.tools import WebSearchTool

web_search_tool = WebSearchTool(api_key="YOUR API KEY")

ron_burgundy = AgentGemini(api_key="YOUR API KEY", model="gemini-1.5-flash",
                        prompt="""
                        You are a news agent that reasearches news of a given topic.
                        You will be given a topic and you will fetch the latest news on that topic, analyze it, and provide a summary of the key points.
                        Your output should be easy to read,should be in markdown format.
                        """,
                        tools=[web_search_tool()])

ret = ron_burgundy.ask("AI related news in the last 24 hours?")
print(ret.parts[0].text)



