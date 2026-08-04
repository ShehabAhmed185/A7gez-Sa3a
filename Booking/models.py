from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class Booking(models.Model):
    # Foreign key to Field model
    field = models.ForeignKey(
        'FiveSideFootball.Field',  # Replace 'Field' with your actual app_label if different
        on_delete=models.CASCADE,
        related_name='bookings'
    )

   

    # Date of the reservation
    date = models.DateField()
    reservationCode = models.CharField(max_length=50)


    # List/Array storing reserved hours (e.g., [14, 15, 16] for 2 PM to 5 PM)
    # Starts empty/free [] by default
    reserved_hours = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensures only one booking record per field per date
        unique_together = ('field', 'date')


from django.db import models
from django.core.validators import MinValueValidator

class MoneyCalc(models.Model):
    owner = models.OneToOneField(
        "FieldOwner.FieldOwner",
        on_delete=models.CASCADE,
        related_name="money_calc",
    )

    total_reserved_hours = models.PositiveIntegerField(default=0)

    company_rate_per_hour = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
    )

    total_company_money = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
    )

    updated_at = models.DateTimeField(auto_now=True)


    def add_reservation(self, hours_count=1, rate_per_hour=None):
        if rate_per_hour is None:
            rate_per_hour = self.company_rate_per_hour

        self.total_reserved_hours += hours_count
        self.total_company_money = Decimal(self.total_company_money) + (
            Decimal(hours_count) * Decimal(rate_per_hour)
        )

        self.company_rate_per_hour = Decimal(rate_per_hour)

        self.save()