from apps.core.views.item.base import BaseItemView
from apps.core.views.utils.base import BaseListView
from apps.core.services.stock_service import StockService


class ItemListView(BaseItemView, BaseListView):
    list_display = [
        "code",
        "name",
        "unit_of_measure",
        "sale_price",
        "quantity",
    ]
    search_fields = ["code", "name", "unit_of_measure", "sale_price"]

    def get_objects_with_values(self, object_list):
        context_data = super().get_objects_with_values(object_list)
        quantities = StockService.get_items_quantities([obj["object"] for obj in context_data])

        for obj in context_data:
            item = obj["object"]
            try:
                quantity_index = self.list_display.index("quantity")
                obj["values"][quantity_index] = quantities.get(item.id, 0)
            except ValueError:
                pass

        return context_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "list_display" in context:
            display = context["list_display"]
            if len(display) == len(self.list_display):
                display[-1] = "Quantidade"
            context["list_display"] = display
        return context
