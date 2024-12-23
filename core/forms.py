from django import forms
from .models import Document


# class DocumentForm(forms.ModelForm):
#     class Meta:
#         model = Document
#         fields = ('arquivo',)

# class InfoBases(forms.Form):
# 	name = forms.CharField(label='Nome', max_length=30)