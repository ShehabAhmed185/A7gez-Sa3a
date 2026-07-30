from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone_number', 'username', 'password', 'email', 'zone']

    def validate_email(self, value):
        if Customer.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A customer with this email already exists.")
        return value

    def validate_username(self, value):
        if Customer.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def create(self, validated_data):
        # Hash the password before saving
        validated_data['password'] = make_password(validated_data['password'])
        return Customer.objects.create(**validated_data)


from django.contrib.auth.hashers import check_password


class CustomerLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        try:
            customer = Customer.objects.get(username__iexact=username)
        except Customer.DoesNotExist:
            raise serializers.ValidationError("Invalid username or password.")

        if not check_password(password, customer.password):
            raise serializers.ValidationError("Invalid username or password.")

        data['customer'] = customer
        return data