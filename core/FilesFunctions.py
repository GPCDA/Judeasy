# -*- coding: utf-8 -*-
import pandas
import os
import csv
import sqlite3
import sys
import shutil
import math
import os, traceback

# Determinando o diretório atual da pasta de arquivos .txt e pegando os arquivos deste diretório
# diretorioAtual = u'C:/FRAMEWORK/media/'
# arquivos = os.listdir(diretorioAtual)
#diretorioCsv = u'C:/FRAMEWORK/csv/'

reload(sys)
sys.setdefaultencoding('utf8')
csv.field_size_limit(sys.maxint)

pastaArquivos = os.path.abspath(".")+"/arquivos/"

def verificarArquivosClasse(caminho):
    caminho += "/"

    etiquetas = os.listdir(caminho)

    listaEtiquetasRemovidas = []

    for etiqueta in etiquetas: 
        classeZero = 0
        classeUm = 0

        with open(caminho + etiqueta, 'r') as arquivo:
            ler = csv.reader(arquivo)
            next(ler)
            for linha in ler:
                if(linha[2] == "0"): 
                    classeZero += 1
                elif(linha[2] == "1"): 
                    classeUm += 1

        if (classeZero <= 1 or classeUm <= 1):
            listaEtiquetasRemovidas.append(etiqueta.replace('.csv', ''))
            fechar = open(caminho + etiqueta)
            fechar.close()
            try:
                os.remove(caminho + etiqueta)
            except Exception as error:
                traceback.print_exc()

    return listaEtiquetasRemovidas
 

def listarInfoBasesTreinadas(pasta):
    dicio_base_info = None

    try:
        info = os.listdir(pasta)
        pasta += "/"
        dicio_base_info = {}
        lista_temp = []

        for base_treinada in info:
             with open(pasta + base_treinada) as infoBaseTreinada:
                for linha in infoBaseTreinada:
                    lista_temp.append(linha)

                caminho_da_base = lista_temp[0].replace('Caminho do motor = ', '').replace("\n", '')
                lista_temp[1] = lista_temp[1].replace('Nome da base = ', '').replace("\n", '')
                lista_temp[2] = lista_temp[2].replace('Período da base = ', '').replace("\n", '')
                lista_temp[3] = lista_temp[3].replace('Classificador = ', '').replace("\n", '')
                lista_temp[4] = lista_temp[4].replace('Data do treino = ', '').replace("\n", '')
                lista_temp[5] = lista_temp[5].replace('Horário do treino = ', '').replace("\n", '')

                dicio_base_info[caminho_da_base] = lista_temp[1:6]
                dicio_base_info[caminho_da_base].append(base_treinada)

                lista_temp = []
    except Exception as error:
             traceback.print_exc()

    return dicio_base_info



def etiquetasPreProcessadas(etiquetas_escolhidas_global, nome_da_base, inicio, fim):
    conexao = sqlite3.connect('db.sqlite3')
    cursor = conexao.cursor()
    base_Pre_Processada = "UPDATE basedados_basedados SET etiquetas_pre_processadas = '" + str(etiquetas_escolhidas_global) + "'" + "WHERE name = '" + nome_da_base + "'" + " AND inicio = '" + inicio + "'" + " AND fim = '" + fim + "'" 
    print(base_Pre_Processada)
    cursor.execute(base_Pre_Processada)
    conexao.commit()
    cursor.close()
    conexao.close()

def tecnicasDePP(etecnicas_pre_processamento, nome_da_base, inicio, fim):
    conexao = sqlite3.connect('db.sqlite3')
    cursor = conexao.cursor()
    base_Pre_Processada = "UPDATE basedados_basedados SET tecnicas_pre_processamento = '" + str(etecnicas_pre_processamento) + "'" + "WHERE name = '" + nome_da_base + "'" + " AND inicio = '" + inicio + "'" + " AND fim = '" + fim + "'" 
    print(base_Pre_Processada)
    cursor.execute(base_Pre_Processada)
    conexao.commit()
    cursor.close()
    conexao.close()


def alterarDados(nome_da_base, inicio, fim):
    conexao = sqlite3.connect('db.sqlite3')
    cursor = conexao.cursor()
    base_Pre_Processada = "UPDATE basedados_basedados SET pre_processada = 'Sim' WHERE name = '" + nome_da_base + "'" + " AND inicio = '" + inicio + "'" + " AND fim = '" + fim + "'" 
    print(base_Pre_Processada)
    cursor.execute(base_Pre_Processada)
    conexao.commit()
    cursor.close()
    conexao.close()


