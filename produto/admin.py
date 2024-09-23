from django.contrib import admin
from .forms import VariacaoObrigatoria
from . import models
from django.utils.html import format_html



class VariacaoInline(admin.TabularInline):
    model = models.Variacao
    formset = VariacaoObrigatoria
    min_num = 1
    extra = 0
    can_delete = True


class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao_curta', 'get_preco_formatado', 'get_preco_promocional_formatado', 'imagem_preview']
    
    def imagem_preview(self, obj):
        if obj.imagem:
            return format_html('<img src="{}" style="max-width: 100px; max-height: 100px;" />', obj.imagem.url)
        return "Nenhuma imagem"
    
    imagem_preview.short_description = "Preview da Imagem"

class CategoryAdmin(admin.ModelAdmin):
    list_display = 'name',
    ordering = '-id',

admin.site.register(models.Produto, ProdutoAdmin)
admin.site.register(models.Variacao)
admin.site.register(models.Category)
