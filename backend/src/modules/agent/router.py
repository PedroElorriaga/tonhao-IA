from src.modules.agent.graph import AgentGraph
from rich import print
from rich.markdown import Markdown

if __name__ == "__main__":
    ticket_teste = "Estou com um problema no meu computador, ele está muito lento e travando frequentemente. Já tentei reiniciar, mas não resolveu. O que posso fazer para melhorar o desempenho?"

    graph = AgentGraph().build()
    result = graph.invoke({"messages": ticket_teste})

    print(Markdown(result['messages'][-1].content[0]['text']))

# APENAS PARA EU TESTAR O AGENT, NÃO É PARA SER USADO EM PRODUÇÃO