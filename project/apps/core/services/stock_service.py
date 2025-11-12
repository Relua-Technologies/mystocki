from apps.core.models import StockMovement


class StockService:
    @staticmethod
    def convert_quantity_by_unit(unit: str, value):
        if unit in ["un", "pc", "cx"]:
            return int(value)
        return round(float(value), 2)

    @staticmethod
    def _calculate_total_quantities(items):
        if not isinstance(items, (list, tuple, set)):
            items = [items]

        quantities = {item.id: 0 for item in items}
        movements = StockMovement.objects.filter(item__in=items)

        for movement in movements:
            if movement.movement_type == "IN":
                quantities[movement.item_id] += movement.quantity
            elif movement.movement_type == "OUT":
                quantities[movement.item_id] -= movement.quantity

        return quantities

    @staticmethod
    def get_items_quantities(items):
        raw_quantities = StockService._calculate_total_quantities(items)
        for item in items:
            raw_quantities[item.id] = StockService.convert_quantity_by_unit(
                item.unit_of_measure, raw_quantities[item.id]
            )
        return raw_quantities

    @staticmethod
    def get_item_quantity(item):
        total = StockService._calculate_total_quantities(item)[item.id]
        return StockService.convert_quantity_by_unit(item.unit_of_measure, total)
