from langchain_google_genai import ChatGoogleGenerativeAI
from src.modules.agent.state import State
from langchain_core.prompts import ChatPromptTemplate


class Extractor:
    def __init__(self, *args, **kwargs):
        self.llm = ChatGoogleGenerativeAI(*args, **kwargs)
        self.prompt = ChatPromptTemplate.from_template(
            """Você é um extrator de informações.
            Dada as informações do ticket abaixo, extraia as informações relevantes.
            
            {ticket}
            """
        )

    def extract(self, state: State) -> State:
        chain = self.prompt | self.llm.with_retry(
            stop_after_attempt=3,
            wait_exponential_jitter=True
        )
        llm_response = chain.invoke({"ticket": state["messages"]})

        return {"messages": [llm_response]}