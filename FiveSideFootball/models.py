from django.db import models

class Field(models.Model):
    field_name = models.CharField(max_length=50)
    code = models.CharField(max_length=15, unique=True)
    
    # ForeignKey to the Club model in another app
    club = models.ForeignKey(
        'clubs_app.Club',  # Replace 'clubs_app' with your actual app label!
        on_delete=models.CASCADE,
        related_name="fields"
    )
    
    # Hourly price in EGP (DecimalField is ideal for prices)
    hour_rate = models.DecimalField(max_digits=8, decimal_places=2) 

    def __str__(self):
        return f"{self.club.title} - {self.field_name}"