from rest_framework import serializers
from .models import Booking
from FiveSideFootball.models import Field  # Replace 'Field' with your actual app name if different
from Customer.models import Customer  # Replace 'Customer' with your actual app name if different

class BookingSerializer(serializers.ModelSerializer):
    # Allow passing field ID and customer ID explicitly
    field_id = serializers.PrimaryKeyRelatedField(
        queryset=Field.objects.all(), 
        source='field', 
        write_only=True
    )
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(), 
        source='customer', 
        required=False, 
        allow_null=True, 
        write_only=True
    )

    # List of hours being booked/reserved (e.g., [14, 15, 16])
    hours_to_reserve = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=23),
        write_only=True,
        required=True,
        help_text="List of integer hours between 0 and 23 to reserve."
    )

    class Meta:
        model = Booking
        fields = [
            'id',
            'field',
            'field_id',
            'customer',
            'customer_id',
            'date',
            'reserved_hours',
            'hours_to_reserve',
            'created_at'
        ]
        read_only_fields = ['id', 'field', 'customer', 'reserved_hours', 'created_at']

    def validate(self, attrs):
        field = attrs.get('field')
        date = attrs.get('date')
        hours_to_reserve = attrs.get('hours_to_reserve', [])

        if not hours_to_reserve:
            raise serializers.ValidationError({"hours_to_reserve": "You must select at least one hour to reserve."})

        # Check if a booking record already exists for this field on this date
        existing_booking = Booking.objects.filter(field=field, date=date).first()

        if existing_booking:
            already_reserved = existing_booking.reserved_hours
            # Find any overlap between requested hours and already reserved hours
            conflict_hours = set(hours_to_reserve).intersection(set(already_reserved))
            
            if conflict_hours:
                raise serializers.ValidationError({
                    "hours_to_reserve": f"The following hour(s) are already reserved: {sorted(list(conflict_hours))}"
                })

        return attrs

    def create(self, validated_data):
        field = validated_data['field']
        date = validated_data['date']
        customer = validated_data.get('customer', None)
        hours_to_reserve = validated_data.pop('hours_to_reserve')

        # Get existing booking or prepare a new instance
        booking, created = Booking.objects.get_or_create(
            field=field,
            date=date,
            defaults={'customer': customer, 'reserved_hours': []}
        )

        # Merge new hours and sort them
        updated_hours = sorted(list(set(booking.reserved_hours + hours_to_reserve)))
        booking.reserved_hours = updated_hours
        
        # Update customer if provided
        if customer:
            booking.customer = customer

        booking.save()
        return booking