from langchain_google_genai import ChatGoogleGenerativeAI
from src.modules.agent.state import State
from langchain_core.prompts import ChatPromptTemplate
from src.modules.agent.schema import ExtractorSchema
from langchain_core.messages import AIMessage


class Extractor:
    def __init__(self, *args, **kwargs):
        self.llm = ChatGoogleGenerativeAI(*args, **kwargs)
        self.prompt = ChatPromptTemplate.from_template(
            """Você é um extrator de informações.
            Dada as informações do ticket abaixo, extraia as informações relevantes.
            
            {ticket}

            e retorne as informações como titulo, categoria, descrição, historico de interações e em português. 
            Escreva um resumo do estado atual status atual.
            Se não tiver alguma informação, deixe em branco.
            """
        )

    def extract(self, state: State) -> State:
        chain = self.prompt | self.llm.with_structured_output(ExtractorSchema)
        llm_response = chain.with_retry(
            stop_after_attempt=3,
            wait_exponential_jitter=True
        ).invoke({"ticket": state["messages"]})

        structtured_response = (
            f"titulo: {llm_response.title}\n"
            f"categoria: {llm_response.category}\n"
            f"descricao: {llm_response.description}\n"
            f"historico de interacoes: {llm_response.interaction_history}\n"
            f"status atual: {llm_response.current_status}\n"
        )

        return {
            "messages": [AIMessage(content=structtured_response)],
            "extract_ticket_data": llm_response.model_dump(),
        }
