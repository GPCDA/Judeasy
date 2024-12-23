# coding: utf-8

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
import io, sys, socket
from django.http import FileResponse
from reportlab.pdfgen import canvas
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.template import loader
from basedados.models import BaseDados
# from .models import Technics
# from .forms import DocumentForm, InfoBases
from . import Import, ImportValidacao
from . import FilesFunctions as FF
from . import PreprocessamentoNovo as PP_NEW
from . import PreprocessamentoValidacao as PP_VALIDACAO
from . import arvoredecisaoclassifier, bernoulliclassifier, ensembleclassicoclassifier, ensembledinamicoclassifier, \
    knnclassifier, linearsvm, mlpclassifier, multinomialnbclassifier, randomforestclassifier, \
    regressaologisticaclassifier, sgd_classifier, svmclassifier
import pandas as pd
from sklearn.ensemble import AdaBoostClassifier, BaggingClassifier, ExtraTreesClassifier, GradientBoostingClassifier, \
    RandomForestClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.linear_model import SGDClassifier, Perceptron, LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.neural_network import MLPClassifier
from sklearn.svm import LinearSVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import BernoulliNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.calibration import CalibratedClassifierCV
import os, traceback
import shutil
from datetime import datetime
import webbrowser

pastaArquivos = os.path.abspath(".")+"/arquivos/"

def index(request):
    try:
        return render(request, "index.html")
    except:
        erromessage = {
            'message': "Erro inesperado: " + str(sys.exc_info()[0]),
        }
        return HttpResponse(render(request, "index.html", erromessage))
        raise


def database(request):
    try:
        bases = BaseDados.objects.all()
        lista_arquivos_txt = []

        context = {
            'bases': bases,
        }

        if request.is_ajax() and request.method == 'POST':
            def process(f):
                with open(pastaArquivos+'media/' + f.name, 'wb+') as destination:
                    for count, chunk in enumerate(f.chunks()):
                        destination.write(chunk)
                        lista_arquivos_txt.append(f.name)

            # FF.apagarArquivosTxt(arquivos)

            for count, x in enumerate(request.FILES.getlist("files")):
                # O padrão é que o nome do arquivo .txt, na posição, seja "TRTF"
                if ("Revisado" in x.name or "Verificado" in x.name) and (x.name.split('_')[3].upper() == 'TRTF'):
                    process(x)

            return HttpResponse('')

        return render(request, "database.html", context)

    except (MemoryError):
        erromessage = {
            'message': "O servidor não suporta este processamento. Tente utilizar uma base de dados menor.",
        }
        return HttpResponse(render(request, "database.html", erromessage))

    except IOError as (errno, strerror):
        erromessage = {
            'message': "I/O error({0}): {1}".format(errno, strerror),
        }
        return HttpResponse(render(request, "database.html", erromessage))

    except ValueError:
        erromessage = {
            'message': "Os valores recebidos não correspondem ao esperado pelo sistema.",
        }
        return HttpResponse(render(request, "database.html", erromessage))

    except:
        erromessage = {
            'message': "Erro inesperado: "+str(sys.exc_info()[0]),
        }
        return HttpResponse(render(request, "database.html", erromessage))
        raise

def transformarBase(request):
    try:
        bases = BaseDados.objects.all()
        if request.is_ajax():
            nome_base_digitado = request.POST.get('nome_base_digitado')
            dontCare, listaEtiquetasRemovidas = Import.transformarBase(nome_base_digitado, 'database')

            context = {
                'bases': bases,
                'listaEtiquetasRemovidas': listaEtiquetasRemovidas
            }

            return HttpResponse(render(request, "database.html", context))

    except (MemoryError):
        erromessage = {
            'message': "O servidor não suporta este processamento. Tente carregar uma menor quantidade de arquivos.",
        }
        return HttpResponse(render(request, "database.html", erromessage))

    except IOError as (errno, strerror):
        erromessage = {
            'message': "I/O error({0}): {1}".format(errno, strerror),
        }
        return HttpResponse(render(request, "database.html", erromessage))

    except ValueError:
        erromessage = {
            'message': "Os valores recebidos não correspondem ao esperado pelo sistema.",
        }
        return HttpResponse(render(request, "database.html", erromessage))

    except:
        erromessage = {
            'message': "Erro inesperado: " + str(sys.exc_info()[0]),
        }
        return HttpResponse(render(request, "database.html", erromessage))
        raise


def excluirBase(request):

    try:
        bases = BaseDados.objects.all()
        context = {
            'bases': bases,
        }
        if request.is_ajax():
            nome_da_base = request.POST.get('nome_da_base')
            inicio = request.POST.get('inicio')
            fim = request.POST.get('fim')
            FF.apagarBase(nome_da_base, inicio, fim)

            return HttpResponse(render(request, "database.html", context))

    except IOError as (errno, strerror):
        erromessage = {
            'message': "I/O error({0}): {1}".format(errno, strerror),
        }
        return HttpResponse(render(request, "database.html", erromessage))

    except:
        erromessage = {
            'message': "Erro inesperado: " + str(sys.exc_info()[0]),
        }
        return HttpResponse(render(request, "database.html", erromessage))
        raise


def buscarBasesTreinadas(request):

    try:
        if request.is_ajax():
            # TROCAR ESTE DIRETÓRIO PELO DA KURIER (Aqui estão armazenadas as informações das bases que já foram treinadas)
            pasta = pastaArquivos+'historico'

            info_bases_treinadas = FF.listarInfoBasesTreinadas(pasta)

            context = {
                'info_bases_treinadas': info_bases_treinadas
            }

            return HttpResponse(render(request, "modal_historico.html", context))


    except IOError as (errno, strerror):
        erromessage = {
            'message': "I/O error({0}): {1}".format(errno, strerror),
        }
        return HttpResponse(render(request, "modal_historico.html", erromessage))

    except ValueError:
        erromessage = {
            'message': "Os valores recebidos não correspondem ao esperado pelo sistema.",
        }
        return HttpResponse(render(request, "modal_historico.html", erromessage))

    except:
        erromessage = {
            'message': "Erro inesperado: " + str(sys.exc_info()[0]),
        }
        return HttpResponse(render(request, "modal_historico.html", erromessage))
        raise


def pp(request):
    try:

        return render(request, "pre_processamento.html")

    except IOError as (errno, strerror):
        erromessage = {
            'message': "I/O error({0}): {1}".format(errno, strerror),
        }
        return HttpResponse(render(request, "pre_processamento.html", erromessage))

    except ValueError:
        erromessage = {
            'message': "Os valores recebidos não correspondem ao esperado pelo sistema.",
        }
        return HttpResponse(render(request, "pre_processamento.html", erromessage))

    except:
        erromessage = {
            'message': "Erro inesperado: "+str(sys.exc_info()[0]),
        }
        return HttpResponse(render(request, "pre_processamento.html", erromessage))
        raise

# View para abrir o arquivo .txt dos resultados da base treinada escolhida
def abrirTxtResultados(request):

    try:
        if request.method == 'POST':
            # TROCAR ESTE DIRETÓRIO PELO DA KURIER (Aqui estão armazenadas as informações das bases que já foram treinadas)
            pasta = pastaArquivos+'historico/'

            new = 2

            nome_arquivo_txt = request.POST.get('nome_arquivo_txt')
            url = pasta + nome_arquivo_txt

            # webbrowser.open(url, new=new)

            os.startfile(url)

        return HttpResponse()

    except IOError as (errno, strerror):
        erromessage = {
            'message': "I/O error({0}): {1}".format(errno, strerror),
        }
        return HttpResponse(render(request, "historico.html", erromessage))

    except ValueError:
        erromessage = {
            'message': "Os valores recebidos não correspondem ao esperado pelo sistema.",
        }
        return HttpResponse(render(request, "historico.html", erromessage))

    except:
        erromessage = {
            'message': "Erro inesperado: "+str(sys.exc_info()[0]),
        }
        return HttpResponse(render(request, "historico.html", erromessage))
        raise

def treinamento(request):

    try:
        if request.method == 'POST':
            nome_da_base = request.POST.get('nome_da_base')
            periodo = request.POST.get('periodo')
            etiquetas_escolhidas_global = request.POST.get('etiquetas_escolhidas_global')

            inicio = periodo.split('-')[0].replace(" ", "")
            fim = periodo.split('-')[1].replace(" ", "")
            periodo = periodo.replace('/', '').replace(' - ', '_')

            # SE O USUÁRIO ESCOLHER PRÉ-PROCESSAMENTO, TUDO ABAIXO É FEITO
            if etiquetas_escolhidas_global != None:
                lematizacao = request.POST.get('lematizacao').capitalize()
                redesComplexas = request.POST.get('redesComplexas').capitalize()
                removePontuacao = request.POST.get('removePontuacao').capitalize()
                removeNumeros = request.POST.get('removeNumeros').capitalize()
                stopWords = request.POST.get('stopWords').capitalize()
                stemming = request.POST.get('stemming').capitalize()
                tokenizer = request.POST.get('tokenizer').capitalize()

                etiquetas_escolhidas_global = etiquetas_escolhidas_global.replace('Etiquetas escolhidas: ', '')
                etiquetas_pre_processadas = etiquetas_escolhidas_global.replace(',', '/')
                etiquetas_escolhidas_global = etiquetas_escolhidas_global.split(',')

                # Criando lista que armazena as técnicas utilizadas no pré-processamento e coloca essa informação no banco de dados
                tecnicas_pre_processamento = ""

                if (lematizacao == "True"):
                    tecnicas_pre_processamento += "lematizacao,"
                print("lematizacao = " + lematizacao)

                if (redesComplexas == "True"):
                    tecnicas_pre_processamento += "redesComplexas,"
                print("redesComplexas = " + redesComplexas)

                if (removePontuacao == "True"):
                    tecnicas_pre_processamento += "removePontuacao,"
                print("removePontuacao = " + removePontuacao)

                if (removeNumeros == "True"):
                    tecnicas_pre_processamento += "removeNumeros,"
                print("removeNumeros = " + removeNumeros)

                if (stopWords == "True"):
                    tecnicas_pre_processamento += "stopWords,"
                print("stopWords = " + stopWords)

                if (stemming == "True"):
                    tecnicas_pre_processamento += "stemming,"
                print("stemming = " + stemming)

                if (tokenizer == "True"):
                    tecnicas_pre_processamento += "tokenizer"
                print("tokenizer = " + tokenizer)

                # CRIANDO A PASTA DAS ETIQUETAS PRÉ-PROCESSADAS
                # TROCAR ESTE DIRETÓRIO PELO DA KURIER
                pasta = pastaArquivos+'bases/'
                pasta += nome_da_base + '_' + periodo + "/"
                pasta += "PRE-PROCESSADO"
                print(pasta)

                if os.path.exists(pasta):
                    shutil.rmtree(pasta)
                    print('Pasta existente está sendo apagada (Base já pré-processada será sobreescrita pela atual)')

                os.mkdir(pasta)
                # INSERINDO ETIQUETAS PRÉ-PROCESSADAS NA BASE DE DADOS
                FF.etiquetasPreProcessadas(etiquetas_pre_processadas, nome_da_base, inicio, fim)
                # MUDANDO O STATUS DA BASE PARA "PRÉ-PROCESSADA = SIM"
                FF.alterarDados(nome_da_base, inicio, fim)
                # INSERINDO TÉCNICAS UTILZIADAS NO PRÉ-PROCESSAMENTO NA BASE DE DADOS
                FF.tecnicasDePP(tecnicas_pre_processamento, nome_da_base, inicio, fim)

                # PARA CADA ETIQUETA ESCOLHIDA NA TELA DATABASE, APLICAR AS TÉCNICAS ESCOLHIDAS
                for etiqueta in etiquetas_escolhidas_global:
                    etiqueta = etiqueta.replace(' ', '').upper().strip()
                    PP_NEW.chamarFuncoes(nome_da_base=nome_da_base, periodo=periodo, etiqueta=etiqueta,
                                         database_ou_validacao='database', redescomplesxasfunc=redesComplexas,
                                         removepontfunc=removePontuacao, stemmingfunc=stemming,
                                         remove_stopwordsfunc=stopWords, remove_numerosfunc=removeNumeros,
                                         lematizacaofunc=lematizacao, tokenizacaofunc=tokenizer)

            # SE O USUÁRIO ESCOLHER TREINAMENTO DIRETO, A PARTIR DE UMA BASE JÁ PRÉ-PROCESSADA, AS ETIQUETAS TERÃO DE SER PEGAS DA BASE DE DADOS
            else:
                etiquetas_pp_pasta = FF.pegarEtiquetasPP(nome_da_base, inicio, fim)
                etiquetas_escolhidas_global = etiquetas_pp_pasta[0][0]
                etiquetas_escolhidas_global = etiquetas_escolhidas_global.split('/')
                # print(etiquetas_escolhidas_global)

            context = {
                'etiquetas_escolhidas_global': etiquetas_escolhidas_global,
            }

            return HttpResponse(render(request, "treinamento.html", context))
        else:
            return render(request, "treinamento.html")

    except (MemoryError):
        erromessage = {
            'message': "O servidor não suporta este processamento. Tente utilizar uma base de dados menor.",
        }
        return HttpResponse(render(request, "treinamento.html", erromessage))

    except IOError as (errno, strerror):
        erromessage = {
            'message': "I/O error({0}): {1}".format(errno, strerror),
        }
        return HttpResponse(render(request, "treinamento.html", erromessage))

    except ValueError:
        erromessage = {
            'message': "Os valores recebidos não correspondem ao esperado pelo sistema.",
        }
        return HttpResponse(render(request, "treinamento.html", erromessage))

    except:
        erromessage = {
            'message': "Erro inesperado: "+str(sys.exc_info()[0]),
        }
        return HttpResponse(render(request, "treinamento.html", erromessage))
        raise

