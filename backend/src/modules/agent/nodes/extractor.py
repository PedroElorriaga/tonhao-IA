from langchain_google_genai import ChatGoogleGenerativeAI
from src.modules.agent.state import State
from langchain_core.prompts import ChatPromptTemplate
from src.modules.agent.schema import ExtractorSchema
from langchain_core.messages import AIMessage, HumanMessage


class Extractor:
    def __init__(self, *args, **kwargs):
        self.llm = ChatGoogleGenerativeAI(*args, **kwargs)
        self.prompt = ChatPromptTemplate.from_template(
            """Você é um extrator e classificador de tickets de suporte.
            Dada as informações do ticket abaixo, extraia e corrija as informações.

            {ticket}

            Regras obrigatórias:
            - Extraia o título, descrição, histórico de interações e escreva um resumo do status atual em português.
            - Para a categoria, IGNORE o valor fornecido no ticket e determine a categoria correta com base exclusivamente no TÍTULO e na DESCRIÇÃO do problema.
            - A categoria DEVE ser uma dessas opções exatas (em inglês):
                * "technical support" — problemas de TI: hardware, software, redes, wifi, acesso, dispositivos, sistemas
                * "billing"           — faturamento: cobranças, faturas, pagamentos, reembolsos, estornos
                * "hr"                — recursos humanos: férias, holerite, benefícios, admissão, desligamento
                * "account"           — conta do usuário: login, senha, permissões, cadastro
                * "other"             — qualquer assunto que não se enquadre nas categorias acima
            - Se não houver alguma informação, deixe o campo em branco.
            """
        )

    def extract(self, state: State) -> State:
        chain = self.prompt | self.llm.with_structured_output(ExtractorSchema)
        # print(state["messages"])
        human_messages = [msg for msg in state["messages"]
                          if isinstance(msg, HumanMessage)]
        llm_response = chain.with_retry(
            stop_after_attempt=3,
            wait_exponential_jitter=True
        ).invoke({"ticket": human_messages})

        structtured_response = (
            f"titulo: {llm_response.title}\n"
            f"categoria: {llm_response.category}\n"
            f"descricao: {llm_response.description}\n"
            f"historico de interacoes: {llm_response.interaction_history}\n"
            f"status atual: {llm_response.current_status}\n"
        )

        # print("Structured Response:\n", structtured_response)

        return {
            "messages": [AIMessage(content=structtured_response)],
            "extract_ticket_data": llm_response.model_dump()
        }
