# -*- coding: utf-8 -*-
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, confusion_matrix, classification_report, accuracy_score, f1_score, roc_auc_score
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import cross_validate
from sklearn.pipeline import Pipeline
import pickle
import os, sys, csv
from datetime import datetime   

def classificador(max_depth, treino_tam, teste_tam, folds_tam, criterion, splitter, divisao, vec_tipo, etiqueta, caminho, caminho_motores):

    reload(sys)
    sys.setdefaultencoding('utf8')
    csv.field_size_limit(sys.maxint)

    # Criando a lista de resultados dos parâmetros 
    resultados_treinamento = []
    
    #Nesta etapa, diz o nome do arquivo que vai ser classificado
    listaDados = []
    for chunk in pd.read_csv(caminho + etiqueta, sep=',', chunksize=20000):
        listaDados.append(chunk)

    print(etiqueta)

    df_cont = pd.concat(listaDados, axis=0)
    del listaDados

    count_vect = CountVectorizer()
    X = df_cont.conteudo
    y = df_cont.saida
    print "Carregou a base"

    arvoredecisao = DecisionTreeClassifier(splitter=splitter, criterion=criterion, max_depth=max_depth)
    
    #Vê qual tipo de divisão da base o usuário solicitou
    if (divisao == 'percent_split'):
        X_treino, X_teste, y_treino, y_teste = train_test_split(X, y, train_size=treino_tam, test_size=teste_tam)

        # Verifica qual tipo de transformação o usuário escolheu
        if (vec_tipo == 'countvec'):
            vec_clf = Pipeline([('vectorizer', count_vect), ('clf', arvoredecisao)])

        if (vec_tipo == 'tdidf_transf'):
            tfidf_transformer = TfidfVectorizer()
            vec_clf = Pipeline([('vectorizer', tfidf_transformer), ('clf', arvoredecisao)])

        # Salva em disco o modelo treinado para fazer predições posteriormente na tela de "Teste/Validação"
        vec_clf.fit(X_treino, y_treino)
        pickle.dump(vec_clf, open(caminho_motores + 'decisionTree_@' + etiqueta.replace('.csv','') + '.sav', 'wb'))

        print "Classificador treinado"

        predicao = vec_clf.predict(X_teste)
        accuracy_value = (accuracy_score(y_teste, predicao))
        precision_value = (recall_score(y_teste, predicao))
        recall_value = (precision_score(y_teste, predicao))
        f1_value = (f1_score(y_teste, predicao))
        cl_report = (classification_report(y_teste, predicao))
        conf_matrix = (confusion_matrix(y_teste, predicao))

        print ("Acurácia: %0.2f" % accuracy_value)
        resultados_treinamento.insert(0, (round(accuracy_value, 2)))

        print ("Precision: %0.2f" % precision_value)
        resultados_treinamento.insert(1, (round(precision_value, 2)))

        print ("Recall: %0.2f" % recall_value)
        resultados_treinamento.insert(2, (round(recall_value, 2)))

        print ("F1: %0.2f" % f1_value)
        resultados_treinamento.insert(3, (round(f1_value, 2)))

        print cl_report
        resultados_treinamento.insert(4, (cl_report))

        print conf_matrix
        resultados_treinamento.insert(5, (conf_matrix))


    if (divisao == 'cross_val'):
        scoring = ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro']

        if (vec_tipo == 'countvec'):
            vec_clf = Pipeline([('vectorizer', count_vect), ('clf', arvoredecisao)])
            scores = cross_validate(vec_clf, X, y, cv=folds_tam, scoring=scoring, return_train_score=False)

        if (vec_tipo == 'tdidf_transf'):
            tfidf_transformer = TfidfVectorizer()
            vec_clf = Pipeline([('vectorizer', tfidf_transformer), ('clf', arvoredecisao)])
            scores = cross_validate(vec_clf, X, y, cv=folds_tam, scoring=scoring, return_train_score=False)

            # Salva em disco o modelo treinado para fazer predições posteriormente na tela de "Teste/Validação"
        vec_clf.fit(X, y)
        pickle.dump(vec_clf, open(caminho_motores + 'decisionTree_@' + etiqueta.replace('.csv', '') + '.sav', 'wb'))

        accuracy_value = ((scores['test_accuracy']).mean(), (scores['test_accuracy']).std() * 2)
        precision_value = ((scores['test_precision_macro']).mean(), (scores['test_precision_macro']).std() * 2)
        recall_value = ((scores['test_recall_macro']).mean(), (scores['test_recall_macro']).std() * 2)
        f1_value = ((scores['test_f1_macro']).mean(), (scores['test_f1_macro']).std() * 2)
        #roc_value = ((scores['test_roc_auc']).mean(), (scores['test_roc_auc']).std() * 2)

        # O resultado final se dá pela pontuação média das métricas com um intervalo de confiança de 95% da estimativa de pontuação
        #Reproduzir da mesma maneira do Framework
        print ("Acurácia: %0.2f (+/- %0.2f)" % accuracy_value)
        resultados_treinamento.insert(0, (round(accuracy_value[0], 2), "+/- " + str(round(accuracy_value[1], 2))))

        print ("Precision: %0.2f (+/- %0.2f)" % precision_value)
        resultados_treinamento.insert(1, (round(precision_value[0], 2), "+/- " + str(round(precision_value[1], 2))))

        print ("Recall: %0.2f (+/- %0.2f)" % recall_value)
        resultados_treinamento.insert(2, (round(recall_value[0], 2), "+/- " + str(round(recall_value[1], 2))))

        print ("F1: %0.2f (+/- %0.2f)" % f1_value)
        resultados_treinamento.insert(3, (round(f1_value[0], 2), "+/- " + str(round(f1_value[1], 2))))

    # Armazenando o tamanho da lista
    tamanho_da_lista = len(resultados_treinamento)

    # A ordem da lista "resultados_treinamento" será sempre: [accuracy_value, precision_value, recall_value, f1_value, roc_value, *cl_report* e *matriz de confusão*]
    return resultados_treinamento, tamanho_da_lista, caminho_motores

#OPÇÕES

# Criterion:
    # gini
    # entropy

    #PADRÃO: gini

# Splitter:
    # best
    # random

    #PADRÃO: best

# Max_depth:
    # Um INTEIRO qualquer ou None.

    # PADRÃO: None

# Divisão:
    # percent_split
    # cross_val

    #PADRÃO: percent_split

# Treino_tam:
    # Qualquer valor numérico, levando em consideração que trata-se de porcentagem e a soma de treino_tam + teste_tam deve ser igual a 1.

    #PADRÃO: 0.66

# Teste_tam:
    # Qualquer valor numérico, levando em consideração que trata-se de porcentagem e a soma de treino_tam + teste_tam deve ser igual a 1.

    #PADRÃO: 0.33

# Folds_tam:
    # Qualquer valor numérico INTEIRO

    #PADRÃO: 5

# Vec_tipo:
    # countvec
    # tdidf_transf

# OBS.1: Onde tem a palavra "PADRÃO" significa que se o usuário não informar nada, você deve adotar esse valores,
        #onde eu não coloquei "PADRÃO" é porque é de escolha obrigatória.

#classificador(criterion='gini', splitter ='best', max_depth =None, divisao='cross_val', treino_tam=0.66, teste_tam=0.33, folds_tam=5, vec_tipo='countvec')