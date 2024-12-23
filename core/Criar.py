# -*- coding: utf-8 -*-
import pandas as pd
import gc
import csv, os
import sys
from . import FilesFunctions as FF

def multiplicarArquivos(URL, lista_de_colunas, lista_de_registros, database_ou_validacao):
    # encoding=utf8
    reload(sys)
    sys.setdefaultencoding('utf8')

    #TESTAR A LINHA DE CÓDIGO ABAIXO PARA VER SE FUNCIONA, EM DETRIMENTO DA FUNÇÃO ABAIXO, QUE TRATA O ERRO NO MOMENTO.
    #csv.field_size_limit(long(sys.maxint))

    maxInt = sys.maxint
    decrement = True

    pastaArquivos = os.path.abspath(".")+"/arquivos/"

    while decrement:
        # decrease the maxInt value by factor 10 
        # as long as the OverflowError occurs.
        decrement = False
        try:
            csv.field_size_limit(maxInt)
        except OverflowError:
            maxInt = int(maxInt/(2))
            decrement = True

    # Caminho das etiquetas ".csv"
    pasta = ""
    caminho = ""
    listaEtiquetasRemovidas = []

    if database_ou_validacao == "database":
        # TROCAR ESTE DIRETÓRIO PELO DA KURIER
        pasta = pastaArquivos+'bases'
         # Se a pasta "bases" não tiver sido criada, é criada agora
        if not os.path.exists(pasta):
            os.mkdir(pasta)
        pasta += "/"

    else:
         # TROCAR ESTE DIRETÓRIO PELO DA KURIER
        pasta =  pastaArquivos+'validacao'
         # Se a pasta "bases" não tiver sido criada, é criada agora
        if not os.path.exists(pasta):
            os.mkdir(pasta)
        pasta += "/"


    listaDados = []

    for chunk in pd.read_csv(URL, sep=',', chunksize=20000):
        listaDados.append(chunk)

    arquivoFinal = pd.concat(listaDados, axis=0)
    del listaDados

    arquivoFinal = arquivoFinal.dropna()

    dadosTag = arquivoFinal.tag.tolist()
    dadosTag = set(dadosTag)
    dadosTag = list(dadosTag)


    pasta += lista_de_registros[0] + '_' + lista_de_registros[1].replace('/', '') + '_' + lista_de_registros[2].replace('/', '')
    

    if database_ou_validacao == "database":
        # TROCAR ESTE DIRETÓRIO PELO DA KURIER
        caminho = pastaArquivos+'bases/' + lista_de_registros[0] + '_' + lista_de_registros[1].replace('/', '') + '_' + lista_de_registros[2].replace('/', '')
    else:
        # TROCAR ESTE DIRETÓRIO PELO DA KURIER
        caminho = pastaArquivos+'validacao/' + lista_de_registros[0] + '_' + lista_de_registros[1].replace('/', '') + '_' + lista_de_registros[2].replace('/', '')

    try:
        os.mkdir(pasta)
    except Exception:
        print('A Pasta ' + pasta + ' já existe')
    pasta += '/'

    # Criando a lista das etiquetas para depois mandá-las para a base de dados
    lista_de_nomes_etiquetas = []

    print("Escrevendo arquivos com os nomes das etiquetas")
    for etiqueta in dadosTag:
        # Adicionando cada nome de etiqueta à lista de etiquetas
        new_etiqueta1 = etiqueta.replace(" \r\n", '')
        lista_de_nomes_etiquetas.append(new_etiqueta1)
        new_etiqueta = new_etiqueta1.replace(" ", "")
        with open(pasta+new_etiqueta+'.csv', 'wb') as csvTag:
            spamwriter = csv.writer(csvTag, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(['tag', 'conteudo', 'saida'])

    gc.collect()
    resultadoLinha = []
    print("Montar Array com conteúdo dos arquivos")
    print("Aguarde...")
    for i, row in arquivoFinal.iterrows():
        new_tag1 = row['tag'].replace(" \r\n", '')
        new_tag = new_tag1.replace(" ", "")

        montaLinha = []
        montaLinha.insert(0, new_tag)
        montaLinha.insert(1, row["conteudo"])
        montaLinha.insert(2, row["saida"])
        resultadoLinha.append(montaLinha)

    print("Array com conteudo dos arquivos montado")
    #arquivosCsv = os.listdir(pasta)
    pasta.encode('utf-8')
    caminhos = [os.path.join(pasta, nome) for nome in os.listdir(pasta)]
    csvEtiquetas = [arq for arq in caminhos if arq.lower().endswith(".csv")]

    gc.collect()
    print("Preencher arquivos")
    print("Aguarde... Pode demorar...")

    for file in csvEtiquetas:
        open_file = open(file, 'r')
        read_file = open_file.readlines()
        name = open_file.name

        with open(name, 'wb') as csvEtiqueta:
            tagWriter = csv.writer(csvEtiqueta, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            tagWriter.writerow(['tag', 'conteudo', 'saida'])

            for resL in resultadoLinha:
                #Nome do arquivo
                new_name = name.split('/')
                new_name[-1] = new_name[-1].replace('.csv', '')
                new_name[-1] = new_name[-1].replace(' ', '')
                #Se o nome do arquivo for igual ao nome da tag, escreva no csv.
                if (new_name[-1] == resL[0]):
                    tagWriter.writerow(resL)


    #os.remove(URL)

   

    lista_temp_coluna = []
    lista_temp_registro = []

    # SÓ PRECISA DESSE PROCESSO SE VIER DA TELA DE DATABASE
    if database_ou_validacao == "database":

        # Função para apagar as etiquetas que são muito pequenas para serem pré-processadas e treinadas, futuramente
        listaEtiquetasRemovidas = FF.verificarArquivosClasse(caminho)


        # Declarando as strings e listas que servirão temporariamente, apenas para os cálculos necessários
        string_temp_coluna = ""
        string_temp_registro = ""

        # Recebendo uma string com o nome da coluna "nomes_das_etiquetas" e uma stringzona com os registros de "nomes_das_etiquetas"  
        string_temp_coluna, string_temp_registro = FF.nomeDaEtiqueta(lista_de_nomes_etiquetas, listaEtiquetasRemovidas)

        # Colocando as duas strings anteriores numa lista temporária
        lista_temp_coluna.append(string_temp_coluna)
        lista_temp_registro.append(string_temp_registro)

        # Recebendo uma string com o nome da coluna "tamanho_dos_arquivos" e uma stringzona com os registros de "tamanho_dos_arquivos"
        string_temp_coluna, string_temp_registro = FF.tamanhoDosArquivos(caminho)
        # Colocando as duas strings anteriores numa lista temporária
        lista_temp_coluna.append(string_temp_coluna)
        lista_temp_registro.append(string_temp_registro)

        # Recebendo uma string com o nome da coluna "quantidade_de_instancias" e uma stringzona com os registros de "quantidade_de_instancias"
        string_temp_coluna, string_temp_registro = FF.quantidadeDeInstancias(caminho)
        # Colocando as duas strings anteriores numa lista temporária
        lista_temp_coluna.append(string_temp_coluna)
        lista_temp_registro.append(string_temp_registro)

        # Últimos itens a serem adicionados
        string_temp_coluna, string_temp_registro = FF.quantidadeDeProcessos(caminho)
        # Colocando as duas strings anteriores numa lista temporária
        lista_temp_coluna.append(string_temp_coluna)
        lista_temp_registro.append(string_temp_registro)

        print(lista_temp_coluna)
        print(lista_temp_registro)

    print("\n Todos os seus arquivos estão em: "+str(pasta))
    print("\n FIM!!!")

    return lista_temp_coluna, lista_temp_registro, listaEtiquetasRemovidas