from django.forms.models import BaseInlineFormSet
from django import forms
from .models import Produto
import requests
from django.core.exceptions import ValidationError

SUPABASE_URL = 'https://tqcxzefejgyitlnzdncp.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxY3h6ZWZlamd5aXRsbnpkbmNwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjU5MTgxNzQsImV4cCI6MjA0MTQ5NDE3NH0.m09ci5J3_PHObVv3U8NY2ZeMmhCQHDzLTbmGtsecvBE'
SUPABASE_BUCKET = 'media'  


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

    def save(self, commit=True):
        produto = super().save(commit=False)
        imagem = self.cleaned_data.get('imagem')
        
        if imagem:
            # URL para upload da imagem no Supabase
            upload_url = f'{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/produto_imagens/{imagem.name}'
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/octet-stream"
            }

            try:
                # Fazendo o upload da imagem
                response = requests.post(upload_url, headers=headers, files={"file": imagem})

                # Debugging: Print da resposta para análise
                print(f"Status Code: {response.status_code}")
                print(f"Response Text: {response.text}")

                # Verificar se o upload foi bem-sucedido
                if response.status_code != 200:
                    # Levantar erro detalhado caso o upload falhe
                    raise ValidationError(f"Erro ao fazer upload da imagem: {response.json()}")

                # Definir a URL da imagem no produto
                produto.imagem_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/produto_imagens/{imagem.name}"
            
            except requests.exceptions.RequestException as e:
                # Tratamento de exceções de rede
                raise ValidationError(f"Erro de rede ao fazer upload da imagem: {str(e)}")
            except Exception as e:
                # Tratamento de qualquer outro tipo de exceção
                raise ValidationError(f"Erro inesperado ao fazer upload da imagem: {str(e)}")

        # Salvar o produto se `commit` for True
        if commit:
            produto.save()
        return produto



class VariacaoObrigatoria(BaseInlineFormSet):
    def _construct_form(self, i, **kwargs):
        form = super(VariacaoObrigatoria, self)._construct_form(i, **kwargs)
        form.empty_permitted = False
        return form
    

