from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)  # Expanded for hashed passwords
    email = models.EmailField(max_length=254, unique=True)  # Replaces 'gmail' with standard EmailField
    zone = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} - {self.zone}"