def pegarTecnicasUtilizadas(nome_da_base, inicio, fim):
    conexao = sqlite3.connect('db.sqlite3')
    cursor = conexao.cursor()
    tecnicas = "SELECT tecnicas_pre_processamento FROM basedados_basedados WHERE name = '" + nome_da_base + "'" + " AND inicio = '" + inicio + "'" + " AND fim = '" + fim + "'" 
    print(tecnicas)
    cursor.execute(tecnicas)
    unique_row = cursor.fetchall()
    print(unique_row)
    cursor.close()
    conexao.close()
    return unique_row


def pegarEtiquetasPP(nome_da_base, inicio, fim):
    conexao = sqlite3.connect('db.sqlite3')
    cursor = conexao.cursor()
    etiquetas = "SELECT etiquetas_pre_processadas FROM basedados_basedados WHERE name = '" + nome_da_base + "'" + " AND inicio = '" + inicio + "'" + " AND fim = '" + fim + "'" 
    print(etiquetas)
    cursor.execute(etiquetas)
    unique_row = cursor.fetchall()
    print(unique_row)
    cursor.close()
    conexao.close()
    return unique_row


def apagarArquivosTxt(arquivos):

    for arquivoTxt in arquivos:
        try:
            arquivoDeletar = pastaArquivos+'media/' + arquivoTxt
            with open(arquivoDeletar, 'r') as delArquivo:
                delArquivo.close()
            os.remove(arquivoDeletar)
        except Exception as error:
            traceback.print_exc()


def apagarBase(nome, inicio, fim):
    conexao = sqlite3.connect('db.sqlite3')
    cursor = conexao.cursor()
    # TROCAR ESTE DIRETÓRIO PELO DA KURIER
    pasta = pastaArquivos+'bases/' + nome + '_' + inicio.replace('/', '') + '_' + fim.replace('/', '')

    print(pasta)
    try:
        shutil.rmtree(pasta)
    except:
        print('Caminho não existe no sistema')   

    cursor.execute("DELETE FROM basedados_basedados WHERE name = '" + nome + "' AND inicio = '" + inicio + "' AND fim = '" + fim + "'")
    conexao.commit()
    cursor.close()
    conexao.close()

           
def nomeDaBase(arquivos):
    coluna = "name"
    nomes = ''
    for arquivo in arquivos:
        nomes += arquivo
    nomes = nomes.split("_")
    nome = nomes[0] + '_' + nomes[1]

    # Retornando a coluna e o registro para colocar nas suas respectivas listas
    return coluna, nome

def inicioDaBase(arquivos):
    nomes = ''
    periodos = []
    inicio = '32132050'
    coluna = "inicio"
    #Pegando os nomes inteiros dos arquivos
    for arquivo in arquivos:
        nomes += arquivo
    # Dividindo os nomes por "_"
    nomes = nomes.split("_")
    # Pegando apenas as datas dos nomes
    for nome in nomes:
        if nome.isdigit():
            periodos.append(nome)
    # Determinando o fim da base
    for periodo in periodos:
        if(len(periodo) > 2):
            if int(periodo[4:8]) < int(inicio[4:8]):
                inicio = periodo
            elif int(periodo[4:8]) == int(inicio[4:8]) and int(periodo[2:4]) < int(inicio[2:4]):
                inicio = periodo
            elif int(periodo[4:8]) == int(inicio[4:8]) and int(periodo[2:4]) == int(inicio[2:4]) and int(periodo[0:2]) < int(inicio[0:2]):
                inicio = periodo
    inicio = inicio[0:2] + '/' + inicio[2:4] + '/' + inicio[4:8]
    registro = inicio

    # Retornando a coluna e o registro para colocar nas suas respectivas listas
    return coluna, registro

def fimDaBase(arquivos):
    nomes = ''
    periodos = []
    fim = '00000000'
    coluna = "fim"
    #Pegando os nomes inteiros dos arquivos
    for arquivo in arquivos:
        nomes += arquivo
    # Dividindo os nomes por "_"
    nomes = nomes.split("_")
    # Pegando apenas as datas dos nomes
    for nome in nomes:
        if nome.isdigit():
            periodos.append(nome)
    # Determinando o fim da base
    for periodo in periodos:
        if(len(periodo) > 2):
            if int(periodo[4:8]) > int(fim[4:8]):
                fim = periodo
            elif int(periodo[4:8]) == int(fim[4:8]) and int(periodo[2:4]) > int(fim[2:4]):
                fim = periodo
            elif int(periodo[4:8]) == int(fim[4:8]) and int(periodo[2:4]) == int(fim[2:4]) and int(periodo[0:2]) > int(fim[0:2]):
                fim = periodo
    fim = fim[0:2] + '/' + fim[2:4] + '/' + fim[4:8]
    registro = fim

    # Retornando a coluna e o registro para colocar nas suas respectivas listas
    return coluna, registro


