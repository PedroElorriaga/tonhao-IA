from langchain_google_genai import ChatGoogleGenerativeAI
from src.modules.agent.state import State
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage


class TechNode:
    def __init__(self, *args, **kwargs):
        self.llm = ChatGoogleGenerativeAI(*args, **kwargs)
        self.prompt = ChatPromptTemplate.from_template(
            """Você é um especialista técnico de TI.
            Dada as informações abaixo, analise o problema e forneça uma solução com o passo a passo para o cliente.
            Seja claro e objetivo, forneça passos para resolução do problema e possíveis causas.
            Sem ser em markdown, apenas texto simples, mas pode listar com numeros se necessario.
            comece a respora com: "Ao verificar as informações, verifiquei as seguintes causas possíveis para o problema:" e depois liste as causas.
            e dpois forneça os passos para resolução do problema, começando com "Para resolver o problema, siga os seguintes passos:" e depois liste os passos.
            
            {extracted_info}
            """
        )

    def generate_response(self, state: State) -> State:
        chain = self.prompt | self.llm
        llm_response = chain.with_retry(
            stop_after_attempt=3,
            wait_exponential_jitter=True
        ).invoke({"extracted_info": state["messages"][-1].content})

        return {"messages": [llm_response]}
