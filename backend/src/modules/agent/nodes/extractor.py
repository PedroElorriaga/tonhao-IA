from langchain_google_genai import ChatGoogleGenerativeAI
from src.modules.agent.state import State
from src.modules.agent.schema import ExtractorSchema
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


# Não é bom usar chat_template quando temos imagens ou documentos anexados, pois o modelo pode não conseguir interpretar corretamente as informações.
SYSTEM_PROMPT = (
    "Você é um extrator e classificador de tickets de suporte.\n"
    "Dada as informações do ticket abaixo, extraia e corrija as informações.\n"
    "Se houver imagem ou documento anexado, considere seu conteúdo na extração e na descrição.\n\n"
    "Regras obrigatórias:\n"
    "- Extraia o título, descrição, histórico de interações e escreva um resumo do status atual em português.\n"
    "- Para o campo latest_user_question: identifique a pergunta ou solicitação MAIS RECENTE do usuário que ainda NÃO foi respondida pela IA. "
    "Se for o primeiro contato (sem histórico), copie a descrição do problema. "
    "Se já houve respostas anteriores, extraia APENAS o que o usuário pediu por último, ignorando o que já foi respondido.\n"
    "- Para a categoria, IGNORE o valor fornecido no ticket e determine a categoria correta com base "
    "exclusivamente no TÍTULO e na DESCRIÇÃO do problema.\n"
    "- A categoria DEVE ser uma dessas opções exatas (em inglês):\n"
    '    * "technical support" — problemas de TI: hardware, software, redes, wifi, acesso, dispositivos, sistemas\n'
    '    * "billing"           — faturamento: cobranças, faturas, pagamentos, reembolsos, estornos\n'
    '    * "hr"                — recursos humanos: férias, holerite, benefícios, admissão, desligamento\n'
    '    * "account"           — conta do usuário: login, senha, permissões, cadastro\n'
    '    * "other"             — qualquer assunto que não se enquadre nas categorias acima\n'
    "- Se não houver alguma informação, deixe o campo em branco."
)


class Extractor:
    def __init__(self, *args, **kwargs):
        self.llm = ChatGoogleGenerativeAI(*args, **kwargs)

    def extract(self, state: State) -> State:
        structured_llm = self.llm.with_structured_output(ExtractorSchema)
        human_messages = [msg for msg in state["messages"]
                          if isinstance(msg, HumanMessage)]
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + human_messages
        llm_response = structured_llm.with_retry(
            stop_after_attempt=3,
            wait_exponential_jitter=True
        ).invoke(messages)

        structured_response = (
            f"titulo: {llm_response.title}\n"
            f"categoria: {llm_response.category}\n"
            f"descricao: {llm_response.description}\n"
            f"historico de interacoes: {llm_response.interaction_history}\n"
            f"status atual: {llm_response.current_status}\n"
        )

        # print("Structured Response:\n", structured_response)

        return {
            "messages": [AIMessage(content=structured_response)],
            "extract_ticket_data": llm_response.model_dump()
        }
