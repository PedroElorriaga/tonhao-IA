import re
from langchain_google_genai import ChatGoogleGenerativeAI
from src.modules.agent.state import State
from src.modules.agent.schema import NodeResponse
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage


class HRNode:
    def __init__(self, *args, **kwargs):
        self.llm = ChatGoogleGenerativeAI(*args, **kwargs)
        self.prompt = ChatPromptTemplate.from_template(
            """Você é um especialista em Recursos Humanos com amplo conhecimento em legislação trabalhista, benefícios, folha de pagamento, processos de admissão e desligamento, férias, licenças e políticas internas da empresa.

            Analise as informações do ticket abaixo e forneça uma resposta clara, empática e objetiva ao colaborador.
            Leve em consideração situações comuns como dúvidas sobre holerite, solicitação de documentos, férias, banco de horas, plano de saúde, treinamentos e conflitos no ambiente de trabalho.

            Regras de resposta:
            - Escreva em texto simples, sem markdown.
            - Pode usar listas numeradas quando necessário.
            - Seja empático e discreto, pois questões de RH podem ser sensíveis e pessoais.
            - Se o caso envolver algo que requer análise individualizada (ex: rescisão, afastamento médico), oriente o colaborador a entrar em contato diretamente com o RH.
            - Respeite a confidencialidade das informações; não especule sobre situações não mencionadas no ticket.
            - Após cada frase introdutória de seção, pule uma linha antes de listar os itens. Cada item numerado deve estar em sua própria linha.

            Comece com: "Ao analisar a sua solicitação, identifiquei os seguintes pontos relevantes:" e liste os pontos.
            Em seguida, escreva "Para encaminhar a resolução, recomendo os seguintes passos:" e liste os passos detalhados.
            Finalize com uma frase de encerramento cordial, reforçando que a equipe de RH está à disposição para apoiar o colaborador.

            Verificação de domínio:
            Antes de gerar a resposta, verifique se este ticket realmente pertence ao domínio de Recursos Humanos (férias, holerite, benefícios, admissão, desligamento, legislação trabalhista).
            - Se pertencer, deixe reclassified_category como null e responda normalmente.
            - Se NÃO pertencer, defina reclassified_category com o domínio correto: "tech_support" (suporte técnico de TI), "billing" (faturamento/cobranças) ou "other" (dúvidas gerais).
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
