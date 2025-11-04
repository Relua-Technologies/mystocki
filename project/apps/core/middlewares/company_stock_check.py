from django.core.exceptions import PermissionDenied
from apps.core.models import Stock


class CompanyStockCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        if user.is_authenticated:
            company = getattr(user, "company", None)

            if not company:
                raise PermissionDenied("User has no associated company.")

            has_stock = Stock.objects.filter(company=company).exists()
            if not has_stock:
                raise PermissionDenied("The company has no stock registered.")

        return self.get_response(request)
