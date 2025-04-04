from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q

from . import models
from perfil.models import Perfil
from .models import Category


# class store(ListView):
#     model = models.Produto
#     template_name = 'produto/store.html'
#     context_object_name = 'produtos'
#     paginate_by = 15
#     ordering = ['-id']

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['categories'] = Category.objects.all()
#         return context

# class Index(ListView):
#     model = models.Produto
#     template_name = 'produto/index.html'
#     context_object_name = 'produtos'
#     paginate_by = 10
#     ordering = ['-id']

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['categories'] = Category.objects.all()
#         return context
    
# class Carrinho(View):
#     def get(self, *args, **kwargs):
#         contexto = {
#             'carrinho': self.request.session.get('carrinho', {})
#         }

#         return render(self.request, 'produto/carrinho.html', contexto)

class Index(ListView):
    model = models.Produto
    template_name = 'produto/index.html'
    context_object_name = 'produtos'
    paginate_by = 10
    ordering = ['-id']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        # Adiciona o carrinho ao contexto
        context['carrinho'] = self.request.session.get('carrinho', {})
        context['favoritos'] = self.request.session.get('favoritos', {})  # Adiciona os favoritos  

        return context
    

class product(ListView):
    model = models.Produto
    template_name = 'produto/detalhe1.html'
    context_object_name = 'produtos'
    paginate_by = 10
    ordering = ['-id']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context
    
class checkout(ListView):
    model = models.Produto
    template_name = 'produto/checkout.html'
    context_object_name = 'produtos'
    paginate_by = 10
    ordering = ['-id']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['carrinho'] = self.request.session.get('carrinho', {})

        return context



class ListaProdutos(ListView):
    model = models.Produto
    template_name = 'produto/store.html'
    context_object_name = 'produtos'
    paginate_by = 10
    ordering = ['-id']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['carrinho'] = self.request.session.get('carrinho', {})

        return context


class Busca(ListaProdutos):
    def get_queryset(self, *args, **kwargs):
        termo = self.request.GET.get('termo') or self.request.session['termo']
        qs = super().get_queryset(*args, **kwargs)

        if not termo:
            return qs

        self.request.session['termo'] = termo

        qs = qs.filter(
            Q(nome__icontains=termo) |
            Q(descricao_curta__icontains=termo) |
            Q(descricao_longa__icontains=termo)
        )

        self.request.session.save()
        return qs


# class DetalheProduto(DetailView):
#     model = models.Produto
#     template_name = 'produto/detalhe.html'
#     context_object_name = 'produto'
#     slug_url_kwarg = 'slug'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         produto_atual = self.get_object()
        
#         # Busca 4 produtos quaisquer (excluindo o produto atual)
#         context['produtos'] = models.Produto.objects.exclude(
#             id=produto_atual.id
#         )[:4]  # Limita a 4 produtos
        
#         context['categories'] = Category.objects.all()
#         context['carrinho'] = self.request.session.get('carrinho', {})

#         return context

from django.views.generic.detail import DetailView
from . import models
from .models import Category


class DetalheProduto(DetailView):
    model = models.Produto
    template_name = 'produto/detalhe.html'
    context_object_name = 'produto'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        produto_atual = self.get_object()
        
        # Busca produtos relacionados (da mesma categoria, excluindo o atual)
        produtos_relacionados = models.Produto.objects.filter(
            category=produto_atual.category
        ).exclude(id=produto_atual.id)[:4]
        
        # Se não houver produtos suficientes na mesma categoria, complementa com outros
        if len(produtos_relacionados) < 4:
            outros_produtos = models.Produto.objects.exclude(
                id=produto_atual.id
            ).exclude(
                id__in=[p.id for p in produtos_relacionados]
            )[:4-len(produtos_relacionados)]
            
            context['produtos'] = list(produtos_relacionados) + list(outros_produtos)
        else:
            context['produtos'] = produtos_relacionados
        
        # Obtém todas as variações do produto, incluindo suas imagens
        variacoes = models.Variacao.objects.filter(produto=produto_atual).order_by('nome')
        context['variacoes'] = variacoes
        
        # Cria uma lista das imagens de todas as variações para o carrossel
        imagens_variacoes = []
        for variacao in variacoes:
            if variacao.imagem:
                imagens_variacoes.append(variacao.imagem.url)
        
        # Adiciona a imagem principal do produto se existir
        if produto_atual.imagem:
            if produto_atual.imagem.url not in imagens_variacoes:
                imagens_variacoes.insert(0, produto_atual.imagem.url)
        
        context['imagens_produto'] = imagens_variacoes
        context['categories'] = Category.objects.all()
        context['carrinho'] = self.request.session.get('carrinho', {})

        return context