def ensembleDinamico(request):
    try:
        if request.method == 'POST':

            nome_da_base = request.POST.get('nome_da_base')
            periodo = request.POST.get('periodo')
            etiquetas_escolhidas_global = request.POST.get('etiquetas_escolhidas_global')
            lista_de_parametros = request.POST.get('lista_de_parametros')
            classificador = request.POST.get('classificador')
            dicionario_classificadores_ensemble = request.POST.get('dicionario_classificadores_ensemble')

            dicionario_classificadores_ensemble = dicionario_classificadores_ensemble.replace("[", "").replace("]", "")
            dicionario_classificadores_ensemble = dicionario_classificadores_ensemble.split('",')
            print(dicionario_classificadores_ensemble)

            periodo_pasta = periodo.replace('/', '').replace(' - ', '_')

            arquivar_parametros = lista_de_parametros

            lista_de_parametros = lista_de_parametros.split(',')

            print(lista_de_parametros)

            # Pasta para saber onde está o motor de inferência, na próxima tela "Validação"
            pasta_motores = ""

            # Criando a lista de parâmetros que serão passados para o ensemble dinâmico
            parametros_finais = []

            # Tratando a lista de parâmetros
            for cont, parametro in enumerate(lista_de_parametros):
                parametros_finais.append(lista_de_parametros[cont].split("=")[1])

            # Criando o dicionário que irá conter o par: chave (etiqueta) e valor (uma lista com os parâmetros de resultados da etiqueta)
            par_etiqueta_resultados = {}

            # Criando a variável que vai armazenar a quantidade de itens em cada lista do dicionário, para saber se "divisao == 'cross_val'"
            # ou se "divisao == 'percent_split'"
            tamanho_da_lista = 0;

            # TROCAR ESTE DIRETÓRIO PELO DA KURIER
            pasta = pastaArquivos+'bases/'

            caminho_motores = pasta + nome_da_base + '_' + periodo_pasta + "/Motores de Inferencia"
            pasta += nome_da_base + '_' + periodo_pasta + "/PRE-PROCESSADO"
            caminho = pasta + "/"
            etiquetas = os.listdir(pasta)

            # Se a pasta de motores de inferência ainda não existir, nesse momento ela é criada
            if not os.path.exists(caminho_motores):
                os.mkdir(caminho_motores)

            # TROCAR ESTE DIRETÓRIO PELO DA KURIER
            # Este é o caminho do histórico de todas as bases já treinadas, ou seja, onde ficarão os motores de inferência disponíveis
            caminho_historico_bases_treinadas = pastaArquivos+'historico'

            # Se a pasta de histórico dos motores ainda não existir, nesse momento ela é criada
            if not os.path.exists(caminho_historico_bases_treinadas):
                os.mkdir(caminho_historico_bases_treinadas)

            caminho_historico_bases_treinadas += "/"

            # Se a pasta de histórico dos motores ainda não existir, nesse momento ela é criada
            if not os.path.exists(caminho_historico_bases_treinadas):
                os.mkdir(caminho_historico_bases_treinadas)

            caminho_historico_bases_treinadas += "/"

            caminho_motores += "/Ensemble Dinâmico"

            # Se a pasta dos motores de Árvore de decisão ainda não existir, nesse momento ela é criada
            if not os.path.exists(caminho_motores):
                os.mkdir(caminho_motores)

            # Pegando a data e hora atual de Recife, para ser o nome da subpasta dentro da pasta do classificador atual
            data_e_hora_atuais = datetime.now()
            data_e_hora_em_texto = data_e_hora_atuais.strftime('%d-%m-%Y_%H;%M;%S')

            # Determinando caminho da sub_pasta do motor em questão
            caminho_motores += "/" + data_e_hora_em_texto

            # Se a pasta desse sub_motor de Árvore de decisão ainda não existir, nesse momento ela é criada
            if not os.path.exists(caminho_motores):
                os.mkdir(caminho_motores)

            # Determinando caminho final
            caminho_motores += "/"
            # Criando o arquivo txt que vai salvar os parâmetros utilizados no treinamento
            arquivoParametros = open(caminho_motores + "Parâmetros.txt", "w")
            arquivoParametros.writelines(arquivar_parametros)
            arquivoParametros.close()

            dictParamsAlgoritmos = {}
            estimators = []

            # Tratando a lista que contém os algoritmos e seus parâmetros (inserindo num dicionário)
            for item in dicionario_classificadores_ensemble:
                algoritmo = item.split(":")[0].replace('"', '')
                print(algoritmo)
                listaDeParams = item.split(": ")[1].replace('"', '').split(",")
                print(listaDeParams)
                dictParamsAlgoritmos[algoritmo] = listaDeParams

            # Tratando o dicionário que contem os algoritmos escolhidos e seus respectivos parâmetros
            for algoritmo, listaParams in dictParamsAlgoritmos.items():

                for cont, param in enumerate(listaParams):
                    listaParams[cont] = param.split("= ")[1]

                if algoritmo == "DecisionTree":
                    if (listaParams[0] == "None"):
                        listaParams[0] = None
                    else:
                        listaParams[0] = int(listaParams[0])

                    model1 = DecisionTreeClassifier(max_depth=listaParams[0], criterion=str(listaParams[1]),
                                                    splitter=str(listaParams[2]))
                    estimators.append(model1)

                elif algoritmo == "Bernoulli":
                    model2 = BernoulliNB(alpha=float(listaParams[0]))
                    estimators.append(model2)

                elif algoritmo == "KNN":
                    model3 = KNeighborsClassifier(n_neighbors=int(listaParams[0]), metric=str(listaParams[1]))
                    estimators.append(model3)

                elif algoritmo == "LinearSVM":
                    model4 = CalibratedClassifierCV(
                        LinearSVC(C=float(listaParams[0]), penalty=str(listaParams[1]), loss=str(listaParams[2])))
                    estimators.append(model4)

                elif algoritmo == "MultilayerPerceptron":
                    model5 = MLPClassifier(hidden_layer_sizes=int(listaParams[0]),
                                           learning_rate_init=float(listaParams[1]), activation=str(listaParams[2]),
                                           solver=str(listaParams[3]),
                                           learning_rate=str(listaParams[4]))
                    estimators.append(model5)

                elif algoritmo == "MultinomialNB":
                    if listaParams[1] == "True":
                        listaParams[1] = True
                    else:
                        listaParams[1] = False

                    model6 = MultinomialNB(alpha=float(listaParams[0]), fit_prior=listaParams[1])
                    estimators.append(model6)

                elif algoritmo == "RandomForest":
                    if listaParams[1] == "None":
                        listaParams[1] = None
                    else:
                        listaParams[1] = int(float(listaParams[1]))

                    model7 = RandomForestClassifier(n_estimators=int(listaParams[0]), max_depth=listaParams[1],
                                                    criterion=str(listaParams[2]))
                    estimators.append(model7)

                elif algoritmo == "LogisticRegression":
                    model8 = LogisticRegression(C=float(listaParams[0]), penalty=str(listaParams[1]),
                                                solver=str(listaParams[2]))
                    estimators.append(model8)

                elif algoritmo == "SGD":
                    model9 = SGDClassifier(max_iter=int(listaParams[0]), loss='modified_huber',
                                           penalty=str(listaParams[2]))
                    estimators.append(model9)

                elif algoritmo == "SVM":
                    if (listaParams[0] == "auto"):
                        listaParams[0] = str(listaParams[0])
                    else:
                        listaParams[0] = float(listaParams[0])

                    model10 = SVC(probability=True, gamma=listaParams[0], C=float(listaParams[1]),
                                  kernel=str(listaParams[2]))
                    estimators.append(model10)

                elif algoritmo == "Perceptron":
                    model11 = CalibratedClassifierCV(
                        Perceptron(alpha=float(listaParams[0]), penalty=str(listaParams[1])))
                    estimators.append(model11)

            if parametros_finais[2] == "false":
                parametros_finais[2] = False
            else:
                parametros_finais[2] = True

            for etiqueta in etiquetas:
                resultados_treinamento, tamanho_da_lista, pasta_motores = ensembledinamicoclassifier.classificador(
                    pool_classifiers=estimators, k=int(parametros_finais[0]),
                    algoritmodinamico=str(parametros_finais[1]), DFP=parametros_finais[2],
                    vec_tipo=str(parametros_finais[3]), etiqueta=etiqueta, caminho=caminho,
                    caminho_motores=caminho_motores)

                if (len(resultados_treinamento) > 4):
                    resultados_treinamento[5] = str(resultados_treinamento[5]).replace(' [', '\n[')
                par_etiqueta_resultados[etiqueta.replace('.csv', '')] = resultados_treinamento

            dataTreino = data_e_hora_em_texto.split("_")[0]
            inicioTreino = data_e_hora_em_texto.split("_")[1]

            arquivos_no_historico = os.listdir(caminho_historico_bases_treinadas)

            cont = 1

            while True:
                if not str(cont) + ".txt" in arquivos_no_historico:
                    nome_do_motor = str(cont)
                    break
                else:
                    cont += 1

            # Criando o arquivo txt que vai salvar as informações (na pasta de de histórico) de todos os treinamentos feitos
            with open(caminho_historico_bases_treinadas + nome_do_motor + ".txt", "w") as nomeMotor:
                nomeMotor.write("Caminho do motor = " + pasta_motores + "\n")
                nomeMotor.write("Nome da base = " + nome_da_base + "\n")
                nomeMotor.write("Período da base = " + periodo + "\n")
                nomeMotor.write("Classificador = " + classificador + "\n")
                nomeMotor.write("Data do treino = " + dataTreino.replace("-", "/") + "\n")
                nomeMotor.write("Horário do treino = " + inicioTreino.replace(";", ":") + "\n\n")
                nomeMotor.write("Algoritmo = " + str(parametros_finais[1]) + "\n")
                nomeMotor.write("Classificadores = " + str(dictParamsAlgoritmos) + "\n")

                for etiqueta, lista_resultados in par_etiqueta_resultados.items():
                    etiqueta = etiqueta.replace("_PRE-PROCESSADO", '')
                    nomeMotor.write(etiqueta + " \n\n")

                    for cont, resultado in enumerate(lista_resultados):

                        if cont < 5:
                            if cont == 0:
                                name_result = "Acurácia: "
                            elif cont == 1:
                                name_result = "Precisão: "
                            elif cont == 2:
                                name_result = "Recall: "
                            elif cont == 3:
                                name_result = "F1: "
                            nomeMotor.write(name_result + str(resultado) + "\n\n")

                        elif cont == (len(lista_resultados) - 1):
                            name_result = "Matriz de Confusão \n"
                            nomeMotor.write(name_result + (str(resultado) + "\n\n"))

                        else:
                            name_result = "Classification Report \n"
                            nomeMotor.write(name_result + (str(resultado) + "\n"))

            # Criando o arquivo txt que vai salvar os resultados do treinamento feito
            with open(caminho_motores + "Resultados.txt", "w") as salvarResultados:
                infoHistorico = open(caminho_historico_bases_treinadas + nome_do_motor + ".txt", "r")
                for line in infoHistorico.readlines():
                    salvarResultados.write(line)
                infoHistorico.close()

            context = {
                'par_etiqueta_resultados': par_etiqueta_resultados,
                'tamanho_da_lista': tamanho_da_lista,
                'nome_da_base': nome_da_base,
                'periodo': periodo,
                'classificador': classificador,
                'pasta_motores': pasta_motores,
                'algoritmo': parametros_finais[1],
            }

            return HttpResponse(render(request, "resultados.html", context))


        else:
            return render(request, "resultados.html")


    except (MemoryError):
        erromessage = {
            'message': "Os resultados não foram extraídos. O servidor não suporta este processamento. Tente utilizar uma base de dados menor.",
        }
        return HttpResponse(render(request, "resultados.html", erromessage))

    except IOError as (errno, strerror):
        erromessage = {
            'message': "I/O error({0}): {1}".format(errno, strerror),
        }
        return HttpResponse(render(request, "resultados.html", erromessage))

    except ValueError:
        erromessage = {
            'message': "Os valores recebidos não correspondem ao esperado pelo sistema.",
        }
        return HttpResponse(render(request, "resultados.html", erromessage))

    except:
        erromessage = {
            'message': "Erro inesperado: "+str(sys.exc_info()[0]),
        }
        return HttpResponse(render(request, "resultados.html", erromessage))
        raise


