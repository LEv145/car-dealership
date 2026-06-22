from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.db.models import Model, Q, QuerySet
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.views.generic.base import TemplateView

from .forms import (
    BuyerForm,
    CarForm,
    ColorForm,
    CountryForm,
    FirmForm,
    ProductForm,
    SaleActForm,
    SellerForm,
)
from .models import Buyer, Car, Color, Country, Firm, Product, SaleAct, Seller


@dataclass(frozen=True)
class TableColumn:
    title: str
    accessor: str


@dataclass(frozen=True)
class RelatedLink:
    title: str
    url: str


class AccessorResolverMixin:
    def resolve_accessor(self, obj: Model, accessor: str) -> Any:
        value: Any = obj
        for part in accessor.split("."):
            value = getattr(value, part)
        return value

    def format_value(self, value: Any) -> Any:
        if isinstance(value, bool):
            return "Да" if value else "Нет"
        if value is None:
            return "-"
        return value


class HomeView(TemplateView):
    template_name = "dealership/home.html"


class BaseEntityListView(AccessorResolverMixin, ListView[Model]):
    template_name = "dealership/generic_list.html"
    paginate_by = 20
    columns: tuple[TableColumn, ...] = ()
    title: str = ""
    create_url_name: str = ""
    search_param: str = "q"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        object_list = context.get("object_list", [])

        context["title"] = self.title
        context["columns"] = self.columns
        context["create_url"] = reverse(self.create_url_name)
        context["search_query"] = self._get_search_query()
        context["table_rows"] = self._build_table_rows(object_list)

        return context

    def _get_search_query(self) -> str:
        value = self.request.GET.get(self.search_param, "")
        return value.strip()

    def _get_filter_value(self, name: str) -> str:
        return self.request.GET.get(name, "").strip()

    def _apply_search(
        self,
        queryset: QuerySet[Any],
        lookup: str,
    ) -> QuerySet[Any]:
        query = self._get_search_query()
        if not query:
            return queryset
        return queryset.filter(**{lookup: query})

    def _build_table_rows(self, object_list: list[Model]) -> list[dict[str, Any]]:
        return [
            {
                "object": obj,
                "cells": [
                    self.format_value(self.resolve_accessor(obj, column.accessor))
                    for column in self.columns
                ],
            }
            for obj in object_list
        ]


class BaseEntityDetailView(AccessorResolverMixin, DetailView[Model]):
    template_name = "dealership/generic_detail.html"
    title: str = ""
    fields_map: tuple[tuple[str, str], ...] = ()
    update_url_name: str = ""
    delete_url_name: str = ""
    related_getters: tuple[str, ...] = ()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        obj = self.object

        context["title"] = self.title
        context["field_rows"] = [
            (label, self.format_value(self.resolve_accessor(obj, accessor)))
            for label, accessor in self.fields_map
        ]
        context["update_url"] = reverse(self.update_url_name, kwargs={"pk": obj.pk})
        context["delete_url"] = reverse(self.delete_url_name, kwargs={"pk": obj.pk})
        context["related_links"] = self._build_related_links(obj)

        return context

    def _build_related_links(self, obj: Model) -> list[RelatedLink]:
        links: list[RelatedLink] = []
        for related_getter_name in self.related_getters:
            getter = getattr(self, related_getter_name)
            links.extend(getter(obj))
        return links


class BaseEntityCreateView(CreateView[Model, Any]):
    template_name = "dealership/generic_form.html"
    title: str = ""
    submit_label: str = "Создать"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["submit_label"] = self.submit_label
        return context


class BaseEntityUpdateView(UpdateView[Model, Any]):
    template_name = "dealership/generic_form.html"
    title: str = ""
    submit_label: str = "Сохранить"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["submit_label"] = self.submit_label
        return context


class BaseEntityDeleteView(DeleteView[Model, Any]):
    template_name = "dealership/generic_confirm_delete.html"
    title: str = ""
    success_url: Any

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        return context


