# coding: utf-8

import re, ast, csv, pickle
import itertools as it
import networkx as nx
import pandas as pd
import sys, csv, os

pastaArquivos = os.path.abspath(".")+"/core/"

def redecomplexaexc(URL):
    reload(sys)
    sys.setdefaultencoding('utf8')
    csv.field_size_limit(sys.maxint)

    listaDados = []
    for chunk in pd.read_csv(URL, sep=',', chunksize=20000):
        listaDados.append(chunk)

    df_cont = pd.concat(listaDados, axis=0)
    del listaDados

    #ESSE É O DIRETÓRIO QUE ESTOU TRABALHANDO. NA KURIER, O DIRETÓRIO SERÁ OUTRO.
    tagger = pickle.load(open(pastaArquivos+"tagger.pkl"))


    tagged_sents = []
    noun_phrases = []
    edgelist = []

    def remove_caracteres(row):
        dict = {"\"'": "\"",  "{": "", "}": "", "(": "", ")": ""}
        regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
        return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], row)

    for idx, word in enumerate(df_cont['conteudo']):
        tagged_sents.append([tagger.tag(sentence) for sentence in ast.literal_eval(word)])

    for linha2 in tagged_sents:
        noun_phrases.append([[token for token, tag in sent if re.match(r'NOUN*|ADJ*|VERB*|ADV*', tag)]
                            for sent in linha2])


    for phrase in noun_phrases:
        edgelist.append([edge for ph in phrase for edge in it.combinations(ph, 2)])

    G = []
    index = []

    for token in edgelist:
        G.append(nx.Graph(token))

    for indG in G:
        index.append([nx.betweenness_centrality(indG, normalized=True)])

    dfFinal = pd.DataFrame({'conteudo': index})

    resultadoLinha = []

    for i, row in dfFinal.iterrows():
        linha = remove_caracteres(str(row["conteudo"]))

        montaLinha = []
        montaLinha.insert(0, df_cont['tag'][i])
        if len(linha) > 2:
            montaLinha.insert(1, linha)
        if  len(linha) == 2:
            montaLinha.insert(1, (df_cont['conteudo'][i]))

        montaLinha.insert(2,  df_cont['saida'][i])

        resultadoLinha.append(montaLinha)

    print("Criando CSV Redes Complexas")
    #CRIANDO NOVOS ARQUIVOS CSV COM REDES COMPLEXAS. ELES TÊM NOMES DIFERENTES PORQUE OS ANTERIORES SÃO EXCLUIDOS
    with open(URL.replace(".csv", "_RC.csv"), 'wb') as csvEtiqueta:
        tagWriter = csv.writer(csvEtiqueta, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        tagWriter.writerow(['tag', 'conteudo', 'saida'])
        for resL in resultadoLinha:
            tagWriter.writerow(resL)

    print ("Fim")
