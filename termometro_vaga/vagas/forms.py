from django import forms
from .models import Candidato

class InscricaoForm(forms.ModelForm):
    class Meta:
        model = Candidato
        fields = ['nome', 'email', 'cpf', 'tipo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Seu nome completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'voce@email.com'}),
            'cpf': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '000.000.000-00'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_cpf(self):
        cpf = self.cleaned_data['cpf']
        cpf_limpo = cpf.replace('.', '').replace('-', '').strip()
        if not cpf_limpo.isdigit() or len(cpf_limpo) != 11:
            raise forms.ValidationError('CPF inválido. Use 11 dígitos.')
        return cpf_limpo