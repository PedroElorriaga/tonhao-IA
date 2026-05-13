from src.modules.agent.graph import AgentGraph
from rich import print
from rich.markdown import Markdown
from langchain_core.messages import HumanMessage

if __name__ == "__main__":
    ticket_teste = "Estou com um problema no meu computador, ele está muito lento e travando frequentemente. Já tentei reiniciar, mas não resolveu. O que posso fazer para melhorar o desempenho?"

    graph = AgentGraph().build()
    content = (f"titulo: wifi\n"
               f"categoria: Technical Support\n"
               f"descrição: nao conecta no wifi\n"
               f"replies anteriores: ja tentei a senha, nao conecta\n"
               )

    graph.invoke({"messages": [HumanMessage(content=content)]})

    # print(Markdown(result['messages'][-1].content[0]['text']))

# APENAS PARA EU TESTAR O AGENT, NÃO É PARA SER USADO EM PRODUÇÃO