def ensembleClassico(request):

    try:
        if request.method == 'POST':

            nome_da_base = request.POST.get('nome_da_base')
            periodo = request.POST.get('periodo')
            etiquetas_escolhidas_global = request.POST.get('etiquetas_escolhidas_global')
            lista_de_parametros = request.POST.get('lista_de_parametros')
            classificador = request.POST.get('classificador')
            lista_parametros_ensemble = request.POST.get('lista_parametros_ensemble')
            myMethod = request.POST.get('myMethod')

            if (myMethod == "voting"):
                dicionario_classificadores_ensemble = request.POST.get('dicionario_classificadores_ensemble')
                dicionario_classificadores_ensemble = dicionario_classificadores_ensemble.replace("[", "").replace("]", "")
                dicionario_classificadores_ensemble = dicionario_classificadores_ensemble.split('",')
                print(dicionario_classificadores_ensemble)

            if (myMethod == "adaboost" or myMethod == "bagging"):
                lista_classificador_ensemble = request.POST.get('lista_classificador_ensemble')
                lista_classificador_ensemble = lista_classificador_ensemble.split(",")
                print(lista_classificador_ensemble)

            base_estimator = None

            periodo_pasta = periodo.replace('/', '').replace(' - ', '_')

            arquivar_parametros = lista_de_parametros

            lista_de_parametros = lista_de_parametros.split(',')

            lista_parametros_ensemble = lista_parametros_ensemble.split(',')

            data_e_hora_em_texto = ""

            print(lista_de_parametros)

            print(lista_parametros_ensemble)

            # Pasta para saber onde está o motor de inferência, na próxima tela "Validação"
            pasta_motores = ""

            # Criando a lista de parâmetros que serão passados para o método do classificador a ser escolhido
            parametros_finais = []

            # Criando a lista de parâmetros do ensemble que serão passados para o método do classificador a ser escolhido
            parametros_finais_ensemble = []

            # Criando a lista de parâmetros do algolritmo de ensemble cujo método seja "adaboost" or "bagging"
            parametros_finais_adaboost_or_bagging = []

            # Tratando a lista de parâmetros
            for cont, parametro in enumerate(lista_de_parametros):
                parametros_finais.append(lista_de_parametros[cont].split("=")[1])

            print(parametros_finais)

            # Criando o dicionário que irá conter o par: chave (etiqueta) e valor (uma lista com os parâmetros de resultados da etiqueta)
            par_etiqueta_resultados = {}

            # Criando a variável que vai armazenar a quantidade de itens em cada lista do dicionário, para saber se "divisao == 'cross_val'"
            # ou se "divisao == 'percent_split'"
            tamanho_da_lista = 0;

            # TROCAR ESTE DIRETÓRIO PELO DA KURIER
            pasta = pastaArquivos+'bases/'

            caminho_motores = pasta + nome_da_base + '_' + periodo_pasta + "/Motores de Inferencia"
            pasta += nome_da_base + '_' + periodo_pasta + "/PRE-PROCESSADO"
            caminho = pasta + "/"
            etiquetas = os.listdir(pasta)

            # Se a pasta de motores de inferência ainda não existir, nesse momento ela é criada
            if not os.path.exists(caminho_motores):
                os.mkdir(caminho_motores)

            # TROCAR ESTE DIRETÓRIO PELO DA KURIER
            # Este é o caminho do histórico de todas as bases já treinadas, ou seja, onde ficarão os motores de inferência disponíveis
            caminho_historico_bases_treinadas = pastaArquivos+'historico'

            # Se a pasta de histórico dos motores ainda não existir, nesse momento ela é criada
            if not os.path.exists(caminho_historico_bases_treinadas):
                os.mkdir(caminho_historico_bases_treinadas)

            caminho_historico_bases_treinadas += "/"

            caminho_motores += "/Ensemble Classico"

            # Se a pasta dos motores de Árvore de decisão ainda não existir, nesse momento ela é criada
            if not os.path.exists(caminho_motores):
                os.mkdir(caminho_motores)

            # Pegando a data e hora atual de Recife, para ser o nome da subpasta dentro da pasta do classificador atual
            data_e_hora_atuais = datetime.now()
            data_e_hora_em_texto = data_e_hora_atuais.strftime('%d-%m-%Y_%H;%M;%S')

            # Determinando caminho da sub_pasta do motor em questão
            caminho_motores += "/" + data_e_hora_em_texto

            # Se a pasta desse sub_motor de Árvore de decisão ainda não existir, nesse momento ela é criada
            if not os.path.exists(caminho_motores):
                os.mkdir(caminho_motores)

            # Determinando caminho final
            caminho_motores += "/"

            # Criando o arquivo txt que vai salvar os parâmetros utilizados no treinamento
            arquivoParametros = open(caminho_motores + "Parâmetros.txt", "w")
            arquivoParametros.writelines(arquivar_parametros)
            arquivoParametros.close()

            # Começando a verificação: O método do ensemble clássico é "voting", "adaboost", "bagging" ou outro?
            if (parametros_finais[3] == "adaboost"):
                myMethod = "Adaboost"

                # Tratando a lista de parâmetros do ensemble clássico
                for cont, parametro in enumerate(lista_parametros_ensemble):
                    parametros_finais_ensemble.append(lista_parametros_ensemble[cont].split("=")[1])

                # Tratando a lista de parâmetros do algoritmo escolhido para o ensemble clássico
                for cont, parametro in enumerate(lista_classificador_ensemble):
                    parametros_finais_adaboost_or_bagging.append(lista_classificador_ensemble[cont].split("= ")[1])

                # Verificando o algoritmo escolhido para o Adaboost

                if parametros_finais_ensemble[0] == "decisionTree":
                    base_estimator = "Decision Tree"

                    if (parametros_finais_adaboost_or_bagging[0] == "None"):
                        parametros_finais_adaboost_or_bagging[0] = None
                    else:
                        parametros_finais_adaboost_or_bagging[0] = int(parametros_finais_adaboost_or_bagging[0])

                    model = DecisionTreeClassifier(max_depth=parametros_finais_adaboost_or_bagging[0],
                                                   criterion=str(parametros_finais_adaboost_or_bagging[1]),
                                                   splitter=str(parametros_finais_adaboost_or_bagging[2]))


                elif parametros_finais_ensemble[0] == "bernoulli":
                    base_estimator = "Bernoulli"

                    model = BernoulliNB(alpha=float(parametros_finais_adaboost_or_bagging[0]))


                elif parametros_finais_ensemble[0] == "knn":
                    base_estimator = "K-Nearest Neighbors"

                    model = KNeighborsClassifier(n_neighbors=int(parametros_finais_adaboost_or_bagging[0]),
                                                 metric=str(parametros_finais_adaboost_or_bagging[1]))


                elif parametros_finais_ensemble[0] == "linearSVM":
                    base_estimator = "Linear Support Vector Machine"

                    model = LinearSVC(C=float(parametros_finais_adaboost_or_bagging[0]),
                                      penalty=str(parametros_finais_adaboost_or_bagging[1]),
                                      loss=str(parametros_finais_adaboost_or_bagging[2]))


                elif parametros_finais_ensemble[0] == "multilayerPerceptron":
                    base_estimator = "Multilayer Perceptron"

                    model = MLPClassifier(hidden_layer_sizes=int(parametros_finais_adaboost_or_bagging[0]),
                                          learning_rate_init=float(parametros_finais_adaboost_or_bagging[1]),
                                          activation=str(parametros_finais_adaboost_or_bagging[2]),
                                          solver=str(parametros_finais_adaboost_or_bagging[3]),
                                          learning_rate=str(parametros_finais_adaboost_or_bagging[4]))


                elif parametros_finais_ensemble[0] == "multinomialNaiveBayes":
                    base_estimator = "Multinomial Naive Bayes"

                    if parametros_finais_adaboost_or_bagging[1] == "True":
                        parametros_finais_adaboost_or_bagging[1] = True
                    else:
                        parametros_finais_adaboost_or_bagging[1] = False

                    model = MultinomialNB(alpha=float(parametros_finais_adaboost_or_bagging[0]),
                                          fit_prior=parametros_finais_adaboost_or_bagging[1])


                elif parametros_finais_ensemble[0] == "randomForest":
                    base_estimator = "Random Forest"

                    if parametros_finais_adaboost_or_bagging[1] == "None":
                        parametros_finais_adaboost_or_bagging[1] = None
                    else:
                        parametros_finais_adaboost_or_bagging[1] = int(float(parametros_finais_adaboost_or_bagging[1]))

                    model = RandomForestClassifier(n_estimators=int(parametros_finais_adaboost_or_bagging[0]),
                                                   max_depth=parametros_finais_adaboost_or_bagging[1],
                                                   criterion=str(parametros_finais_adaboost_or_bagging[2]))


                elif parametros_finais_ensemble[0] == "logisticRegression":
                    base_estimator = "Logistic Regression"

                    model = LogisticRegression(C=float(parametros_finais_adaboost_or_bagging[0]),
                                               penalty=str(parametros_finais_adaboost_or_bagging[1]),
                                               solver=str(parametros_finais_adaboost_or_bagging[2]))


                elif parametros_finais_ensemble[0] == "sgd":
                    base_estimator = "Gradient Descent SGD"

                    model = SGDClassifier(max_iter=int(parametros_finais_adaboost_or_bagging[0]),
                                          loss=str(parametros_finais_adaboost_or_bagging[1]),
                                          penalty=str(parametros_finais_adaboost_or_bagging[2]))


                elif parametros_finais_ensemble[0] == "supportVectorMachine":
                    base_estimator = "Support Vector Machine"

                    if (parametros_finais_adaboost_or_bagging[0] == "auto"):
                        parametros_finais_adaboost_or_bagging[0] = str(parametros_finais_adaboost_or_bagging[0])
                    else:
                        parametros_finais_adaboost_or_bagging[0] = float(parametros_finais_adaboost_or_bagging[0])

                    model = SVC(gamma=parametros_finais_adaboost_or_bagging[0],
                                C=float(parametros_finais_adaboost_or_bagging[1]),
                                kernel=str(parametros_finais_adaboost_or_bagging[2]))

                adaboost = AdaBoostClassifier(base_estimator=model, n_estimators=int(parametros_finais_ensemble[1]),
                                              learning_rate=float(parametros_finais_ensemble[2]), algorithm='SAMME',
                                              random_state=None)

                for etiqueta in etiquetas:
                    resultados_treinamento, tamanho_da_lista, pasta_motores = ensembleclassicoclassifier.classificador(
                        treino_tam=float(parametros_finais[0]), teste_tam=float(parametros_finais[1]),
                        folds_tam=int(parametros_finais[2]), metodo=adaboost, divisao=str(parametros_finais[4]),
                        vec_tipo=str(parametros_finais[5]), etiqueta=etiqueta, caminho=caminho,
                        caminho_motores=caminho_motores)

                    if (len(resultados_treinamento) > 4):
                        resultados_treinamento[5] = str(resultados_treinamento[5]).replace(' [', '\n[')
                    par_etiqueta_resultados[etiqueta.replace('.csv', '')] = resultados_treinamento


            elif ((parametros_finais[3]) == "bagging"):
                myMethod = "Bagging"

                # Tratando a lista de parâmetros do ensemble clássico
                for cont, parametro in enumerate(lista_parametros_ensemble):
                    parametros_finais_ensemble.append(lista_parametros_ensemble[cont].split("=")[1])
                print(parametros_finais_ensemble)

                # Tratando a lista de parâmetros do algoritmo escolhido para o ensemble clássico
                for cont, parametro in enumerate(lista_classificador_ensemble):
                    parametros_finais_adaboost_or_bagging.append(lista_classificador_ensemble[cont].split("= ")[1])

                if parametros_finais_ensemble[5] == "true":
                    parametros_finais_ensemble[5] = True
                else:
                    parametros_finais_ensemble[5] = False

                if parametros_finais_ensemble[6] == "true":
                    parametros_finais_ensemble[6] = True
                else:
                    parametros_finais_ensemble[6] = False

                if parametros_finais_ensemble[7] == "true":
                    parametros_finais_ensemble[7] = True
                else:
                    parametros_finais_ensemble[7] = False

                # Verificando o algoritmo escolhido para o Bagging

                if parametros_finais_ensemble[0] == "decisionTree":
                    base_estimator = "Decision Tree"

                    if (parametros_finais_adaboost_or_bagging[0] == "None"):
                        parametros_finais_adaboost_or_bagging[0] = None
                    else:
                        parametros_finais_adaboost_or_bagging[0] = int(parametros_finais_adaboost_or_bagging[0])

                    model = DecisionTreeClassifier(max_depth=parametros_finais_adaboost_or_bagging[0],
                                                   criterion=str(parametros_finais_adaboost_or_bagging[1]),
                                                   splitter=str(parametros_finais_adaboost_or_bagging[2]))


                elif parametros_finais_ensemble[0] == "bernoulli":
                    base_estimator = "Bernoulli"

                    model = BernoulliNB(alpha=float(parametros_finais_adaboost_or_bagging[0]))


                elif parametros_finais_ensemble[0] == "knn":
                    base_estimator = "K-Nearest Neighbors"

                    model = KNeighborsClassifier(n_neighbors=int(parametros_finais_adaboost_or_bagging[0]),
                                                 metric=str(parametros_finais_adaboost_or_bagging[1]))


                elif parametros_finais_ensemble[0] == "linearSVM":
                    base_estimator = "Linear Support Vector Machine"

                    model = LinearSVC(C=float(parametros_finais_adaboost_or_bagging[0]),
                                      penalty=str(parametros_finais_adaboost_or_bagging[1]),
                                      loss=str(parametros_finais_adaboost_or_bagging[2]))


                elif parametros_finais_ensemble[0] == "multilayerPerceptron":
                    base_estimator = "Multilayer Perceptron"

                    model = MLPClassifier(hidden_layer_sizes=int(parametros_finais_adaboost_or_bagging[0]),
                                          learning_rate_init=float(parametros_finais_adaboost_or_bagging[1]),
                                          activation=str(parametros_finais_adaboost_or_bagging[2]),
                                          solver=str(parametros_finais_adaboost_or_bagging[3]),
                                          learning_rate=str(parametros_finais_adaboost_or_bagging[4]))


                elif parametros_finais_ensemble[0] == "multinomialNaiveBayes":
                    base_estimator = "Multinomial Naive Bayes"

                    if parametros_finais_adaboost_or_bagging[1] == "true":
                        parametros_finais_adaboost_or_bagging[1] = True
                    else:
                        parametros_finais_adaboost_or_bagging[1] = False

                    model = MultinomialNB(alpha=float(parametros_finais_adaboost_or_bagging[0]),
                                          fit_prior=parametros_finais_adaboost_or_bagging[1])


                elif parametros_finais_ensemble[0] == "randomForest":
                    base_estimator = "Random Forest"

                    if parametros_finais_adaboost_or_bagging[1] == "None":
                        parametros_finais_adaboost_or_bagging[1] = None
                    else:
                        parametros_finais_adaboost_or_bagging[1] = int(float(parametros_finais_adaboost_or_bagging[1]))

                    model = RandomForestClassifier(n_estimators=int(parametros_finais_adaboost_or_bagging[0]),
                                                   max_depth=parametros_finais_adaboost_or_bagging[1],
                                                   criterion=str(parametros_finais_adaboost_or_bagging[2]))


                elif parametros_finais_ensemble[0] == "logisticRegression":
                    base_estimator = "Logistic Regression"

                    model = LogisticRegression(C=float(parametros_finais_adaboost_or_bagging[0]),
                                               penalty=str(parametros_finais_adaboost_or_bagging[1]),
                                               solver=str(parametros_finais_adaboost_or_bagging[2]))


                elif parametros_finais_ensemble[0] == "sgd":
                    base_estimator = "Gradient Descent SGD"

                    model = SGDClassifier(max_iter=int(parametros_finais_adaboost_or_bagging[0]),
                                          loss=str(parametros_finais_adaboost_or_bagging[1]),
                                          penalty=str(parametros_finais_adaboost_or_bagging[2]))


                elif parametros_finais_ensemble[0] == "supportVectorMachine":
                    base_estimator = "Support Vector Machine"

                    if (parametros_finais_adaboost_or_bagging[0] == "auto"):
                        parametros_finais_adaboost_or_bagging[0] = str(parametros_finais_adaboost_or_bagging[0])
                    else:
                        parametros_finais_adaboost_or_bagging[0] = float(parametros_finais_adaboost_or_bagging[0])

                    model = SVC(gamma=parametros_finais_adaboost_or_bagging[0],
                                C=float(parametros_finais_adaboost_or_bagging[1]),
                                kernel=str(parametros_finais_adaboost_or_bagging[2]))

                bagging = BaggingClassifier(base_estimator=model, n_estimators=int(parametros_finais_ensemble[1]),
                                            max_samples=int(parametros_finais_ensemble[2]),
                                            max_features=int(parametros_finais_ensemble[3]), random_state=None,
                                            bootstrap=parametros_finais_ensemble[4],
                                            bootstrap_features=parametros_finais_ensemble[5],
                                            oob_score=parametros_finais_ensemble[6])

                for etiqueta in etiquetas:
                    resultados_treinamento, tamanho_da_lista, pasta_motores = ensembleclassicoclassifier.classificador(
                        treino_tam=float(parametros_finais[0]), teste_tam=float(parametros_finais[1]),
                        folds_tam=int(parametros_finais[2]), metodo=bagging, divisao=str(parametros_finais[4]),
                        vec_tipo=str(parametros_finais[5]), etiqueta=etiqueta, caminho=caminho,
                        caminho_motores=caminho_motores)

                    if (len(resultados_treinamento) > 4):
                        resultados_treinamento[5] = str(resultados_treinamento[5]).replace(' [', '\n[')
                    par_etiqueta_resultados[etiqueta.replace('.csv', '')] = resultados_treinamento


            elif ((parametros_finais[3]) == "extraTrees"):
                myMethod = "Extra Trees"

                # Tratando a lista de parâmetros do ensemble clássico
                for cont, parametro in enumerate(lista_parametros_ensemble):
                    parametros_finais_ensemble.append(lista_parametros_ensemble[cont].split("=")[1])
                print(parametros_finais_ensemble)

                if parametros_finais_ensemble[2] == "None":
                    parametros_finais_ensemble[2] = None
                else:
                    parametros_finais_ensemble[2] = int(parametros_finais_ensemble[2])

                if parametros_finais_ensemble[3] == "false":
                    parametros_finais_ensemble[3] = False
                else:
                    parametros_finais_ensemble[3] = True

                extratrees = ExtraTreesClassifier(n_estimators=int(parametros_finais_ensemble[0]),
                                                  criterion=str(parametros_finais_ensemble[1]),
                                                  max_depth=parametros_finais_ensemble[2],
                                                  bootstrap=parametros_finais_ensemble[3])

                for etiqueta in etiquetas:
                    resultados_treinamento, tamanho_da_lista, pasta_motores = ensembleclassicoclassifier.classificador(
                        treino_tam=float(parametros_finais[0]), teste_tam=float(parametros_finais[1]),
                        folds_tam=int(parametros_finais[2]), metodo=extratrees, divisao=str(parametros_finais[4]),
                        vec_tipo=str(parametros_finais[5]), etiqueta=etiqueta, caminho=caminho,
                        caminho_motores=caminho_motores)

                    if (len(resultados_treinamento) > 4):
                        resultados_treinamento[5] = str(resultados_treinamento[5]).replace(' [', '\n[')
                    par_etiqueta_resultados[etiqueta.replace('.csv', '')] = resultados_treinamento


            elif ((parametros_finais[3]) == "gradientboosting"):
                myMethod = "Gradient Boosting"

                # Tratando a lista de parâmetros do ensemble clássico
                for cont, parametro in enumerate(lista_parametros_ensemble):
                    parametros_finais_ensemble.append(lista_parametros_ensemble[cont].split("=")[1])
                print(parametros_finais_ensemble)

                if parametros_finais_ensemble[2] == "None":
                    parametros_finais_ensemble[2] = None
                else:
                    parametros_finais_ensemble[2] = int(parametros_finais_ensemble[2])

                if parametros_finais_ensemble[3] == "false":
                    parametros_finais_ensemble[3] = False
                else:
                    parametros_finais_ensemble[3] = True

                gradientboosting = GradientBoostingClassifier(loss=str(parametros_finais_ensemble[0]),
                                                              learning_rate=float(parametros_finais_ensemble[1]),
                                                              n_estimators=int(parametros_finais_ensemble[2]),
                                                              subsample=float(parametros_finais_ensemble[3]),
                                                              criterion=str(parametros_finais_ensemble[4]),
                                                              max_depth=int(parametros_finais_ensemble[5]))

                for etiqueta in etiquetas:
                    resultados_treinamento, tamanho_da_lista, pasta_motores = ensembleclassicoclassifier.classificador(
                        treino_tam=float(parametros_finais[0]), teste_tam=float(parametros_finais[1]),
                        folds_tam=int(parametros_finais[2]), metodo=gradientboosting, divisao=str(parametros_finais[4]),
                        vec_tipo=str(parametros_finais[5]), etiqueta=etiqueta, caminho=caminho,
                        caminho_motores=caminho_motores)

                    if (len(resultados_treinamento) > 4):
                        resultados_treinamento[5] = str(resultados_treinamento[5]).replace(' [', '\n[')
                    par_etiqueta_resultados[etiqueta.replace('.csv', '')] = resultados_treinamento


            elif ((parametros_finais[3]) == "randomForest"):
                myMethod = "Random Forest"

                # Tratando a lista de parâmetros do ensemble clássico
                for cont, parametro in enumerate(lista_parametros_ensemble):
                    parametros_finais_ensemble.append(lista_parametros_ensemble[cont].split("=")[1])
                print(parametros_finais_ensemble)

                if parametros_finais_ensemble[2] == "None":
                    parametros_finais_ensemble[2] = None
                else:
                    parametros_finais_ensemble[2] = int(float(parametros_finais_ensemble[2]))

                if parametros_finais_ensemble[3] == "false":
                    parametros_finais_ensemble[3] = False
                else:
                    parametros_finais_ensemble[3] = True

                randomforest = RandomForestClassifier(n_estimators=int(parametros_finais_ensemble[0]),
                                                      criterion=str(parametros_finais_ensemble[1]),
                                                      max_depth=parametros_finais_ensemble[2],
                                                      bootstrap=parametros_finais_ensemble[3])

                for etiqueta in etiquetas:
                    resultados_treinamento, tamanho_da_lista, pasta_motores = ensembleclassicoclassifier.classificador(
                        treino_tam=float(parametros_finais[0]), teste_tam=float(parametros_finais[1]),
                        folds_tam=int(parametros_finais[2]), metodo=randomforest, divisao=str(parametros_finais[4]),
                        vec_tipo=str(parametros_finais[5]), etiqueta=etiqueta, caminho=caminho,
                        caminho_motores=caminho_motores)

                    if (len(resultados_treinamento) > 4):
                        resultados_treinamento[5] = str(resultados_treinamento[5]).replace(' [', '\n[')
                    par_etiqueta_resultados[etiqueta.replace('.csv', '')] = resultados_treinamento

            elif ((parametros_finais[3]) == "voting"):
                myMethod = "Voting"

                # Tratando a lista de parâmetros do ensemble clássico
                for cont, parametro in enumerate(lista_parametros_ensemble):
                    parametros_finais_ensemble.append(lista_parametros_ensemble[cont].split("=")[1])
                print(parametros_finais_ensemble)

                dictParamsAlgoritmos = {}
                estimators = []

                # Tratando a lista que contém os algoritmos e seus parâmetros (inserindo num dicionário)
                for item in dicionario_classificadores_ensemble:
                    algoritmo = item.split(":")[0].replace('"', '')
                    print(algoritmo)
                    listaDeParams = item.split(": ")[1].replace('"', '').split(",")
                    print(listaDeParams)
                    dictParamsAlgoritmos[algoritmo] = listaDeParams

                # Tratando o dicionário que contem os algoritmos escolhidos e seus respectivos parâmetros
                for algoritmo, listaParams in dictParamsAlgoritmos.items():

                    for cont, param in enumerate(listaParams):
                        listaParams[cont] = param.split("= ")[1]

                    if algoritmo == "DecisionTree":
                        if (listaParams[0] == "None"):
                            listaParams[0] = None
                        else:
                            listaParams[0] = int(listaParams[0])

                        model1 = DecisionTreeClassifier(max_depth=listaParams[0], criterion=str(listaParams[1]),
                                                        splitter=str(listaParams[2]))
                        estimators.append((algoritmo, model1))

                    elif algoritmo == "Bernoulli":
                        model2 = BernoulliNB(alpha=float(listaParams[0]))
                        estimators.append((algoritmo, model2))

                    elif algoritmo == "KNN":
                        model3 = KNeighborsClassifier(n_neighbors=int(listaParams[0]), metric=str(listaParams[1]))
                        estimators.append((algoritmo, model3))

                    elif algoritmo == "LinearSVM":
                        model4 = LinearSVC(C=float(listaParams[0]), penalty=str(listaParams[1]), loss=str(listaParams[2]))
                        estimators.append((algoritmo, model4))

                    elif algoritmo == "MultilayerPerceptron":
                        model5 = MLPClassifier(hidden_layer_sizes=int(listaParams[0]),
                                               learning_rate_init=float(listaParams[1]), activation=str(listaParams[2]),
                                               solver=str(listaParams[3]),
                                               learning_rate=str(listaParams[4]))
                        estimators.append((algoritmo, model5))

                    elif algoritmo == "MultinomialNB":
                        if listaParams[1] == "True":
                            listaParams[1] = True
                        else:
                            listaParams[1] = False

                        model6 = MultinomialNB(alpha=float(listaParams[0]), fit_prior=listaParams[1])
                        estimators.append((algoritmo, model6))

                    elif algoritmo == "RandomForest":
                        if listaParams[1] == "None":
                            listaParams[1] = None
                        else:
                            listaParams[1] = int(float(listaParams[1]))

                        model7 = RandomForestClassifier(n_estimators=int(listaParams[0]), max_depth=listaParams[1],
                                                        criterion=str(listaParams[2]))
                        estimators.append((algoritmo, model7))

                    elif algoritmo == "LogisticRegression":
                        model8 = LogisticRegression(C=float(listaParams[0]), penalty=str(listaParams[1]),
                                                    solver=str(listaParams[2]))
                        estimators.append((algoritmo, model8))

                    elif algoritmo == "SGD":
                        model9 = SGDClassifier(max_iter=int(listaParams[0]), loss=str(listaParams[1]),
                                               penalty=str(listaParams[2]))
                        estimators.append((algoritmo, model9))

                    elif algoritmo == "SVM":
                        if (listaParams[0] == "auto"):
                            listaParams[0] = str(listaParams[0])
                        else:
                            listaParams[0] = float(listaParams[0])

                        model10 = SVC(probability=True, gamma=listaParams[0], C=float(listaParams[1]),
                                      kernel=str(listaParams[2]))
                        estimators.append((algoritmo, model10))

                voting = VotingClassifier(estimators, voting=str(parametros_finais_ensemble[0]))

                for etiqueta in etiquetas:
                    resultados_treinamento, tamanho_da_lista, pasta_motores = ensembleclassicoclassifier.classificador(
                        treino_tam=float(parametros_finais[0]), teste_tam=float(parametros_finais[1]),
                        folds_tam=int(parametros_finais[2]), metodo=voting, divisao=str(parametros_finais[4]),
                        vec_tipo=str(parametros_finais[5]), etiqueta=etiqueta, caminho=caminho,
                        caminho_motores=caminho_motores)

                    if (len(resultados_treinamento) > 4):
                        resultados_treinamento[5] = str(resultados_treinamento[5]).replace(' [', '\n[')
                    par_etiqueta_resultados[etiqueta.replace('.csv', '')] = resultados_treinamento

            dataTreino = data_e_hora_em_texto.split("_")[0]
            inicioTreino = data_e_hora_em_texto.split("_")[1]

            arquivos_no_historico = os.listdir(caminho_historico_bases_treinadas)

            cont = 1

            while True:
                if not str(cont) + ".txt" in arquivos_no_historico:
                    nome_do_motor = str(cont)
                    break
                else:
                    cont += 1

            # Criando o arquivo txt que vai salvar as informações (na pasta de de histórico) de todos os treinamentos feitos
            with open(caminho_historico_bases_treinadas + nome_do_motor + ".txt", "w") as nomeMotor:
                nomeMotor.write("Caminho do motor = " + pasta_motores + "\n")
                nomeMotor.write("Nome da base = " + nome_da_base + "\n")
                nomeMotor.write("Período da base = " + periodo + "\n")
                nomeMotor.write("Classificador = " + classificador + "\n")
                nomeMotor.write("Data do treino = " + dataTreino.replace("-", "/") + "\n")
                nomeMotor.write("Horário do treino = " + inicioTreino.replace(";", ":") + "\n\n")
                nomeMotor.write("Método = " + myMethod + "\n")
                if myMethod == "Adaboost" or myMethod == "Bagging":
                    nomeMotor.write("Algoritmo = " + base_estimator + "\n")
                # Alterar o código abaixo para incluir todos os algoritmos utilizados pelo método "Voting"
                elif myMethod == "Voting":
                    nomeMotor.write("Algoritmos = " + "\n")

                for etiqueta, lista_resultados in par_etiqueta_resultados.items():
                    etiqueta = etiqueta.replace("_PRE-PROCESSADO", '')
                    nomeMotor.write(etiqueta + " \n\n")

                    for cont, resultado in enumerate(lista_resultados):

                        if cont < 5:
                            if cont == 0:
                                name_result = "Acurácia: "
                            elif cont == 1:
                                name_result = "Precisão: "
                            elif cont == 2:
                                name_result = "Recall: "
                            elif cont == 3:
                                name_result = "F1: "
                            nomeMotor.write(name_result + str(resultado) + "\n\n")

                        elif cont == (len(lista_resultados) - 1):
                            name_result = "Matriz de Confusão \n"
                            nomeMotor.write(name_result + (str(resultado) + "\n\n"))

                        else:
                            name_result = "Classification Report \n"
                            nomeMotor.write(name_result + (str(resultado) + "\n"))

            # Criando o arquivo txt que vai salvar os resultados do treinamento feito
            with open(caminho_motores + "Resultados.txt", "w") as salvarResultados:
                infoHistorico = open(caminho_historico_bases_treinadas + nome_do_motor + ".txt", "r")
                for line in infoHistorico.readlines():
                    salvarResultados.write(line)
                infoHistorico.close()

            context = {
                'par_etiqueta_resultados': par_etiqueta_resultados,
                'tamanho_da_lista': tamanho_da_lista,
                'nome_da_base': nome_da_base,
                'periodo': periodo,
                'classificador': classificador,
                'pasta_motores': pasta_motores,
                'myMethod': myMethod,
                'base_estimator': base_estimator,
            }

            return HttpResponse(render(request, "resultados.html", context))
        else:
            return render(request, "resultados.html")

    except (MemoryError):
        erromessage = {
            'message': "Os resultados não foram extraídos. O servidor não suporta este processamento. Tente utilizar uma base de dados menor.",
        }
        return HttpResponse(render(request, "resultados.html", erromessage))

    except IOError as (errno, strerror):
        erromessage = {
            'message': "I/O error({0}): {1}".format(errno, strerror),
        }
        return HttpResponse(render(request, "resultados.html", erromessage))

    except ValueError:
        erromessage = {
            'message': "Os valores recebidos não correspondem ao esperado pelo sistema.",
        }
        return HttpResponse(render(request, "resultados.html", erromessage))

    except:
        erromessage = {
            'message': "Erro inesperado: "+str(sys.exc_info()[0]),
        }
        return HttpResponse(render(request, "resultados.html", erromessage))
        raise

