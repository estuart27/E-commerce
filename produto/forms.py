from django.forms.models import BaseInlineFormSet
from django import forms
from .models import Produto
from supabase import create_client, Client

url = 'https://tqcxzefejgyitlnzdncp.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInRxY3h6ZWZlamd5aXRsbnpkbmNwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjU5MTgxNzQsImV4cCI6MjA0MTQ5NDE3NH0.m09ci5J3_PHObVv3U8NY2ZeMmhCQHDzLTbmGtsecvBE'

supabase: Client = create_client(url, key)

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'descricao_curta', 'imagem']  # Adicione outros campos conforme necessário

    def save(self, commit=True):
        produto = super().save(commit=False)
        
        # Verifique se a imagem foi fornecida
        imagem = self.cleaned_data.get('imagem_url')
        if imagem:
            # Envie a imagem para o Supabase e obtenha a URL
            resposta = supabase.storage.from_("your_bucket_name").upload(f"produto_imagens/{imagem.name}", imagem)
            produto.imagem_url = resposta.data['Key']  # Ajuste de acordo com a resposta do Supabase
            
        if commit:
            produto.save()
        return produto
class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            'nome', 
            'descricao_curta', 
            'descricao_longa', 
            'imagem', 
            'slug', 
            'preco_marketing', 
            'preco_marketing_promocional', 
            'tipo', 
            'category'
        ]


class VariacaoObrigatoria(BaseInlineFormSet):
    def _construct_form(self, i, **kwargs):
        form = super(VariacaoObrigatoria, self)._construct_form(i, **kwargs)
        form.empty_permitted = False
        return form
    

