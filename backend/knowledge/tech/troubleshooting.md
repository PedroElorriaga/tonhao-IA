# Guia de Solução de Problemas de TI

## Problemas de Conectividade Wi-Fi

Verifique se o adaptador de rede está habilitado no Gerenciador de Dispositivos.
Reinicie o roteador desligando-o por 30 segundos antes de ligar novamente.
Execute o diagnóstico de rede: Configurações > Rede e Internet > Solução de Problemas.
Esqueça a rede Wi-Fi e reconecte inserindo a senha novamente.
Atualize o driver do adaptador de rede pelo Gerenciador de Dispositivos.

## Computador Lento ou Travando

Abra o Gerenciador de Tarefas (Ctrl+Shift+Esc) e verifique processos consumindo alta CPU ou memória.
Execute uma varredura de malware com o Windows Defender ou antivírus instalado.
Verifique o espaço em disco: o sistema operacional precisa de ao menos 15% do disco livre.
Desative programas que iniciam com o Windows em Gerenciador de Tarefas > Inicializar.
Se o problema persistir, considere aumentar a memória RAM ou migrar o SO para um SSD.

## Erro de Tela Azul (BSOD)

Anote o código de erro exibido na tela azul (ex: MEMORY_MANAGEMENT, IRQL_NOT_LESS_OR_EQUAL).
Reinicie o computador e observe se o erro se repete.
Verifique se há atualizações do Windows pendentes.
Execute o sfc /scannow no Prompt de Comando como administrador para reparar arquivos do sistema.
Se o erro ocorreu após instalar um driver ou software, faça a restauração do sistema para um ponto anterior.

## Problemas de Acesso e Login

Verifique se o Caps Lock está ativado ao digitar a senha.
Tente redefinir a senha pelo portal de usuários da empresa.
Se a conta estiver bloqueada, aguarde 15 minutos ou contate o suporte para desbloqueio manual.
Verifique se o computador está conectado ao domínio da empresa (necessário para login corporativo).

## Impressora Não Imprime

Verifique se a impressora está ligada e com papel.
Remova trabalhos travados na fila de impressão em Configurações > Impressoras > Ver fila de impressão.
Reinicie o serviço de spooler: services.msc > Print Spooler > Reiniciar.
Desinstale e reinstale o driver da impressora pelo site do fabricante.
Verifique se a impressora está na mesma rede que o computador (para impressoras de rede).

## Problemas com VPN

Certifique-se de que o cliente VPN está atualizado para a versão mais recente.
Verifique se suas credenciais corporativas estão corretas e não expiraram.
Desative temporariamente o antivírus ou firewall para testar se estão bloqueando a conexão.
Se o erro for de certificado, contate o TI para renovação do certificado de acesso.
