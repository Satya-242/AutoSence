from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Car

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            "name", "year", "mileage", "engine", "max_power", "torque",
            "fuel", "transmission", "location", "expected_price", "image"
        ]

class PredictForm(forms.Form):
    km_driven = forms.IntegerField(label="Kilometers Driven")
    fuel = forms.IntegerField(label="Fuel (encoded number)")
    seller_type = forms.IntegerField(label="Seller Type (encoded number)")
    transmission = forms.IntegerField(label="Transmission (encoded number)")
    owner = forms.IntegerField(label="Owner (encoded number)")
    mileage = forms.FloatField(label="Mileage")
    engine = forms.FloatField(label="Engine (CC)")
    max_power = forms.FloatField(label="Max Power (bhp)")
    torque = forms.FloatField(label="Torque (numeric)")
    seats = forms.IntegerField(label="Seats")
    Age = forms.IntegerField(label="Car Age")

class PurchaseForm(forms.Form):
    full_name = forms.CharField(max_length=120)
    email = forms.EmailField()
    phone = forms.CharField(max_length=32)
    address = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}))
    agreed_terms = forms.BooleanField(label="I agree to the terms and confirm this purchase")