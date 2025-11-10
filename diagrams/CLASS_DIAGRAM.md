# Диаграмма классов системы SanderStu

## Основные классы

```mermaid
classDiagram
    class User {
        +String username
        +String email
        +String first_name
        +String last_name
        +Boolean is_staff
        +Boolean is_superuser
        +DateTime date_joined
    }

    class Profile {
        +String full_name
        +Integer birth_year
        +String role
        +String card_last4
        +User user
    }

    class Manager {
        +String phone
        +String department
        +Date hire_date
        +Boolean is_active
        +User user
    }

    class Blogger {
        +String name
        +String social_network
        +String topic
        +Integer audience_size
        +Manager manager
    }

    class AdOffer {
        +String title
        +String description
        +Decimal price
        +String social_network
        +Boolean is_active
        +DateTime created_at
        +DateTime updated_at
        +Blogger blogger
    }

    class AdService {
        +String name
        +String social_network
        +Decimal price
        +String description
        +Boolean is_active
        +Blogger blogger
        +Manager manager
    }

    class Order {
        +String order_type
        +String status
        +String payment_status
        +Decimal payment_amount
        +DateTime payment_date
        +String full_name
        +String email
        +String phone
        +String ad_type
        +Decimal budget
        +String description
        +User user
        +AdOffer offer
    }

    class ManagerOrder {
        +String order_type
        +String status
        +String client_name
        +String client_email
        +String client_phone
        +String service_description
        +Decimal budget
        +Manager manager
        +Order blogger_order
    }

    class Category {
        +String name
        +String slug
    }

    class Ad {
        +String title
        +String description
        +Decimal price
        +Integer popularity
        +String image
        +Boolean is_active
        +Category category
    }

    class Review {
        +Integer rating
        +String text
        +DateTime created_at
        +User user
        +Blogger blogger
        +AdOffer offer
    }

    class WeeklyReport {
        +Date week_start
        +Date week_end
        +Integer total_orders
        +Decimal total_revenue
        +Integer active_services
        +File pdf_file
        +Manager manager
    }

    class Notification {
        +String notification_type
        +String title
        +String message
        +Boolean is_read
        +DateTime created_at
        +Manager manager
    }

    User ||--|| Profile : has
    User ||--o| Manager : has
    Manager ||--o{ Blogger : manages
    Blogger ||--o{ AdOffer : has
    Manager ||--o{ AdService : creates
    Blogger ||--o{ AdService : has
    Manager ||--o{ ManagerOrder : manages
    Manager ||--o{ WeeklyReport : generates
    Manager ||--o{ Notification : receives
    
    User ||--o{ Order : makes
    AdOffer ||--o{ Order : generates
    Order ||--o{ ManagerOrder : creates
    
    AdOffer ||--o{ Review : has
    Blogger ||--o{ Review : receives
    
    Category ||--o{ Ad : contains
```

## Описание отношений

### Пользователи и профили
- `User` - стандартная модель Django для пользователей
- `Profile` - расширенный профиль с дополнительной информацией (1:1 с User)
- `Manager` - профиль менеджера (1:1 с User)

### Блоггеры и услуги
- `Blogger` - модель блоггера, который продает рекламу
- `AdOffer` - предложения блоггеров (привязаны к блоггерам)
- `AdService` - услуги, созданные менеджерами (привязаны к блоггерам и менеджерам)

### Заказы
- `Order` - заказы пользователей на рекламу
- `ManagerOrder` - заказы под управлением менеджеров (связаны с Order для блоггеров или независимы для персональных)

### Система отчетности
- `WeeklyReport` - еженедельные отчеты менеджеров
- `Notification` - уведомления для менеджеров

### Отзывы
- `Review` - отзывы пользователей о блоггерах и их услугах

