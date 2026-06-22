from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class Country(models.Model):
    name = models.CharField("Название страны", max_length=255, unique=True)

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("dealership:country-detail", kwargs={"pk": self.pk})


class Color(models.Model):
    name = models.CharField("Название цвета", max_length=255, unique=True)
    hex = models.CharField("HEX-код", max_length=7)

    class Meta:
        verbose_name = "Цвет"
        verbose_name_plural = "Цвета"
        ordering = ["name"]

    def clean(self) -> None:
        super().clean()
        if not self.hex.startswith("#") or len(self.hex) != 7:
            raise ValidationError({"hex": "HEX-код должен быть в формате #RRGGBB."})

    def __str__(self) -> str:
        return f"{self.name} ({self.hex})"

    def get_absolute_url(self) -> str:
        return reverse("dealership:color-detail", kwargs={"pk": self.pk})


class Seller(models.Model):
    name = models.CharField("Имя продавца", max_length=255)

    class Meta:
        verbose_name = "Продавец"
        verbose_name_plural = "Продавцы"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("dealership:seller-detail", kwargs={"pk": self.pk})


class Buyer(models.Model):
    name = models.CharField("Имя покупателя", max_length=255)

    class Meta:
        verbose_name = "Покупатель"
        verbose_name_plural = "Покупатели"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("dealership:buyer-detail", kwargs={"pk": self.pk})


class Firm(models.Model):
    name = models.CharField("Название фирмы", max_length=255, unique=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="firms",
        verbose_name="Страна",
    )

    class Meta:
        verbose_name = "Фирма"
        verbose_name_plural = "Фирмы"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("dealership:firm-detail", kwargs={"pk": self.pk})


class Car(models.Model):
    model = models.CharField("Модель", max_length=255)
    engine_power = models.DecimalField(
        "Мощность двигателя",
        max_digits=12,
        decimal_places=3,
    )
    length = models.DecimalField("Длина", max_digits=12, decimal_places=3)
    width = models.DecimalField("Ширина", max_digits=12, decimal_places=3)
    release_year = models.PositiveIntegerField("Год выпуска")
    firm = models.ForeignKey(
        Firm,
        on_delete=models.PROTECT,
        related_name="cars",
        verbose_name="Фирма",
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="cars",
        verbose_name="Страна",
    )
    color = models.ForeignKey(
        Color,
        on_delete=models.PROTECT,
        related_name="cars",
        verbose_name="Цвет",
    )

    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"
        ordering = ["model", "release_year"]

    def clean(self) -> None:
        super().clean()
        if self.engine_power <= Decimal("0"):
            raise ValidationError({"engine_power": "Мощность должна быть больше 0."})
        if self.length <= Decimal("0"):
            raise ValidationError({"length": "Длина должна быть больше 0."})
        if self.width <= Decimal("0"):
            raise ValidationError({"width": "Ширина должна быть больше 0."})

    def __str__(self) -> str:
        return f"{self.firm.name} ({self.model})"

    def get_absolute_url(self) -> str:
        return reverse("dealership:car-detail", kwargs={"pk": self.pk})


class Product(models.Model):
    price = models.DecimalField("Цена", max_digits=12, decimal_places=3)
    car = models.ForeignKey(
        Car,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Автомобиль",
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["-price", "id"]

    def clean(self) -> None:
        super().clean()
        if self.price <= Decimal("0"):
            raise ValidationError({"price": "Цена должна быть больше 0."})

    def __str__(self) -> str:
        return f"{self.car}: {self.price}₽"

    def get_absolute_url(self) -> str:
        return reverse("dealership:product-detail", kwargs={"pk": self.pk})

    @property
    def is_sold(self) -> bool:
        return self.sale_acts.exists()


class SaleAct(models.Model):
    buy_at = models.DateTimeField("Дата и время покупки")
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="sale_acts",
        verbose_name="Товар",
    )
    buyer = models.ForeignKey(
        Buyer,
        on_delete=models.PROTECT,
        related_name="sale_acts",
        verbose_name="Покупатель",
    )
    seller = models.ForeignKey(
        Seller,
        on_delete=models.PROTECT,
        related_name="sale_acts",
        verbose_name="Продавец",
    )

    class Meta:
        verbose_name = "Акт продажи"
        verbose_name_plural = "Акты продажи"
        ordering = ["-buy_at"]

    def clean(self):
        super().clean()

        if not self.product_id:
            return

        query = SaleAct.objects.filter(product_id=self.product_id)

        if self.pk:
            query = query.exclude(pk=self.pk)

        if query.exists():
            raise ValidationError(
                {"product": "Данный товар уже продан."}
            )

    def __str__(self) -> str:
        return f"Продажа #{self.pk}"

    def get_absolute_url(self) -> str:
        return reverse("dealership:sale-act-detail", kwargs={"pk": self.pk})
