import re
from langchain_google_genai import ChatGoogleGenerativeAI
from src.modules.agent.state import State
from src.modules.agent.schema import NodeResponse
from src.modules.agent.prompts import general_prompt
from langchain_core.messages import AIMessage


class GeneralNode:
    def __init__(self, *args, **kwargs):
        self.llm = ChatGoogleGenerativeAI(*args, **kwargs)

    def generate_response(self, state: State) -> State:
        chain = general_prompt | self.llm.with_structured_output(NodeResponse)
        llm_response = chain.with_retry(
            stop_after_attempt=3,
            wait_exponential_jitter=True
        ).invoke({
            "extracted_info": state["messages"][-1].content,
            "retrieved_context": state.get("retrieved_context") or "Nenhum contexto adicional disponível.",
        })

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