class CountryListView(BaseEntityListView):
    model = Country
    title = "Страны"
    create_url_name = "dealership:country-create"
    columns = (TableColumn("ID", "id"), TableColumn("Название", "name"))

    def get_queryset(self) -> QuerySet[Country]:
        queryset = Country.objects.all()
        return self._apply_search(queryset, "name__icontains")


class CountryDetailView(BaseEntityDetailView):
    model = Country
    title = "Страна"
    fields_map = (("ID", "id"), ("Название", "name"))
    update_url_name = "dealership:country-update"
    delete_url_name = "dealership:country-delete"


class CountryCreateView(BaseEntityCreateView):
    model = Country
    form_class = CountryForm
    title = "Добавить страну"


class CountryUpdateView(BaseEntityUpdateView):
    model = Country
    form_class = CountryForm
    title = "Редактировать страну"


class CountryDeleteView(BaseEntityDeleteView):
    model = Country
    title = "Удалить страну"
    success_url = reverse_lazy("dealership:country-list")


class ColorListView(BaseEntityListView):
    model = Color
    title = "Цвета"
    create_url_name = "dealership:color-create"
    columns = (
        TableColumn("ID", "id"),
        TableColumn("Название", "name"),
        TableColumn("HEX", "hex"),
    )

    def get_queryset(self) -> QuerySet[Color]:
        queryset = Color.objects.all()
        return self._apply_search(queryset, "name__icontains")


class ColorDetailView(BaseEntityDetailView):
    model = Color
    title = "Цвет"
    fields_map = (("ID", "id"), ("Название", "name"), ("HEX", "hex"))
    update_url_name = "dealership:color-update"
    delete_url_name = "dealership:color-delete"


class ColorCreateView(BaseEntityCreateView):
    model = Color
    form_class = ColorForm
    title = "Добавить цвет"


class ColorUpdateView(BaseEntityUpdateView):
    model = Color
    form_class = ColorForm
    title = "Редактировать цвет"


class ColorDeleteView(BaseEntityDeleteView):
    model = Color
    title = "Удалить цвет"
    success_url = reverse_lazy("dealership:color-list")


class FirmListView(BaseEntityListView):
    model = Firm
    title = "Фирмы"
    create_url_name = "dealership:firm-create"
    columns = (
        TableColumn("ID", "id"),
        TableColumn("Название", "name"),
        TableColumn("Страна", "country.name"),
    )

    def get_queryset(self) -> QuerySet[Firm]:
        queryset = Firm.objects.select_related("country")
        queryset = self._apply_search(queryset, "name__icontains")

        country_id = self._get_filter_value("country")
        if country_id:
            queryset = queryset.filter(country_id=country_id)

        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["countries"] = Country.objects.all()
        context["selected_country"] = self._get_filter_value("country")
        return context


class FirmDetailView(BaseEntityDetailView):
    model = Firm
    title = "Фирма"
    fields_map = (("ID", "id"), ("Название", "name"), ("Страна", "country.name"))
    update_url_name = "dealership:firm-update"
    delete_url_name = "dealership:firm-delete"


class FirmCreateView(BaseEntityCreateView):
    model = Firm
    form_class = FirmForm
    title = "Добавить фирму"


class FirmUpdateView(BaseEntityUpdateView):
    model = Firm
    form_class = FirmForm
    title = "Редактировать фирму"


class FirmDeleteView(BaseEntityDeleteView):
    model = Firm
    title = "Удалить фирму"
    success_url = reverse_lazy("dealership:firm-list")


class SellerListView(BaseEntityListView):
    model = Seller
    title = "Продавцы"
    create_url_name = "dealership:seller-create"
    columns = (TableColumn("ID", "id"), TableColumn("Имя", "name"))

    def get_queryset(self) -> QuerySet[Seller]:
        queryset = Seller.objects.all()
        return self._apply_search(queryset, "name__icontains")


