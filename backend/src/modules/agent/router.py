from src.modules.agent.graph import get_graph
from rich import print
from langchain_core.messages import HumanMessage

if __name__ == "__main__":
    ticket_teste = "Estou com um problema no meu computador, ele está muito lento e travando frequentemente. Já tentei reiniciar, mas não resolveu. O que posso fazer para melhorar o desempenho?"

    content = (f"titulo: Solicitação de treinamento no sistema\n"
               f"categoria: Hr\n"
               f"descrição: Nossa equipe é nova e precisa de um treinamento guiado para utilizar as principais funcionalidades.\n"
               f"replies anteriores: \n"
               )

    graph = get_graph()
    # Salva a imagem do grafo para visualização
    # graph.get_graph().draw_mermaid_png(output_file_path="agent_graph_out_rerouter.png")
    result = graph.invoke(
        {"messages": [HumanMessage(content=content)]}, config={"configurable": {"thread_id": "test_thread"}})

    print(result)

    ai_text = result["messages"][-1].content
    if isinstance(ai_text, list):
        ai_text = ai_text[0]["text"]

    print(ai_text, result.get("model_used"))

# APENAS PARA EU TESTAR O AGENT, NÃO É PARA SER USADO EM PRODUÇÃO
