(function($) {
    'use strict';

    const Dashboard = {
        apiUrl: null,
        currentPeriod: 'last_month',
        
        charts: {
            monthly: null
        },
        
        periodLabels: {
            'today': 'Hoje',
            'this_week': 'Esta semana',
            'this_month': 'Mês atual',
            'this_year': 'Ano'
        },
        
        chartTitles: {
            'today': 'Faturamento Diário',
            'this_week': 'Faturamento Semanal',
            'this_month': 'Faturamento Mensal',
            'this_year': 'Faturamento Anual'
        },
        
        init: function() {
            this.apiUrl = $('#dashboard-api-url').data('url');
            this.currentPeriod = $('#period-select').val() || 'this_month';
            this.setupPeriodFilter();
            this.loadData();
            this.setupTabs();
        },
        
        setupTabs: function() {
        },
        
        setupPeriodFilter: function() {
            const self = this;
            
            $('#period-select').on('change', function() {
                const period = $(this).val();
                self.currentPeriod = period;
                self.loadData();
            });
        },
        
        loadData: function() {
            const self = this;
            
            this.showLoading();
            
            $.ajax({
                url: this.apiUrl,
                method: 'GET',
                dataType: 'json',
                data: {
                    period: this.currentPeriod
                },
                success: function(data) {
                    self.updateStats(data);
                    self.updateCharts(data);
                    self.updateTopProducts(data.top_products);
                    self.updateTopCustomers(data.top_customers);
                    self.updateChartTitle(data.period);
                    self.hideLoading();
                },
                error: function(xhr, status, error) {
                    console.error('Error loading dashboard data:', error);
                    self.hideLoading();
                    self.showError('Error loading dashboard data');
                }
            });
        },
        
        updateStats: function(data) {
            $('#stat-revenue').text(this.formatCurrency(data.revenue));
            $('#stat-costs').text(this.formatCurrency(data.costs));
            $('#stat-profit').text(this.formatCurrency(data.profit));
            
            $('#stat-sales-count').text(data.sales_count.toLocaleString('pt-BR'));
            $('#stat-items-sold').text(data.items_sold.toLocaleString('pt-BR', {
                minimumFractionDigits: 0,
                maximumFractionDigits: 2
            }));
            
            if (!data.profit_is_reliable && data.missing_costs_message) {
                $('#alert-missing-costs-icon').removeClass('hidden');
                $('#tooltip-missing-costs-text').text(data.missing_costs_message);
            } else {
                $('#alert-missing-costs-icon').addClass('hidden');
            }
            
            if (data.items_null_price && data.items_null_price.length > 0) {
                const itemsList = data.items_null_price.map(function(item) {
                    return item.item_name;
                }).join(', ');
                $('#alert-null-price-text').text(
                    'Alguns itens vendidos não possuem preço de venda cadastrado: ' + itemsList + '. Os valores podem estar incorretos.'
                );
                $('#alert-null-price').removeClass('hidden');
            }
        },
        
        updateCharts: function(data) {
            this.updatePeriodChart(data.period_revenue || data.monthly_revenue);
        },
        
        updateChartTitle: function(period) {
            const title = this.chartTitles[period] || 'Faturamento Mensal';
            $('#chart-title').text(title);
        },
        
        updatePeriodChart: function(data) {
            const chartElement = $('#chart-monthly');
            if (!chartElement.length) return;
            
            if (this.charts.monthly) {
                this.charts.monthly.destroy();
            }
            
            const isDarkMode = document.documentElement.classList.contains('dark');
            const textColor = isDarkMode ? '#9ca3af' : '#6b7280';
            const gridColor = isDarkMode ? '#374151' : '#e5e7eb';
            
            const chartTitle = this.chartTitles[this.currentPeriod] || 'Faturamento Mensal';
            
            const options = {
                series: [{
                    name: chartTitle,
                    data: data.values
                }],
                chart: {
                    type: 'bar',
                    height: 300,
                    toolbar: { show: false },
                    zoom: { enabled: false }
                },
                plotOptions: {
                    bar: {
                        horizontal: false,
                        columnWidth: '55%',
                        endingShape: 'rounded'
                    }
                },
                dataLabels: {
                    enabled: false
                },
                stroke: {
                    show: true,
                    width: 2,
                    colors: ['transparent']
                },
                xaxis: {
                    categories: data.labels,
                    labels: {
                        style: {
                            colors: textColor,
                            fontSize: '12px'
                        }
                    },
                    axisBorder: {
                        color: gridColor
                    },
                    axisTicks: {
                        color: gridColor
                    }
                },
                yaxis: {
                    title: {
                        text: 'Faturamento (R$)',
                        style: {
                            color: textColor,
                            fontSize: '12px'
                        }
                    },
                    labels: {
                        style: {
                            colors: textColor,
                            fontSize: '12px'
                        }
                    }
                },
                fill: {
                    opacity: 1
                },
                colors: ['#3b82f6'],
                tooltip: {
                    theme: isDarkMode ? 'dark' : 'light',
                    y: {
                        formatter: function(val) {
                            return 'R$ ' + val.toFixed(2);
                        }
                    }
                },
                grid: {
                    borderColor: gridColor
                }
            };
            
            this.charts.monthly = new ApexCharts(chartElement[0], options);
            this.charts.monthly.render();
        },
        
        updateTopProducts: function(products) {
            const container = $('#top-products-list');
            container.empty();
            
            if (products.length === 0) {
                container.html('<p class="text-gray-500 dark:text-gray-400">Nenhum produto encontrado</p>');
                return;
            }
            
            products.forEach(function(product, index) {
                const item = $('<div>').addClass('flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700');
                
                const left = $('<div>').addClass('flex items-center gap-4');
                left.append($('<span>').addClass('text-gray-500 dark:text-gray-400 font-medium').text('#' + (index + 1)));
                left.append($('<div>')
                    .append($('<p>').addClass('font-semibold text-gray-900 dark:text-white').text(product.name))
                    .append($('<p>').addClass('text-sm text-gray-500 dark:text-gray-400')
                        .text('Quantidade: ' + product.quantity.toLocaleString('pt-BR', {maximumFractionDigits: 2}))));
                
                const right = $('<div>').addClass('text-right');
                right.append($('<p>').addClass('font-semibold text-gray-900 dark:text-white')
                    .text(Dashboard.formatCurrency(product.revenue)));
                
                item.append(left).append(right);
                container.append(item);
            });
        },
        
        updateTopCustomers: function(customers) {
            const container = $('#top-customers-list');
            container.empty();
            
            if (customers.length === 0) {
                container.html('<p class="text-gray-500 dark:text-gray-400">Nenhum cliente encontrado</p>');
                return;
            }
            
            customers.forEach(function(customer, index) {
                const item = $('<div>').addClass('flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700');
                
                const left = $('<div>').addClass('flex items-center gap-4');
                left.append($('<span>').addClass('text-gray-500 dark:text-gray-400 font-medium').text('#' + (index + 1)));
                left.append($('<div>')
                    .append($('<p>').addClass('font-semibold text-gray-900 dark:text-white').text(customer.name))
                    .append($('<p>').addClass('text-sm text-gray-500 dark:text-gray-400')
                        .text(customer.sales_count + ' venda(s)')));
                
                const right = $('<div>').addClass('text-right');
                right.append($('<p>').addClass('font-semibold text-gray-900 dark:text-white')
                    .text(Dashboard.formatCurrency(customer.revenue)));
                
                item.append(left).append(right);
                container.append(item);
            });
        },
        
        formatCurrency: function(value) {
            return 'R$ ' + parseFloat(value).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        },
        
        showLoading: function() {
            $('#dashboard-loading').removeClass('hidden');
            $('#dashboard-content').addClass('hidden');
        },
        
        hideLoading: function() {
            $('#dashboard-loading').addClass('hidden');
            $('#dashboard-content').removeClass('hidden');
        },
        
        showError: function(message) {
            console.error('Dashboard error:', message);
        }
    };
    
    $(document).ready(function() {
        Dashboard.init();
    });
    
})(jQuery);

