from datetime import datetime, timedelta, time as dt_time
from calendar import monthrange
from django.db.models import Sum, F, Q, Count, Avg
from django.utils import timezone
from django.db.models.functions import TruncDate, TruncDay, TruncWeek, TruncMonth, TruncYear
from apps.core.models import Sale, SaleItem, StockMovement


class PeriodConstants:
    TODAY = 'today'
    THIS_WEEK = 'this_week'
    THIS_MONTH = 'this_month'
    THIS_YEAR = 'this_year'
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    YEAR = 'year'


class MovementType:
    IN = 'IN'
    OUT = 'OUT'


class ChartType:
    REVENUE = 'revenue'
    COSTS = 'costs'
    PROFIT = 'profit'
    SALES_COUNT = 'sales_count'
    ITEMS_SOLD = 'items_sold'


class DateFormats:
    DAY_FULL = '%d/%m/%Y'
    DAY_SHORT = '%d/%m'
    MONTH = '%m/%Y'
    YEAR = '%Y'


class Localization:
    WEEKDAYS = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    MONTHS = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
              'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']


class DateRangeCalculator:
    
    @staticmethod
    def calculate(period):
        today = timezone.now().date()
        
        if period in (PeriodConstants.TODAY, PeriodConstants.DAY):
            return today, today
        
        elif period in (PeriodConstants.THIS_WEEK, PeriodConstants.WEEK):
            days_since_monday = today.weekday()
            start_date = today - timedelta(days=days_since_monday)
            return start_date, today
        
        elif period in (PeriodConstants.THIS_MONTH, PeriodConstants.MONTH):
            start_date = today.replace(day=1)
            last_day = monthrange(today.year, today.month)[1]
            end_date = today.replace(day=last_day)
            return start_date, end_date
        
        elif period in (PeriodConstants.THIS_YEAR, PeriodConstants.YEAR):
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
            return start_date, end_date
        
        return None, None
    
    @staticmethod
    def to_datetime_range(start_date, end_date):
        start_datetime = datetime.combine(start_date, dt_time.min) if start_date else None
        end_datetime = datetime.combine(end_date, dt_time.max) if end_date else None
        return start_datetime, end_datetime


class DateFormatter:
    
    @staticmethod
    def format_day_label(date_obj):
        date_str = date_obj.strftime(DateFormats.DAY_FULL)
        weekday_index = date_obj.weekday()
        weekday_name = Localization.WEEKDAYS[weekday_index]
        return f"{date_str}\n({weekday_name})"
    
    @staticmethod
    def format_week_label(week_start_date):
        week_end_date = week_start_date + timedelta(days=6)
        start_str = week_start_date.strftime('%d/%m')
        end_str = week_end_date.strftime('%d/%m')
        return f"{start_str} - {end_str}"
    
    @staticmethod
    def format_month_label(date_obj):
        month_year = date_obj.strftime(DateFormats.MONTH)
        month_name = Localization.MONTHS[date_obj.month]
        return f"{month_year} ({month_name})"
    
    @staticmethod
    def format_year_label(year):
        return str(year)


class CostCalculator:
    
    @staticmethod
    def calculate_item_average_cost_until_date(item_id, date_limit):
        try:
            date_limit = CostCalculator._normalize_date(date_limit)
            date_limit_datetime = datetime.combine(date_limit, dt_time.max)
            
            movements = StockMovement.objects.filter(
                item_id=item_id,
                movement_type=MovementType.IN,
                total_purchase_price__isnull=False,
                total_purchase_price__gt=0,
                created__lte=date_limit_datetime
            ).order_by('-created_at')
            
            if not movements.exists():
                return 0.0
            
            total_cost = 0.0
            total_quantity = 0.0
            
            for movement in movements:
                if movement.total_purchase_price and movement.quantity:
                    try:
                        movement_cost = float(movement.total_purchase_price)
                        movement_quantity = float(movement.quantity)
                        
                        if movement_quantity > 0 and movement_cost > 0:
                            total_cost += movement_cost
                            total_quantity += movement_quantity
                    except (ValueError, TypeError):
                        continue
            
            if total_quantity > 0 and total_cost > 0:
                return float(total_cost / total_quantity)
            
            return 0.0
        except Exception:
            return 0.0
    
    @staticmethod
    def _normalize_date(date_limit):
        if isinstance(date_limit, str):
            return datetime.strptime(date_limit, '%Y-%m-%d').date()
        if hasattr(date_limit, 'date'):
            return date_limit.date()
        return date_limit


