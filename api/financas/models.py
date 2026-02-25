from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

# lidar com imagens
from PIL import Image
import os
from io import BytesIO
from django.core.files.base import ContentFile


class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=1, choices=(('E','Entrada'),('S','Saída')))
    descricao = models.TextField(blank=True)   
    icone = models.ImageField(upload_to='categorias/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    class Meta:
        ordering = ['nome']
        unique_together = ('nome', 'created_by')
    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)

            if self.icone:
                img = Image.open(self.icone)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                width, height = img.size
                min_dim = min(width, height)
                left = (width - min_dim) // 2
                top = (height - min_dim) // 2
                right = (width + min_dim) // 2
                bottom = (height + min_dim) // 2
                img = img.crop((left, top, right, bottom))
                img = img.resize((60, 60), Image.Resampling.LANCZOS)
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=85, optimize=True)
                buffer.seek(0)
                self.icone.save(
                    self.icone.name,
                    ContentFile(buffer.read()),
                    save=False
                )
                super().save(update_fields=['icone'])
        except Exception as e:
            print(f"[ERRO] Falha ao otimizar imagem: {e}")

    def __str__(self):    
        return self.nome  
    
class Movimentacao(models.Model):
    tipo = models.CharField(max_length=1, choices=(('E','Entrada'),('S','Saída')))
    valor = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    data = models.DateField()
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    descricao = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    
    def clean(self):    
        if self.categoria.tipo != self.tipo:
            raise ValidationError("Tipo da categoria incompatível com a movimentação.")
        super().clean()

    class Meta:
        ordering = ['-data']
        indexes = [
            models.Index(fields=['data']),
            models.Index(fields=['created_by']),
            models.Index(fields=['tipo']),
        ]
    def __str__(self):
        return f"{self.valor} - {self.tipo} - {self.data} - {self.categoria} - {self.descricao}"

class MovimentacaoRecorrente(models.Model):
    FREQUENCIA_CHOICES = (
        ('M', 'Mensal'),
        ('A', 'Anual'),
        ('S', 'Semanal'),
        ('D', 'Diária')
    )
    frequencia = models.CharField(max_length=1, choices=FREQUENCIA_CHOICES)
    tipo = models.CharField(max_length=1, choices=(('E','Entrada'),('S','Saída')))
    valor = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    descricao = models.TextField(blank=True)
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    ativa = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

    def clean(self):
        if self.categoria.tipo != self.tipo:
            raise ValidationError("Tipo da categoria incompatível com a movimentação recorrente.")
        if self.data_fim and self.data_fim < self.data_inicio:
            raise ValidationError("Data fim não pode ser menor que data início.")
        super().clean()

    class Meta:
        ordering = ['-data_inicio']
    
    def __str__(self):
        return f"{self.valor} - {self.data_inicio} - {self.data_fim} - {self.categoria} - {self.descricao}"