class AdicionarAoCarrinho(View):
    def get(self, *args, **kwargs):
        request = self.request
        http_referer = request.META.get('HTTP_REFERER', reverse('produto:lista'))
        variacao_id = request.GET.get('vid')

        # Validação da quantidade
        try:
            quantidade = int(request.GET.get('quantidade', 1))
            if quantidade < 1:
                messages.error(request, 'A quantidade deve ser maior que zero.')
                return redirect(http_referer)
        except ValueError:
            messages.error(request, 'Quantidade inválida.')
            return redirect(http_referer)

        if not variacao_id:
            messages.error(request, 'Produto não existe')
            return redirect(http_referer)

        variacao = get_object_or_404(models.Variacao, id=variacao_id)
        variacao_estoque = variacao.estoque
        produto = variacao.produto

        if variacao.estoque < 1:
            messages.error(request, 'Estoque insuficiente')
            return redirect(http_referer)

        if not request.session.get('carrinho'):
            request.session['carrinho'] = {}
            request.session.save()

        carrinho = request.session['carrinho']

        if variacao_id in carrinho:
            quantidade_carrinho = carrinho[variacao_id]['quantidade'] + quantidade

            if variacao_estoque < quantidade_carrinho:
                messages.warning(
                    request,
                    f'Estoque insuficiente para {quantidade_carrinho}x do produto "{produto.nome}". '
                    f'Adicionamos {variacao_estoque}x no seu carrinho.'
                )
                quantidade_carrinho = variacao_estoque

            carrinho[variacao_id]['quantidade'] = quantidade_carrinho
            carrinho[variacao_id]['preco_quantitativo'] = variacao.preco * quantidade_carrinho
            carrinho[variacao_id]['preco_quantitativo_promocional'] = variacao.preco_promocional * quantidade_carrinho
        else:
            carrinho[variacao_id] = {
                'produto_id': produto.id,
                'produto_nome': produto.nome,
                'variacao_nome': variacao.nome or '',
                'variacao_id': variacao_id,
                'preco_unitario': variacao.preco,
                'preco_unitario_promocional': variacao.preco_promocional,
                'preco_quantitativo': variacao.preco * quantidade,
                'preco_quantitativo_promocional': variacao.preco_promocional * quantidade,
                'quantidade': quantidade,
                'slug': produto.slug,
                'imagem': produto.imagem.name if produto.imagem else '',
            }

        request.session.save()

        messages.success(
            request,
            f'Produto {produto.nome} {variacao.nome} adicionado ao seu '
            f'carrinho {carrinho[variacao_id]["quantidade"]}x.'
        )

        return redirect(http_referer)


class RemoverDoCarrinho(View):
    def get(self, *args, **kwargs):
        http_referer = self.request.META.get(
            'HTTP_REFERER',
            reverse('produto:lista')
        )
        variacao_id = self.request.GET.get('vid')

        if not variacao_id:
            return redirect(http_referer)

        if not self.request.session.get('carrinho'):
            return redirect(http_referer)

        if variacao_id not in self.request.session['carrinho']:
            return redirect(http_referer)

        carrinho = self.request.session['carrinho'][variacao_id]

        messages.success(
            self.request,
            f'Produto {carrinho["produto_nome"]} {carrinho["variacao_nome"]} '
            f'removido do seu carrinho.'
        )

        del self.request.session['carrinho'][variacao_id]
        self.request.session.save()
        return redirect(http_referer)


class Carrinho(View):
    def get(self, *args, **kwargs):
        contexto = {
            'carrinho': self.request.session.get('carrinho', {})
        }

        return render(self.request, 'produto/carrinho.html', contexto)
    


class Favoritos(View):
    def get(self, request, *args, **kwargs):
        contexto = {
            'favoritos': request.session.get('favoritos', {})
        }
        return render(request, 'produto/favoritos.html', contexto)


from django.http import JsonResponse

class AdicionarFavorito(View):
    def post(self, request, *args, **kwargs):
        produto_id = str(request.POST.get('produto_id'))  # ID do produto enviado via POST
        favoritos = request.session.get('favoritos', {})

        if produto_id in favoritos:
            del favoritos[produto_id]  # Remove dos favoritos se já estiver lá
            mensagem = "Removido dos favoritos"
        else:
            favoritos[produto_id] = {'produto_id': produto_id}
            mensagem = "Adicionado aos favoritos"

        request.session['favoritos'] = favoritos  # Atualiza a session
        return JsonResponse({'mensagem': mensagem, 'favoritos_count': len(favoritos)})


class ResumoDaCompra(View):
    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')

        perfil = Perfil.objects.filter(usuario=self.request.user).exists()

        if not perfil:
            messages.error(
                self.request,
                'Usuário sem perfil.'
            )
            return redirect('perfil:criar')

        if not self.request.session.get('carrinho'):
            messages.error(
                self.request,
                'Carrinho vazio.'
            )
            return redirect('produto:lista')

        contexto = {
            'usuario': self.request.user,
            'carrinho': self.request.session['carrinho'],
        }

        return render(self.request, 'produto/resumodacompra.html', contexto)