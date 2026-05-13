import re
from langchain_google_genai import ChatGoogleGenerativeAI
from src.modules.agent.state import State
from src.modules.agent.schema import NodeResponse
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage


class GeneralNode:
    def __init__(self, *args, **kwargs):
        self.llm = ChatGoogleGenerativeAI(*args, **kwargs)
        self.prompt = ChatPromptTemplate.from_template(
            """Você é um atendente especialista em suporte geral ao cliente, com habilidade para lidar com solicitações variadas que não se enquadram em categorias específicas como TI, RH ou faturamento.

            Analise as informações do ticket abaixo e forneça uma resposta clara, empática e objetiva ao cliente.
            Leve em consideração o contexto geral da solicitação, podendo envolver dúvidas sobre produtos, serviços, processos internos, reclamações ou pedidos de informação.

            Regras de resposta:
            - Escreva em texto simples, sem markdown.
            - Pode usar listas numeradas quando necessário.
            - Seja cordial e empático, pois o cliente pode estar frustrado ou confuso.
            - Se a solicitação exigir encaminhamento para outra área, oriente o cliente sobre o próximo passo e quem poderá ajudá-lo.
            - Evite respostas genéricas; adapte a resposta ao contexto específico do ticket.
            - Após cada frase introdutória de seção, pule uma linha antes de listar os itens. Cada item numerado deve estar em sua própria linha.

            Comece com: "Ao analisar a sua solicitação, identifiquei os seguintes pontos relevantes:" e liste os pontos.
            Em seguida, escreva "Para encaminhar a resolução, recomendo os seguintes passos:" e liste os passos detalhados.
            Finalize com uma frase de encerramento cordial, reforçando que a equipe de atendimento está à disposição para ajudar.

            Verificação de domínio:
            Antes de gerar a resposta, verifique se este ticket realmente não se enquadra em TI, RH ou faturamento.
            - Se for realmente geral, deixe reclassified_category como null e responda normalmente.
            - Se este ticket claramente pertencer a outra área, defina reclassified_category: "tech_support" (suporte técnico de TI), "billing" (faturamento/cobranças) ou "hr" (recursos humanos).
              Neste caso, escreva em response apenas: "Este chamado pertence a outra área e será redirecionado."

            Informações do ticket:
            {extracted_info}
            """
        )

    def generate_response(self, state: State) -> State:
        chain = self.prompt | self.llm.with_structured_output(NodeResponse)
        llm_response = chain.with_retry(
            stop_after_attempt=3,
            wait_exponential_jitter=True
        ).invoke({"extracted_info": state["messages"][-1].content})

        if llm_response.reclassified_category:
            return {
                "messages": [],
                "reclassified_category": llm_response.reclassified_category,
                "reroute_count": (state.get("reroute_count") or 0) + 1,
            }

        response_text = re.sub(r' (\d+\.\s)', r'\n\1', llm_response.response)
        response_text = re.sub(
            r'([:.])(\s)(Para |Nossa equipe|Em seguida)', r'\1\n\n\3', response_text)

        return {
            "messages": [AIMessage(content=response_text)],
            "reclassified_category": None,
            "reroute_count": (state.get("reroute_count") or 0) + 1,
        }