def quantidadeDeProcessos(caminho):
    cont = 0
    coluna = "quantidade_de_processos"
    etiqueta_processo = ""

    etiquetas = os.listdir(caminho)

    for etiqueta in etiquetas:
        if "PROCESSO" in etiqueta:
            etiqueta_processo = etiqueta
            break

    caminhoCompleto = caminho + "/" + etiqueta_processo

    with open(caminhoCompleto, 'r') as processo:
        ler = csv.reader(processo)
        for linha in ler:
            cont += 1

    registro = str(cont)
            
    return coluna, registro


def nomeDaEtiqueta(lista_de_nomes_etiquetas, listaEtiquetasRemovidas):
    coluna = "nomes_das_etiquetas"

    lista_de_nomes_etiquetas.sort()

    registros = ""

    for etiqueta in lista_de_nomes_etiquetas:
        if etiqueta.replace(" ", "").upper() not in listaEtiquetasRemovidas:
            etiqueta = etiqueta.lower().title() 
            registros += etiqueta + "/"

    return coluna, registros


def quantidadeDeInstancias(caminho):
    coluna = "quantidade_de_instancias"
    cont = 0
    registros = ''

    etiquetas = os.listdir(caminho)

    for etiqueta in etiquetas:
        if not etiqueta == "PRE-PROCESSADO": 
            caminhoCompleto = caminho + "/" + etiqueta
            with open(caminhoCompleto, 'r') as entrada:
                ler = csv.reader(entrada)
                for linha in ler:
                    cont += 1
                registros += str(cont) + "/"
            cont = 0

    return coluna, registros

        # Depois de inserir a quantidade de instâncias na lista de registros, agora pego o nome da etiqueta pra colocar na lista de colunas

        # Tirando os espaços no começo e no fim do nome do arquivo
        #arquivo = arquivo.strip()

        # Tirando o nome ".csv"
        #arquivo = arquivo.split(".")[0].lower().capitalize()
        #stringDoArquivo += arquivo
        # Armazenando os dados na lista de banco de dados
        #lista_de_colunas.append(stringDaInstancia + stringDoArquivo)
        #stringDoArquivo = ''

'''quantidadeDeInstancias(arquivosCsv)
print(lista_de_colunas)
print(lista_de_registros)'''


def tamanhoDosArquivos(caminho):
    coluna = "tamanho_dos_arquivos"
    registros = ""

    etiquetas = os.listdir(caminho)

    for etiqueta in etiquetas:
        if not etiqueta == "PRE-PROCESSADO":
            caminhoCompleto = caminho + "/" + etiqueta
            tamanho = float(os.path.getsize(caminhoCompleto))
            tamanho = int(math.ceil(tamanho/1024))
            registros += str(tamanho) + "/"

    return coluna, registros

        # Depois de armazenar o tamanho da etiqueta na lista de registros, agora pego o nome da etiqueta pra armazenar na lista de colunas

        # Tirando os espaços no começo e no fim do nome do arquivo
        #etiqueta = etiqueta.strip()

        # Tirando o nome ".csv"
        #etiqueta = etiqueta.split(".")[0].lower().capitalize()
        #stringDoArquivo += etiqueta
        # Armazenando os dados na lista de banco de dados
        #lista_de_colunas.append(stringDoTamanho + stringDoArquivo)
        #stringDoArquivo = ''

        #if tamanho < 1000:
            #print(str(tamanho) + ' Bytes')
        #elif tamanho >= 1000 and tamanho <1000000:
            #print(str(tamanho/1024) + ' KB')
        #else:
            #print(str(tamanho/1048576) + ' MB')

'''tamanhoDosArquivos(arquivosCsv)
print(lista_de_colunas)
print(lista_de_registros)'''

def insereValores(conexao, cursor, lista_de_colunas, lista_de_registros):
    insertPadrao = 'INSERT INTO basedados_basedados ('
    cont = 0

    while cont < len(lista_de_colunas):
        if(cont < len(lista_de_colunas)-1):
            insertPadrao += lista_de_colunas[cont] + ', '
        else:
            insertPadrao += lista_de_colunas[cont] + ') VALUES ('
        cont+=1

    cont = 0

    while cont < len(lista_de_registros):
        if (cont < len(lista_de_registros) - 1):
            if isinstance(lista_de_registros[cont], (int, long)):
                insertPadrao += str(lista_de_registros[cont]) + ', '
            else:
                insertPadrao += "'" + str(lista_de_registros[cont]) + "', "
        else:
            if isinstance(lista_de_registros[cont], (int, long)):
                insertPadrao += str(lista_de_registros[cont]) + ')'
            else:
                insertPadrao += "'" + str(lista_de_registros[cont]) + "')"
        cont += 1

    cursor.execute(insertPadrao)
    conexao.commit()









