# -*- coding: utf-8 -*-
import pandas as pd
from sklearn.ensemble import AdaBoostClassifier, BaggingClassifier, ExtraTreesClassifier, \
                            GradientBoostingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.neural_network import MLPClassifier
from sklearn.svm import LinearSVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import BernoulliNB
from sklearn.tree import DecisionTreeClassifier

from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, confusion_matrix, classification_report, accuracy_score, f1_score
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import cross_validate
from sklearn.pipeline import Pipeline
import pickle
import os, sys, csv
from datetime import datetime  

def classificador(treino_tam, teste_tam, folds_tam, metodo, divisao, vec_tipo, etiqueta, caminho, caminho_motores):

    reload(sys)
    sys.setdefaultencoding('utf8')
    csv.field_size_limit(sys.maxint)

    # Criando a lista de resultados dos parâmetros 
    resultados_treinamento = []

    #Nesta etapa, diz o nome do arquivo que vai ser classificado
    listaDados = []
    for chunk in pd.read_csv(caminho + etiqueta, sep=',', chunksize=20000):
        listaDados.append(chunk)

    df_cont = pd.concat(listaDados, axis=0)
    del listaDados

    count_vect = CountVectorizer()
    X = df_cont.conteudo
    y = df_cont.saida
    print "Carregou a base"

    #Vê qual tipo de divisão da base o usuário solicitou
    if (divisao == 'percent_split'):
        X_treino, X_teste, y_treino, y_teste = train_test_split(X, y, train_size=treino_tam, test_size=teste_tam)
        # Verifica qual tipo de transformação o usuário escolheu
        if (vec_tipo == 'countvec'):
            vec_clf = Pipeline([('vectorizer', count_vect), ('clf', metodo)])

        if (vec_tipo == 'tdidf_transf'):
            tfidf_transformer = TfidfVectorizer()
            vec_clf = Pipeline([('vectorizer', tfidf_transformer), ('clf', metodo)])

        # Salva em disco o modelo treinado para fazer predições posteriormente na tela de "Teste/Validação"
        vec_clf.fit(X_treino, y_treino)
        pickle.dump(vec_clf, open(caminho_motores + "modelo" + str(metodo).split("(")[0] +'_@'+ etiqueta.replace('.csv','') +'.sav', 'wb'))

        print "Classificador treinado e salvo"

        predicao = vec_clf.predict(X_teste)
        accuracy_value = (accuracy_score(y_teste, predicao))
        precision_value = (recall_score(y_teste, predicao))
        recall_value = (precision_score(y_teste, predicao))
        f1_value = (f1_score(y_teste, predicao))
        #roc_value = (roc_auc_score(y_teste, predicao))
        cl_report = (classification_report(y_teste, predicao))
        conf_matrix = (confusion_matrix(y_teste, predicao))

        print ("Acurácia: %0.2f" % accuracy_value)
        resultados_treinamento.append(round(accuracy_value, 2))

        print ("Precision: %0.2f" % precision_value)
        resultados_treinamento.append(round(precision_value, 2))

        print ("Recall: %0.2f" % recall_value)
        resultados_treinamento.append(round(recall_value, 2))

        print ("F1: %0.2f" % f1_value)
        resultados_treinamento.append(round(f1_value, 2))

        # print ("ROC: %0.2f" % roc_value)
        # resultados_treinamento.append(round(roc_value, 2))

        print cl_report
        resultados_treinamento.append(cl_report)

        print conf_matrix
        resultados_treinamento.append(conf_matrix)

    if (divisao == 'cross_val'):
        scoring = ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro']

        if (vec_tipo == 'countvec'):
            vec_clf = Pipeline([('vectorizer', count_vect), ('clf', metodo)])
            scores = cross_validate(vec_clf, X, y, cv=folds_tam, scoring=scoring, return_train_score=False)

        if (vec_tipo == 'tdidf_transf'):
            tfidf_transformer = TfidfVectorizer()
            vec_clf = Pipeline([('vectorizer', tfidf_transformer), ('clf', metodo)])
            scores = cross_validate(vec_clf, X, y, cv=folds_tam, scoring=scoring, return_train_score=False)

            # Salva em disco o modelo treinado para fazer predições posteriormente na tela de "Teste/Validação"
        vec_clf.fit(X, y)

        pickle.dump(vec_clf, open(caminho_motores + "modelo" + str(metodo).split("(")[0] + '_@' + etiqueta.replace('.csv', '') + '.sav', 'wb'))

        accuracy_value = ((scores['test_accuracy']).mean(), (scores['test_accuracy']).std() * 2)
        precision_value = ((scores['test_precision_macro']).mean(), (scores['test_precision_macro']).std() * 2)
        recall_value = ((scores['test_recall_macro']).mean(), (scores['test_recall_macro']).std() * 2)
        f1_value = ((scores['test_f1_macro']).mean(), (scores['test_f1_macro']).std() * 2)
        roc_value = ((scores['test_roc_auc']).mean(), (scores['test_roc_auc']).std() * 2)

        # O resultado final, dá-se pela pontuação média das métricas com um intervalo de confiança de 95% da estimativa de pontuação
        #Reproduzir da mesma maneira do Framework
        print ("Acurácia: %0.2f (+/- %0.2f)" % accuracy_value)
        resultados_treinamento.append((round(accuracy_value[0], 2), "+/- " + str(round(accuracy_value[1], 2))))

        print ("Precision: %0.2f (+/- %0.2f)" % precision_value)
        resultados_treinamento.append((round(precision_value[0], 2), "+/- " + str(round(precision_value[1], 2))))

        print ("Recall: %0.2f (+/- %0.2f)" % recall_value)
        resultados_treinamento.append((round(recall_value[0], 2), "+/- " + str(round(recall_value[1], 2))))

        print ("F1: %0.2f (+/- %0.2f)" % f1_value)
        resultados_treinamento.append((round(f1_value[0], 2), "+/- " + str(round(f1_value[1], 2))))

        # print ("ROC: %0.2f (+/- %0.2f)" % roc_value)
        # resultados_treinamento.append((round(roc_value[0], 2), "+/- " + str(round(roc_value[1], 2))))

    # Armazenando o tamanho da lista
    tamanho_da_lista = len(resultados_treinamento)

    # A ordem da lista "resultados_treinamento" será sempre: [accuracy_value, precision_value, recall_value, f1_value, roc_value, *cl_report* e *matriz de confusão*]
    return resultados_treinamento, tamanho_da_lista, caminho_motores

