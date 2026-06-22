from __future__ import annotations

from django import forms
from django.core.exceptions import ValidationError

from .models import Buyer, Car, Color, Country, Firm, Product, SaleAct, Seller


class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ["name"]


class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ["name", "hex"]

        widgets = {
            "hex": forms.ColorInput(),
        }


class SellerForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ["name"]


class BuyerForm(forms.ModelForm):
    class Meta:
        model = Buyer
        fields = ["name"]


class FirmForm(forms.ModelForm):
    class Meta:
        model = Firm
        fields = ["name", "country"]


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            "model",
            "engine_power",
            "length",
            "width",
            "release_year",
            "firm",
            "country",
            "color",
        ]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["price", "car"]


class SaleActForm(forms.ModelForm):
    class Meta:
        model = SaleAct
        fields = ["buy_at", "product", "buyer", "seller"]
        widgets = {
            "buy_at": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    'class': 'form-control'
                },
                format="%Y-%m-%dT%H:%M",
            )
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.select_related("car", "car__firm")