class PurchaseCostCalculator:
    
    @staticmethod
    def calculate_period_costs(start_date=None, end_date=None, period=None):
        try:
            if period:
                start_date, end_date = DateRangeCalculator.calculate(period)
            
            filter_kwargs = {
                'movement_type': MovementType.IN,
                'total_purchase_price__isnull': False
            }
            
            if start_date:
                start_datetime, _ = DateRangeCalculator.to_datetime_range(start_date, start_date)
                filter_kwargs['created__gte'] = start_datetime
            
            if end_date:
                _, end_datetime = DateRangeCalculator.to_datetime_range(end_date, end_date)
                filter_kwargs['created__lte'] = end_datetime
            
            movements = StockMovement.objects.filter(**filter_kwargs)
            
            if not movements.exists():
                return 0.0, True
            
            total_cost = 0.0
            total_movements = 0
            movements_with_cost = 0
            
            for movement in movements:
                total_movements += 1
                if movement.total_purchase_price and movement.total_purchase_price > 0:
                    movements_with_cost += 1
                    total_cost += float(movement.total_purchase_price)
            
            is_reliable = total_movements > 0 and movements_with_cost == total_movements
            return float(total_cost), is_reliable
            
        except Exception:
            return 0.0, False


class SoldItemsCostCalculator:
    
    @staticmethod
    def calculate(start_date=None, end_date=None, period=None):
        try:
            sales = SaleService._get_filtered_sales(start_date, end_date, period)
            sale_items = SaleItem.objects.filter(sale__in=sales).select_related('item', 'sale')
            
            if not sale_items.exists():
                return 0.0, True
            
            if period:
                _, end_date = DateRangeCalculator.calculate(period)
            
            total_cost = 0.0
            items_costs = {}
            total_items = 0
            items_with_cost = 0
            items_with_sale_price = 0
            
            for sale_item in sale_items:
                item_id = sale_item.item_id
                sale_quantity = float(sale_item.quantity) if sale_item.quantity else 0.0
                sale_date = sale_item.sale.date if sale_item.sale.date else (end_date if end_date else None)
                total_items += 1
                
                if sale_item.item.sale_price and sale_item.item.sale_price > 0:
                    items_with_sale_price += 1
                
                if sale_date:
                    cache_key = f"{item_id}_{sale_date}"
                    if cache_key not in items_costs:
                        items_costs[cache_key] = CostCalculator.calculate_item_average_cost_until_date(
                            item_id, sale_date
                        )
                    
                    item_cost = items_costs[cache_key]
                    
                    if item_cost and item_cost > 0:
                        items_with_cost += 1
                        total_cost += float(item_cost) * sale_quantity
                    else:
                        total_cost += 0.0
            
            is_reliable = (total_items > 0 and 
                          items_with_cost == total_items and 
                          items_with_sale_price == total_items)
            
            return float(total_cost), is_reliable
            
        except Exception:
            return 0.0, False