#OPÇÕES

# Metodo:
    # Cada um dos métodos de ensemble vem no formato abaixo descrito, pois assim como os classificadores eles tem
    # confirações próprias, os métodos possíveis são:

    # adaboost = AdaBoostClassifier(base_estimator=None, n_estimators=50, learning_rate=1.0, algorithm=’SAMME.R’, random_state=None)
    # bagging = BaggingClassifier (base_estimator=None, n_estimators=10, max_samples=1.0, max_features=1.0, bootstrap=True, bootstrap_features=False, oob_score=False, random_state=None)
    # extratrees = ExtraTreesClassifier (n_estimators=10, criterion=’gini’, max_depth=None, bootstrap=False)
    # gradientboosting = GradientBoostingClassifier(loss=’deviance’, learning_rate=0.1, n_estimators=100, subsample=1.0, criterion=’friedman_mse’, max_depth=3)
    # randomforest = RandomForestClassifier(n_estimators=10, criterion=’gini’, max_depth=None)
    # voting = VotingClassifier(pool_classifiers, voting=’hard’)

    # ATENÇÃO, os valores passandos como configuração dos algoritmos acima são meramente ilustrativos, para saber
    # todos os valores possíveis e adicionar às opções do framework, ver a documentação da sklearn.

    # Dadas as variáveis acima, você deve passá-las adiante na função.

    #PADRÃO: voting

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

# Coloquei esse exemplo porque ele é o principal método e o que requer mais atenção. Observe que um de seus parâmetros
# trata-se de uma lista de algoritmos configurados. Voce vai receber isso do front end e passar nesse formato para o
# back end

# estimators = []
# model1 = KNeighborsClassifier()
# model2 = DecisionTreeClassifier()

# #PARA MODELOS PROBABILÍSTICOS, NO CASO DO ENSEMBLE, A MÉTRICA "PROBABILITY" TEM QUE SER TRUE.
# # ELA TEM QUE SER DECLARADA, POIS O DEFAULT DA BIBLIOTECA É FALSE.

# model3 = SVC(probability=True)

# estimators.append(('KNN', model1))
# estimators.append(('RandomForest', model2))
# estimators.append(('SVM', model3))

# voting = VotingClassifier(estimators, voting='soft')

# classificador(metodo=voting, divisao='cross_val', treino_tam=0.66, teste_tam=0.33, folds_tam=5, vec_tipo='tdidf_transf')