def geraPDF(request):

    try:
        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()

        # Create the PDF object, using the buffer as its "file."
        p = canvas.Canvas(buffer)

        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        p.drawString(100, 100, "Hello world.")

        # Close the PDF object cleanly, and we're done.
        p.showPage()
        p.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        return FileResponse(buffer, as_attachment=True, filename='hello.pdf')


    except IOError as (errno, strerror):
        erromessage = {
            'message': "I/O error({0}): {1}".format(errno, strerror),
        }
        return HttpResponse(render(request, "resultados.html", erromessage))

    except ValueError:
        erromessage = {
            'message': "Os valores recebidos não correspondem ao esperado pelo sistema.",
        }
        return HttpResponse(render(request, "resultados.html", erromessage))

    except:
        erromessage = {
            'message': "Erro inesperado: "+str(sys.exc_info()[0]),
        }
        return HttpResponse(render(request, "resultados.html", erromessage))
        raise


def resultados(request):

    try:
            if request.method == 'POST':

                nome_da_base = request.POST.get('nome_da_base')
                periodo = request.POST.get('periodo')
                etiquetas_escolhidas_global = request.POST.get('etiquetas_escolhidas_global')
                lista_de_parametros = request.POST.get('lista_de_parametros')
                classificador = request.POST.get('classificador')

                periodo_pasta = periodo.replace('/', '').replace(' - ', '_')

                arquivar_parametros = lista_de_parametros

                lista_de_parametros = lista_de_parametros.split(',')

                print(lista_de_parametros)

                data_e_hora_em_texto = ""

                # Pasta para saber onde está o motor de inferência, na próxima tela "Validação"
                pasta_motores = ""

                # Criando a lista de parâmetros que serão passados para o método do classificador a ser escolhido
                parametros_finais = []

                # Tratando a lista de parâmetros
                for cont, parametro in enumerate(lista_de_parametros):
                    parametros_finais.append(lista_de_parametros[cont].split("=")[1])

                # Criando o dicionário que irá conter o par: chave (etiqueta) e valor (uma lista com os parâmetros de resultados da etiqueta)
                par_etiqueta_resultados = {}

                # Criando a variável que vai armazenar a quantidade de itens em cada lista do dicionário, para saber se "divisao == 'cross_val'"
                # ou se "divisao == 'percent_split'"
                tamanho_da_lista = 0;

                # TROCAR ESTE DIRETÓRIO PELO DA KURIER
                pasta = pastaArquivos+'bases/'

                caminho_motores = pasta + nome_da_base + '_' + periodo_pasta + "/Motores de Inferencia"
                pasta += nome_da_base + '_' + periodo_pasta + "/PRE-PROCESSADO"
                caminho = pasta + "/"
                etiquetas = os.listdir(pasta)

                # Se a pasta de motores de inferência ainda não existir, nesse momento ela é criada
                if not os.path.exists(caminho_motores):
                    os.mkdir(caminho_motores)

                # TROCAR ESTE DIRETÓRIO PELO DA KURIER
                # Este é o caminho do histórico de todas as bases já treinadas, ou seja, onde ficarão os motores de inferência disponíveis
                caminho_historico_bases_treinadas = pastaArquivos+'historico'

                # Se a pasta de histórico dos motores ainda não existir, nesse momento ela é criada
                if not os.path.exists(caminho_historico_bases_treinadas):
                    os.mkdir(caminho_historico_bases_treinadas)

                caminho_historico_bases_treinadas += "/"

                # Começando a verificação de qual classificador foi escolhido, para assim treinar a base pré-processada e gerar o motor de inferência

                if (classificador == "Decision Tree"):
                    caminho_motores += "/Decision Tree"

                    # Se a pasta dos motores de Árvore de decisão ainda não existir, nesse momento ela é criada
                    if not os.path.exists(caminho_motores):
                        os.mkdir(caminho_motores)

                    # Pegando a data e hora atual de Recife, para ser o nome da subpasta dentro da pasta do classificador atual
                    data_e_hora_atuais = datetime.now()
                    data_e_hora_em_texto = data_e_hora_atuais.strftime('%d-%m-%Y_%H;%M;%S')

                    # Determinando caminho da sub_pasta do motor em questão
                    caminho_motores += "/" + data_e_hora_em_texto

                    # Se a pasta desse sub_motor de Árvore de decisão ainda não existir, nesse momento ela é criada
                    if not os.path.exists(caminho_motores):
                        os.mkdir(caminho_motores)

                    # Determinando caminho final
                    caminho_motores += "/"

                    # Criando o arquivo txt que vai salvar os parâmetros utilizados no treinamento
                    arquivoParametros = open(caminho_motores + "Parâmetros.txt", "w")
                    arquivoParametros.writelines(arquivar_parametros)
                    arquivoParametros.close()

                    if (parametros_finais[0] == "None"):
                        for etiqueta in etiquetas:
                            resultados_treinamento, tamanho_da_lista, pasta_motores = arvoredecisaoclassifier.classificador(
                                None, float(parametros_finais[1]), float(parametros_finais[2]), int(parametros_finais[3]),
                                str(parametros_finais[4]), str(parametros_finais[5]), str(parametros_finais[6]),
                                str(parametros_finais[7]), etiqueta, caminho, caminho_motores)
                            par_etiqueta_resultados[etiqueta] = resultados_treinamento
                    else:
                        for etiqueta in etiquetas:
                            resultados_treinamento, tamanho_da_lista, pasta_motores = arvoredecisaoclassifier.classificador(
                                int(parametros_finais[0]), float(parametros_finais[1]), float(parametros_finais[2]),
                                int(parametros_finais[3]), str(parametros_finais[4]), str(parametros_finais[5]),
                                str(parametros_finais[6]), str(parametros_finais[7]), etiqueta, caminho, caminho_motores)
                            par_etiqueta_resultados[etiqueta] = resultados_treinamento


                elif (classificador == "Bernoulli Naive Bayes"):
                    caminho_motores += "/Bernoulli"

                    # Se a pasta dos motores de Bernoulli ainda não existir, nesse momento ela é criada
                    if not os.path.exists(caminho_motores):
                        os.mkdir(caminho_motores)

                    # Pegando a data e hora atual de Recife, para ser o nome da subpasta dentro da pasta do classificador atual
                    data_e_hora_atuais = datetime.now()
                    data_e_hora_em_texto = data_e_hora_atuais.strftime('%d-%m-%Y_%H;%M;%S')

                    # Determinando caminho da sub_pasta do motor em questão
                    caminho_motores += "/" + data_e_hora_em_texto

                    # Se a pasta desse sub_motor de Árvore de decisão ainda não existir, nesse momento ela é criada
                    if not os.path.exists(caminho_motores):
                        os.mkdir(caminho_motores)

                    # Determinando caminho final
                    caminho_motores += "/"

                    # Criando o arquivo txt que vai salvar os parâmetros utilizados no treinamento
                    arquivoParametros = open(caminho_motores + "Parâmetros.txt", "w")
                    arquivoParametros.writelines(arquivar_parametros)
                    arquivoParametros.close()

                    for etiqueta in etiquetas:
                        resultados_treinamento, tamanho_da_lista, pasta_motores = bernoulliclassifier.classificador(
                            float(parametros_finais[0]), float(parametros_finais[1]), float(parametros_finais[2]),
                            int(parametros_finais[3]), str(parametros_finais[4]), str(parametros_finais[5]), etiqueta, caminho,
                            caminho_motores)
                        par_etiqueta_resultados[etiqueta.replace('_rc.csv', '')] = resultados_treinamento



                elif (classificador == "K-Nearest Neighbors"):
                    caminho_motores += "/K-Nearest Neighbors"

                    # Se a pasta dos motores de K-Nearest Neighbors ainda não existir, nesse momento ela é criada
                    if not os.path.exists(caminho_motores):
                        os.mkdir(caminho_motores)

                    # Pegando a data e hora atual de Recife, para ser o nome da subpasta dentro da pasta do classificador atual
                    data_e_hora_atuais = datetime.now()
                    data_e_hora_em_texto = data_e_hora_atuais.strftime('%d-%m-%Y_%H;%M;%S')

                    # Determinando caminho da sub_pasta do motor em questão
                    caminho_motores += "/" + data_e_hora_em_texto

                    # Se a pasta desse sub_motor de Árvore de decisão ainda não existir, nesse momento ela é criada
                    if not os.path.exists(caminho_motores):
                        os.mkdir(caminho_motores)

                    # Determinando caminho final
                    caminho_motores += "/"

                    # Criando o arquivo txt que vai salvar os parâmetros utilizados no treinamento
                    arquivoParametros = open(caminho_motores + "Parâmetros.txt", "w")
                    arquivoParametros.writelines(arquivar_parametros)
                    arquivoParametros.close()

                    for etiqueta in etiquetas:
                        resultados_treinamento, tamanho_da_lista, pasta_motores = knnclassifier.classificador(
                            int(parametros_finais[0]), float(parametros_finais[1]), float(parametros_finais[2]),
                            int(parametros_finais[3]), str(parametros_finais[4]), str(parametros_finais[5]),
                            str(parametros_finais[6]), etiqueta, caminho, caminho_motores)
                        if (len(resultados_treinamento) >= 5):
                            resultados_treinamento[5] = str(resultados_treinamento[5]).replace(' [', '\n[')
                        par_etiqueta_resultados[etiqueta.replace('.csv', '')] = resultados_treinamento


                elif (classificador == "Linear Support Vector Machine"):
                    caminho_motores += "/Linear Support Vector Machine"

                    # Se a pasta dos motores de Linear Support Vector Machine ainda não existir, nesse momento ela é criada
                    if not os.path.exists(caminho_motores):
                        os.mkdir(caminho_motores)

                    # Pegando a data e hora atual de Recife, para ser o nome da subpasta dentro da pasta do classificador atual
                    data_e_hora_atuais = datetime.now()
                    data_e_hora_em_texto = data_e_hora_atuais.strftime('%d-%m-%Y_%H;%M;%S')

                    # Determinando caminho da sub_pasta do motor em questão
                    caminho_motores += "/" + data_e_hora_em_texto

                    # Se a pasta desse sub_motor de Árvore de decisão ainda não existir, nesse momento ela é criada
                    if not os.path.exists(caminho_motores):
                        os.mkdir(caminho_motores)

                    # Determinando caminho final
                    caminho_motores += "/"

                    # Criando o arquivo txt que vai salvar os parâmetros utilizados no treinamento
                    arquivoParametros = open(caminho_motores + "Parâmetros.txt", "w")
                    arquivoParametros.writelines(arquivar_parametros)
                    arquivoParametros.close()

                    for etiqueta in etiquetas:
                        resultados_treinamento, tamanho_da_lista, pasta_motores = linearsvm.classificador(
                            float(parametros_finais[0]), float(parametros_finais[1]), float(parametros_finais[2]),
                            int(parametros_finais[3]), str(parametros_finais[4]), str(parametros_finais[5]),
                            str(parametros_finais[6]), str(parametros_finais[7]), etiqueta, caminho, caminho_motores)
                        if (len(resultados_treinamento) >= 5):
                            resultados_treinamento[5] = str(resultados_treinamento[5]).replace(' [', '\n[')
                        par_etiqueta_resultados[etiqueta.replace('.csv', '')] = resultados_treinamento


                elif (classificador == "Multilayer Perceptron"):
                    caminho_motores += "/Multilayer Perceptron"

                    # Se a pasta dos motores de Multilayer Perceptron ainda não existir, nesse momento ela é criada
                    if not os.path.exists(caminho_motores):
                        os.mkdir(caminho_motores)

                    # Pegando a data e hora atual de Recife, para ser o nome da subpasta dentro da pasta do classificador atual
                    data_e_hora_atuais = datetime.now()
                    data_e_hora_em_texto = data_e_hora_atuais.strftime('%d-%m-%Y_%H;%M;%S')

                    # Determinando caminho da sub_pasta do motor em questão
                    caminho_motores += "/" + data_e_hora_em_texto

                    # Se a pasta desse sub_motor de Árvore de decisão ainda não existir, nesse momento ela é criada
                    if not os.path.exists(caminho_motores):
                        os.mkdir(caminho_motores)

                    # Determinando caminho final
                    caminho_motores += "/"

                    # Criando o arquivo txt que vai salvar os parâmetros utilizados no treinamento
                    arquivoParametros = open(caminho_motores + "Parâmetros.txt", "w")
                    arquivoParametros.writelines(arquivar_parametros)
                    arquivoParametros.close()

                    for etiqueta in etiquetas:
                        resultados_treinamento, tamanho_da_lista, pasta_motores = mlpclassifier.classificador(
                            int(parametros_finais[0]), float(parametros_finais[1]), float(parametros_finais[2]),
                            int(parametros_finais[3]), float(parametros_finais[4]), str(parametros_finais[5]),
                            str(parametros_finais[6]), str(parametros_finais[7]), str(parametros_finais[8]),
                            str(parametros_finais[9]), etiqueta, caminho, caminho_motores)
                        if (len(resultados_treinamento) >= 5):
                            resultados_treinamento[5] = str(resultados_treinamento[5]).replace(' [', '\n[')
                        par_etiqueta_resultados[etiqueta.replace('.csv', '')] = resultados_treinamento


                elif (classificador == "Multinomial Naive Bayes"):
                    caminho_motores += "/Multinomial Naive Bayes"

                    # Se a pasta dos motores de Multinomial Naive Bayes ainda não existir, nesse momento ela é criada
                    if not os.path.exists(caminho_motores):
                        os.mkdir(caminho_motores)

                    # Pegando a data e hora atual de Recife, para ser o nome da subpasta dentro da pasta do classificador atual
                    data_e_hora_atuais = datetime.now()
                    data_e_hora_em_texto = data_e_hora_atuais.strftime('%d-%m-%Y_%H;%M;%S')

                    # Determinando caminho da sub_pasta do motor em questão
                    caminho_motores += "/" + data_e_hora_em_texto

                    # Se a pasta desse sub_motor de Árvore de decisão ainda não existir, nesse momento ela é criada
                    if not os.path.exists(caminho_motores):
                        os.mkdir(caminho_motores)

                    # Determinando caminho final
                    caminho_motores += "/"

                    # Criando o arquivo txt que vai salvar os parâmetros utilizados no treinamento
                    arquivoParametros = open(caminho_motores + "Parâmetros.txt", "w")
                    arquivoParametros.writelines(arquivar_parametros)
                    arquivoParametros.close()

                    if (parametros_finais[4] == "True"):
                        for etiqueta in etiquetas:
                            resultados_treinamento, tamanho_da_lista, pasta_motores = multinomialnbclassifier.classificador(
                                float(parametros_finais[0]), float(parametros_finais[1]), float(parametros_finais[2]),
                                int(parametros_finais[3]), True, str(parametros_finais[5]), str(parametros_finais[6]), etiqueta,
                                caminho, caminho_motores)
                            if (len(resultados_treinamento) >= 5):
                                resultados_treinamento[5] = str(resultados_treinamento[5]).replace(' [', '\n[')
                            par_etiqueta_resultados[etiqueta.replace('.csv', '')] = resultados_treinamento
                    else:
                        for etiqueta in etiquetas:
                            resultados_treinamento, tamanho_da_lista, pasta_motores = multinomialnbclassifier.classificador(
                                float(parametros_finais[0]), float(parametros_finais[1]), float(parametros_finais[2]),
                                int(parametros_finais[3]), False, str(parametros_finais[5]), str(parametros_finais[6]),
                                etiqueta, caminho, caminho_motores)
                            if (len(resultados_treinamento) >= 5):
                                resultados_treinamento[5] = str(resultados_treinamento[5]).replace(' [', '\n[')
                            par_etiqueta_resultados[etiqueta.replace('.csv', '')] = resultados_treinamento


                elif (classificador == "Random Forest"):
                    caminho_motores += "/Random Forest"

                    # Se a pasta dos motores de Random Forest ainda não existir, nesse momento ela é criada
                    if not os.path.exists(caminho_motores):
                        os.mkdir(caminho_motores)

                    # Pegando a data e hora atual de Recife, para ser o nome da subpasta dentro da pasta do classificador atual
                    data_e_hora_atuais = datetime.now()
                    data_e_hora_em_texto = data_e_hora_atuais.strftime('%d-%m-%Y_%H;%M;%S')

                    # Determinando caminho da sub_pasta do motor em questão
                    caminho_motores += "/" + data_e_hora_em_texto

                    # Se a pasta desse sub_motor de Árvore de decisão ainda não existir, nesse momento ela é criada
                    if not os.path.exists(caminho_motores):
                        os.mkdir(caminho_motores)

                    # Determinando caminho final
                    caminho_motores += "/"

                    # Criando o arquivo txt que vai salvar os parâmetros utilizados no treinamento
                    arquivoParametros = open(caminho_motores + "Parâmetros.txt", "w")
                    arquivoParametros.writelines(arquivar_parametros)
                    arquivoParametros.close()

                    if (parametros_finais[1] == "None"):
                        for etiqueta in etiquetas:
                            resultados_treinamento, tamanho_da_lista, pasta_motores = randomforestclassifier.classificador(
                                int(parametros_finais[0]), None, float(parametros_finais[2]), float(parametros_finais[3]),
                                int(parametros_finais[4]), str(parametros_finais[5]), str(parametros_finais[6]),
                                str(parametros_finais[7]), etiqueta, caminho, caminho_motores)
                            if (len(resultados_treinamento) >= 5):
                                resultados_treinamento[5] = str(resultados_treinamento[5]).replace(' [', '\n[')
                            par_etiqueta_resultados[etiqueta.replace('.csv', '')] = resultados_treinamento
                    else:
                        for etiqueta in etiquetas:
                            resultados_treinamento, tamanho_da_lista, pasta_motores = resultados_treinamento, tamanho_da_lista = randomforestclassifier.classificador(
                                int(parametros_finais[0]), int(parametros_finais[1]), float(parametros_finais[2]),
                                float(parametros_finais[3]), int(parametros_finais[4]), str(parametros_finais[5]),
                                str(parametros_finais[6]), str(parametros_finais[7]), etiqueta, caminho, caminho_motores)
                            if (len(resultados_treinamento) >= 5):
                                resultados_treinamento[5] = str(resultados_treinamento[5]).replace(' [', '\n[')
                            par_etiqueta_resultados[etiqueta.replace('.csv', '')] = resultados_treinamento


                elif (classificador == "Logistic Regression"):
                    caminho_motores += "/Logistic Regression"

                    # Se a pasta dos motores de Logistic Regression ainda não existir, nesse momento ela é criada
                    if not os.path.exists(caminho_motores):
                        os.mkdir(caminho_motores)

                    # Pegando a data e hora atual de Recife, para ser o nome da subpasta dentro da pasta do classificador atual
                    data_e_hora_atuais = datetime.now()
                    data_e_hora_em_texto = data_e_hora_atuais.strftime('%d-%m-%Y_%H;%M;%S')

                    # Determinando caminho da sub_pasta do motor em questão
                    caminho_motores += "/" + data_e_hora_em_texto

                    # Se a pasta desse sub_motor de Árvore de decisão ainda não existir, nesse momento ela é criada
                    if not os.path.exists(caminho_motores):
                        os.mkdir(caminho_motores)

                    # Determinando caminho final
                    caminho_motores += "/"

                    # Criando o arquivo txt que vai salvar os parâmetros utilizados no treinamento
                    arquivoParametros = open(caminho_motores + "Parâmetros.txt", "w")
                    arquivoParametros.writelines(arquivar_parametros)
                    arquivoParametros.close()

                    for etiqueta in etiquetas:
                        resultados_treinamento, tamanho_da_lista, pasta_motores = regressaologisticaclassifier.classificador(
                            float(parametros_finais[0]), float(parametros_finais[1]), float(parametros_finais[2]),
                            int(parametros_finais[3]), str(parametros_finais[4]), str(parametros_finais[5]),
                            str(parametros_finais[6]), str(parametros_finais[7]), etiqueta, caminho, caminho_motores)
                        if (len(resultados_treinamento) >= 5):
                            resultados_treinamento[5] = str(resultados_treinamento[5]).replace(' [', '\n[')
                        par_etiqueta_resultados[etiqueta.replace('.csv', '')] = resultados_treinamento


                elif (classificador == "Stochastic Gradient Descent"):
                    caminho_motores += "/Gradient Descent SGD"

                    # Se a pasta dos motores de Gradient Descent SGD ainda não existir, nesse momento ela é criada
                    if not os.path.exists(caminho_motores):
                        os.mkdir(caminho_motores)

                    # Pegando a data e hora atual de Recife, para ser o nome da subpasta dentro da pasta do classificador atual
                    data_e_hora_atuais = datetime.now()
                    data_e_hora_em_texto = data_e_hora_atuais.strftime('%d-%m-%Y_%H;%M;%S')

                    # Determinando caminho da sub_pasta do motor em questão
                    caminho_motores += "/" + data_e_hora_em_texto

                    # Se a pasta desse sub_motor de Árvore de decisão ainda não existir, nesse momento ela é criada
                    if not os.path.exists(caminho_motores):
                        os.mkdir(caminho_motores)

                    # Determinando caminho final
                    caminho_motores += "/"

                    # Criando o arquivo txt que vai salvar os parâmetros utilizados no treinamento
                    arquivoParametros = open(caminho_motores + "Parâmetros.txt", "w")
                    arquivoParametros.writelines(arquivar_parametros)
                    arquivoParametros.close()

                    for etiqueta in etiquetas:
                        resultados_treinamento, tamanho_da_lista, pasta_motores = sgd_classifier.classificador(
                            int(parametros_finais[0]), float(parametros_finais[1]), float(parametros_finais[2]),
                            int(parametros_finais[3]), str(parametros_finais[4]), str(parametros_finais[5]),
                            str(parametros_finais[6]), str(parametros_finais[7]), etiqueta, caminho, caminho_motores)
                        if (len(resultados_treinamento) >= 5):
                            resultados_treinamento[5] = str(resultados_treinamento[5]).replace(' [', '\n[')
                        par_etiqueta_resultados[etiqueta.replace('.csv', '')] = resultados_treinamento


                elif (classificador == "Support Vector Machine"):
                    caminho_motores += "/Support Vector Machine"

                    # Se a pasta dos motores de Support Vector Machine ainda não existir, nesse momento ela é criada
                    if not os.path.exists(caminho_motores):
                        os.mkdir(caminho_motores)

                    # Pegando a data e hora atual de Recife, para ser o nome da subpasta dentro da pasta do classificador atual
                    data_e_hora_atuais = datetime.now()
                    data_e_hora_em_texto = data_e_hora_atuais.strftime('%d-%m-%Y_%H;%M;%S')

                    # Determinando caminho da sub_pasta do motor em questão
                    caminho_motores += "/" + data_e_hora_em_texto

                    # Se a pasta desse sub_motor de Árvore de decisão ainda não existir, nesse momento ela é criada
                    if not os.path.exists(caminho_motores):
                        os.mkdir(caminho_motores)

                    # Determinando caminho final
                    caminho_motores += "/"

                    # Criando o arquivo txt que vai salvar os parâmetros utilizados no treinamento
                    arquivoParametros = open(caminho_motores + "Parâmetros.txt", "w")
                    arquivoParametros.writelines(arquivar_parametros)
                    arquivoParametros.close()

                    if (parametros_finais[0] == "auto"):
                        for etiqueta in etiquetas:
                            resultados_treinamento, tamanho_da_lista, pasta_motores = svmclassifier.classificador(
                                parametros_finais[0], float(parametros_finais[1]), float(parametros_finais[2]),
                                float(parametros_finais[3]), int(parametros_finais[4]), str(parametros_finais[5]),
                                str(parametros_finais[6]), str(parametros_finais[7]), etiqueta, caminho, caminho_motores)
                            if (len(resultados_treinamento) >= 5):
                                resultados_treinamento[5] = str(resultados_treinamento[5]).replace(' [', '\n[')
                            par_etiqueta_resultados[etiqueta.replace('.csv', '')] = resultados_treinamento
                    else:
                        for etiqueta in etiquetas:
                            resultados_treinamento, tamanho_da_lista, pasta_motores = svmclassifier.classificador(
                                float(parametros_finais[0]), float(parametros_finais[1]), float(parametros_finais[2]),
                                float(parametros_finais[3]), int(parametros_finais[4]), str(parametros_finais[5]),
                                str(parametros_finais[6]), str(parametros_finais[7]), etiqueta, caminho, caminho_motores)
                            if (len(resultados_treinamento) >= 5):
                                resultados_treinamento[5] = str(resultados_treinamento[5]).replace(' [', '\n[')
                            par_etiqueta_resultados[etiqueta.replace('.csv', '')] = resultados_treinamento

                dataTreino = data_e_hora_em_texto.split("_")[0]
                inicioTreino = data_e_hora_em_texto.split("_")[1]

                arquivos_no_historico = os.listdir(caminho_historico_bases_treinadas)

                cont = 1

                while True:
                    if not str(cont) + ".txt" in arquivos_no_historico:
                        nome_do_motor = str(cont)
                        break
                    else:
                        cont += 1

                # Criando o arquivo txt que vai salvar as informações (na pasta de de histórico) de todos os treinamentos feitos
                with open(caminho_historico_bases_treinadas + nome_do_motor + ".txt", "w") as nomeMotor:
                    nomeMotor.write("Caminho do motor = " + pasta_motores + "\n")
                    nomeMotor.write("Nome da base = " + nome_da_base + "\n")
                    nomeMotor.write("Período da base = " + periodo + "\n")
                    nomeMotor.write("Classificador = " + classificador + "\n")
                    nomeMotor.write("Data do treino = " + dataTreino.replace("-", "/") + "\n")
                    nomeMotor.write("Horário do treino = " + inicioTreino.replace(";", ":") + "\n\n")

                    for etiqueta, lista_resultados in par_etiqueta_resultados.items():
                        etiqueta = etiqueta.replace("_PRE-PROCESSADO", '')
                        nomeMotor.write(etiqueta + " \n\n")

                        for cont, resultado in enumerate(lista_resultados):

                            if cont < 5:
                                if cont == 0:
                                    name_result = "Acurácia: "
                                elif cont == 1:
                                    name_result = "Precisão: "
                                elif cont == 2:
                                    name_result = "Recall: "
                                elif cont == 3:
                                    name_result = "F1: "
                                nomeMotor.write(name_result + str(resultado) + "\n\n")

                            elif cont == (len(lista_resultados) - 1):
                                name_result = "Matriz de Confusão \n"
                                nomeMotor.write(name_result + (str(resultado) + "\n\n"))

                            else:
                                name_result = "Classification Report \n"
                                nomeMotor.write(name_result + (str(resultado) + "\n"))

                # Criando o arquivo txt que vai salvar os resultados do treinamento feito
                with open(caminho_motores + "Resultados.txt", "w") as salvarResultados:
                    infoHistorico = open(caminho_historico_bases_treinadas + nome_do_motor + ".txt", "r")
                    for line in infoHistorico.readlines():
                        salvarResultados.write(line)
                    infoHistorico.close()

                context = {
                    'par_etiqueta_resultados': par_etiqueta_resultados,
                    'tamanho_da_lista': tamanho_da_lista,
                    'nome_da_base': nome_da_base,
                    'periodo': periodo,
                    'classificador': classificador,
                    'pasta_motores': pasta_motores,
                }

                return HttpResponse(render(request, "resultados.html", context))
            else:
                return render(request, "resultados.html")

    except (MemoryError):
        erromessage = {
            'message': "O servidor não suporta este processamento. Tente utilizar uma base de dados menor.",
        }
        return HttpResponse(render(request, "resultados.html", erromessage))

    except IOError as (errno, strerror):
        erromessage = {
            'message': "I/O error({0}): {1}".format(errno, strerror),
        }
        return HttpResponse(render(request, "resultados.html", erromessage))

    except ValueError:
        erromessage = {
            'message': "Os valores recebidos não correspondem ao esperado pelo sistema.",
        }
        return HttpResponse(render(request, "resultados.html", erromessage))

    except:
        erromessage = {
            'message': "Erro inesperado: "+str(sys.exc_info()[0]),
        }
        return HttpResponse(render(request, "resultados.html", erromessage))
        raise


