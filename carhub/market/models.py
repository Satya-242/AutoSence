# In models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('APPROVED', 'Car Approved'),
        ('REJECTED', 'Car Rejected'),
        ('SOLD', 'Car Sold'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    car = models.ForeignKey('Car', on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.car.name}"

class Car(models.Model):
    FUEL_CHOICES = [
        ("Petrol", "Petrol"),
        ("Diesel", "Diesel"),
        ("CNG", "CNG"),
        ("Hybrid", "Hybrid"),
    ]
    TRANSMISSION_CHOICES = [
        ("Manual", "Manual"),
        ("Automatic", "Automatic"),
    ]
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("SOLD", "Sold"),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cars")
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchased_cars')
    name = models.CharField(max_length=120)
    year = models.PositiveIntegerField()
    mileage = models.FloatField(help_text="kmpl", null=True, blank=True)
    engine = models.FloatField(help_text="CC", null=True, blank=True)
    max_power = models.FloatField(help_text="BHP", null=True, blank=True)
    torque = models.FloatField(help_text="Nm", null=True, blank=True)
    fuel = models.CharField(max_length=12, choices=FUEL_CHOICES, default="Petrol")
    transmission = models.CharField(max_length=12, choices=TRANSMISSION_CHOICES, default="Manual")
    location = models.CharField(max_length=120, blank=True)
    expected_price = models.PositiveIntegerField()
    predicted_price = models.PositiveIntegerField(null=True, blank=True)
    image = models.ImageField(upload_to="car_images/", blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.year})"

    def mark_as_sold(self, buyer):
        self.status = "SOLD"
        self.buyer = buyer
        self.save()
        
        # Create sold notification
        Notification.objects.create(
            user=self.seller,
            car=self,
            notification_type='SOLD',
            message=f'Your car "{self.name}" has been sold to {buyer.get_full_name() or buyer.username}.'
        )

class Purchase(models.Model):
    car = models.OneToOneField(Car, on_delete=models.PROTECT, related_name="purchase")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="purchases")
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=32)
    address = models.TextField()
    agreed_terms = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Purchase #{self.id} - {self.car.name} by {self.buyer.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Mark car as sold when purchase is created
        if not self.car.status == 'SOLD':
            self.car.mark_as_sold(self.buyer)