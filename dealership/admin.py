from __future__ import annotations

from django.contrib import admin

from .models import Buyer, Car, Color, Country, Firm, Product, SaleAct, Seller


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "hex")
    search_fields = ("name", "hex")


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Firm)
class FirmAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "country")
    search_fields = ("name", "country__name")
    list_filter = ("country",)


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "model",
        "firm",
        "country",
        "color",
        "release_year",
        "engine_power",
    )
    search_fields = ("model", "firm__name", "country__name", "color__name")
    list_filter = ("firm", "country", "color", "release_year")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "car", "price")
    search_fields = ("car__model", "car__firm__name")
    list_filter = ("car__firm",)


@admin.register(SaleAct)
class SaleActAdmin(admin.ModelAdmin):
    list_display = ("id", "buy_at", "product", "buyer", "seller")
    search_fields = (
        "product__car__model",
        "product__car__firm__name",
        "buyer__name",
        "seller__name",
    )
    list_filter = ("buy_at", "seller", "buyer")
