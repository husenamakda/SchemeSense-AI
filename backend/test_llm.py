from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="phi3:latest",
    base_url="http://127.0.0.1:11434"
)

response = llm.invoke("Say hello in one sentence.")

print(response.content)
