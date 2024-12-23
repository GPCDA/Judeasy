# coding: utf-8
from django.db import models

# Create your models here.

class BaseManager(models.Manager):

	# Fazendo uma busca com a lógica "or"
	# def search(self, query):
	# 	return self.get_queryset().filter(
	# 		models.Q(name__icontains=query) | \
	# 		models.Q(qtdProcessos__icontains=query)
	# 	)

	# Chamada da função "visualizar base", buscando na base de dados pelo nome
	def search(self, queryName, queryBegin, queryEnd):
		return self.get_queryset().filter(
			name__icontains=queryName,
			inicio__icontains=queryBegin,
			fim__icontains=queryEnd
		)

class BaseDados(models.Model):

	objects = BaseManager()
	
	name = models.CharField("Nome", max_length=100)
	slug = models.AutoField(primary_key=True)
	inicio = models.CharField("Início", max_length=10, default='')
	fim = models.CharField("Fim", max_length=10, default='')
	quantidade_de_processos = models.IntegerField("Quantidade de processos", blank=False, null=False, default=0)
	pre_processada = models.CharField("Pre-Processada", max_length=4, blank=True, null=True)

	nomes_das_etiquetas = models.CharField("Etiquetas", max_length=300, default='')
	quantidade_de_instancias = models.CharField("Quantidades das Instâncias", max_length=300, default='')
	tamanho_dos_arquivos = models.CharField("Tamanhos dos arquivos", max_length=300, default='')
	etiquetas_pre_processadas = models.CharField("Etiquetas Pre-Processadas", max_length=300, blank=True, null=True)
	tecnicas_pre_processamento = models.CharField("Técnicas de pré-processamento", max_length=300, blank=True, null=True)


	#created_at = models.DateTimeField("Criado em", auto_now_add=True)

	#updated_at = models.DateTimeField('Atualizado em', auto_now=True)

	# Definindo algumas alterações no admin do Django

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "Base"
		verbose_name_plural = "Bases"
		ordering = ['slug']
