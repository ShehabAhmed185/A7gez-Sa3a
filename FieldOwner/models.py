from django.db import models

class FieldOwner(models.Model):
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(max_length=254, unique=True)

    def __str__(self):
        return f"Owner: {self.name}"