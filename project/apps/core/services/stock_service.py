from apps.core.models import StockMovement


class StockService:
    @staticmethod
    def convert_quantity_by_unit(unit: str, value):
        if unit in ["un", "pc", "cx"]:
            return int(value)
        return round(float(value), 2)

    @staticmethod
    def get_items_quantities(items):
        quantities = {item.id: 0 for item in items}
        movements = StockMovement.objects.filter(item__in=items)

        for movement in movements:
            if movement.movement_type == "IN":
                quantities[movement.item_id] += movement.quantity
            elif movement.movement_type == "OUT":
                quantities[movement.item_id] -= movement.quantity

        for item in items:
            quantities[item.id] = StockService.convert_quantity_by_unit(
                item.unit_of_measure, quantities[item.id]
            )

        return quantities
