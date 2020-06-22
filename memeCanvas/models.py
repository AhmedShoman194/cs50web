from django.db import models
from django.conf import settings

# Create your models here.

class Meme(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    topText = models.TextField()
    topTextSize = models.DecimalField(max_digits=4, decimal_places=2)
    bottomText = models.TextField()
    bottomTextSize = models.DecimalField(max_digits=4, decimal_places=2)
    temp = models.ImageField(upload_to='memes/')
