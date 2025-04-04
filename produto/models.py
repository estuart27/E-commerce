from django.conf import settings
import os
from PIL import Image
from django.db import models
from django.utils.text import slugify
from utils import utils


class Category(models.Model):
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def __str__(self) -> str:
        return self.name


class Produto(models.Model):
    nome = models.CharField(max_length=255)
    descricao_curta = models.TextField(max_length=255)
    descricao_longa = models.TextField()
    imagem = models.ImageField(upload_to='imagens/', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    preco_marketing = models.FloatField(verbose_name='Preço')
    preco_marketing_promocional = models.FloatField(default=0, verbose_name='Preço Promo.')
    tipo = models.CharField(default='V', max_length=1, choices=(('V', 'Variável'), ('S', 'Simples'),))
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, blank=True, null=True)
    
    @property
    def percentual_desconto(self):
        if self.preco_marketing_promocional:
            return int(100 - (self.preco_marketing_promocional * 100 / self.preco_marketing))
        return 0

    def get_preco_formatado(self):
        return utils.formata_preco(self.preco_marketing)
    get_preco_formatado.short_description = 'Preço'

    def get_preco_promocional_formatado(self):
        return utils.formata_preco(self.preco_marketing_promocional)
    get_preco_promocional_formatado.short_description = 'Preço Promo.'

    @staticmethod
    def resize_image(img, new_width=800):
        img_full_path = os.path.join(settings.MEDIA_ROOT, img.name)
        img_pil = Image.open(img_full_path)
        original_width, original_height = img_pil.size

        if original_width <= new_width:
            img_pil.close()
            return

        new_height = round((new_width * original_height) / original_width)
        new_img = img_pil.resize((new_width, new_height), Image.LANCZOS)
        new_img.save(img_full_path, optimize=True, quality=50)
        img_pil.close()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)

        super().save(*args, **kwargs)

        max_image_size = 800

        if self.imagem:
            self.resize_image(self.imagem, max_image_size)

    def __str__(self):
        return self.nome


class Variacao(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    nome = models.CharField(max_length=50, blank=True, null=True)
    preco = models.FloatField()
    preco_promocional = models.FloatField(default=0)
    estoque = models.PositiveIntegerField(default=100)
    imagem = models.ImageField(upload_to='variacoes/', blank=True, null=True)
    cor = models.CharField(max_length=50, blank=True, null=True)
    tamanho = models.CharField(max_length=50, blank=True, null=True)
    
    @property
    def percentual_desconto(self):
        if self.preco_promocional:
            return int(100 - (self.preco_promocional * 100 / self.preco))
        return 0
    
    def get_preco_formatado(self):
        return utils.formata_preco(self.preco)
    
    def get_preco_promocional_formatado(self):
        return utils.formata_preco(self.preco_promocional)
    
    @staticmethod
    def resize_image(img, new_width=800):
        img_full_path = os.path.join(settings.MEDIA_ROOT, img.name)
        img_pil = Image.open(img_full_path)
        original_width, original_height = img_pil.size

        if original_width <= new_width:
            img_pil.close()
            return

        new_height = round((new_width * original_height) / original_width)
        new_img = img_pil.resize((new_width, new_height), Image.LANCZOS)
        new_img.save(img_full_path, optimize=True, quality=50)
        img_pil.close()
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        max_image_size = 800
        
        if self.imagem:
            self.resize_image(self.imagem, max_image_size)

    def __str__(self):
        if self.nome:
            return f"{self.produto.nome} - {self.nome}"
        return self.produto.nome

    class Meta:
        verbose_name = 'Variação'
        verbose_name_plural = 'Variações'

