import os

if __name__ == '__main__':
    os.system("cd c:\Hermes-Back")
    os.system("pm2 start monitoramento.py --name Hermes-Monitoramento --namespace Hermes-Monitoramento")
    # os.system("pm2 start loop_monitoramento.py --name Hermes-Monitoramento --namespace Hermes-Monitoramento")



# Sempre uso o PM2 para executar meus scripts python no ambiente Linux. Portanto, considere que um script tem um único parâmetro e precisa ser executado continuamente após algum tempo, então podemos passá-lo assim:
#
# pm2 start <filename.py> --name <nameForJob> --interpreter <InterpreterName> --restart-delay <timeinMilliseconds> -- <param1> <param2>
#
#
# filename.pyé o nome do script python, sem <> símbolos, eu quero executar usando PM2
# nameForJobé o nome significativo para o trabalho, sem <> símbolos
# InterpreterNameé o interpretador python para executar o script, geralmente é python3no linux
# timeinMillisecondsé o tempo que nosso script precisa para esperar e executar novamente
# param1é o primeiro parâmetro para o script
# param2é o segundo parâmetro para o script.