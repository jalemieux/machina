from google import genai
from google.genai import types
from .tools.tools import Tool, WebCrawlerTool, WebSearchTool, PolygonApiTool



class Machina:
    """
    Machina is a class that interfaces with the Gemini model to answer questions
    and perform tasks using a set of tools. It manages the context of interactions
    and handles function calls requested by the model.

    Attributes:
        client (genai.Client): The client used to interact with the Gemini model.
        model (str): The model identifier to be used for generating content.
        tools (dict): A dictionary of tools available for function calls.
        llm_tools_def (list): A list of tool definitions for the model.
        system_prompt (str): The initial system prompt describing available tools.
        context (list): The context of the conversation, including user queries and model responses.
    """

    def __init__(self, api_key: str, model: str, prompt: str = None, tools: list[Tool] = [], name: str = None):
        """
        Initializes the AskGemini object with the specified API key, model, and tools.

        Args:
            api_key (str): The API key for authenticating with the Gemini service.
            model (str): The model identifier to be used for generating content.
            tools (list[Tool]): A list of Tool objects that can be used by the model.
        """
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.tools = {}
        for tool in tools:
            self.tools[tool.declaration().name] = tool
        self.llm_tools_def = [types.Tool(function_declarations=[tool.declaration()]) for tool in self.tools.values()]
        self.system_prompt =  prompt or """
        You are a helpful assistant that can answer questions and help with tasks.
        
        """ 
        if self.tools: 
            self.system_prompt += "You can use the following tools to help you answer questions and help with tasks:\n" + "\n".join([f"- {tool.declaration().name}: {tool.declaration().description}" for tool in self.tools.values()])
        self.context = []
        self.context.append(
            types.Content(role="model", parts=[types.Part.from_text(text=self.system_prompt)]),
        )
        self.name = name or "machina"

    def ask(self, query: str):
        """
        Sends a query to the Gemini model and returns the response.

        Args:
            query (str): The user's query to be sent to the model.

        Returns:
            types.Content: The model's response to the query.
        """
        self.context.append(
            types.Content(role="user", parts=[types.Part.from_text(text=query)]),
        )
        self.think()
        print("### the context before existing is ", self.context)
        return self.context[-1]

    def think(self):
        """
        Processes the current context, handling any function calls requested by the model.
        Updates the context with the model's responses and function call results.
        """
        while True:
            # Generate content with function calling
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=self.context,
                config=types.GenerateContentConfig(
                        # system_instruction=self.system_prompt, 
                        tools=self.llm_tools_def,
                ),
            )
            # Handle the function call in the response
            if hasattr(response, 'function_calls') and response.function_calls:
                
                function_call_response_content = response.candidates[0].content
                id = function_call_response_content.parts[0].function_call.id
                args = function_call_response_content.parts[0].function_call.args
                name = function_call_response_content.parts[0].function_call.name
                print("### Gemini wants to call a function: ", name, "with arguments: ", args)
                
                # function call content that needs to go in the context (ie messages to LLM)
                function_call_content = types.Content(
                    role="tool", parts=[
                        types.Part.from_function_call(
                            name=name,
                            args=args,
                        )
                    ]
                )
                # Add function call Content to context
                self.context.append(function_call_content)
                print("### into gemini context: ", function_call_content)
                # Call the function and get the result

                print("### the script is calling the function: ", name, "with arguments: ", args)
                tool = self.tools[name]
                print("### the tool is: ", tool)
                function_result = tool.execute(name, **args)
                
                #function_result = globals()[name](**args)
                print("### the script called the functions and got the result: ", function_result)

                # Create function response content and add it to context (ie messages from LLM)
                function_response_content = types.Content(
                    role="tool", parts=[
                        types.Part.from_function_response(
                            name=name,
                            response={"result": function_result},
                        )
                    ]
                )
                self.context.append(function_response_content)
                print("### into gemini context: ", function_response_content)
            else:
                print("### Gemini did not call any functions")
                self.context.append(response.candidates[0].content)
                print("### into gemini context: ", response.candidates[0].content)
                return

