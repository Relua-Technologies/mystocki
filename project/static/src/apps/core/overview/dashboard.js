(function($) {
    'use strict';

    const Dashboard = {
        apiUrl: null,
        currentPeriod: 'this_month',
        currentChartType: 'revenue',
        
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
            'revenue': {
                'today': 'Faturamento Diário',
                'this_week': 'Faturamento Semanal',
                'this_month': 'Faturamento Mensal',
                'this_year': 'Faturamento Anual'
            },
            'costs': {
                'today': 'Custos Diários',
                'this_week': 'Custos Semanais',
                'this_month': 'Custos Mensais',
                'this_year': 'Custos Anuais'
            },
            'profit': {
                'today': 'Lucro Diário',
                'this_week': 'Lucro Semanal',
                'this_month': 'Lucro Mensal',
                'this_year': 'Lucro Anual'
            },
            'sales_count': {
                'today': 'Vendas Diárias',
                'this_week': 'Vendas Semanais',
                'this_month': 'Vendas Mensais',
                'this_year': 'Vendas Anuais'
            },
            'items_sold': {
                'today': 'Itens Vendidos Diários',
                'this_week': 'Itens Vendidos Semanais',
                'this_month': 'Itens Vendidos Mensais',
                'this_year': 'Itens Vendidos Anuais'
            }
        },
        
        init: function() {
            this.apiUrl = $('#dashboard-api-url').data('url');
            this.currentPeriod = $('#period-select').val() || 'this_month';
            this.currentChartType = 'revenue';
            this.setupPeriodFilter();
            this.setupStatCards();
            this.setChartType('revenue');
            this.loadData();
            this.setupTabs();
        },
        
        setupStatCards: function() {
            const self = this;
            
            $('.stat-card').on('click', function() {
                const chartType = $(this).data('chart-type');
                self.setChartType(chartType);
            });
        },
        
        setChartType: function(chartType) {
            this.currentChartType = chartType;
            $('.stat-card').removeClass('bg-blue-100 dark:bg-blue-900 border-blue-500').addClass('bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700');
            $('.stat-card[data-chart-type="' + chartType + '"]').removeClass('bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700').addClass('bg-blue-100 dark:bg-blue-900 border-blue-500');
            if (this.currentPeriod) {
                this.loadChartData();
            }
        },
        
        setupTabs: function() {
        },
        
        setupPeriodFilter: function() {
            const self = this;
            
            $('#period-select').on('change', function() {
                const period = $(this).val();
                self.currentPeriod = period;
                self.loadData();
                self.loadChartData();
            });
        },
        
        loadChartData: function() {
            const self = this;
            
            $.ajax({
                url: this.apiUrl,
                method: 'GET',
                dataType: 'json',
                data: {
                    period: this.currentPeriod,
                    chart_type: this.currentChartType
                },
                success: function(data) {
                    self.updateCharts(data);
                    self.updateChartTitle(data.period);
                },
                error: function(xhr, status, error) {
                    console.error('Error loading chart data:', error);
                }
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
                    period: this.currentPeriod,
                    chart_type: this.currentChartType
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
            const chartTypeTitles = this.chartTitles[this.currentChartType] || this.chartTitles['revenue'];
            const title = chartTypeTitles[period] || chartTypeTitles['this_month'] || 'Faturamento Mensal';
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
            
            const chartTypeTitles = this.chartTitles[this.currentChartType] || this.chartTitles['revenue'];
            const chartTitle = chartTypeTitles[this.currentPeriod] || chartTypeTitles['this_month'] || 'Faturamento Mensal';
            
            const isMoneyChart = this.currentChartType === 'revenue' || this.currentChartType === 'costs' || this.currentChartType === 'profit';
            
            let yaxisTitle = 'Faturamento (R$)';
            if (this.currentChartType === 'costs') {
                yaxisTitle = 'Custos (R$)';
            } else if (this.currentChartType === 'profit') {
                yaxisTitle = 'Lucro (R$)';
            } else if (this.currentChartType === 'sales_count') {
                yaxisTitle = 'Número de Vendas';
            } else if (this.currentChartType === 'items_sold') {
                yaxisTitle = 'Quantidade de Itens';
            }
            
            const options = {
                series: [{
                    name: chartTitle,
                    data: data.values
                }],
                chart: {
                    type: 'bar',
                    height: chartElement[0].offsetHeight || 300,
                    toolbar: { show: false },
                    zoom: { enabled: false },
                    width: '100%'
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
                        text: yaxisTitle,
                        style: {
                            color: textColor,
                            fontSize: '12px'
                        }
                    },
                    labels: {
                        style: {
                            colors: textColor,
                            fontSize: '12px'
                        },
                        formatter: function(val) {
                            if (isMoneyChart) {
                                return 'R$ ' + parseFloat(val).toFixed(2).replace('.', ',');
                            } else {
                                return parseFloat(val).toLocaleString('pt-BR', {
                                    minimumFractionDigits: 0,
                                    maximumFractionDigits: 0
                                });
                            }
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
                            if (isMoneyChart) {
                                return 'R$ ' + parseFloat(val).toFixed(2).replace('.', ',');
                            } else {
                                return parseFloat(val).toLocaleString('pt-BR', {
                                    minimumFractionDigits: 0,
                                    maximumFractionDigits: 0
                                });
                            }
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
                const item = $('<div>').addClass('flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 sm:gap-4 p-3 sm:p-4 border-b border-gray-200 dark:border-gray-700');
                
                const left = $('<div>').addClass('flex items-start sm:items-center gap-2 sm:gap-4 flex-1 min-w-0');
                left.append($('<span>').addClass('text-gray-500 dark:text-gray-400 font-medium text-sm sm:text-base flex-shrink-0').text('#' + (index + 1)));
                left.append($('<div>').addClass('min-w-0 flex-1')
                    .append($('<p>').addClass('font-semibold text-gray-900 dark:text-white text-sm sm:text-base truncate').text(product.name))
                    .append($('<p>').addClass('text-xs sm:text-sm text-gray-500 dark:text-gray-400')
                        .text('Código: ' + (product.code || 'N/A') + ' | Quantidade: ' + product.quantity.toLocaleString('pt-BR', {maximumFractionDigits: 2}))));
                
                const right = $('<div>').addClass('text-left sm:text-right flex-shrink-0');
                right.append($('<p>').addClass('font-semibold text-gray-900 dark:text-white text-sm sm:text-base')
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