def validacaoVisualizar(request):

    try:
        return render(request, "validacao.html")

    except IOError as (errno, strerror):
        erromessage = {
            'message': "I/O error({0}): {1}".format(errno, strerror),
        }
        return HttpResponse(render(request, "validacao.html", erromessage))

    except ValueError:
        erromessage = {
            'message': "Os valores recebidos não correspondem ao esperado pelo sistema.",
        }
        return HttpResponse(render(request, "validacao.html", erromessage))

    except:
        erromessage = {
            'message': "Erro inesperado: "+str(sys.exc_info()[0]),
        }
        return HttpResponse(render(request, "validacao.html", erromessage))
        raise

def validacao(request):

    try:
        is_upload = request.POST.get('is_upload')
        is_validacao = request.POST.get('is_validacao')

        if request.method == 'POST' and is_upload is None and is_validacao is None:
            def process(f):
                with open(pastaArquivos+'media/' + f.name,
                          'wb+') as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)

            for count, x in enumerate(request.FILES.getlist("files")):
                if "Verificado" in x.name:
                    process(x)

            # return HttpResponse('')
            return render(request, "validacao.html")

        elif request.method == 'POST' and is_upload == "false":
            caminho_motor = request.POST.get('caminho_motor')
            nome_da_base = request.POST.get('nome_da_base')
            periodo = request.POST.get('periodo')
            classificador = request.POST.get('classificador')

            context = {
                'caminho_base_treinada': caminho_motor,
                'nome_da_base': nome_da_base,
                'periodo': periodo,
                'classificador': classificador
            }

            return render(request, "validacao.html", context)

        elif request.method == 'POST' and is_validacao == "true":
            caminho_base_treinada = request.POST.get('caminho_base_treinada')
            nome_da_base = request.POST.get('nome_da_base')
            periodo_da_base = request.POST.get('periodo_da_base')
            classificador = request.POST.get('classificador')

            context = {
                'caminho_base_treinada': caminho_base_treinada,
                'nome_da_base': nome_da_base,
                'periodo': periodo_da_base,
                'classificador': classificador
            }

            return render(request, "validacao.html", context)

    except (MemoryError):
        erromessage = {
            'message': "O servidor não suporta este processamento. Tente utilizar uma base de dados menor.",
        }
        return HttpResponse(render(request, "validacao.html", erromessage))

    except IOError as (errno, strerror):
        erromessage = {
            'message': "I/O error({0}): {1}".format(errno, strerror),
        }
        return HttpResponse(render(request, "validacao.html", erromessage))

    except ValueError:
        erromessage = {
            'message': "Os valores recebidos não correspondem ao esperado pelo sistema.",
        }
        return HttpResponse(render(request, "validacao.html", erromessage))

    except:
        erromessage = {
            'message': "Erro inesperado: "+str(sys.exc_info()[0]),
        }
        return HttpResponse(render(request, "validacao.html", erromessage))
        raise