class RevenueCalculator:
    
    @staticmethod
    def calculate_sale_item_total(sale_item):
        if not sale_item.item.sale_price:
            return 0.0
        
        sale_price = float(sale_item.item.sale_price)
        discount = float(sale_item.discount) if sale_item.discount else 0.0
        quantity = float(sale_item.quantity) if sale_item.quantity else 0.0
        
        return (sale_price - discount) * quantity
    
    @staticmethod
    def calculate_total(start_date=None, end_date=None, period=None):
        sales = SaleService._get_filtered_sales(start_date, end_date, period)
        sale_items = SaleItem.objects.filter(sale__in=sales).select_related('item')
        
        total = 0.0
        for sale_item in sale_items:
            total += RevenueCalculator.calculate_sale_item_total(sale_item)
        
        return total


class ChartDataCalculator:
    
    @staticmethod
    def get_period_config(period):
        sales = Sale.objects.all()
        
        if period in (PeriodConstants.TODAY, PeriodConstants.DAY):
            return {
                'trunc_field': 'day',
                'date_format': DateFormats.DAY_FULL,
                'period_sales': sales.annotate(day=TruncDay('date')).values('day').annotate(
                    count=Count('id')
                ).order_by('day')
            }
        
        elif period in (PeriodConstants.THIS_WEEK, PeriodConstants.WEEK):
            return {
                'trunc_field': 'week',
                'date_format': DateFormats.DAY_SHORT,
                'period_sales': sales.annotate(week=TruncWeek('date')).values('week').annotate(
                    count=Count('id')
                ).order_by('week')
            }
        
        elif period in (PeriodConstants.THIS_MONTH, PeriodConstants.MONTH):
            return {
                'trunc_field': 'month',
                'date_format': DateFormats.MONTH,
                'period_sales': sales.annotate(month=TruncMonth('date')).values('month').annotate(
                    count=Count('id')
                ).order_by('month')
            }
        
        elif period in (PeriodConstants.THIS_YEAR, PeriodConstants.YEAR):
            return {
                'trunc_field': 'year',
                'date_format': DateFormats.YEAR,
                'period_sales': sales.annotate(year=TruncYear('date')).values('year').annotate(
                    count=Count('id')
                ).order_by('year')
            }
        
        return {
            'trunc_field': 'month',
            'date_format': DateFormats.MONTH,
            'period_sales': sales.annotate(month=TruncMonth('date')).values('month').annotate(
                count=Count('id')
            ).order_by('month')
        }
    
    @staticmethod
    def format_label(sale_data, trunc_field, date_format):
        if trunc_field == 'day':
            date_obj = sale_data['day']
            return DateFormatter.format_day_label(date_obj)
        
        elif trunc_field == 'week':
            week_start = sale_data['week']
            return DateFormatter.format_week_label(week_start)
        
        elif trunc_field == 'month':
            date_obj = sale_data['month']
            return DateFormatter.format_month_label(date_obj)
        
        elif trunc_field == 'year':
            year = sale_data['year'].year
            return DateFormatter.format_year_label(year)
        
        return ''
    
    @staticmethod
    def filter_sales_by_period(sales, sale_data, trunc_field):
        if trunc_field == 'day':
            return sales.filter(date=sale_data['day'])
        
        elif trunc_field == 'week':
            week_start = sale_data['week']
            week_end = week_start + timedelta(days=6)
            return sales.filter(date__gte=week_start, date__lte=week_end)
        
        elif trunc_field == 'month':
            return sales.filter(
                date__year=sale_data['month'].year,
                date__month=sale_data['month'].month
            )
        
        elif trunc_field == 'year':
            return sales.filter(date__year=sale_data['year'].year)
        
        return sales.none()
    
    @staticmethod
    def calculate_chart_value(chart_type, period_sales_filtered, sale_data, trunc_field):
        if chart_type == ChartType.REVENUE:
            return ChartDataCalculator._calculate_revenue(period_sales_filtered)
        
        elif chart_type == ChartType.COSTS:
            return ChartDataCalculator._calculate_costs(sale_data, trunc_field)
        
        elif chart_type == ChartType.PROFIT:
            return ChartDataCalculator._calculate_profit(period_sales_filtered, sale_data, trunc_field)
        
        elif chart_type == ChartType.SALES_COUNT:
            return float(period_sales_filtered.count())
        
        elif chart_type == ChartType.ITEMS_SOLD:
            return ChartDataCalculator._calculate_items_sold(period_sales_filtered)
        
        return 0.0
    
    @staticmethod
    def _calculate_revenue(period_sales_filtered):
        total = SaleItem.objects.filter(sale__in=period_sales_filtered).aggregate(
            total=Sum((F('item__sale_price') - F('discount')) * F('quantity'))
        )['total']
        return float(total or 0)
    
    @staticmethod
    def _calculate_costs(sale_data, trunc_field):
        if trunc_field == 'day':
            start_date = sale_data['day']
            end_date = sale_data['day']
        elif trunc_field == 'week':
            week_start = sale_data['week']
            week_end = week_start + timedelta(days=6)
            start_date = week_start
            end_date = week_end
        elif trunc_field == 'month':
            start_date = sale_data['month'].replace(day=1)
            last_day = monthrange(sale_data['month'].year, sale_data['month'].month)[1]
            end_date = sale_data['month'].replace(day=last_day)
        elif trunc_field == 'year':
            start_date = sale_data['year'].replace(month=1, day=1)
            end_date = sale_data['year'].replace(month=12, day=31)
        else:
            return 0.0
        
        costs, _ = PurchaseCostCalculator.calculate_period_costs(
            start_date=start_date, end_date=end_date
        )
        return float(costs)
    
    @staticmethod
    def _calculate_profit(period_sales_filtered, sale_data, trunc_field):
        revenue = ChartDataCalculator._calculate_revenue(period_sales_filtered)
        
        sale_items = SaleItem.objects.filter(
            sale__in=period_sales_filtered
        ).select_related('item', 'sale')
        
        costs = 0.0
        items_costs = {}
        
        for sale_item in sale_items:
            item_id = sale_item.item_id
            sale_quantity = float(sale_item.quantity) if sale_item.quantity else 0.0
            sale_date = sale_item.sale.date if sale_item.sale.date else None
            
            if sale_date:
                cache_key = f"{item_id}_{sale_date}"
                if cache_key not in items_costs:
                    items_costs[cache_key] = CostCalculator.calculate_item_average_cost_until_date(
                        item_id, sale_date
                    )
                
                item_cost = items_costs[cache_key]
                if item_cost and item_cost > 0:
                    costs += float(item_cost) * sale_quantity
        
        return float(revenue) - float(costs)
    
    @staticmethod
    def _calculate_items_sold(period_sales_filtered):
        total = SaleItem.objects.filter(sale__in=period_sales_filtered).aggregate(
            total=Sum('quantity')
        )['total']
        return float(total or 0)


