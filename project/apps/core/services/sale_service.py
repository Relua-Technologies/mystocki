from datetime import datetime, timedelta
from django.db.models import Sum, F, Q, Count, Avg
from django.utils import timezone
from django.db.models.functions import TruncDate, TruncDay, TruncWeek, TruncMonth
from apps.core.models import Sale, SaleItem, StockMovement


class SaleService:
    @staticmethod
    def _get_date_range(period):
        from calendar import monthrange
        
        today = timezone.now().date()
        
        if period == 'day' or period == 'today':
            start_date = today
            end_date = today
        elif period == 'week' or period == 'this_week':
            days_since_monday = today.weekday()
            start_date = today - timedelta(days=days_since_monday)
            end_date = today
        elif period == 'month' or period == 'this_month':
            start_date = today.replace(day=1)
            last_day = monthrange(today.year, today.month)[1]
            end_date = today.replace(day=last_day)
        elif period == 'year' or period == 'this_year':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        else:
            return None, None
        
        return start_date, end_date

    @staticmethod
    def _get_filtered_sales(start_date=None, end_date=None, period=None):
        queryset = Sale.objects.all()
        
        if period:
            start_date, end_date = SaleService._get_date_range(period)
        
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
        sales = SaleService._get_filtered_sales(
            start_date=start_date,
            end_date=end_date,
            period=period
        )
        
        sale_items = SaleItem.objects.filter(sale__in=sales).select_related('item')
        total = 0
        
        for sale_item in sale_items:
            if sale_item.item.sale_price:
                item_total = (float(sale_item.item.sale_price) - float(sale_item.discount)) * float(sale_item.quantity)
                total += item_total
        
        return total

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
    def _get_item_average_cost_until_date(item_id, date_limit):
        """
        Calcula o custo médio ponderado de um item considerando apenas
        movimentações de entrada (IN) até uma data específica.
        
        Regra: Soma todos os total_purchase_price e divide pela soma
        de todas as quantidades até a data limite.
        
        Args:
            item_id: ID do item
            date_limit: Data limite (date ou datetime) - considera movimentações até esta data
            
        Returns:
            float: Custo médio por unidade (0.0 se não houver movimentações válidas)
        """
        try:
            from datetime import datetime, time as dt_time
            
            if isinstance(date_limit, str):
                date_limit = datetime.strptime(date_limit, '%Y-%m-%d').date()
            
            if hasattr(date_limit, 'date'):
                date_limit = date_limit.date()
            
            date_limit_datetime = datetime.combine(date_limit, dt_time.max)
            
            movements = StockMovement.objects.filter(
                item_id=item_id,
                movement_type='IN',
                total_purchase_price__isnull=False,
                total_purchase_price__gt=0,
                created__lte=date_limit_datetime
            ).order_by('-created_at')
            
            if not movements.exists():
                return 0.0
            
            total_cost = 0.0
            total_quantity = 0.0
            
            for movement in movements:
                if movement.total_purchase_price is not None and movement.quantity is not None:
                    try:
                        movement_cost = float(movement.total_purchase_price)
                        movement_quantity = float(movement.quantity)
                        
                        if movement_quantity > 0 and movement_cost > 0:
                            total_cost += movement_cost
                            total_quantity += movement_quantity
                    except (ValueError, TypeError):
                        continue
            
            if total_quantity > 0 and total_cost > 0:
                weighted_average = total_cost / total_quantity
                return float(weighted_average)
            
            return 0.0
        except Exception:
            return 0.0
    
    @staticmethod
    def _get_period_purchase_costs(start_date=None, end_date=None, period=None):
        """
        Calcula o total de custos de compra (movimentações de entrada) no período.
        
        Regra: Soma todos os total_purchase_price das movimentações de entrada (IN)
        que foram criadas dentro do período especificado.
        
        Args:
            start_date: Data inicial do período (opcional)
            end_date: Data final do período (opcional)
            period: Período pré-definido ('year', 'month', 'week', 'day')
            
        Returns:
            tuple: (total_cost: float, is_reliable: bool)
                - total_cost: Soma de todos os custos de compra do período
                - is_reliable: True se todas as movimentações têm total_purchase_price preenchido
        """
        try:
            if period:
                start_date, end_date = SaleService._get_date_range(period)
            
            filter_kwargs = {
                'movement_type': 'IN',
                'total_purchase_price__isnull': False
            }
            
            if start_date:
                from datetime import datetime, time as dt_time
                start_datetime = datetime.combine(start_date, dt_time.min)
                filter_kwargs['created__gte'] = start_datetime
            if end_date:
                from datetime import datetime, time as dt_time
                end_datetime = datetime.combine(end_date, dt_time.max)
                filter_kwargs['created__lte'] = end_datetime
            
            movements = StockMovement.objects.filter(**filter_kwargs)
            
            if not movements.exists():
                return 0.0, True
            
            total_cost = 0.0
            total_movements = 0
            movements_with_cost = 0
            
            for movement in movements:
                total_movements += 1
                if movement.total_purchase_price is not None and movement.total_purchase_price > 0:
                    movements_with_cost += 1
                    total_cost += float(movement.total_purchase_price)
            
            is_reliable = total_movements > 0 and movements_with_cost == total_movements
            
            return float(total_cost), is_reliable
        except Exception:
            return 0.0, False

    @staticmethod
    def get_total_costs(start_date=None, end_date=None, period=None):
        """
        Retorna o total de custos de compra (movimentações de entrada) no período.
        
        Regra: Soma todos os total_purchase_price das movimentações de entrada (IN)
        criadas dentro do período especificado.
        
        Args:
            start_date: Data inicial (opcional)
            end_date: Data final (opcional)
            period: Período pré-definido ('year', 'month', 'week', 'day')
            
        Returns:
            tuple: (total_cost: float, is_reliable: bool)
                - total_cost: Soma de todos os custos de compra do período
                - is_reliable: True se todas as movimentações têm total_purchase_price preenchido
        """
        return SaleService._get_period_purchase_costs(start_date, end_date, period)
    
    @staticmethod
    def _get_sales_items_costs(start_date=None, end_date=None, period=None):
        """
        Calcula o custo total dos itens vendidos usando média ponderada até a data de cada venda.
        
        Regra: Para cada item vendido, calcula o custo médio ponderado considerando
        todas as movimentações de entrada até a data da venda. Multiplica pelo
        custo médio pela quantidade vendida.
        
        Args:
            start_date: Data inicial (opcional)
            end_date: Data final (opcional)
            period: Período pré-definido ('year', 'month', 'week', 'day')
            
        Returns:
            tuple: (total_cost: float, is_reliable: bool)
                - total_cost: Custo total dos itens vendidos
                - is_reliable: True se todos os itens têm custo e sale_price preenchidos
        """
        try:
            sales = SaleService._get_filtered_sales(start_date, end_date, period)
            sale_items = SaleItem.objects.filter(sale__in=sales).select_related('item', 'sale')
            
            if not sale_items.exists():
                return 0.0, True
            
            if period:
                _, end_date = SaleService._get_date_range(period)
            
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
                
                if sale_item.item.sale_price is not None and sale_item.item.sale_price > 0:
                    items_with_sale_price += 1
                
                if sale_date:
                    cache_key = f"{item_id}_{sale_date}"
                    if cache_key not in items_costs:
                        items_costs[cache_key] = SaleService._get_item_average_cost_until_date(item_id, sale_date)
                    
                    item_cost = items_costs[cache_key]
                    
                    if item_cost and item_cost > 0:
                        items_with_cost += 1
                        total_cost += float(item_cost) * sale_quantity
                    else:
                        total_cost += 0.0 * sale_quantity
                else:
                    total_cost += 0.0 * sale_quantity
            
            is_reliable = (total_items > 0 and 
                          items_with_cost == total_items and 
                          items_with_sale_price == total_items)
            
            return float(total_cost), is_reliable
        except Exception:
            return 0.0, False

    @staticmethod
    def get_total_profit(start_date=None, end_date=None, period=None):
        """
        Calcula o lucro total (receita - custos dos itens vendidos).
        
        Regra: Receita das vendas menos o custo dos itens vendidos.
        O custo é calculado usando média ponderada até a data de cada venda.
        
        Args:
            start_date: Data inicial (opcional)
            end_date: Data final (opcional)
            period: Período pré-definido ('year', 'month', 'week', 'day')
            
        Returns:
            tuple: (profit: float, is_reliable: bool)
                - profit: Lucro total (receita - custos)
                - is_reliable: True se todos os itens têm custo e sale_price preenchidos
        """
        revenue = SaleService.get_sales_total_amount(start_date, end_date, period)
        costs, is_reliable = SaleService._get_sales_items_costs(start_date, end_date, period)
        
        profit = revenue - costs
        
        return profit, is_reliable

    @staticmethod
    def get_items_sold_count(start_date=None, end_date=None, period=None):
        sales = SaleService._get_filtered_sales(start_date, end_date, period)
        total = SaleItem.objects.filter(sale__in=sales).aggregate(
            total=Sum('quantity')
        )['total']
        return float(total or 0)

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
        from datetime import timedelta
        from django.db.models.functions import TruncMonth, TruncDay, TruncYear
        
        sales = Sale.objects.all()
        
        if period == 'today' or period == 'day':
            period_sales = sales.annotate(day=TruncDay('date')).values('day').annotate(
                count=Count('id')
            ).order_by('day')
            date_format = '%d/%m/%Y'
            trunc_field = 'day'
        elif period == 'this_week' or period == 'week':
            period_sales = sales.annotate(day=TruncDay('date')).values('day').annotate(
                count=Count('id')
            ).order_by('day')
            date_format = '%d/%m'
            trunc_field = 'day'
        elif period == 'this_month' or period == 'month':
            period_sales = sales.annotate(month=TruncMonth('date')).values('month').annotate(
                count=Count('id')
            ).order_by('month')
            date_format = '%m/%Y'
            trunc_field = 'month'
        elif period == 'this_year' or period == 'year':
            period_sales = sales.annotate(year=TruncYear('date')).values('year').annotate(
                count=Count('id')
            ).order_by('year')
            date_format = '%Y'
            trunc_field = 'year'
        else:
            period_sales = sales.annotate(month=TruncMonth('date')).values('month').annotate(
                count=Count('id')
            ).order_by('month')
            date_format = '%m/%Y'
            trunc_field = 'month'
        
        labels = []
        values = []
        
        weekdays_pt = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        months_pt = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                     'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        
        for sale_data in period_sales:
            if trunc_field in sale_data and sale_data[trunc_field]:
                if trunc_field == 'day':
                    period_sales_filtered = sales.filter(date=sale_data['day'])
                    date_str = sale_data['day'].strftime(date_format)
                    weekday_index = sale_data['day'].weekday()
                    weekday_pt = weekdays_pt[weekday_index]
                    labels.append(f"{date_str}\n({weekday_pt})")
                elif trunc_field == 'month':
                    period_sales_filtered = sales.filter(
                        date__year=sale_data['month'].year,
                        date__month=sale_data['month'].month
                    )
                    month_year = sale_data['month'].strftime(date_format)
                    month_name = months_pt[sale_data['month'].month]
                    labels.append(f"{month_year} ({month_name})")
                elif trunc_field == 'year':
                    period_sales_filtered = sales.filter(date__year=sale_data['year'].year)
                    labels.append(str(sale_data['year'].year))
                else:
                    period_sales_filtered = sales.none()
                
                if chart_type == 'revenue':
                    total = SaleItem.objects.filter(sale__in=period_sales_filtered).aggregate(
                        total=Sum((F('item__sale_price') - F('discount')) * F('quantity'))
                    )['total']
                    values.append(float(total or 0))
                elif chart_type == 'costs':
                    if trunc_field == 'day':
                        start_date = sale_data['day']
                        end_date = sale_data['day']
                    elif trunc_field == 'month':
                        from calendar import monthrange
                        start_date = sale_data['month'].replace(day=1)
                        last_day = monthrange(sale_data['month'].year, sale_data['month'].month)[1]
                        end_date = sale_data['month'].replace(day=last_day)
                    elif trunc_field == 'year':
                        start_date = sale_data['year'].replace(month=1, day=1)
                        end_date = sale_data['year'].replace(month=12, day=31)
                    else:
                        start_date = None
                        end_date = None
                    
                    costs, _ = SaleService._get_period_purchase_costs(start_date=start_date, end_date=end_date)
                    values.append(float(costs))
                elif chart_type == 'profit':
                    revenue = SaleItem.objects.filter(sale__in=period_sales_filtered).aggregate(
                        total=Sum((F('item__sale_price') - F('discount')) * F('quantity'))
                    )['total']
                    
                    sale_items = SaleItem.objects.filter(sale__in=period_sales_filtered).select_related('item', 'sale')
                    
                    costs = 0.0
                    items_costs = {}
                    
                    for sale_item in sale_items:
                        item_id = sale_item.item_id
                        sale_quantity = float(sale_item.quantity) if sale_item.quantity else 0.0
                        sale_date = sale_item.sale.date if sale_item.sale.date else None
                        
                        if sale_date:
                            cache_key = f"{item_id}_{sale_date}"
                            if cache_key not in items_costs:
                                items_costs[cache_key] = SaleService._get_item_average_cost_until_date(item_id, sale_date)
                            
                            item_cost = items_costs[cache_key]
                            if item_cost and item_cost > 0:
                                costs += float(item_cost) * sale_quantity
                    
                    profit = float(revenue or 0) - float(costs)
                    values.append(profit)
                elif chart_type == 'sales_count':
                    count = period_sales_filtered.count()
                    values.append(count)
                elif chart_type == 'items_sold':
                    total = SaleItem.objects.filter(sale__in=period_sales_filtered).aggregate(
                        total=Sum('quantity')
                    )['total']
                    values.append(float(total or 0))
                else:
                    values.append(0)
        
        return {'labels': labels, 'values': values}
    
    @staticmethod
    def _get_period_purchase_costs_for_chart(date_filter, trunc_field):
        try:
            from datetime import datetime, time as dt_time
            from calendar import monthrange
            
            filter_kwargs = {
                'movement_type': 'IN',
                'total_purchase_price__isnull': False,
                'total_purchase_price__gt': 0
            }
            
            if date_filter:
                if trunc_field == 'day':
                    start_datetime = datetime.combine(date_filter, dt_time.min)
                    end_datetime = datetime.combine(date_filter, dt_time.max)
                    filter_kwargs['created__gte'] = start_datetime
                    filter_kwargs['created__lte'] = end_datetime
                elif trunc_field == 'month':
                    start_date = date_filter.replace(day=1)
                    last_day = monthrange(date_filter.year, date_filter.month)[1]
                    end_date = date_filter.replace(day=last_day)
                    start_datetime = datetime.combine(start_date, dt_time.min)
                    end_datetime = datetime.combine(end_date, dt_time.max)
                    filter_kwargs['created__gte'] = start_datetime
                    filter_kwargs['created__lte'] = end_datetime
                elif trunc_field == 'year':
                    start_date = date_filter.replace(month=1, day=1)
                    end_date = date_filter.replace(month=12, day=31)
                    start_datetime = datetime.combine(start_date, dt_time.min)
                    end_datetime = datetime.combine(end_date, dt_time.max)
                    filter_kwargs['created__gte'] = start_datetime
                    filter_kwargs['created__lte'] = end_datetime
            
            movements = StockMovement.objects.filter(**filter_kwargs)
            
            if not movements.exists():
                return 0.0, True
            
            total_cost = 0.0
            total_movements = 0
            movements_with_cost = 0
            
            for movement in movements:
                total_movements += 1
                if movement.total_purchase_price is not None and movement.total_purchase_price > 0:
                    movements_with_cost += 1
                    total_cost += float(movement.total_purchase_price)
            
            is_reliable = total_movements > 0 and movements_with_cost == total_movements
            
            return float(total_cost), is_reliable
        except Exception:
            return 0.0, False
    
    @staticmethod
    def get_period_revenue(start_date=None, end_date=None, period=None):
        return SaleService.get_period_chart_data('revenue', start_date, end_date, period)

    @staticmethod
    def get_yearly_revenue():
        from datetime import timedelta
        from django.db.models.functions import TruncYear
        
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

