from google.genai import types
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from polygon import RESTClient

class Tool:
    def declaration(self) -> types.FunctionDeclaration:
        pass

    def execute(self, **kwargs):
        pass


class WebCrawlerTool(Tool):
    """
    WebCrawlerTool is a tool class designed to fetch and process the content of a web page given its URL.

    Attributes:
        tool (types.Tool): A tool object containing the function declaration for fetching web page content.

    """
    def declaration(self) -> types.FunctionDeclaration:    
        return types.FunctionDeclaration(
                    name="get_web_url_content",
                    description="Get the real time web page content of a given URL",
                    parameters=types.Schema(
                        type="OBJECT",
                        properties={
                            "url": types.Schema(
                                type="STRING",
                                description="The URL of the web page to fetch"
                            )
                        },
                        required=["url"]
                    )
                )

 
    def execute(self, function_name, url):
        if function_name == "get_web_page":
            print(f"Fetching web page from {url}...")
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove all script and style elements
            for script_or_style in soup(['script', 'style']):
                script_or_style.decompose()

            # Get text and remove navigational links
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            return text
        else:
            raise ValueError(f"Function {function_name} is not supported.")

class WebSearchTool:
    """
    WebSearchTool is a tool class designed to fetch and process search results from Tavily given a query.

    Attributes:
        tool (types.Tool): A tool object containing the function declaration for fetching search results.

    Methods:
        __init__(): Initializes the WebSearchTool with the function declaration.
        execute(function_name, query): Fetches the search results from Tavily for the given query and returns the context.
    """
    def __init__(self, api_key):
        self.tavily_client = TavilyClient(api_key=api_key)

    def declaration(self) -> types.FunctionDeclaration:
        return types.FunctionDeclaration(
                name="realtime_web_search",
                description="Realtime web search results for a given query, topic, and time range",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "query": types.Schema(
                            type="STRING",
                            description="The search query to fetch results for"
                        ),
                        "topic": types.Schema(
                            type="STRING",
                            enum=["general", "news"],
                            description="The category of the search. Supported values are 'general' and 'news'. Default is 'general'."
                        ),
                        "time_range": types.Schema(
                            type="STRING",
                            enum=["day", "week", "month", "year", "d", "w", "m", "y"],
                            description="The time range back from the current date to include in the search results. Accepted values include 'day', 'week', 'month', 'year' or 'd', 'w', 'm', 'y'. Default is None."
                        )
                    },
                    required=["query"]
                )
            )
        
    def execute(self, function_name, query, topic="general", time_range=None):
        if function_name == "realtime_web_search":
            if topic not in ["general", "news"]:
                raise ValueError(f"Topic {topic} is not supported. Supported topics are 'general' and 'news'.")
            
            if time_range and time_range not in ["day", "week", "month", "year", "d", "w", "m", "y"]:
                raise ValueError(f"Time range {time_range} is not supported. Supported time ranges are 'day', 'week', 'month', 'year' or 'd', 'w', 'm', 'y'.")
            
            print(f"Fetching search results for query: {query} with topic: {topic} and time range: {time_range}...")
            context = self.tavily_client.get_search_context(
                query=query, 
                topic=topic, 
                time_range=time_range,
                max_results=25
            )
            return context
        else:
            raise ValueError(f"Function {function_name} is not supported.")

    

class PolygonApiTool:
    """
    PolygonApiTool is a tool class designed to fetch and process data from the Polygon API given a ticker.

    Attributes:
        tool (types.Tool): A tool object containing the function declaration for fetching data from the Polygon API.
    
    Methods:
        __init__(): Initializes the PolygonApiTool with the function declaration.
        execute(ticker): Fetches the last quote from the Polygon API for the given ticker and returns the data.
    """
    def __init__(self, api_key):
        self.client = RESTClient(api_key=api_key)

    def declaration(self) -> types.FunctionDeclaration:
        # return types.FunctionDeclaration(
        #     name="get_stock_quote",
        #         description="Get the last quote for a given ticker",
        #         parameters=types.Schema(
        #             type="OBJECT",
        #             properties={
        #                 "ticker": types.Schema(
        #                     type="STRING",
        #                     description="The ticker symbol to fetch the last quote for"
        #                 )
        #             },
        #             required=["ticker"]
        #         )
        #     ),
        return types.FunctionDeclaration(
                name="get_stock_ticker_data",
                description="Get latest data for a given stock ticker",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "ticker": types.Schema(
                            type="STRING",
                            description="The ticker symbol to fetch the latest data for"
                        )
                    },
                    required=["ticker"]
                )
            )
    
    def execute(self, function_name, ticker):
        # if function_name == "get_stock_quote":
        #     print(f"Fetching last quote for ticker: {ticker}...")
        #     return self.client.get_last_quote(ticker=ticker)
        if function_name == "get_previous_day_quote":
            print(f"Fetching previous day's aggregate data for ticker: {ticker}...")

            previous_close_agg = self.client.get_previous_close_agg(ticker=ticker)
            previous_close_agg_list = []
            for agg in previous_close_agg:
                agg_dict = {
                    "Ticker": agg.ticker,
                    "Close": agg.close,
                    "High": agg.high,
                    "Low": agg.low,
                    "Open": agg.open,
                    "Timestamp": agg.timestamp,
                    "Volume": agg.volume,
                    "VWAP": agg.vwap
                }
                previous_close_agg_list.append(agg_dict)
            return previous_close_agg_list[0]
        else:
            raise ValueError(f"Function {function_name} is not supported.")