class SaleService:
    
    @staticmethod
    def _get_date_range(period):
        return DateRangeCalculator.calculate(period)
    
    @staticmethod
    def _get_filtered_sales(start_date=None, end_date=None, period=None):
        queryset = Sale.objects.all()
        
        if period:
            start_date, end_date = DateRangeCalculator.calculate(period)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset
    
    @staticmethod
    def get_sales_count(start_date=None, end_date=None, period=None):
        queryset = SaleService._get_filtered_sales(
            start_date=start_date,
            end_date=end_date,
            period=period
        )
        return queryset.count()
    
    @staticmethod
    def get_sales_total_amount(start_date=None, end_date=None, period=None):
        return RevenueCalculator.calculate_total(start_date, end_date, period)
    
    @staticmethod
    def get_items_sold_count(start_date=None, end_date=None, period=None):
        sales = SaleService._get_filtered_sales(start_date, end_date, period)
        total = SaleItem.objects.filter(sale__in=sales).aggregate(
            total=Sum('quantity')
        )['total']
        return float(total or 0)
    
    @staticmethod
    def get_total_costs(start_date=None, end_date=None, period=None):
        return PurchaseCostCalculator.calculate_period_costs(
            start_date, end_date, period
        )
    
    @staticmethod
    def get_total_profit(start_date=None, end_date=None, period=None):
        revenue = RevenueCalculator.calculate_total(start_date, end_date, period)
        costs, is_reliable = SoldItemsCostCalculator.calculate(start_date, end_date, period)
        
        profit = revenue - costs
        return profit, is_reliable
    
    @staticmethod
    def get_top_5_products(start_date=None, end_date=None, period=None):
        sales = SaleService._get_filtered_sales(start_date, end_date, period)
        top_products = SaleItem.objects.filter(sale__in=sales).values(
            'item__id', 'item__name', 'item__code'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum((F('item__sale_price') - F('discount')) * F('quantity'))
        ).order_by('-total_quantity')[:5]
        
        return [
            {
                'id': p['item__id'],
                'name': p['item__name'],
                'code': p['item__code'],
                'quantity': float(p['total_quantity'] or 0),
                'revenue': float(p['total_revenue'] or 0)
            }
            for p in top_products
        ]
    
    @staticmethod
    def get_top_5_customers(start_date=None, end_date=None, period=None):
        sales = SaleService._get_filtered_sales(start_date, end_date, period)
        customer_sales = sales.exclude(
            customer_name__isnull=True
        ).exclude(customer_name='').values('customer_name').annotate(
            total_sales=Count('id')
        ).order_by('-total_sales')[:5]
        
        result = []
        for customer_data in customer_sales:
            customer_sales_queryset = sales.filter(customer_name=customer_data['customer_name'])
            total_revenue = SaleItem.objects.filter(sale__in=customer_sales_queryset).aggregate(
                total=Sum((F('item__sale_price') - F('discount')) * F('quantity'))
            )['total']
            
            result.append({
                'name': customer_data['customer_name'],
                'revenue': float(total_revenue or 0),
                'sales_count': customer_data['total_sales']
            })
        
        result.sort(key=lambda x: x['revenue'], reverse=True)
        return result
    
    @staticmethod
    def get_period_chart_data(chart_type='revenue', start_date=None, end_date=None, period=None):
        config = ChartDataCalculator.get_period_config(period or PeriodConstants.THIS_MONTH)
        trunc_field = config['trunc_field']
        date_format = config['date_format']
        period_sales = config['period_sales']
        
        labels = []
        values = []
        sales = Sale.objects.all()
        
        for sale_data in period_sales:
            if trunc_field in sale_data and sale_data[trunc_field]:
                label = ChartDataCalculator.format_label(sale_data, trunc_field, date_format)
                labels.append(label)
                
                period_sales_filtered = ChartDataCalculator.filter_sales_by_period(
                    sales, sale_data, trunc_field
                )
                
                value = ChartDataCalculator.calculate_chart_value(
                    chart_type, period_sales_filtered, sale_data, trunc_field
                )
                values.append(value)
        
        return {'labels': labels, 'values': values}
    
    @staticmethod
    def get_period_revenue(start_date=None, end_date=None, period=None):
        return SaleService.get_period_chart_data(
            ChartType.REVENUE, start_date, end_date, period
        )
    
    @staticmethod
    def get_items_with_null_price(start_date=None, end_date=None, period=None):
        sales = SaleService._get_filtered_sales(start_date, end_date, period)
        sale_items = SaleItem.objects.filter(
            sale__in=sales,
            item__sale_price__isnull=True
        ).select_related('item').values('item__id', 'item__name').distinct()
        
        return [
            {
                'item_id': si['item__id'],
                'item_name': si['item__name']
            }
            for si in sale_items[:10]
        ]
    
    @staticmethod
    def _get_item_average_cost_until_date(item_id, date_limit):
        return CostCalculator.calculate_item_average_cost_until_date(item_id, date_limit)
    
    @staticmethod
    def _get_period_purchase_costs(start_date=None, end_date=None, period=None):
        return PurchaseCostCalculator.calculate_period_costs(start_date, end_date, period)
    
    @staticmethod
    def _get_sales_items_costs(start_date=None, end_date=None, period=None):
        return SoldItemsCostCalculator.calculate(start_date, end_date, period)
    
    @staticmethod
    def get_sales_chart_data(start_date=None, end_date=None, period=None):
        sales = SaleService._get_filtered_sales(
            start_date=start_date,
            end_date=end_date,
            period=period
        )
        
        sale_items = SaleItem.objects.filter(sale__in=sales)
        
        if period == 'day':
            sales_list = list(sales.values('date').annotate(
                count=Count('id')
            ).order_by('date'))
            labels = [sale['date'].strftime('%d/%m') for sale in sales_list]
        elif period == 'week':
            sales_list = list(sales.annotate(
                day=TruncDate('date')
            ).values('day').annotate(
                count=Count('id')
            ).order_by('day'))
            labels = [sale['day'].strftime('%d/%m') if sale['day'] else '' for sale in sales_list]
        elif period == 'month':
            sales_list = list(sales.annotate(
                day=TruncDate('date')
            ).values('day').annotate(
                count=Count('id')
            ).order_by('day'))
            labels = [sale['day'].strftime('%d/%m') if sale['day'] else '' for sale in sales_list]
        elif period == 'year':
            sales_list = list(sales.annotate(
                month=TruncMonth('date')
            ).values('month').annotate(
                count=Count('id')
            ).order_by('month'))
            labels = [sale['month'].strftime('%m/%Y') if sale['month'] else '' for sale in sales_list]
        else:
            sales_list = list(sales.annotate(
                day=TruncDate('date')
            ).values('day').annotate(
                count=Count('id')
            ).order_by('day'))
            labels = [sale['day'].strftime('%d/%m') if sale['day'] else '' for sale in sales_list]
        
        values = [sale['count'] or 0 for sale in sales_list]
        
        amounts = []
        for sale_data in sales_list:
            if period == 'day':
                sale_queryset = sales.filter(date=sale_data['date'])
            elif period == 'week' or period == 'month':
                if 'day' in sale_data and sale_data['day']:
                    sale_queryset = sales.filter(date=sale_data['day'])
                else:
                    sale_queryset = sales.none()
            elif period == 'year':
                if 'month' in sale_data and sale_data['month']:
                    sale_queryset = sales.filter(date__year=sale_data['month'].year, date__month=sale_data['month'].month)
                else:
                    sale_queryset = sales.none()
            else:
                if 'day' in sale_data and sale_data['day']:
                    sale_queryset = sales.filter(date=sale_data['day'])
                else:
                    sale_queryset = sales.none()
            
            total = SaleItem.objects.filter(
                sale__in=sale_queryset
            ).aggregate(
                total=Sum(
                    (F('item__sale_price') - F('discount')) * F('quantity')
                )
            )['total']
            amounts.append(float(total or 0))
        
        return {
            'labels': labels,
            'values': values,
            'amounts': amounts
        }
    
    @staticmethod
    def get_yearly_revenue():
        today = timezone.now().date()
        start_date = today.replace(month=1, day=1) - timedelta(days=1825)
        
        sales = Sale.objects.filter(date__gte=start_date)
        yearly_sales = sales.annotate(year=TruncYear('date')).values('year').annotate(
            count=Count('id')
        ).order_by('year')
        
        labels = []
        values = []
        for sale_data in yearly_sales:
            if sale_data['year']:
                year_sales = sales.filter(date__year=sale_data['year'].year)
                total = SaleItem.objects.filter(sale__in=year_sales).aggregate(
                    total=Sum((F('item__sale_price') - F('discount')) * F('quantity'))
                )['total']
                labels.append(str(sale_data['year'].year))
                values.append(float(total or 0))
        
        return {'labels': labels, 'values': values}
