# -*- coding: utf-8 -*-
from deslib.des.probabilistic import Exponential
from deslib.des.probabilistic import DESKL
from deslib.des.des_knn import DESKNN
from deslib.des.probabilistic import Logarithmic
from deslib.des.probabilistic import MinimumDifference
from deslib.des.des_p import DESP
from deslib.des.knop import KNOP
from deslib.des.knora_e import KNORAE
from deslib.des.knora_u import KNORAU
from deslib.des.meta_des import METADES
from deslib.des.probabilistic import RRC

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer

#Classificadores
from sklearn.naive_bayes import BernoulliNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import Perceptron
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import FunctionTransformer

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.pipeline import FeatureUnion
import gc, dill, sys, csv
import numpy as np
import pandas as pd

from sklearn.metrics import precision_score, \
    recall_score, confusion_matrix, classification_report, \
    accuracy_score, f1_score

def classificador(algoritmodinamico, pool_classifiers, k, DFP, vec_tipo, etiqueta, caminho, caminho_motores):

    reload(sys)
    sys.setdefaultencoding('utf8')
    csv.field_size_limit(sys.maxint)

    rng = np.random.RandomState(42)

    # Criando a lista de resultados dos parâmetros 
    resultados_treinamento = []

    listaDados = []
    for chunk in pd.read_csv(caminho + etiqueta, sep=',', chunksize=20000):
        listaDados.append(chunk)

    df_cont = pd.concat(listaDados, axis=0)
    del listaDados
    print ("Carregou a base")

    tdidf_transf = TfidfVectorizer()
    countvec = CountVectorizer()

    if (vec_tipo == 'countvec'):
        vec_clf = Pipeline([('vectorizer', countvec),
                            ('to_dense', FunctionTransformer(lambda x: x.todense(), accept_sparse=True))])

    if (vec_tipo == 'tdidf_transf'):
        vec_clf = Pipeline([('vectorizer', tdidf_transf),
                            ('to_dense', FunctionTransformer(lambda x: x.todense(), accept_sparse=True))])


    X_train_counts = vec_clf.fit_transform(df_cont.conteudo)
    X = X_train_counts
    y = df_cont.saida

    # Dividir treinamento e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=rng)
    # Dividir fatia da seleção dinâmica
    X_train, X_dsel, y_train, y_dsel = train_test_split(X, y, test_size=0.5, random_state=rng)

    print ("Dividiu treinamento e teste")

    # Inicializar Classificadores
    conjunto = []
    for i in pool_classifiers:
        aux = i.fit(X_train, y_train)
        conjunto.append(aux)

    gc.collect()

    if (algoritmodinamico == "exponential"): algoritmoCallable = Exponential
    elif (algoritmodinamico == "deskl"): algoritmoCallable = DESKL
    elif (algoritmodinamico == "desknn"): algoritmoCallable = DESKNN
    elif (algoritmodinamico == "logarithmic"): algoritmoCallable = Logarithmic
    elif (algoritmodinamico == "minimumdifference"): algoritmoCallable = MinimumDifference
    elif (algoritmodinamico == "desp"): algoritmoCallable = DESP
    elif (algoritmodinamico == "knop"): algoritmoCallable = KNOP
    elif (algoritmodinamico == "knorae"): algoritmoCallable = KNORAE
    elif (algoritmodinamico == "knorau"): algoritmoCallable = KNORAU
    elif (algoritmodinamico == "metades"): algoritmoCallable = METADES
    elif (algoritmodinamico == "rrc"): algoritmoCallable = RRC


    des_model = algoritmoCallable(conjunto, k=k, DFP=DFP)
    modelo_clf = Pipeline([('clf', des_model)])
    modelo_clf.fit(X_dsel, y_dsel)

    pipeline = Pipeline([
        ('feats', FeatureUnion([
            ('countvec', vec_clf),
        ])),
        ('clf', modelo_clf)
    ])

    # Lembre que pela nova validação, o formato do nome de todo e qualquer motor tem que ser exatamente esse:
    # nomemodelo_nomeetiqueta.sav

    dill.dump(pipeline, open(caminho_motores + "modelo" + str(algoritmodinamico) +'_@'+ etiqueta.replace('.csv','') +'.sav', 'wb'))

    print "Classificador treinado e salvo"

    prediction = modelo_clf.predict(X_test)

    accuracy_value = (accuracy_score(y_test, prediction))
    precision_value = (precision_score(y_test, prediction))
    recall_value = (recall_score(y_test, prediction))
    f1_value = (f1_score(y_test, prediction))
    cl_report = classification_report(y_test, prediction)
    conf_matrix = confusion_matrix(y_test, prediction)

    print ("Acurácia: %0.2f" % accuracy_value)
    resultados_treinamento.append(round(accuracy_value, 2))
    print ("Precision: %0.2f" % precision_value)
    resultados_treinamento.append(round(precision_value, 2))
    print ("Recall: %0.2f" % recall_value)
    resultados_treinamento.append(round(recall_value, 2))
    print ("F1: %0.2f" % f1_value)
    resultados_treinamento.append(round(f1_value, 2))
    print cl_report
    resultados_treinamento.append(cl_report)
    print conf_matrix
    resultados_treinamento.append(conf_matrix)

    # Armazenando o tamanho da lista
    tamanho_da_lista = len(resultados_treinamento)

    print ("Fim")

    # A ordem da lista "resultados_treinamento" será sempre: [accuracy_value, precision_value, recall_value, f1_value, *cl_report* e *matriz de confusão*]
    return resultados_treinamento, tamanho_da_lista, caminho_motores

