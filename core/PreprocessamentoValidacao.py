# -*- coding: utf-8 -*-
import nltk
import csv, codecs
import pandas as pd
import sys
import re, os, gc
import pt_core_news_sm
from nltk.corpus import stopwords
import RemoverCaracteres as RC
import RC as redec
from nltk.tokenize import sent_tokenize
reload(sys)
sys.setdefaultencoding('utf8')
csv.field_size_limit(sys.maxint)

stok = nltk.data.load('tokenizers/punkt/portuguese.pickle')
nlp = pt_core_news_sm.load()
stops = set(stopwords.words("portuguese"))

final =[]
listaTokens = []

print"Arquivo Carregado"

#FUNÇÃO STEMMING
def stemming(frase):
    st = nltk.stem.RSLPStemmer()
    frase = frase.lower()
    tokens = nltk.word_tokenize(frase)
    final = [st.stem(tagged_word) for tagged_word in tokens]
    return " ".join(final)

#FUNÇÃO QUE REMOVE NÚMEROS
def remove_numeros(frase):
    dict = {":": "", "0": "",  "1": "", "2": "", "3": "", "4": "",  "5": "", "6": "", "7": "",  "8": "", "9": "", }
    regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], frase)

#FUNÇÃO QUE REMOVE ACENTUAÇÃO
def remove_acentos(frase):
    dict = {":": "", ".": "", ",": "",  ";": "", "?": "", "!": "", "'": "",  ":": "", "$": "", "-": "",  "_": ""}
    regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], frase)

#FUNÇÃO DE LEMATIZAÇÃO
def lematizacao(frase):
    frase = frase.lower()
    frase = nlp(unicode(frase))
    lemmatized = list()

    for word in frase:
        lemma = word.lemma_.strip()
        if lemma:
            l2 = lemma.encode('ascii', 'ignore')
            lemmatized.append(l2)
    return " ".join(lemmatized)

#FUNÇÃO QUE REMOVE STOPWORDS
def remove_stopwords(frase):
    frase = frase.lower()
    stopwords = set(nltk.corpus.stopwords.words('portuguese'))
    palavras = [i for i in frase.split() if not i in stopwords]
    return (" ".join(palavras))

#FUNÇÃO DE TOKENIZAÇÃO
def tokenizacao(palavras):
    texto = []
    for tok in palavras:
        texto.append(nltk.word_tokenize(tok))
    return texto

#FUNÇÃO DE DIVIDIR AS SETENÇAS
def sentencas(frase):
    texto = []
    texto.append(sent_tokenize(frase))
    return texto

#CHAMA AS FUNÇÕES ESCOLHIDAS PELO USUÁRIO
def chamarFuncoes(URL, stemmingfunc, remove_stopwordsfunc, remove_numerosfunc, lematizacaofunc, tokenizacaofunc, redescomplesxasfunc, removeacentofunc):

    # CARREGA ARQUIVO QUE VAI SER PREPROCESSADO

    listaDados = []
    for chunk in pd.read_csv(URL, sep=',', chunksize=20000, encoding='latin-1'):
        listaDados.append(chunk)

    df = pd.concat(listaDados, axis=0)
    del listaDados


    lemm = []
    nostop = []
    nonum = []
    tokn = []
    stm = []
    sent = []
    rmvacent = []

    if (remove_numerosfunc == True):
        for s in df['conteudo']:
            nonum.append(remove_numeros(s))
        df['conteudo'] = nonum
        print ("Fim da remoção de números")

    if (remove_stopwordsfunc == True):
        for s in df['conteudo']:
            nostop.append(remove_stopwords(s))
        df['conteudo'] = nostop
        print ("Fim da remoção de stop words")

    if (lematizacaofunc == True):
        df['textolimpo'] = df['conteudo'].apply(lematizacao)
        for s in df['textolimpo']:
            lemm.append(s)
        df['conteudo'] = lemm
        print ("Fim da lemmatização")

    if (stemmingfunc == True):
        df['textostm'] = df['conteudo'].apply(stemming)
        for s in df['textostm']:
            stm.append(s)
        df['conteudo'] = stm
        print ("Fim do Stemming")

    #A tokenização de redes complexas é especial, por isso ela vai ser feita nos seus próprios moldes, automaticamente,
    # caso o usuário esteja utilizando redes complexas.
    # A remoção de pontuação só deve ser feita se redes complexas não for utilizada, pois ela faz uso da
    # pontuação para dividir as setenças.

    if (redescomplesxasfunc == True):

        for st in df['conteudo']:
            sent.append(sent_tokenize(st))
        df['conteudo'] = sent

        montaArray = []
        for i, row in df.iterrows():
            montaTok = []
            for tok in row['conteudo']:
                montaTok.append(nltk.word_tokenize(tok))
            montaArray.append(montaTok)
        df['conteudo'] = montaArray

        print ("Fim da divisão de sentenças")

    else:
        if (removeacentofunc == True):
            for s in df['conteudo']:
                rmvacent.append(remove_acentos(s))
            df['conteudo'] = rmvacent
            print ("Fim da remoção de acentos")

        if (tokenizacaofunc == True):
            for tok in df['conteudo']:
                tokn.append(nltk.word_tokenize(tok))
            df['conteudo'] = tokn
            print ("Fim da tokenização")


    print ("Texto Pré-Processado\n Iniciando a montagem do conteúdo")

    #MONTANDO O CONTEÚDO DO NOVO ARQUIVO
    resultadoLinha = []

    for i, row in df.iterrows():
        montaLinha = []
        montaLinha.insert(0, row['tag'])
        montaLinha.insert(1, row["conteudo"])
        montaLinha.insert(2, row["saida"])

        resultadoLinha.append(montaLinha)

    #CRIA CSV PRE-PROCESSADO
    print("Criando CSV")

    with open('ArquivoPreProcessado.csv', 'wb') as csvEtiqueta:
        tagWriter = csv.writer(csvEtiqueta, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        tagWriter.writerow(['tag', 'conteudo', 'saida'])
        for resL in resultadoLinha:
            tagWriter.writerow(resL)

    arquivoFinalCSV = ""

    #Depois dos pre-processamentos clássicos, se aplica a rede complexa por cima desse arquivo e o arquivo final é gerado.
    if (redescomplesxasfunc == True):
        redec.redecomplexaexc('ArquivoPreProcessado.csv')
        gc.collect()
        arquivo = open('ArquivoPreProcessado.csv', 'r')
        arquivo.close()
        os.remove('ArquivoPreProcessado.csv')
        arquivoFinalCSV = "ArquivoPreProcessado_RC.csv"
    else:
        arquivoFinalCSV = "ArquivoPreProcessado.csv"
    
    print ("Fim do Pré-Processamento")

    return arquivoFinalCSV
