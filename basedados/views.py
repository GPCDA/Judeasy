# coding: utf-8

from django.shortcuts import render

from .models import BaseDados

# Create your views here.

# Isso aqui é insignificante, pois preciso transferir as informações daqui para o template "index.html" da aplicação "core"

# Importando informações da base de dados para a view
# def index(request):
# 	bases = BaseDados.objects.all()
# 	template_name = "templates/index.html"
# 	context = {
# 		'bases': bases
# 	}

# 	return render(request, template_name, context) 