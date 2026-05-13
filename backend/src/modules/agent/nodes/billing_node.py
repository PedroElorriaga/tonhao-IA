import re
from langchain_google_genai import ChatGoogleGenerativeAI
from src.modules.agent.state import State
from src.modules.agent.schema import NodeResponse
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage


class BillingNode:
    def __init__(self, *args, **kwargs):
        self.llm = ChatGoogleGenerativeAI(*args, **kwargs)
        self.prompt = ChatPromptTemplate.from_template(
            """Você é um especialista em faturamento e cobranças com amplo conhecimento em processos financeiros, emissão de notas fiscais, cobranças indevidas, reembolsos, inadimplência e contestação de faturas.

            Analise as informações do ticket abaixo e forneça uma resposta clara e objetiva ao cliente.
            Leve em consideração possíveis erros de cobrança, atrasos no processamento de pagamentos, problemas com método de pagamento, cancelamentos e estornos.

            Regras de resposta:
            - Escreva em texto simples, sem markdown.
            - Pode usar listas numeradas quando necessário.
            - Seja empático, pois questões financeiras geram preocupação no cliente.
            - Se o problema envolver reembolso ou estorno, oriente sobre prazos típicos (ex: 5 a 10 dias úteis).
            - Se houver cobrança indevida, oriente o cliente a não efetuar o pagamento até a regularização.
            - Após cada frase introdutória de seção, pule uma linha antes de listar os itens. Cada item numerado deve estar em sua própria linha.

            Comece com: "Ao analisar as informações da sua solicitação, identifiquei as seguintes possíveis causas:" e liste as causas.
            Em seguida, escreva "Para resolver a situação, siga os passos abaixo:" e liste os passos detalhados.
            Finalize com uma frase de encerramento cordial, reforçando que a equipe financeira está à disposição.

            Verificação de domínio:
            Antes de gerar a resposta, verifique se este ticket realmente pertence ao domínio de faturamento e cobranças (faturas, pagamentos, reembolsos, estornos, cobranças indevidas).
            - Se pertencer, deixe reclassified_category como null e responda normalmente.
            - Se NÃO pertencer, defina reclassified_category com o domínio correto: "tech_support" (suporte técnico de TI), "hr" (recursos humanos) ou "other" (dúvidas gerais).
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
