// Admin Dashboard JavaScript
class AdminDashboard {
    constructor() {
        this.currentSection = 'dashboard';
        this.charts = {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboardData();
        this.initializeCharts();
        this.loadNotifications();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.dataset.section;
                this.navigateToSection(section);
            });
        });

        // User menu
        const userMenuBtn = document.querySelector('.user-menu-btn');
        const userDropdown = document.querySelector('.user-dropdown');
        
        if (userMenuBtn && userDropdown) {
            userMenuBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                userDropdown.style.display = userDropdown.style.display === 'block' ? 'none' : 'block';
            });

            document.addEventListener('click', () => {
                userDropdown.style.display = 'none';
            });
        }

        // Logout
        const logoutBtn = document.getElementById('logoutAdmin');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.logout();
            });
        }
    }

    navigateToSection(section) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // Update page title
        const titles = {
            dashboard: { title: 'Дашборд', subtitle: 'Обзор системы и ключевые показатели' },
            services: { title: 'Услуги', subtitle: 'Управление каталогом услуг' },
            orders: { title: 'Заказы', subtitle: 'Обработка и управление заказами' },
            users: { title: 'Пользователи', subtitle: 'Управление пользователями и ролями' },
            analytics: { title: 'Аналитика', subtitle: 'Статистика и аналитические данные' },
            reports: { title: 'Отчеты', subtitle: 'Генерация и экспорт отчетов' },
            settings: { title: 'Настройки', subtitle: 'Конфигурация системы' }
        };

        const pageTitle = document.getElementById('page-title');
        const pageSubtitle = document.getElementById('page-subtitle');
        
        if (pageTitle && pageSubtitle && titles[section]) {
            pageTitle.textContent = titles[section].title;
            pageSubtitle.textContent = titles[section].subtitle;
        }

        this.currentSection = section;
        this.loadSectionContent(section);
    }

    loadSectionContent(section) {
        const content = document.getElementById('admin-content');
        
        switch (section) {
            case 'dashboard':
                this.loadDashboardContent();
                break;
            case 'services':
                this.loadServicesContent();
                break;
            case 'orders':
                this.loadOrdersContent();
                break;
            case 'users':
                this.loadUsersContent();
                break;
            case 'analytics':
                this.loadAnalyticsContent();
                break;
            case 'reports':
                this.loadReportsContent();
                break;
            case 'settings':
                this.loadSettingsContent();
                break;
        }
    }

    loadDashboardContent() {
        const content = document.getElementById('admin-content');
        content.innerHTML = `
            <!-- KPI Cards -->
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-icon">💰</div>
                    <div class="kpi-content">
                        <h3>Общая выручка</h3>
                        <div class="kpi-value" id="totalRevenue">0 ₽</div>
                        <div class="kpi-change positive">+12.5%</div>
                    </div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-icon">📦</div>
                    <div class="kpi-content">
                        <h3>Заказы за месяц</h3>
                        <div class="kpi-value" id="monthlyOrders">0</div>
                        <div class="kpi-change positive">+8.2%</div>
                    </div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-icon">👥</div>
                    <div class="kpi-content">
                        <h3>Активные пользователи</h3>
                        <div class="kpi-value" id="activeUsers">0</div>
                        <div class="kpi-change positive">+15.3%</div>
                    </div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-icon">📊</div>
                    <div class="kpi-content">
                        <h3>Средний чек</h3>
                        <div class="kpi-value" id="averageOrder">0 ₽</div>
                        <div class="kpi-change negative">-2.1%</div>
                    </div>
                </div>
            </div>

            <!-- Charts Row -->
            <div class="charts-row">
                <div class="chart-container">
                    <h3>Выручка по месяцам</h3>
                    <canvas id="revenueChart"></canvas>
                </div>
                <div class="chart-container">
                    <h3>Популярные услуги</h3>
                    <canvas id="servicesChart"></canvas>
                </div>
            </div>

            <!-- Recent Orders -->
            <div class="recent-section">
                <div class="section-header">
                    <h3>Последние заказы</h3>
                    <a href="#" onclick="openOrdersModal(); return false;" class="view-all">Все заказы →</a>
                </div>
                <div class="recent-orders" id="recentOrders">
                    <!-- Orders will be loaded here -->
                </div>
            </div>

            <!-- Notifications -->
            <div class="notifications-section">
                <div class="section-header">
                    <h3>Уведомления</h3>
                    <span class="notification-count" id="notificationCount">0</span>
                </div>
                <div class="notifications" id="notifications">
                    <!-- Notifications will be loaded here -->
                </div>
            </div>
        `;

        this.loadDashboardData();
        this.initializeCharts();
        this.loadRecentOrders();
        this.loadNotifications();
    }

    async loadDashboardData() {
        try {
            // Load KPI data
            const response = await fetch('/api/v2/admin/stats/', {
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                this.updateKPICards(data);
            } else if (response.status === 401) {
                // Try to refresh token
                try {
                    const refreshResponse = await this.refreshToken();
                    if (refreshResponse.access) {
                        this.setTokens(refreshResponse.access, refreshResponse.refresh);
                        const retryResponse = await fetch('/api/v2/admin/stats/', {
                            headers: this.getAuthHeaders()
                        });
                        if (retryResponse.ok) {
                            const data = await retryResponse.json();
                            this.updateKPICards(data);
                            return;
                        }
                    }
                } catch (refreshError) {
                    console.error('Token refresh failed:', refreshError);
                }
                
                // Fallback to mock data
                this.updateKPICards({
                    totalRevenue: 1250000,
                    monthlyOrders: 156,
                    activeUsers: 89,
                    averageOrder: 8012
                });
            } else {
                // Fallback to mock data
                this.updateKPICards({
                    totalRevenue: 1250000,
                    monthlyOrders: 156,
                    activeUsers: 89,
                    averageOrder: 8012
                });
            }
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            // Use mock data
            this.updateKPICards({
                totalRevenue: 1250000,
                monthlyOrders: 156,
                activeUsers: 89,
                averageOrder: 8012
            });
        }
    }

    updateKPICards(data) {
        const totalRevenue = document.getElementById('totalRevenue');
        const monthlyOrders = document.getElementById('monthlyOrders');
        const activeUsers = document.getElementById('activeUsers');
        const averageOrder = document.getElementById('averageOrder');

        if (totalRevenue) totalRevenue.textContent = data.totalRevenue?.toLocaleString('ru-RU') + ' ₽' || '0 ₽';
        if (monthlyOrders) monthlyOrders.textContent = data.monthlyOrders || '0';
        if (activeUsers) activeUsers.textContent = data.activeUsers || '0';
        if (averageOrder) averageOrder.textContent = data.averageOrder?.toLocaleString('ru-RU') + ' ₽' || '0 ₽';
    }

    initializeCharts() {
        // Revenue Chart
        const revenueCtx = document.getElementById('revenueChart');
        if (revenueCtx) {
            this.charts.revenue = new Chart(revenueCtx, {
                type: 'line',
                data: {
                    labels: ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн'],
                    datasets: [{
                        label: 'Выручка (₽)',
                        data: [850000, 920000, 780000, 1100000, 1250000, 980000],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return value.toLocaleString('ru-RU') + ' ₽';
                                }
                            }
                        }
                    }
                }
            });
        }

        // Services Chart
        const servicesCtx = document.getElementById('servicesChart');
        if (servicesCtx) {
            this.charts.services = new Chart(servicesCtx, {
                type: 'doughnut',
                data: {
                    labels: ['YouTube', 'Instagram', 'Telegram', 'TikTok', 'VK'],
                    datasets: [{
                        data: [35, 25, 20, 15, 5],
                        backgroundColor: [
                            '#ff6b6b',
                            '#4ecdc4',
                            '#45b7d1',
                            '#96ceb4',
                            '#feca57'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
    }

    async loadRecentOrders() {
        try {
            const response = await fetch('/api/v2/orders/?limit=5', {
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                const orders = data.results || data;
                this.renderRecentOrders(orders);
            } else {
                this.renderRecentOrders([]);
            }
        } catch (error) {
            console.error('Error loading recent orders:', error);
            this.renderRecentOrders([]);
        }
    }

    renderRecentOrders(orders) {
        const container = document.getElementById('recentOrders');
        if (!container) return;

        if (orders.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #64748b; padding: 20px;">Нет заказов</p>';
            return;
        }

        container.innerHTML = orders.map(order => `
            <div class="order-item">
                <div class="order-info">
                    <h4>Заказ #${order.id}</h4>
                    <p>${order.full_name || order.user?.username || 'Неизвестно'} • ${new Date(order.created_at).toLocaleDateString('ru-RU')}</p>
                </div>
                <div class="order-status ${order.status}">${this.getStatusText(order.status)}</div>
            </div>
        `).join('');
    }

    getStatusText(status) {
        const statusMap = {
            'new': 'Новый',
            'paid': 'Оплачен',
            'in_progress': 'В работе',
            'done': 'Выполнен',
            'cancelled': 'Отменен'
        };
        return statusMap[status] || status;
    }

    async loadNotifications() {
        // Mock notifications
        const notifications = [
            {
                icon: '📦',
                title: 'Новый заказ',
                message: 'Получен заказ #1234 от Иванов И.И.',
                time: '2 мин назад'
            },
            {
                icon: '👤',
                title: 'Новый пользователь',
                message: 'Зарегистрирован пользователь Петров П.П.',
                time: '15 мин назад'
            },
            {
                icon: '⚠️',
                title: 'Системное уведомление',
                message: 'Обновление системы завершено',
                time: '1 час назад'
            }
        ];

        this.renderNotifications(notifications);
    }

    renderNotifications(notifications) {
        const container = document.getElementById('notifications');
        const count = document.getElementById('notificationCount');
        
        if (count) count.textContent = notifications.length;

        if (container) {
            container.innerHTML = notifications.map(notification => `
                <div class="notification-item">
                    <div class="notification-icon">${notification.icon}</div>
                    <div class="notification-content">
                        <h4>${notification.title}</h4>
                        <p>${notification.message} • ${notification.time}</p>
                    </div>
                </div>
            `).join('');
        }
    }

    loadServicesContent() {
        const content = document.getElementById('admin-content');
        content.innerHTML = `
            <div class="services-section">
                <div class="section-header">
                    <h3>Управление услугами</h3>
                    <button class="btn btn-primary" onclick="adminDashboard.addService()">+ Добавить услугу</button>
                </div>
                <div class="services-grid" id="servicesGrid">
                    <!-- Services will be loaded here -->
                </div>
            </div>
        `;
        this.loadServices();
    }

    loadOrdersContent() {
        const content = document.getElementById('admin-content');
        content.innerHTML = `
            <div class="orders-section">
                <div class="section-header">
                    <h3>Управление заказами</h3>
                    <div class="filters">
                        <select id="statusFilter">
                            <option value="">Все статусы</option>
                            <option value="new">Новые</option>
                            <option value="paid">Оплаченные</option>
                            <option value="in_progress">В работе</option>
                            <option value="done">Выполненные</option>
                            <option value="cancelled">Отмененные</option>
                        </select>
                    </div>
                </div>
                <div class="orders-table" id="ordersTable">
                    <!-- Orders will be loaded here -->
                </div>
            </div>
        `;
        this.loadOrders();
    }

    loadUsersContent() {
        const content = document.getElementById('admin-content');
        content.innerHTML = `
            <div class="users-section">
                <div class="section-header">
                    <h3>Управление пользователями</h3>
                    <button class="btn btn-primary">+ Добавить пользователя</button>
                </div>
                <div class="users-table" id="usersTable">
                    <!-- Users will be loaded here -->
                </div>
            </div>
        `;
        this.loadUsers();
    }

    loadAnalyticsContent() {
        const content = document.getElementById('admin-content');
        content.innerHTML = `
            <div class="analytics-section">
                <div class="section-header">
                    <h3>Аналитика и статистика</h3>
                    <div class="date-filters">
                        <select id="dateRange">
                            <option value="week">Неделя</option>
                            <option value="month" selected>Месяц</option>
                            <option value="quarter">Квартал</option>
                            <option value="year">Год</option>
                        </select>
                    </div>
                </div>
                <div class="analytics-grid">
                    <div class="chart-container">
                        <h3>Динамика продаж</h3>
                        <canvas id="salesChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <h3>Распределение по категориям</h3>
                        <canvas id="categoriesChart"></canvas>
                    </div>
                </div>
            </div>
        `;
        this.loadAnalytics();
    }

    loadReportsContent() {
        const content = document.getElementById('admin-content');
        content.innerHTML = `
            <div class="reports-section">
                <div class="section-header">
                    <h3>Отчеты и экспорт</h3>
                </div>
                <div class="reports-grid">
                    <div class="report-card">
                        <h4>Ежемесячный отчет</h4>
                        <p>Полный отчет по продажам и заказам</p>
                        <button class="btn btn-primary" onclick="adminDashboard.generateReport('monthly')">Сгенерировать PDF</button>
                    </div>
                    <div class="report-card">
                        <h4>Экспорт заказов</h4>
                        <p>Экспорт данных заказов в Excel</p>
                        <button class="btn btn-secondary" onclick="adminDashboard.exportOrders('excel')">Экспорт Excel</button>
                    </div>
                    <div class="report-card">
                        <h4>Экспорт пользователей</h4>
                        <p>Экспорт данных пользователей в CSV</p>
                        <button class="btn btn-secondary" onclick="adminDashboard.exportUsers('csv')">Экспорт CSV</button>
                    </div>
                </div>
            </div>
        `;
    }

    loadSettingsContent() {
        const content = document.getElementById('admin-content');
        content.innerHTML = `
            <div class="settings-section">
                <div class="section-header">
                    <h3>Настройки системы</h3>
                </div>
                <div class="settings-grid">
                    <div class="setting-card">
                        <h4>Общие настройки</h4>
                        <form>
                            <label>Название компании</label>
                            <input type="text" value="SanderStu" />
                            <label>Email для уведомлений</label>
                            <input type="email" value="admin@sanderstu.com" />
                            <button type="submit" class="btn btn-primary">Сохранить</button>
                        </form>
                    </div>
                    <div class="setting-card">
                        <h4>Тема оформления</h4>
                        <div class="theme-options">
                            <button class="theme-btn active" data-theme="light">Светлая</button>
                            <button class="theme-btn" data-theme="dark">Темная</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        this.setupThemeToggle();
    }

    setupThemeToggle() {
        document.querySelectorAll('.theme-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                const theme = btn.dataset.theme;
                document.body.classList.toggle('dark', theme === 'dark');
                localStorage.setItem('admin-theme', theme);
            });
        });

        // Load saved theme
        const savedTheme = localStorage.getItem('admin-theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark');
            document.querySelector('[data-theme="dark"]')?.classList.add('active');
        }
    }

    async loadServices() {
        // Mock services data
        const services = [
            { id: 1, name: 'YouTube реклама', price: 50000, status: 'active', orders: 15 },
            { id: 2, name: 'Instagram Stories', price: 25000, status: 'active', orders: 23 },
            { id: 3, name: 'Telegram канал', price: 30000, status: 'inactive', orders: 8 }
        ];

        this.renderServices(services);
    }

    renderServices(services) {
        const container = document.getElementById('servicesGrid');
        if (!container) return;

        container.innerHTML = services.map(service => `
            <div class="service-card">
                <div class="service-header">
                    <h4>${service.name}</h4>
                    <span class="service-status ${service.status}">${service.status === 'active' ? 'Активна' : 'Неактивна'}</span>
                </div>
                <div class="service-info">
                    <p>Цена: ${service.price.toLocaleString('ru-RU')} ₽</p>
                    <p>Заказов: ${service.orders}</p>
                </div>
                <div class="service-actions">
                    <button class="btn btn-sm" onclick="adminDashboard.editService(${service.id})">Редактировать</button>
                    <button class="btn btn-sm btn-danger" onclick="adminDashboard.deleteService(${service.id})">Удалить</button>
                </div>
            </div>
        `).join('');
    }

    async loadOrders() {
        try {
            const response = await fetch('/api/v2/admin/orders/', {
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                const orders = data.results || data;
                this.renderOrders(orders);
            } else if (response.status === 401) {
                // Try to refresh token
                try {
                    const refreshResponse = await this.refreshToken();
                    if (refreshResponse.access) {
                        this.setTokens(refreshResponse.access, refreshResponse.refresh);
                        const retryResponse = await fetch('/api/v2/admin/orders/', {
                            headers: this.getAuthHeaders()
                        });
                        if (retryResponse.ok) {
                            const data = await retryResponse.json();
                            const orders = data.results || data;
                            this.renderOrders(orders);
                        }
                    }
                } catch (refreshError) {
                    console.error('Token refresh failed:', refreshError);
                }
            }
        } catch (error) {
            console.error('Error loading orders:', error);
        }
    }

    renderOrders(orders) {
        const container = document.getElementById('ordersTable');
        if (!container) return;

        container.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Клиент</th>
                        <th>Услуга</th>
                        <th>Статус</th>
                        <th>Дата</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    ${orders.map(order => `
                        <tr>
                            <td>#${order.id}</td>
                            <td>${order.full_name || order.user?.username || 'Неизвестно'}</td>
                            <td>${order.offer?.title || 'Персональный заказ'}</td>
                            <td><span class="status-badge ${order.status}">${this.getStatusText(order.status)}</span></td>
                            <td>${new Date(order.created_at).toLocaleDateString('ru-RU')}</td>
                            <td>
                                <button class="btn btn-sm" onclick="adminDashboard.viewOrder(${order.id})">Просмотр</button>
                                <button class="btn btn-sm" onclick="adminDashboard.updateOrderStatus(${order.id})">Изменить статус</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    async loadUsers() {
        try {
            const response = await fetch('/api/v2/admin/users/', {
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                const users = data.results || data;
                this.renderUsers(users);
            } else if (response.status === 401) {
                // Try to refresh token
                try {
                    const refreshResponse = await this.refreshToken();
                    if (refreshResponse.access) {
                        this.setTokens(refreshResponse.access, refreshResponse.refresh);
                        const retryResponse = await fetch('/api/v2/admin/users/', {
                            headers: this.getAuthHeaders()
                        });
                        if (retryResponse.ok) {
                            const data = await retryResponse.json();
                            const users = data.results || data;
                            this.renderUsers(users);
                        }
                    }
                } catch (refreshError) {
                    console.error('Token refresh failed:', refreshError);
                }
            }
        } catch (error) {
            console.error('Error loading users:', error);
        }
    }

    renderUsers(users) {
        const container = document.getElementById('usersTable');
        if (!container) return;

        container.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Имя</th>
                        <th>Email</th>
                        <th>Роль</th>
                        <th>Статус</th>
                        <th>Дата регистрации</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    ${users.map(user => `
                        <tr>
                            <td>${user.id}</td>
                            <td>${user.profile?.full_name || user.username}</td>
                            <td>${user.email}</td>
                            <td>${user.profile?.role || 'user'}</td>
                            <td><span class="status-badge ${user.is_active ? 'active' : 'inactive'}">${user.is_active ? 'Активен' : 'Заблокирован'}</span></td>
                            <td>${new Date(user.date_joined).toLocaleDateString('ru-RU')}</td>
                            <td>
                                <button class="btn btn-sm" onclick="adminDashboard.editUser(${user.id})">Редактировать</button>
                                <button class="btn btn-sm ${user.is_active ? 'btn-danger' : 'btn-success'}" onclick="adminDashboard.toggleUserStatus(${user.id})">
                                    ${user.is_active ? 'Заблокировать' : 'Разблокировать'}
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    loadAnalytics() {
        // Initialize analytics charts
        setTimeout(() => {
            this.initializeAnalyticsCharts();
        }, 100);
    }

    initializeAnalyticsCharts() {
        // Sales Chart
        const salesCtx = document.getElementById('salesChart');
        if (salesCtx) {
            new Chart(salesCtx, {
                type: 'bar',
                data: {
                    labels: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
                    datasets: [{
                        label: 'Продажи',
                        data: [120000, 150000, 180000, 200000, 160000, 140000, 110000],
                        backgroundColor: '#3b82f6'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }

        // Categories Chart
        const categoriesCtx = document.getElementById('categoriesChart');
        if (categoriesCtx) {
            new Chart(categoriesCtx, {
                type: 'pie',
                data: {
                    labels: ['YouTube', 'Instagram', 'Telegram', 'TikTok'],
                    datasets: [{
                        data: [40, 30, 20, 10],
                        backgroundColor: ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
    }

    // Utility methods
    getAuthHeaders() {
        const token = localStorage.getItem('access');
        return {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }

    setTokens(access, refresh) {
        localStorage.setItem('access', access);
        if (refresh) {
            localStorage.setItem('refresh', refresh);
        }
    }

    async refreshToken() {
        const refreshToken = localStorage.getItem('refresh');
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }

        const response = await fetch('/api/v2/auth/refresh/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                refresh: refreshToken
            })
        });

        if (!response.ok) {
            throw new Error('Token refresh failed');
        }

        return await response.json();
    }

    showToast(message, type = 'info') {
        const toast = document.getElementById('adminToast');
        if (toast) {
            toast.textContent = message;
            toast.className = `admin-toast ${type} show`;
            
            setTimeout(() => {
                toast.classList.remove('show');
            }, 3000);
        }
    }

    logout() {
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        localStorage.removeItem('userEmail');
        localStorage.removeItem('userFullName');
        window.location.href = '/';
    }

    // Action methods
    async addService() {
        const title = prompt('Название услуги:');
        if (!title) return;
        
        const description = prompt('Описание услуги:');
        const price = prompt('Цена услуги:');
        if (!price || isNaN(price)) {
            this.showToast('Введите корректную цену', 'error');
            return;
        }
        
        const social_network = prompt('Социальная сеть:');

        try {
            const response = await fetch('/api/v2/admin/services/create/', {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({
                    title: title,
                    description: description || '',
                    price: parseFloat(price),
                    social_network: social_network || ''
                })
            });

            if (response.ok) {
                this.showToast('Услуга добавлена успешно', 'success');
                this.loadServices(); // Refresh services list
            } else {
                const error = await response.json();
                this.showToast('Ошибка добавления услуги: ' + error.detail, 'error');
            }
        } catch (error) {
            console.error('Error adding service:', error);
            this.showToast('Ошибка добавления услуги', 'error');
        }
    }

    async editService(id) {
        const title = prompt('Новое название услуги:');
        if (!title) return;
        
        const description = prompt('Новое описание услуги:');
        const price = prompt('Новая цена услуги:');
        if (!price || isNaN(price)) {
            this.showToast('Введите корректную цену', 'error');
            return;
        }
        
        const social_network = prompt('Социальная сеть:');
        const is_active = confirm('Услуга активна?');

        try {
            const response = await fetch(`/api/v2/admin/services/${id}/update/`, {
                method: 'PUT',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({
                    title: title,
                    description: description || '',
                    price: parseFloat(price),
                    social_network: social_network || '',
                    is_active: is_active
                })
            });

            if (response.ok) {
                this.showToast('Услуга обновлена успешно', 'success');
                this.loadServices(); // Refresh services list
            } else {
                const error = await response.json();
                this.showToast('Ошибка обновления услуги: ' + error.detail, 'error');
            }
        } catch (error) {
            console.error('Error updating service:', error);
            this.showToast('Ошибка обновления услуги', 'error');
        }
    }

    async deleteService(id) {
        if (!confirm('Вы уверены, что хотите удалить эту услугу?')) {
            return;
        }

        try {
            const response = await fetch(`/api/v2/admin/services/${id}/delete/`, {
                method: 'DELETE',
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                this.showToast('Услуга удалена успешно', 'success');
                this.loadServices(); // Refresh services list
            } else {
                this.showToast('Ошибка удаления услуги', 'error');
            }
        } catch (error) {
            console.error('Error deleting service:', error);
            this.showToast('Ошибка удаления услуги', 'error');
        }
    }

    viewOrder(id) {
        this.showToast(`Просмотр заказа #${id}`, 'info');
    }

    updateOrderStatus(id) {
        this.showToast(`Изменение статуса заказа #${id}`, 'info');
    }

    async editUser(id) {
        const email = prompt('Новый email:');
        if (!email) return;
        
        const full_name = prompt('Новое ФИО:');
        const password = prompt('Новый пароль (оставьте пустым, чтобы не менять):');
        const role = prompt('Роль (user/admin):') || 'user';

        try {
            const response = await fetch(`/api/v2/admin/users/${id}/update/`, {
                method: 'PUT',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({
                    email: email,
                    full_name: full_name || '',
                    password: password || '',
                    role: role
                })
            });

            if (response.ok) {
                this.showToast('Пользователь обновлен успешно', 'success');
                this.loadUsers(); // Refresh users list
            } else {
                const error = await response.json();
                this.showToast('Ошибка обновления пользователя: ' + error.detail, 'error');
            }
        } catch (error) {
            console.error('Error updating user:', error);
            this.showToast('Ошибка обновления пользователя', 'error');
        }
    }

    async deleteUser(id) {
        if (!confirm('Вы уверены, что хотите удалить этого пользователя?')) {
            return;
        }

        try {
            const response = await fetch(`/api/v2/admin/users/${id}/delete/`, {
                method: 'DELETE',
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                this.showToast('Пользователь удален успешно', 'success');
                this.loadUsers(); // Refresh users list
            } else {
                this.showToast('Ошибка удаления пользователя', 'error');
            }
        } catch (error) {
            console.error('Error deleting user:', error);
            this.showToast('Ошибка удаления пользователя', 'error');
        }
    }

    async addUser() {
        const email = prompt('Email пользователя:');
        if (!email) return;
        
        const password = prompt('Пароль:');
        if (!password) {
            this.showToast('Пароль обязателен', 'error');
            return;
        }
        
        const full_name = prompt('ФИО:');
        const role = prompt('Роль (user/admin):') || 'user';

        try {
            const response = await fetch('/api/v2/admin/users/create/', {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({
                    email: email,
                    password: password,
                    full_name: full_name || '',
                    role: role
                })
            });

            if (response.ok) {
                this.showToast('Пользователь создан успешно', 'success');
                this.loadUsers(); // Refresh users list
            } else {
                const error = await response.json();
                this.showToast('Ошибка создания пользователя: ' + error.detail, 'error');
            }
        } catch (error) {
            console.error('Error creating user:', error);
            this.showToast('Ошибка создания пользователя', 'error');
        }
    }

    generateReport(type) {
        this.showToast(`Генерация отчета: ${type}`, 'info');
    }

    async exportOrders(format) {
        try {
            const response = await fetch('/api/v2/admin/export/orders/csv/', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'orders.csv';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                this.showToast('Заказы экспортированы в CSV', 'success');
            } else {
                this.showToast('Ошибка экспорта заказов', 'error');
            }
        } catch (error) {
            console.error('Export error:', error);
            this.showToast('Ошибка экспорта заказов', 'error');
        }
    }

    async exportUsers(format) {
        try {
            const response = await fetch('/api/v2/admin/export/users/csv/', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'users.csv';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                this.showToast('Пользователи экспортированы в CSV', 'success');
            } else {
                this.showToast('Ошибка экспорта пользователей', 'error');
            }
        } catch (error) {
            console.error('Export error:', error);
            this.showToast('Ошибка экспорта пользователей', 'error');
        }
    }

    async exportServices(format) {
        try {
            const response = await fetch('/api/v2/admin/export/services/csv/', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'services.csv';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                this.showToast('Услуги экспортированы в CSV', 'success');
            } else {
                this.showToast('Ошибка экспорта услуг', 'error');
            }
        } catch (error) {
            console.error('Export error:', error);
            this.showToast('Ошибка экспорта услуг', 'error');
        }
    }

    async generateMonthlyReport() {
        try {
            const response = await fetch('/api/v2/admin/reports/monthly/', {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'monthly_report.json';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                this.showToast('Месячный отчет сгенерирован', 'success');
            } else {
                this.showToast('Ошибка генерации отчета', 'error');
            }
        } catch (error) {
            console.error('Report generation error:', error);
            this.showToast('Ошибка генерации отчета', 'error');
        }
    }

    // Modal management
    openOrdersModal() {
        const modal = document.getElementById('ordersModal');
        if (modal) {
            modal.style.display = 'block';
            this.loadAllOrders();
        }
    }

    closeOrdersModal() {
        const modal = document.getElementById('ordersModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    async loadAllOrders() {
        try {
            const response = await fetch('/api/v2/admin/orders/', {
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                const orders = data.results || data;
                this.renderOrdersTable(orders);
            }
        } catch (error) {
            console.error('Error loading orders:', error);
        }
    }

    renderOrdersTable(orders) {
        const container = document.getElementById('ordersTableContainer');
        if (!container) return;

        const statusMap = {
            'new': {text: 'Новый', class: 'new'},
            'paid': {text: 'Оплачен', class: 'paid'},
            'in_progress': {text: 'В работе', class: 'in_progress'},
            'done': {text: 'Выполнен', class: 'done'},
            'cancelled': {text: 'Отменен', class: 'cancelled'}
        };

        container.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Клиент</th>
                        <th>Email</th>
                        <th>Телефон</th>
                        <th>Услуга</th>
                        <th>Цена</th>
                        <th>Статус</th>
                        <th>Дата</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    ${orders.map(order => `
                        <tr>
                            <td>#${order.id}</td>
                            <td>${order.full_name || order.user?.username || 'Неизвестно'}</td>
                            <td>${order.email || order.user?.email || ''}</td>
                            <td>${order.phone || ''}</td>
                            <td>${order.offer?.title || 'Персональный заказ'}</td>
                            <td>${order.offer?.price ? order.offer.price.toLocaleString('ru-RU') + ' ₽' : '-'}</td>
                            <td><span class="status-badge ${order.status}">${statusMap[order.status]?.text || order.status}</span></td>
                            <td>${new Date(order.created_at).toLocaleDateString('ru-RU')}</td>
                            <td>
                                <button class="btn btn-sm" onclick="adminDashboard.changeOrderStatus(${order.id}, '${order.status}')">Изменить</button>
                                <button class="btn btn-sm btn-danger" onclick="adminDashboard.deleteOrder(${order.id})">Удалить</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    changeOrderStatus(id, currentStatus) {
        const statusModal = document.getElementById('statusModal');
        const orderIdInput = document.getElementById('statusOrderId');
        const statusSelect = document.getElementById('newStatus');
        
        if (statusModal && orderIdInput && statusSelect) {
            orderIdInput.value = id;
            statusSelect.value = currentStatus;
            statusModal.style.display = 'block';
        }
    }

    closeStatusModal() {
        const modal = document.getElementById('statusModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    async saveStatusChange() {
        const orderId = document.getElementById('statusOrderId').value;
        const newStatus = document.getElementById('newStatus').value;

        try {
            const response = await fetch(`/api/v2/admin/orders/${orderId}/status/`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({status: newStatus})
            });

            if (response.ok) {
                this.showToast('Статус изменен успешно', 'success');
                this.closeStatusModal();
                this.loadAllOrders(); // Refresh orders
            } else {
                const error = await response.json();
                this.showToast('Ошибка изменения статуса: ' + error.detail, 'error');
            }
        } catch (error) {
            console.error('Error updating status:', error);
            this.showToast('Ошибка изменения статуса', 'error');
        }
    }

    async deleteOrder(id) {
        if (!confirm('Вы уверены, что хотите удалить этот заказ?')) {
            return;
        }

        try {
            const response = await fetch(`/api/v2/admin/orders/${id}/delete/`, {
                method: 'DELETE',
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                this.showToast('Заказ удален успешно', 'success');
                this.loadAllOrders(); // Refresh orders
            } else {
                this.showToast('Ошибка удаления заказа', 'error');
            }
        } catch (error) {
            console.error('Error deleting order:', error);
            this.showToast('Ошибка удаления заказа', 'error');
        }
    }
}

// Global functions for modal management
function openOrdersModal() {
    window.adminDashboard.openOrdersModal();
}

function closeOrdersModal() {
    window.adminDashboard.closeOrdersModal();
}

function closeStatusModal() {
    window.adminDashboard.closeStatusModal();
}

// Initialize admin dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.adminDashboard = new AdminDashboard();
    
    // Setup status change form
    const statusForm = document.getElementById('statusChangeForm');
    if (statusForm) {
        statusForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await window.adminDashboard.saveStatusChange();
        });
    }
});
