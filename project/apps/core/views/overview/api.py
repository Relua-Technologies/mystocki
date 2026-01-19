from django.http import JsonResponse
from django.views import View
from django.conf import settings
from apps.core.services.sale_service import SaleService
import traceback
import logging

logger = logging.getLogger(__name__)


class OverviewStatsAPIView(View):
    
    def get(self, request, *args, **kwargs):
        try:
            period = request.GET.get('period', 'last_month')
            
            revenue = SaleService.get_sales_total_amount(period=period)
            costs, costs_is_reliable = SaleService.get_total_costs(period=period)
            profit, profit_is_reliable = SaleService.get_total_profit(period=period)
            sales_count = SaleService.get_sales_count(period=period)
            items_sold = SaleService.get_items_sold_count(period=period)
            items_null_price = SaleService.get_items_with_null_price(period=period)
            top_products = SaleService.get_top_5_products(period=period)
            top_customers = SaleService.get_top_5_customers(period=period)
            chart_type = request.GET.get('chart_type', 'revenue')
            period_revenue = SaleService.get_period_chart_data(chart_type=chart_type, period=period)
            
            missing_costs_message = 'Dados de custos incompletos. Algumas movimentações de entrada do período não possuem preço de compra cadastrado.' if not costs_is_reliable else None
            missing_profit_message = 'Dados incompletos para cálculo do lucro. Alguns itens vendidos não possuem informações de preço de compra cadastradas nas movimentações de estoque, tornando o cálculo do lucro impreciso.' if not profit_is_reliable else None
            
            return JsonResponse({
                'revenue': float(revenue or 0),
                'costs': float(costs),
                'costs_is_reliable': costs_is_reliable,
                'profit': float(profit),
                'profit_is_reliable': profit_is_reliable,
                'has_missing_costs': not profit_is_reliable,
                'missing_costs_message': missing_profit_message or missing_costs_message,
                'sales_count': sales_count or 0,
                'items_sold': items_sold or 0,
                'items_null_price': items_null_price or [],
                'top_products': top_products or [],
                'top_customers': top_customers or [],
                'period_revenue': period_revenue or {'labels': [], 'values': []},
                'period': period
            })
        except Exception as e:
            logger.error(f'Error in OverviewStatsAPIView: {str(e)}', exc_info=True)
            error_response = {'error': 'Internal server error'}
            if settings.DEBUG:
                error_response['details'] = str(e)
                error_response['traceback'] = traceback.format_exc()
            return JsonResponse(error_response, status=500)

