from django.db import models

class Club(models.Model):
    # Reference model as 'app_label.ModelName' string
    owner = models.ForeignKey(
        'FieldOwner.FieldOwner',  # Replace 'owners_app' with your actual app name!
        on_delete=models.CASCADE,
        related_name="clubs"
    )

    title = models.CharField(max_length=50)
    code = models.CharField(max_length=15, unique=True)
    zone = models.CharField(max_length=50)
    address = models.CharField(max_length=150)
    num_of_fields = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.title} ({self.zone})"


class ClubImage(models.Model):
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(upload_to="clubs/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.club.title} - Image {self.id}"