def validarArquivo(request):

    try:
        if request.is_ajax():
            # Informações do motor
            caminho_base_treinada = request.POST.get('caminho_base_treinada')
            nome_da_base_do_motor = request.POST.get('diario')
            periodo_motor = request.POST.get('periodo')
            classificador = request.POST.get('classifiedChoosed')

            periodo_motor = periodo_motor.replace(' - ', '_')
            periodo_motor = periodo_motor.split("_")
            inicio = periodo_motor[0]
            fim = periodo_motor[1]

            # TROCAR ESTE DIRETÓRIO PELO DA KURIER
            # caminho_etiquetas_validacao = 'C:/Users/kurier.juridico1/PycharmProjects/framework/arquivos/validacao/' + nome_da_base_do_motor + "_" + str(periodo_motor)

            # TROCAR ESTE DIRETÓRIO PELO DA KURIER (aqui ficará o arquivo VERIFICADO que o usuário subirá)
            caminhoArquivo = pastaArquivos+"media/"

            # Pegando as técnicas de pré-processamento a serem utilizadas
            consulta_tecnicas = FF.pegarTecnicasUtilizadas(nome_da_base_do_motor, inicio, fim)
            tecnicas_de_pp = consulta_tecnicas[0][0]
            tecnicas_de_pp = tecnicas_de_pp.split(',')

            # Inicializando técnicas de PP como False
            lematizacao = 'False'
            redesComplexas = 'False'
            removePontuacao = 'False'
            removeNumeros = 'False'
            stopWords = 'False'
            stemming = 'False'
            tokenizer = 'False'

            # Criando dicionário das técnicas utilizadas no PP do motor que foi treinado anteriormente
            dictTecnicasPP = {}

            # Setando as técnicas de PP para True, as que estiverem na lista de tecnicas_de_pp
            if "lematizacao" in tecnicas_de_pp:
                lematizacao = "True"
                dictTecnicasPP['lematizacao'] = True
            if "redesComplexas" in tecnicas_de_pp:
                redesComplexas = "True"
                dictTecnicasPP['redesComplexas'] = True
            if "removePontuacao" in tecnicas_de_pp:
                removePontuacao = "True"
                dictTecnicasPP['removePontuacao'] = True
            if "removeNumeros" in tecnicas_de_pp:
                removeNumeros = "True"
                dictTecnicasPP['removeNumeros'] = True
            if "stopWords" in tecnicas_de_pp:
                stopWords = "True"
                dictTecnicasPP['stopWords'] = True
            if "stemming" in tecnicas_de_pp:
                stemming = "True"
                dictTecnicasPP['stemming'] = True
            if "tokenizer" in tecnicas_de_pp:
                tokenizer = "True"
                dictTecnicasPP['tokenizer'] = True

            # Transformando o arquivo que será classificado
            ImportValidacao.transformarArquivo(caminhoArquivo, caminho_base_treinada, dictTecnicasPP)

            FF.apagarArquivosTxt(os.listdir(caminhoArquivo))

            return HttpResponse('')

    except (MemoryError):
        erromessage = {
            'message': "O servidor não suporta este processamento. Tente utilizar uma base de dados menor.",
        }
        return HttpResponse(render(request, "validacao.html", erromessage))

    except IOError as (errno, strerror):
        erromessage = {
            'message': "I/O error({0}): {1}".format(errno, strerror),
        }
        return HttpResponse(render(request, "validacao.html", erromessage))

    except ValueError:
        erromessage = {
            'message': "Os valores recebidos não correspondem ao esperado pelo sistema.",
        }
        return HttpResponse(render(request, "validacao.html", erromessage))

    except:
        erromessage = {
            'message': "Erro inesperado: "+str(sys.exc_info()[0]),
        }
        return HttpResponse(render(request, "validacao.html", erromessage))
        raise


