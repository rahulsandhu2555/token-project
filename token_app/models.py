from django.db import models

class Tokens(models.Model):
    token = models.CharField(max_length=50)
    user = models.IntegerField(null=True)
    time = models.DateTimeField()