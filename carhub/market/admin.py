from django.contrib import admin
from .models import Car

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "year", "seller", "expected_price", "status", "created_at")
    list_filter = ("status", "fuel", "transmission", "year")
    search_fields = ("name", "seller__username", "location")
