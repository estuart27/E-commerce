from django.contrib import admin
from .forms import VariacaoObrigatoria # Certifique-se de incluir ProdutoForm
from . import models


class VariacaoInline(admin.TabularInline):
    model = models.Variacao
    formset = VariacaoObrigatoria
    min_num = 1
    extra = 0
    can_delete = True


class ProdutoAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 
        'descricao_curta', 
        'get_preco_formatado', 
        'get_preco_promocional_formatado', 
        'tipo', 
        'category', 
        'slug'
    ]
    search_fields = ['nome', 'slug']
    list_filter = ['tipo', 'category']
    prepopulated_fields = {'slug': ('nome',)}  # Preenche automaticamente o campo slug
    ordering = ['nome']

    inlines = [VariacaoInline]

    def get_preco_formatado(self, obj):
        return obj.get_preco_formatado()
    get_preco_formatado.short_description = 'Preço'

    def get_preco_promocional_formatado(self, obj):
        return obj.get_preco_promocional_formatado()
    get_preco_promocional_formatado.short_description = 'Preço Promo.'


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image')

admin.site.register(models.Produto, ProdutoAdmin)
admin.site.register(models.Variacao)
admin.site.register(models.Category, CategoryAdmin)  # Registrar CategoryAdmin se for usado
