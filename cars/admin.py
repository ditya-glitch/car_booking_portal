from django.contrib import admin
from django.utils.html import format_html

from .models import Car, Booking


# =====================================================
# CAR ADMIN
# =====================================================

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):

    list_display = (
        "car_image_preview",
        "car_name",
        "brand",
        "model",
        "category",
        "fuel_type",
        "transmission",
        "price_per_day",
        "location",
        "available",
        "created_at",
    )

    list_filter = (
        "category",
        "fuel_type",
        "transmission",
        "available",
    )

    search_fields = (
        "car_name",
        "brand",
        "model",
        "location",
    )

    list_editable = (
        "price_per_day",
        "available",
    )

    readonly_fields = (
        "car_image_preview",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 20


    # =================================================
    # IMAGE PREVIEW
    # =================================================

    @admin.display(description="Image")
    def car_image_preview(self, obj):

        if obj.car_image:

            return format_html(
                '<img src="{}" width="80" height="55" '
                'style="object-fit:cover; border-radius:6px;" />',
                obj.car_image.url
            )

        return "No Image"


# =====================================================
# BOOKING ADMIN
# =====================================================

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = (
        "booking_id",
        "customer_name",
        "customer_email",
        "customer_phone",
        "car",
        "pickup_date",
        "return_date",
        "total_days",
        "total_price",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "pickup_date",
        "return_date",
        "created_at",
    )

    search_fields = (
        "booking_id",
        "customer_name",
        "customer_email",
        "customer_phone",
        "car__car_name",
        "car__brand",
    )

    list_editable = (
        "status",
    )

    readonly_fields = (
        "booking_id",
        "total_days",
        "total_price",
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 20