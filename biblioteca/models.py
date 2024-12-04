from django.db import models
from site_principal.models import CustomUser 

class Partitura(models.Model):
    partitura = models.ImageField(upload_to='partituras/', default="media/mini-imagem1.png")
    nome = models.CharField(max_length=150)
    clave = models.CharField(max_length=10)
    tempo = models.CharField(max_length=10)
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='partituras')

    def __str__(self) -> str:
        return self.nome
    
    class Meta:
        db_table = 'biblioteca_partitura'  # Especifica o novo nome da tabela