def historico(request):

    try:
        if request.is_ajax():
            # TROCAR ESTE DIRETÓRIO PELO DA KURIER (Aqui estão armazenadas as informações das bases que já foram treinadas)
            pasta = pastaArquivos+'historico'

            info_bases_treinadas = FF.listarInfoBasesTreinadas(pasta)

            context = {
                'info_bases_treinadas': info_bases_treinadas
            }

            return HttpResponse(render(request, "historico.html", context))

    except IOError as (errno, strerror):
        erromessage = {
            'message': "I/O error({0}): {1}".format(errno, strerror),
        }
        return HttpResponse(render(request, "historico.html", erromessage))

    except ValueError:
        erromessage = {
            'message': "Os valores recebidos não correspondem ao esperado pelo sistema.",
        }
        return HttpResponse(render(request, "historico.html", erromessage))

    except:
        erromessage = {
            'message': "Erro inesperado: "+str(sys.exc_info()[0]),
        }
        return HttpResponse(render(request, "historico.html", erromessage))
        raise


def apagarTreinamento(request):

    try:
        if request.is_ajax():

            # TROCAR ESTE DIRETÓRIO PELO DA KURIER (Aqui estão armazenadas as informações das bases que já foram treinadas)
            pasta = pastaArquivos+'historico/'

            nome_arquivo_txt = request.POST.get('nome_arquivo_txt')

            print(nome_arquivo_txt)

            try:
                os.remove(pasta + nome_arquivo_txt)

            except Exception as error:
                traceback.print_exc()

            info_bases_treinadas = FF.listarInfoBasesTreinadas(pasta)

            context = {
                'info_bases_treinadas': info_bases_treinadas
            }

        return HttpResponse(render(request, "bases_treinadas_historico.html", context))

    except IOError as (errno, strerror):
        erromessage = {
            'message': "I/O error({0}): {1}".format(errno, strerror),
        }
        return HttpResponse(render(request, "bases_treinadas_historico.html", erromessage))

    except ValueError:
        erromessage = {
            'message': "Os valores recebidos não correspondem ao esperado pelo sistema.",
        }
        return HttpResponse(render(request, "bases_treinadas_historico.html", erromessage))

    except:
        erromessage = {
            'message': "Erro inesperado: "+str(sys.exc_info()[0]),
        }
        return HttpResponse(render(request, "bases_treinadas_historico.html", erromessage))
        raise





