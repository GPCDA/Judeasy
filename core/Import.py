# -*- coding: utf-8 -*-
import os
from . import RemoverCaracteres as RC
from . import Criar
import csv
from collections import OrderedDict
import sys
import gc
import sqlite3
from . import FilesFunctions as FF
import warnings

warnings.filterwarnings("always")


#TESTAR A LINHA DE CÓDIGO ABAIXO PARA VER SE FUNCIONA, EM DETRIMENTO DA FUNÇÃO ABAIXO, QUE TRATA O ERRO NO MOMENTO.
#csv.field_size_limit(long(sys.maxint))

# Meu código para tratar o erro do "csv.field_size_limit(long(sys.maxsize))"
maxInt = sys.maxint
decrement = True

while decrement:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.
    decrement = False
    try:
        csv.field_size_limit(maxInt)
    except OverflowError:
        maxInt = int(maxInt/(2))
        decrement = True

reload(sys)
sys.setdefaultencoding('utf-8')

pastaArquivos = os.path.abspath(".")+"/arquivos/"

def transformarBase(nome_base_digitado, database_ou_validacao): 

    if database_ou_validacao == "database":
        # Criando conexão com o banco de dados e o seu cursor
        conexao = sqlite3.connect('db.sqlite3')
        cursor = conexao.cursor()
    
    # Listas de colunas e registros a serem colocados no banco de dados
    lista_de_colunas = []
    lista_de_registros = []

    pasta = pastaArquivos+'media/'
    pasta.encode('utf-8')

    nomesArquivos = os.listdir(pasta)

    auxC = ""
    auxT = ""
    cont = 0
    resultadoVer = []
    resultadoRev = []

    print("Criando TXT's em branco")
    arqRev = open('REVISADO.txt', 'wb')
    arqVer = open('VERIFICADO.txt', 'wb')

    print("Copiando conteúdos para um array, para após isso escrever tudo nos TXTs anteriormente criados")
    print("Aguarde... Pode demorar")


    # Código meu para tentar acabar com o erro de sempre sobrar um txt, mas não funciona por completo.
    # lista_de_arquivos = []

    # for arquivo in nomesArquivos:
    #     lista_de_arquivos.append(arquivo)

    # for cont, nome in enumerate(lista_de_arquivos, 0):
    #     try:
    #         if (nome.split('_')[0] != lista_de_arquivos[cont+1].split('_')[0]):
    #             os.remove(pasta + lista_de_arquivos[0])

    #         if ((nome.split('_')[0] == lista_de_arquivos[cont+1].split('_')[0]) and ((nome.split('_')[2][4:8] != lista_de_arquivos[cont+1].split('_')[2][4:8]) or (nome.split('_')[2][2:4] != lista_de_arquivos[cont+1].split('_')[2][2:4]))):
    #             os.remove(pasta + lista_de_arquivos[0])
    #     except: 
    #         pass

    # As três variáveis abaixo retornam a mesma coisa, não!?
    caminhos = [os.path.join(pasta, nome) for nome in os.listdir(pasta)]
    arquivos = [arq for arq in caminhos if os.path.isfile(arq)]
    txt = [arq for arq in arquivos if arq.lower().endswith(".txt")]

    print "PASTA ------"
    print nomesArquivos

    for file in txt:
        open_file = open(file, 'r')
        read_file = open_file.readlines()
        name = open_file.name

        if(name.count('Verificado')):
            nome_arqVerificado = name.split('_')
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



        if (name.count('Revisado')):
            nome_arqRevisado = name.split('_')
            nome_arqVerificado = name.split('_')
            for linha in read_file:
                if (linha[0] == '*' and linha[1] == '*'):
                    auxT = "\n\n" + (linha[14:55]) + "\n"
                    if (auxT == "") and cont > 0: auxT = auxT[cont - 1]
                else:
                    auxC = (linha.replace('\n', ''))
                    if (auxC == ""): auxC = "-1"

                if (auxC != "-1" and auxT != "-1"):
                    auxR = []
                    auxR.insert(0, auxT)
                    auxR.insert(1, auxC)
                    auxT = ""
                    auxC = ""

                    resultadoRev.append(" ".join(auxR))

    
    for resVer in resultadoVer:
        arqVer.write(resVer)

    for resRev in resultadoRev:
        arqRev.write(resRev)

    # Incluindo informações na lista da base de dados
    if nome_base_digitado is not None:
        # Se existe um nome da base digitado, então isso vem da tela de "database"
        lista_de_colunas.append('name')
        lista_de_registros.append(nome_base_digitado)
    else:
        # Se NÃO existe um nome da base digitado, então isso vem da tela de "validação"
        coluna, registro = FF.nomeDaBase(nomesArquivos)
        lista_de_colunas.append(coluna)
        lista_de_registros.append(registro)

    # Recebendo o nome da coluna "Início da base" e o registro da mesma. Posteriormente, colocando na lista da base de dados   
    coluna, registro = FF.inicioDaBase(nomesArquivos)
    lista_de_colunas.append(coluna)
    lista_de_registros.append(registro)

    # Recebendo o nome da coluna "Fim da base" e o registro da mesma. Posteriormente, colocando na lista da base de dados
    coluna, registro = FF.fimDaBase(nomesArquivos)
    lista_de_colunas.append(coluna)
    lista_de_registros.append(registro)


    # Listando os nomes dos arquivos novamente, já que um foi apagado (gambiarra, pois sempre sobra um arquivo txt na pasta, na hora da exclusão)
    pasta = pastaArquivos+'media/'
    pasta.encode('utf-8')
    nomesArquivos = os.listdir(pasta) 

    print('Removendo os arquivos .txt')
    # Ajeitar a função abaixo (Sempre sobra um arquivo a ser removido)
    FF.apagarArquivosTxt(nomesArquivos)

    print("Array  txt's unificados foram preenchidos")

    arquivoRev = open('REVISADO.txt', 'r')
    arquivoVer = open('VERIFICADO.txt', 'r')

    print("Aguarde...")

    textoRev = arquivoRev.readlines()
    textoVer = arquivoVer.readlines()

    auxContVer = ""
    auxContRev = ""
    auxTitVer = ""
    auxTitRev = ""
    contadorVer = 0
    contadorRev = 0
    resultadoVerF = []
    resultadoRevF = []

    gc.collect()
    #VERIFICADO
    for linhaVer in textoVer:
        if linhaVer[0] == '*':
            auxTitVer = linhaVer.replace('*', '')
            try:
                if (auxTitVer == "") and contadorVer > 0: auxTitVer = auxTitVer[contadorVer - 1]
            except: 
                pass

        else:
            auxContVer = (linhaVer.replace('\n', ''))
            if (auxContVer == ""): auxContVer = "-1"

        if(auxContVer != "-1" and auxTitVer != "-1"):
            auxVer = []
            auxVer.insert(0, RC.removeAcento(auxTitVer))
            auxVer.insert(1, RC.removeAcento(auxContVer))
            auxTitVer = ""
            auxContVer = ""

            contadorVer = contadorVer + 1
            resultadoVerF.append(auxVer)

    with open('ArquivoVerificadoFinal.csv', 'wb') as csvfileVer:
        spamwriterVer = csv.writer(csvfileVer, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        spamwriterVer.writerow(['tag', 'conteudo', 'saida'])
        for resVer in resultadoVerF:
            spamwriterVer.writerow(resVer)

    print('Arquivo CSV Verificado Gerado')

    print('Excluindo o arquivo de texto Verificado...')
    arquivoVer.close()
    arqVer.close()
    #os.remove('VERIFICADO.txt')

    print ("Aguarde...")
    gc.collect()
    #REVISADO
    for linhaRev in textoRev:
        if linhaRev[0] == '*':
            auxTitRev = linhaRev.replace('*', '')
            if (auxTitRev == "") and contadorRev > 0: auxTitRev = auxTitRev[contadorRev - 1]
        else:
            auxContRev = (linhaRev.replace('\n', ''))
            if (auxContRev == ""): auxContRev = "-1"

        if(auxContRev != "-1" and auxTitRev != "-1"):
            auxRev = []
            auxRev.insert(0, RC.removeAcento(auxTitRev))
            auxRev.insert(1, RC.removeAcento(auxContRev))
            auxTitRev = ""
            auxContRev = ""

            contadorRev = contadorRev + 1
            resultadoRevF.append(auxRev)


    with open('ArquivoRevisadoFinal.csv', 'wb') as csvfileRev:
        spamwriterRev = csv.writer(csvfileRev, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        spamwriterRev.writerow(['tag', 'conteudo', 'saida'])
        for resRev in resultadoRevF:
            spamwriterRev.writerow(resRev)

    print ('Arquivo CSV Revisado gerado ')
    print ('Excluindo o arquivo de texto Revisado...')
    arquivoRev = open('REVISADO.txt', 'r')
    arquivoRev.close()
    arqRev = open('REVISADO.txt', 'wb')
    arqRev.close()
    #os.remove('REVISADO.txt')

    print ("Aguarde...")
    #Verifica quais dados estão no arquivo Verificado, mas não estão fielmente no arquivo Revisado. Sendo assim, acha os erros.
    signature_row_map = OrderedDict()
    gc.collect()
    print("Comparando os arquivos CSV's")
    print("Aguarde... Pode demorar")

    with open('ArquivoVerificadoFinal.csv') as file_object:
        for line in csv.DictReader(file_object, delimiter=','):
            signature_row_map[line['conteudo']] = {'line': line, 'found_at': None}


    with open('ArquivoRevisadoFinal.csv') as file_object:
        for i, line in enumerate(csv.DictReader(file_object, delimiter=','), 1):
            if line['conteudo'] in signature_row_map:
                signature_row_map[line['conteudo']]['found_at'] = i

    print("Criando arquivo final com a classe 0 ou 1...")
    with open('update.csv', 'w') as file_object:
        fieldnames = ['tag', 'conteudo', 'saida']
        writer = csv.DictWriter(file_object, fieldnames, delimiter=',')
        writer.writer.writerow(fieldnames)
        for signature_info in signature_row_map.itervalues():
            result = '0'
            if signature_info['found_at'] is not None:
                result = result.format('', '(row %s)' % signature_info['found_at'])
            else:
                result = '1'
            payload = signature_info['line']
            payload['saida'] = result

            writer.writerow(payload)

    print("Excluindo arquivos CSV's temporários")
    #os.remove('ArquivoVerificadoFinal.csv')
    #os.remove('ArquivoRevisadoFinal.csv')
    print("Comparação finalizada, iniciando a multiplicação dos arquivos...")

    gc.collect()

    
    # Recebendo o nome da coluna "Quantidade de processos" e o registro da mesma. Posteriormente, colocando na lista da base de dados
    lista_temp_coluna, lista_temp_registro, listaEtiquetasRemovidas = Criar.multiplicarArquivos("update.csv", lista_de_colunas, lista_de_registros, database_ou_validacao)

    if database_ou_validacao == "database":
        # for coluna in lista_temp_coluna:
        lista_de_colunas.extend(lista_temp_coluna)

        # for registro in lista_temp_registro:
        lista_de_registros.extend(lista_temp_registro)

        print(lista_de_colunas)
        print(lista_de_registros)

        # Inserindo os valores na base de dados
        FF.insereValores(conexao, cursor, lista_de_colunas, lista_de_registros)

        # Finalizando a conexão com a base de dados
        cursor.close()
        conexao.close()

    return lista_de_registros, listaEtiquetasRemovidas





