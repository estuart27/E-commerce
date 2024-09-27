from django.forms.models import BaseInlineFormSet
from django import forms
from django import forms
from django.core.exceptions import ValidationError
from supabase import create_client, Client
from .models import Produto  # Importe seu modelo Produto

# Supabase settings
url = "https://tqcxzefejgyitlnzdncp.supabase.co"
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxY3h6ZWZlamd5aXRsbnpkbmNwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjU5MTgxNzQsImV4cCI6MjA0MTQ5NDE3NH0.m09ci5J3_PHObVv3U8NY2ZeMmhCQHDzLTbmGtsecvBE'
supabase: Client = create_client(url, key)

SUPABASE_BUCKET = 'media'  # Nome do bucket no Supabase Storage


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
            'category',
        ]

    def clean_imagem(self):
        imagem = self.cleaned_data.get('imagem')

        if not imagem:
            raise ValidationError("Nenhuma imagem fornecida")
        return imagem

    def save(self, commit=True):
        # Salva o produto normalmente primeiro, sem a imagem
        produto = super().save(commit=False)

        # Upload da imagem para o Supabase
        imagem = self.cleaned_data.get('imagem')

        if imagem:
            # Carregar a imagem no Supabase
            supabase_storage = supabase.storage().from_(SUPABASE_BUCKET)

            # Defina o caminho no bucket e o nome do arquivo da imagem
            image_path = f'produtos/{imagem.name}'

            # Envia a imagem para o Supabase Storage
            response = supabase_storage.upload(image_path, imagem)

            if response['error']:
                raise ValidationError(f"Erro ao enviar imagem para Supabase: {response['error']['message']}")

            # Recupera a URL pública da imagem armazenada no Supabase
            public_url = supabase_storage.get_public_url(image_path)

            # Salva a URL pública da imagem no campo do modelo
            produto.imagem = public_url['data']['publicURL']

        # Se commit=True, salva o objeto no banco de dados
        if commit:
            produto.save()

        return produto




class VariacaoObrigatoria(BaseInlineFormSet):
    def _construct_form(self, i, **kwargs):
        form = super(VariacaoObrigatoria, self)._construct_form(i, **kwargs)
        form.empty_permitted = False
        return form
    