class SellerDetailView(BaseEntityDetailView):
    model = Seller
    title = "Продавец"
    fields_map = (("ID", "id"), ("Имя", "name"))
    update_url_name = "dealership:seller-update"
    delete_url_name = "dealership:seller-delete"


class SellerCreateView(BaseEntityCreateView):
    model = Seller
    form_class = SellerForm
    title = "Добавить продавца"


class SellerUpdateView(BaseEntityUpdateView):
    model = Seller
    form_class = SellerForm
    title = "Редактировать продавца"


class SellerDeleteView(BaseEntityDeleteView):
    model = Seller
    title = "Удалить продавца"
    success_url = reverse_lazy("dealership:seller-list")


class BuyerListView(BaseEntityListView):
    model = Buyer
    title = "Покупатели"
    create_url_name = "dealership:buyer-create"
    columns = (TableColumn("ID", "id"), TableColumn("Имя", "name"))

    def get_queryset(self) -> QuerySet[Buyer]:
        queryset = Buyer.objects.all()
        return self._apply_search(queryset, "name__icontains")


class BuyerDetailView(BaseEntityDetailView):
    model = Buyer
    title = "Покупатель"
    fields_map = (("ID", "id"), ("Имя", "name"))
    update_url_name = "dealership:buyer-update"
    delete_url_name = "dealership:buyer-delete"


class BuyerCreateView(BaseEntityCreateView):
    model = Buyer
    form_class = BuyerForm
    title = "Добавить покупателя"


class BuyerUpdateView(BaseEntityUpdateView):
    model = Buyer
    form_class = BuyerForm
    title = "Редактировать покупателя"


class BuyerDeleteView(BaseEntityDeleteView):
    model = Buyer
    title = "Удалить покупателя"
    success_url = reverse_lazy("dealership:buyer-list")


class CarListView(BaseEntityListView):
    model = Car
    title = "Автомобили"
    create_url_name = "dealership:car-create"
    columns = (
        TableColumn("ID", "id"),
        TableColumn("Модель", "model"),
        TableColumn("Фирма", "firm.name"),
        TableColumn("Страна", "country.name"),
        TableColumn("Цвет", "color.name"),
        TableColumn("Год", "release_year"),
    )

    def get_queryset(self) -> QuerySet[Car]:
        queryset = Car.objects.select_related("firm", "country", "color")
        queryset = self._apply_search(queryset, "model__icontains")

        firm_id = self._get_filter_value("firm")
        color_id = self._get_filter_value("color")

        if firm_id:
            queryset = queryset.filter(firm_id=firm_id)
        if color_id:
            queryset = queryset.filter(color_id=color_id)

        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["firms"] = Firm.objects.all()
        context["colors"] = Color.objects.all()
        context["selected_firm"] = self._get_filter_value("firm")
        context["selected_color"] = self._get_filter_value("color")
        return context


class CarDetailView(BaseEntityDetailView):
    model = Car
    title = "Автомобиль"
    fields_map = (
        ("ID", "id"),
        ("Модель", "model"),
        ("Фирма", "firm.name"),
        ("Страна", "country.name"),
        ("Цвет", "color.name"),
        ("Мощность", "engine_power"),
        ("Длина", "length"),
        ("Ширина", "width"),
        ("Год выпуска", "release_year"),
    )
    update_url_name = "dealership:car-update"
    delete_url_name = "dealership:car-delete"


class CarCreateView(BaseEntityCreateView):
    model = Car
    form_class = CarForm
    title = "Добавить автомобиль"


class CarUpdateView(BaseEntityUpdateView):
    model = Car
    form_class = CarForm
    title = "Редактировать автомобиль"


class CarDeleteView(BaseEntityDeleteView):
    model = Car
    title = "Удалить автомобиль"
    success_url = reverse_lazy("dealership:car-list")


