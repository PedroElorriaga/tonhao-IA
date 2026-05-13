from src.modules.agent.graph import AgentGraph
from rich import print
from rich.markdown import Markdown
from langchain_core.messages import HumanMessage

if __name__ == "__main__":
    ticket_teste = "Estou com um problema no meu computador, ele está muito lento e travando frequentemente. Já tentei reiniciar, mas não resolveu. O que posso fazer para melhorar o desempenho?"

    graph = AgentGraph().build()
    content = (f"titulo: problemas com wifi\n"
               f"categoria: billing\n"
               f"descrição: Nao consigo logar no wifi\n"
               f"replies anteriores: \n"
               )

    result = graph.invoke({"messages": [HumanMessage(content=content)]})

    ai_text = result["messages"][-1].content
    if isinstance(ai_text, list):
        ai_text = ai_text[0]["text"]

    print(ai_text, result["reclassified_category"], result["reroute_count"])

# APENAS PARA EU TESTAR O AGENT, NÃO É PARA SER USADO EM PRODUÇÃO
