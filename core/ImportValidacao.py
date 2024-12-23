# -*- coding: utf-8 -*-
from collections import OrderedDict
import RemoverCaracteres as RC
import Validacao
import os, csv, sys, gc

def transformarArquivo(caminhoArquivo, caminhoMotores, dictTecnicasPP): 

    csv.field_size_limit(sys.maxint)

    reload(sys)
    sys.setdefaultencoding('utf-8')

    pastaArquivo = caminhoArquivo
    pastaArquivo.encode('utf-8')

    # Aqui (abaixo) você deve colocar o endereço da pasta onde os motores de inferência de um determinado diário
    # que foi escolhido pelo usuário estão.

    # ATENÇÃO: Isso é MUITO importante, o nome dos motores devem vir neste formato:
    # modeloarvoredecisao_caderno.sav
    # modeloarvoredecisao_enunciado.sav
    # modeloarvoredecisao_orgao.sav
    # Etc...

    # SE FOR DINÂMICO, EXEMPLO PARA O DESKL:
    # modelodeskl_orgao.sav
    # modelodeskl_processo.sav
    # modelodeskl_resenha.sav
    # modelodeskl_suborgao.sav
    # Etc...

    # O formato do nome do motor SEMPRE SERÁ: nomemodelo_nomeetiqueta.sav

    # A essa altura você já sabe que sempre temos um motor para cada etiqueta de cada diário.

    pastaMotores = caminhoMotores
    pastaMotores.encode('utf-8')

    #Esse  código é basicamente o que já conhecemos antes, com uma diferença importante: A ideia de validar é você
    # classificar o diário do dia, a partir de agora NÃO PERMITA o upload de múltiplos arquivos.
    # O usuário informará A PASTA onde o arquivo verificado está. E o código fará o resto.
    # ********Não pode haver mais de um arquivo verificado dentro da mesma pasta em hipótese alguma.*********

    caminhos = [os.path.join(pastaArquivo, nome) for nome in os.listdir(pastaArquivo) if nome == os.listdir(pastaArquivo)[0]]
    arquivos = [arq for arq in caminhos if os.path.isfile(arq)]
    txt = [arq for arq in arquivos if arq.lower().endswith(".txt")]

    auxC = ""
    auxT = ""
    cont = 0
    resultadoVer = []

    arqVer = open('VERIFICADO.txt', 'wb')

    print("Arquivos Carregados, iniciando a escrita do conteúdo em array")
    nomearquivo = ""

    for file in txt:
        open_file = open(file, 'r')
        read_file = open_file.readlines()
        name = open_file.name


        if(name.count('Verificado')):
            nomearquivo = name
            for linha in read_file:
                if (linha[0] == '*' and linha[1] == '*'):
                    auxT = "\n\n" + (linha[14:55]) + "\n"
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

                    resultadoVer.append(" ".join(auxV))

    for resVer in resultadoVer:
        arqVer.write(resVer)

    arqVer.close()

    arquivoVer = open('VERIFICADO.txt', 'r')
    textoVer = arquivoVer.readlines()

    auxContVer = ""
    auxTitVer = ""
    contadorVer = 0
    resultadoVerF = []

    for linhaVer in textoVer:
        if linhaVer[0] == '*':
            auxTitVer = linhaVer.replace('*', '')
            if (auxTitVer == "") and contadorVer > 0: auxTitVer = auxTitVer[contadorVer - 1]

        else:
            auxContVer = (linhaVer.replace('\n', ''))
            if (auxContVer == ""): auxContVer = "-1"

        if(auxContVer != "-1" and auxTitVer != "-1"):
            auxVer = []
            auxVer.insert(0, RC.removeAcento(auxTitVer))
            auxVer.insert(1, RC.removeAcento(auxContVer))
            auxVer.insert(2, " ")
            auxTitVer = ""
            auxContVer = ""

            contadorVer = contadorVer + 1
            resultadoVerF.append(auxVer)

    print("Montagem do CSV")

    with open('ArquivoVerificadoFinal.csv', 'wb') as csvfileVer:
        spamwriterVer = csv.writer(csvfileVer, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        spamwriterVer.writerow(['tag', 'conteudo', 'saida'])
        for resVer in resultadoVerF:
            spamwriterVer.writerow(resVer)

    print('Arquivo CSV Gerado')

    print('Excluindo arquivos temporários...')
    arquivoVer.close()
    arqVer.close()
    os.remove('VERIFICADO.txt')

    print("Iniciando a validação dos arquivos...")

    gc.collect()

    # Aqui você deve passar:

    # Arquivo CSV que foi gerado por esse algoritmo (ImportValidacao.py), que tradicionamente estamos dando o nome de ArquivoVerificadoFinal.csv
    # pastaArquivo: A pasta onde o arquivo Verificado está.
    # pastaMotores: A pasta onde os Motores de inferência deste diário estão.
    # nomearquivo: nome do arquivo revisado que vamos trabalhar.
    # dictTecnicasPP: dicionário de técnicas utilizadas no Pré-processamento do motor escolhido

    print("nomearquivo = " + nomearquivo)

    Validacao.validarArquivo("ArquivoVerificadoFinal.csv", pastaArquivo, pastaMotores, nomearquivo, dictTecnicasPP)