# DES-Exponential

#OPÇÕES

# pool_classifiers:
    # Conjunto de classificadores que vão entrar no pool do DES-RRC. Vou colocar um exemplo para você entender melhor.

    # O que é: O pool de classificadores treinados para o problema de classificação correspondente.
             # Cada classificador base deve suportar o método "predict".
             # Se "None", o conjunto de classificadores é um bagging classifier. Dúvidas sobre o bagging, olhar
             # os cometários do arquivo baggingexample que mandei anteriormente.

# k:
    #Qualquer inteiro a partir de 1. O Default é 7.

#DFP
    # False
    # True

    # Default: False

# O que é: Determina se o FIRE vai ser aplicado para este algoritmo (COLOQUE ISSO EM ALGUM LUGAR PARA O USUÁRIO SABER O QUE É).

# vec_tipo:
    # countvec
    # tdidf_transf

# algoritmodinamico:
    # exponential
    # deskl
    # desknn
    # logarithmic
    # minimumdifference
    # desp
    # knop
    # knorae
    # knorau
    # metades
    # rrc

# Atenção, tem que passar o algoritmodinamico exatamente como coloquei acima, em letra minúscula, pq faço uma comparação depois pra chamar o método da DESLIB.


# EXEMPLO COM O POOL DE CLASSIFICADORES, COM CASOS ESPECIAIS:

# if __name__ == "__main__":
#     estimators = []

#     model1 = KNeighborsClassifier(n_neighbors=5, metric='euclidean')
#     model2 = DecisionTreeClassifier(criterion='entropy', splitter ='best', max_depth =None)

#     # A calibração de probabilidade (CalibratedClassifierCV), é OBRIGATÓRIA para o LINEARSVC, ou seja, se o usuário escolhe o SVM,
#     # envolva o algoritmo com esta função, tal como o exemplo abaixo:
#     model3 = CalibratedClassifierCV(LinearSVC(penalty='l2', loss='squared_hinge', C=1.0))

#     # ATENÇÃO, A ÚNICA MÉTRICA PARA 'LOSS' SUPORTADA PELO ENSEMBLE DINÂMICO PARA O SGDClassifier É O 'modified_huber'.
#     # NÃO COLOQUE ESSA OPÇÃO PARA O USUÁRIO, PARA QUE ELE NÃO ESCOLHA UMA INCORRETA, VAMOS PASSAR ELA POR PADRÃO, TEM QUE
#     # SER DECLARADA, POIS O DEFAULT DA BIBLIOTECA É OUTRO.
#     model4 = SGDClassifier(loss='modified_huber', penalty ='l2', max_iter=1000)

#     # A calibração de probabilidade (CalibratedClassifierCV), é OBRIGATÓRIA para o PERCEPTRON, ou seja, se o usuário escolhe o PERCEPTRON,
#     # envolva o algoritmo com esta função, tal como o exemplo abaixo:
#     model5 = CalibratedClassifierCV(Perceptron(penalty='l2', alpha=0.0001))
#     model6 = BernoulliNB(alpha=1)
#     model7 = MultinomialNB(alpha=1, fit_prior=True)
#     model8 = RandomForestClassifier(n_estimators=10, criterion='gini', max_depth=None)
#     model9 = LogisticRegression(penalty='l2', solver ='liblinear', C=1.0)
#     model10 = MLPClassifier(hidden_layer_sizes=100, activation='relu', solver ='adam', learning_rate = 'constant', learning_rate_init=0.001)

#     #Lembrar que no SVC, o parâmetro 'probability' OBRIGATORIAMENTE tem que ser TRUE, os demais fica a critério do usuário.
#     model11 = SVC(probability=True, gamma='auto', kernel='rbf', C=1.0)

#     estimators.append(model1)
#     estimators.append(model2)
#     estimators.append(model3)
#     estimators.append(model4)
#     estimators.append(model5)
#     estimators.append(model6)
#     estimators.append(model7)
#     estimators.append(model8)
#     estimators.append(model9)
#     estimators.append(model10)
#     estimators.append(model11)

#     # VOCÊ PODE ACHAR ESTRANHO EU NÃO TER COLOCADO O PERCENT_SPLIT E CROSS_VALIDATION. A SELEÇÃO DINÂMICA EXIGE UMA DIVISÃO
#     # DIFERENCIADA, IRIAM SE FAZER NECERRÁRIAS MUITAS REGRAS DE NEGÓCIO NO CROSS_VAL DE AMBOS OS LADOS (MEU E SEU), O TEMPO ESTÁ APERTADO.
#     # VAMOS DEIXAR SÓ PERCENT-SPLIT POR PADRÃO EM ENSEMBLE DINÂMICO. NÃO EXIBA ESSA OPÇÃO AO USUÁRIO.

#     # Aqui você passa o nome do algoritmo dinâmico escolhido, conforme já orientado, tem que ser exatamente como passei nos exemplos de 'algoritmodinamico',
#     # ir ir no formato de string, como no exemplo abaixo.
#     algoritmodinamico = "desknn"

#     classificador(algoritmodinamico, pool_classifiers=estimators, k=9, DFP=True, vec_tipo='countvec')