class ProductListView(BaseEntityListView):
    model = Product
    title = "Товары"
    create_url_name = "dealership:product-create"
    columns = (
        TableColumn("ID", "id"),
        TableColumn("Автомобиль", "car"),
        TableColumn("Цена", "price"),
        TableColumn("Продан", "is_sold"),
    )

    def get_queryset(self) -> QuerySet[Product]:
        queryset = Product.objects.select_related("car", "car__firm")
        queryset = self._apply_search(queryset, "car__model__icontains")

        sold = self._get_filter_value("sold")
        if sold == "yes":
            queryset = queryset.filter(sale_acts__isnull=False).distinct()
        elif sold == "no":
            queryset = queryset.filter(sale_acts__isnull=True)

        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["selected_sold"] = self._get_filter_value("sold")
        return context


class ProductDetailView(BaseEntityDetailView):
    model = Product
    title = "Товар"
    fields_map = (
        ("ID", "id"),
        ("Автомобиль", "car"),
        ("Цена", "price"),
        ("Продан", "is_sold"),
    )
    update_url_name = "dealership:product-update"
    delete_url_name = "dealership:product-delete"


class ProductCreateView(BaseEntityCreateView):
    model = Product
    form_class = ProductForm
    title = "Добавить товар"


class ProductUpdateView(BaseEntityUpdateView):
    model = Product
    form_class = ProductForm
    title = "Редактировать товар"


class ProductDeleteView(BaseEntityDeleteView):
    model = Product
    title = "Удалить товар"
    success_url = reverse_lazy("dealership:product-list")


class SaleActListView(BaseEntityListView):
    model = SaleAct
    title = "Акты продажи"
    create_url_name = "dealership:sale-act-create"
    columns = (
        TableColumn("ID", "id"),
        TableColumn("Дата", "buy_at"),
        TableColumn("Товар", "product"),
        TableColumn("Покупатель", "buyer.name"),
        TableColumn("Продавец", "seller.name"),
    )

    def get_queryset(self) -> QuerySet[SaleAct]:
        queryset = SaleAct.objects.select_related(
            "product",
            "product__car",
            "product__car__firm",
            "buyer",
            "seller",
        )
        queryset = self._apply_search(queryset, "product__car__model__icontains")

        seller_id = self._get_filter_value("seller")
        if seller_id:
            queryset = queryset.filter(seller_id=seller_id)

        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["sellers"] = Seller.objects.all()
        context["selected_seller"] = self._get_filter_value("seller")
        return context


class SaleActDetailView(BaseEntityDetailView):
    model = SaleAct
    title = "Акт продажи"
    fields_map = (
        ("ID", "id"),
        ("Дата и время", "buy_at"),
        ("Товар", "product"),
        ("Покупатель", "buyer.name"),
        ("Продавец", "seller.name"),
    )
    update_url_name = "dealership:sale-act-update"
    delete_url_name = "dealership:sale-act-delete"


class SaleActCreateView(BaseEntityCreateView):
    model = SaleAct
    form_class = SaleActForm
    title = "Добавить акт продажи"

    def get_form(self, form_class: type[SaleActForm] | None = None) -> SaleActForm:
        form = super().get_form(form_class)
        form.fields["product"].queryset = self._get_available_products()
        return form

    def _get_available_products(self) -> QuerySet[Product]:
        return Product.objects.select_related("car", "car__firm").filter(
            sale_acts__isnull=True,
        )


class SaleActUpdateView(BaseEntityUpdateView):
    model = SaleAct
    form_class = SaleActForm
    title = "Редактировать акт продажи"

    def get_form(self, form_class: type[SaleActForm] | None = None) -> SaleActForm:
        form = super().get_form(form_class)
        form.fields["product"].queryset = self._get_available_products()
        return form

    def _get_available_products(self) -> QuerySet[Product]:
        return Product.objects.select_related("car", "car__firm").filter(
            Q(sale_acts__isnull=True) | Q(pk=self.object.product_id),
        ).distinct()


class SaleActDeleteView(BaseEntityDeleteView):
    model = SaleAct
    title = "Удалить акт продажи"
    success_url = reverse_lazy("dealership:sale-act-list")
