from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.db import models

class Document(models.Model):
    description = models.CharField(max_length=255, blank=True)
    arquivo = models.FileField(upload_to="media/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Technics(models.Model):
    stopWords = models.BooleanField(default=True)
    stemming = models.BooleanField(default=True)
    tokenizer = models.BooleanField(default=True)
    suavizacao = models.BooleanField(default=True)
    # n = models.IntegerField(default=1)