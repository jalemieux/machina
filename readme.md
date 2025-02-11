# README

Wouldn’t it be great to have a programmable object that can handle basic tasks and improve over time?

This is the core idea behind Machina. The initial version is built on Gemini but the architecture allows for integrating other models as needed.

How It Works

A Machina instance is initialized with:
	•	A Base Prompt – Defines the agent’s purpose and focus.
	•	A Set of Tools – Extends the agent’s capabilities based on its intended function.

For example, if you want an agent that fetches and summarizes news on a given topic, the prompt should describe this goal, and the agent should be equipped with a tool that retrieves news articles from the web. See news-agent.py for an example.

This project is designed to be flexible, allowing the agent to evolve and incorporate new capabilities over time.


# What is Next 

- [ ] Make LLM used swapable
- [ ] utility to convert function to Tool


create an agent that improves a prompt

store prompt in db for agent 



catalog all agents, with what they good for 
during agent exectuion givem access to all agent as tools 
a request starts with an init agent who routes request based on what agents can do 




