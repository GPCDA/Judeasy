# -*- coding: utf-8 -*-
import traceback

from joblib import Parallel, delayed
import pandas as pd
import csv, os, sys, gc, dill
import PreprocessamentoValidacao as preprocess


def validarArquivo(URL, pastaArquivo, pastaMotores, nomeArquivo, dictTecnicasPP):

    reload(sys)
    sys.setdefaultencoding('utf8')
    csv.field_size_limit(sys.maxint)

    #Vamos carregar os motores de inferência para trabalhar posteriormente
    caminhos = [os.path.join(pastaMotores, nome) for nome in os.listdir(pastaMotores)]
    arquivos = [arq for arq in caminhos if os.path.isfile(arq)]
    sav = [arq for arq in arquivos if arq.lower().endswith(".sav")]

    # Aqui, chamamos a função de preprocessamento, passando um parâmetro a mais, que seria a URL onde o arquivo CSV de
    # validação está, ele deve ser préprocessado exatamente IGUAL ao arquivo que foi usado por este motor para treinar
    # cada uma das etiquetas. Como o préprocessamento é o mesmo para todas as etiquetas de um mesmo diário, só precisamos
    # de uma URL onde coloquei todas as etiquetas em um mesmo arquivo.

    # Esses parâmtros "True" e "False" você deve puxar do banco de dados, onde vai ter informando exatamente qual foi o
    # pre processamento utilizado no treinamento do diário, conforme já comentamos.

    arquivoFinalCSV = preprocess.chamarFuncoes(URL, stemmingfunc=dictTecnicasPP.get('stemming', False), remove_stopwordsfunc=dictTecnicasPP.get('stopWords', False),
                             remove_numerosfunc=dictTecnicasPP.get('removeNumeros', False), lematizacaofunc=dictTecnicasPP.get('lematizacao', False), tokenizacaofunc=dictTecnicasPP.get('tokenizer', False),
                             redescomplesxasfunc=dictTecnicasPP.get('redesComplexas', False), removeacentofunc=dictTecnicasPP.get('removePontuacao', False))

    # O preprocessamento dá origem a um arquivo preprocessado, certo?
    # Agora devemos carregar o arquivo preprocessado que geramos anteriomente.

    listaDados = []
    for chunk in pd.read_csv(arquivoFinalCSV, sep=',', chunksize=20000):
        listaDados.append(chunk)

    # Deletando o arquivo final .csv, já que o mesmo já foi utilizado acima
    try:
        os.remove(arquivoFinalCSV)
    except Exception as error:
        traceback.print_exc()

    arquivoFinal = pd.concat(listaDados, axis=0)
    del listaDados

    print("Validando as instâncias de acordo com os nomes das etiquetas")

    saida = []
    nomesMotores = []

    # Vamos criar um array com o nome de todas as etiquetas que possuem um motor de inferência.
    for file in sav:
        open_file = open(file, 'r')

        # Extrair, do nome do arquivo do motor de inferência, o nome da etiqueta.
        # Lembra que lá no arquivo ImportValidacao eu disse que o motor tem que ter o nome da etiqueta após
        # o "_"? Damos um split para pegar somente o nome da etiqueta do motor.
        name = (open_file.name).split("@")
        new_name = name[1].split("_")

        nomesMotores.append(new_name[0])

    # Agora vamos ler o arquivo preprocessado.
    for i, row in arquivoFinal.iterrows():
        # Nome etiqueta no arquivo CSV
        # Temos um arquivo CSV que possui todas as etiquetas misturadas, vamos extrair o nome delas
        # isoladamente para trabalhar mais adiante.
        etiqueta = (str(row['tag']).lower()).replace(" ", "")
        new_etq = etiqueta.replace("\r\n", '')
        new_etq = new_etq.replace('\n', '')
        # Vamos verificar se existe de fato um nome de etiqueta para ser analisado
        if(new_etq != 'nan'):
            # Se esta etiqueta não estiver na lista de motores que montamos anteriormente, é porque não existe um
            # motor para ela, isso deve ser informado no TXT, por isso confiro aqui.

            if (new_etq.upper() not in nomesMotores):
                saida.append("Etiqueta Sem Motor de Inferência")
            else:
                #Para cada etiqueta estudada, vamos abrir os motores até achar aquele que leva o nome desta etiqueta.
                for file in sav:
                    open_motor = open(file, 'r')
                    motordeinferencia = (open_motor.name).split("@")
                    new_motor = motordeinferencia[1].split("_")

                    # Agora a gente compara, o nome do motor de inferência é igual ao da etiqueta?
                    if (new_motor[0] == new_etq.upper()):
                        print(open_motor.name)
                        # Se for, então pegue o conteudo desta etiqueta e o classifique com o motor de mesmo nome.
                        modelo = dill.load(open(open_motor.name, 'rb'))
                        input = [row['conteudo']]
                        with Parallel(n_jobs=1, backend='multiprocessing') as parallel:
                            predicao = modelo.predict(input)
                            saida.append(predicao)


    #Agora não precisamos mais do arquivo update.csv para nada, vamos excluir.
    os.remove(URL)
    pastaArquivo.encode('utf-8')

    # Vamos criar um arquivo txt exatamente no padrão da Kurier, ou seja, com o mesmo nome
    # do arquivo Verificado que analisamos, sendo que este será "REVISADOJudeasy".

    nometxt = nomeArquivo.split("/")
    new_nometxt = nometxt[-1].replace("Verificado", "REVISADOJudeasy")
    #Criando o nosso arquivo revisado
    arqVer = open(new_nometxt, 'wb')

    auxC = ""
    auxT = ""
    cont = 0
    i = -1
    resultadoVer = []

    # Agora escrever no TXT a saída dos motores de inferências.

    open_file = open(nomeArquivo, 'r')
    name = open_file.name

    if (name.count('Verificado')):
        read_file = open_file.readlines()
        for linha in read_file:
            if (linha[0] == '*' and linha[1] == '*'):
                i = i + 1

                Resultado = "[Etiqueta Sem Motor de Inferência]"

                if(str(saida[i]) == '[0]'):
                    Resultado = "[Correto]"
                if (str(saida[i]) == '[1]'):
                    Resultado = "[Incorreto]"

                auxT = "\n\n" + (linha) + Resultado + "\n"
                if (auxT == "") and cont > 0: auxT = auxT[cont - 1]

            else:
                auxC = (linha.replace('\n', ''))
                if (auxC == ""): auxC = "-1"

            if (auxC != "-1" and auxT != "-1"):
                auxV = []
                auxV.insert(0, auxT)
                auxV.insert(1, auxC)
                auxT = ""
                auxC = ""

                resultadoVer.append("\n".join(auxV))

    # Montar o txt final
    for resVer in resultadoVer:
        arqVer.write(resVer)

    print("FIM")