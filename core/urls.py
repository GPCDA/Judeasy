from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^database/', views.database, name="database"),
    url(r'^pp/', views.pp, name="pp"),
    url(r'^transformarBase/', views.transformarBase, name='transformarBase'),
    url(r'^excluirBase/', views.excluirBase, name='excluirBase'),
    url(r'^treinamento/', views.treinamento, name='treinamento'),
    url(r'^resultados/', views.resultados, name='resultados'),
    url(r'^validacao/', views.validacao, name='validacao'),
    url(r'^validacaoVisualizar/', views.validacaoVisualizar, name='validacaoVisualizar'),
    url(r'^validarArquivo/', views.validarArquivo, name='validarArquivo'),
    url(r'^buscarBasesTreinadas/', views.buscarBasesTreinadas, name='buscarBasesTreinadas'),
    url(r'^historico/', views.historico, name='historico'),
    url(r'^abrirTxtResultados/', views.abrirTxtResultados, name='abrirTxtResultados'),
    url(r'^apagarTreinamento/', views.apagarTreinamento, name='apagarTreinamento'),
    url(r'^ensembleDinamico/', views.ensembleDinamico, name='ensembleDinamico'),
    url(r'^ensembleClassico/', views.ensembleClassico, name='ensembleClassico'),
    url(r'^geraPDF/', views.geraPDF, name='geraPDF'),
]
