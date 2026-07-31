from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Booking(models.Model):
    # Foreign key to Field model
    field = models.ForeignKey(
        'FiveSideFootball.Field',  # Replace 'Field' with your actual app_label if different
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    # Foreign key to Customer model (optional/nullable)
    # customer = models.ForeignKey(
    #     'Customer.Customer',  # Replace 'Customer' with your actual app_label if different
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name='bookings'
    # )

    # Date of the reservation
    date = models.DateField()

    # List/Array storing reserved hours (e.g., [14, 15, 16] for 2 PM to 5 PM)
    # Starts empty/free [] by default
    reserved_hours = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensures only one booking record per field per date
        unique_together = ('field', 'date')

    # def __str__(self):
    #     customer_name = self.customer if self.customer else "Guest"
    #     return f"Booking: {self.field} on {self.date} by {customer_name}"