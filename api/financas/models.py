from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError


class Icone(models.Model):
    nome = models.CharField(max_length=100)
    classe_css = models.CharField(max_length=100)  # ex: "pi pi-wallet"
    categoria_visual = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    class Meta:
        ordering = ['nome']
        unique_together = ('nome', 'created_by')
    def __str__(self):
        return self.nome

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=1, choices=(('E','Entrada'),('S','Saída')))
    descricao = models.TextField(blank=True)   
    icone = models.ForeignKey(Icone, on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    class Meta:
        ordering = ['nome']
        unique_together = ('nome', 'created_by')   
    def __str__(self):           
        if self.icone:
            return f"{self.nome} - {self.icone.nome}"
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


class Meta(models.Model):
    PRIORIDADE_CHOICES = (
        ('R', 'Rápida'),
        ('M', 'Média'),
        ('L', 'Longa'),
    )
    nome = models.CharField(max_length=120)
    valor_meta = models.DecimalField(max_digits=12, decimal_places=2)
    data_meta = models.DateField()
    prioridade = models.CharField(max_length=1, choices=PRIORIDADE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    concluida = models.BooleanField(default=False)

    class Meta:
        ordering = ['-data_meta']
        indexes = [
            models.Index(fields=['data_meta']),
            models.Index(fields=['created_by']),
            models.Index(fields=['prioridade']),
        ]
    def __str__(self):
        return f"{self.nome} - {self.valor_meta} - {self.data_meta} - {self.prioridade}"


class ConsolidadoMensal(models.Model):
    ano = models.IntegerField()
    mes = models.IntegerField()
    total_entradas = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_saidas = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    class Meta:
        unique_together = ('ano', 'mes', 'created_by')
    def __str__(self):
        return f"{self.ano} - {self.mes} - {self.total_entradas} - {self.total_saidas}"


