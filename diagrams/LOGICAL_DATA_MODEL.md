# Логическая модель данных системы SanderStu

## Обзор системы

Система SanderStu предназначена для управления заказами рекламы у блоггеров. Логическая модель данных описывает структуру базы данных, все таблицы, их атрибуты, типы данных, ограничения и связи.

**Тип БД:** PostgreSQL 15  
**ORM:** Django 5.2.6  
**Кодировка:** UTF-8

---

## 1. Сущности и атрибуты

### 1.1. Пользователи и аутентификация

#### Таблица: `auth_user` (Django системная)
**Описание:** Системная таблица Django для хранения пользователей

| Атрибут | Тип данных | Ограничения | Описание |
|---------|-----------|-------------|----------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Уникальный идентификатор |
| `username` | VARCHAR(150) | UNIQUE, NOT NULL | Имя пользователя |
| `email` | VARCHAR(254) | NOT NULL | Email адрес |
| `password` | VARCHAR(128) | NOT NULL | Хэш пароля |
| `first_name` | VARCHAR(150) | | Имя |
| `last_name` | VARCHAR(150) | | Фамилия |
| `is_staff` | BOOLEAN | DEFAULT FALSE | Является сотрудником |
| `is_superuser` | BOOLEAN | DEFAULT FALSE | Является администратором |
| `date_joined` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Дата регистрации |
| `last_login` | TIMESTAMP | NULL | Дата последнего входа |

---

#### Таблица: `accounts_profile`
**Описание:** Расширенный профиль пользователя

| Атрибут | Тип данных | Ограничения | Описание |
|---------|-----------|-------------|----------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Уникальный идентификатор |
| `user_id` | INTEGER | FOREIGN KEY → auth_user.id, UNIQUE, NOT NULL | Связь с пользователем (1:1) |
| `full_name` | VARCHAR(200) | NOT NULL | Полное имя |
| `birth_year` | INTEGER | CHECK (birth_year >= 1900) | Год рождения |
| `role` | VARCHAR(20) | NOT NULL, DEFAULT 'user' | Роль: 'user', 'admin', 'manager' |
| `card_last4` | VARCHAR(4) | | Последние 4 цифры карты |

**Связи:**
- `user_id` → `auth_user.id` (ONE-TO-ONE)

---

### 1.2. Менеджеры

#### Таблица: `managers_manager`
**Описание:** Менеджеры системы с дополнительной информацией

| Атрибут | Тип данных | Ограничения | Описание |
|---------|-----------|-------------|----------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Уникальный идентификатор |
| `user_id` | INTEGER | FOREIGN KEY → auth_user.id, UNIQUE, NOT NULL | Связь с пользователем (1:1) |
| `phone` | VARCHAR(20) | | Телефон |
| `department` | VARCHAR(100) | | Отдел |
| `hire_date` | DATE | NOT NULL, DEFAULT CURRENT_DATE | Дата найма |
| `is_active` | BOOLEAN | DEFAULT TRUE | Активен ли менеджер |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Дата обновления |

**Связи:**
- `user_id` → `auth_user.id` (ONE-TO-ONE)

---

### 1.3. Блоггеры и предложения

#### Таблица: `bloggers_blogger`
**Описание:** Блоггеры, которые продают рекламу

| Атрибут | Тип данных | Ограничения | Описание |
|---------|-----------|-------------|----------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Уникальный идентификатор |
| `name` | VARCHAR(200) | NOT NULL | Имя блоггера |
| `social_network` | VARCHAR(30) | NOT NULL, CHECK IN ('instagram', 'tiktok', 'youtube', 'vk', 'telegram') | Соц. сеть |
| `topic` | VARCHAR(120) | NOT NULL | Тематика |
| `audience_size` | INTEGER | NOT NULL, DEFAULT 0, CHECK (audience_size >= 0) | Размер аудитории |
| `manager_id` | INTEGER | FOREIGN KEY → managers_manager.id, NULL | Менеджер (N:1) |

**Связи:**
- `manager_id` → `managers_manager.id` (MANY-TO-ONE)

**Индексы:**
- INDEX `idx_social_network` (`social_network`)
- INDEX `idx_manager_id` (`manager_id`)

---

#### Таблица: `bloggers_adoffer`
**Описание:** Рекламные предложения блоггеров

| Атрибут | Тип данных | Ограничения | Описание |
|---------|-----------|-------------|----------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Уникальный идентификатор |
| `blogger_id` | INTEGER | FOREIGN KEY → bloggers_blogger.id, NULL | Блоггер (N:1) |
| `title` | VARCHAR(200) | NOT NULL | Название предложения |
| `description` | TEXT | | Описание |
| `price` | DECIMAL(10,2) | NOT NULL, CHECK (price >= 0) | Цена |
| `social_network` | VARCHAR(30) | NOT NULL, CHECK IN ('instagram', 'tiktok', 'youtube', 'vk', 'telegram') | Соц. сеть |
| `is_active` | BOOLEAN | DEFAULT TRUE | Активно ли предложение |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Дата создания |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Дата обновления |

**Связи:**
- `blogger_id` → `bloggers_blogger.id` (MANY-TO-ONE)

**Индексы:**
- INDEX `idx_blogger_id` (`blogger_id`)
- INDEX `idx_is_active` (`is_active`)
- INDEX `idx_created_at` (`created_at`)

---

#### Таблица: `managers_adservice`
**Описание:** Рекламные услуги, созданные менеджерами

| Атрибут | Тип данных | Ограничения | Описание |
|---------|-----------|-------------|----------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Уникальный идентификатор |
| `name` | VARCHAR(200) | NOT NULL | Название услуги |
| `social_network` | VARCHAR(20) | NOT NULL | Соц. сеть |
| `price` | DECIMAL(10,2) | NOT NULL, CHECK (price >= 0) | Цена |
| `description` | TEXT | NOT NULL | Описание |
| `blogger_id` | INTEGER | FOREIGN KEY → bloggers_blogger.id, NOT NULL | Блоггер (N:1) |
| `manager_id` | INTEGER | FOREIGN KEY → managers_manager.id, NOT NULL | Менеджер (N:1) |
| `is_active` | BOOLEAN | DEFAULT TRUE | Активна ли услуга |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Дата обновления |

**Связи:**
- `blogger_id` → `bloggers_blogger.id` (MANY-TO-ONE)
- `manager_id` → `managers_manager.id` (MANY-TO-ONE)

**Индексы:**
- INDEX `idx_blogger_manager` (`blogger_id`, `manager_id`)
- INDEX `idx_is_active` (`is_active`)

---

### 1.4. Заказы

#### Таблица: `ads_order`
**Описание:** Заказы пользователей на рекламу

| Атрибут | Тип данных | Ограничения | Описание |
|---------|-----------|-------------|----------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Уникальный идентификатор |
| `user_id` | INTEGER | FOREIGN KEY → auth_user.id, NULL | Пользователь (N:1) |
| `offer_id` | INTEGER | FOREIGN KEY → bloggers_adoffer.id, NULL | Предложение (N:1) |
| `order_type` | VARCHAR(20) | NOT NULL, DEFAULT 'personal', CHECK IN ('offer', 'personal') | Тип заказа |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'new', CHECK IN ('new', 'paid', 'in_progress', 'done', 'cancelled') | Статус |
| `payment_status` | VARCHAR(20) | NOT NULL, DEFAULT 'pending', CHECK IN ('pending', 'paid', 'failed') | Статус оплаты |
| `payment_amount` | DECIMAL(10,2) | CHECK (payment_amount >= 0) | Сумма оплаты |
| `payment_date` | TIMESTAMP | | Дата оплаты |
| `performance` | JSON | DEFAULT '{}' | Эффективность (показы, переходы, CTR) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |
| `full_name` | VARCHAR(200) | | Полное имя (для персональных заказов) |
| `email` | VARCHAR(254) | | Email (для персональных заказов) |
| `phone` | VARCHAR(40) | | Телефон (для персональных заказов) |
| `ad_type` | VARCHAR(50) | | Тип рекламы |
| `budget` | DECIMAL(10,2) | CHECK (budget >= 0) | Бюджет |
| `description` | TEXT | | Описание |
| `deadline` | INTEGER | CHECK (deadline > 0) | Срок выполнения в днях |
| `requirements` | TEXT | | Дополнительные требования |

**Связи:**
- `user_id` → `auth_user.id` (MANY-TO-ONE)
- `offer_id` → `bloggers_adoffer.id` (MANY-TO-ONE)

**Индексы:**
- INDEX `idx_user_id` (`user_id`)
- INDEX `idx_offer_id` (`offer_id`)
- INDEX `idx_status` (`status`)
- INDEX `idx_created_at` (`created_at`)

---

#### Таблица: `managers_managerorder`
**Описание:** Заказы под управлением менеджеров

| Атрибут | Тип данных | Ограничения | Описание |
|---------|-----------|-------------|----------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Уникальный идентификатор |
| `manager_id` | INTEGER | FOREIGN KEY → managers_manager.id, NOT NULL | Менеджер (N:1) |
| `order_type` | VARCHAR(20) | NOT NULL, DEFAULT 'blogger', CHECK IN ('blogger', 'personal') | Тип заказа |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'new', CHECK IN ('new', 'accepted', 'in_progress', 'completed', 'cancelled') | Статус |
| `blogger_order_id` | INTEGER | FOREIGN KEY → ads_order.id, NULL | Заказ от блоггера (N:1) |
| `client_name` | VARCHAR(200) | | Имя клиента |
| `client_email` | VARCHAR(254) | | Email клиента |
| `client_phone` | VARCHAR(20) | | Телефон клиента |
| `service_description` | TEXT | | Описание услуги |
| `budget` | DECIMAL(10,2) | CHECK (budget >= 0) | Бюджет |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Дата обновления |

**Связи:**
- `manager_id` → `managers_manager.id` (MANY-TO-ONE)
- `blogger_order_id` → `ads_order.id` (MANY-TO-ONE)

**Индексы:**
- INDEX `idx_manager_id` (`manager_id`)
- INDEX `idx_status` (`status`)
- INDEX `idx_created_at` (`created_at`)

---

### 1.5. Категории и реклама (Shop)

#### Таблица: `shop_category`
**Описание:** Категории рекламы

| Атрибут | Тип данных | Ограничения | Описание |
|---------|-----------|-------------|----------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Уникальный идентификатор |
| `name` | VARCHAR(120) | UNIQUE, NOT NULL | Название категории |
| `slug` | VARCHAR(140) | UNIQUE, NOT NULL | URL slug |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Дата обновления |

**Индексы:**
- UNIQUE INDEX `idx_name` (`name`)
- UNIQUE INDEX `idx_slug` (`slug`)

---

#### Таблица: `shop_ad`
**Описание:** Рекламные объявления в магазине

| Атрибут | Тип данных | Ограничения | Описание |
|---------|-----------|-------------|----------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Уникальный идентификатор |
| `title` | VARCHAR(200) | NOT NULL | Название |
| `description` | TEXT | | Описание |
| `category_id` | INTEGER | FOREIGN KEY → shop_category.id, NOT NULL | Категория (N:1) |
| `price` | DECIMAL(10,2) | NOT NULL, CHECK (price >= 0) | Цена |
| `popularity` | INTEGER | DEFAULT 0, CHECK (popularity >= 0) | Популярность |
| `image` | VARCHAR(200) | | URL изображения |
| `is_active` | BOOLEAN | DEFAULT TRUE | Активно |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Дата обновления |

**Связи:**
- `category_id` → `shop_category.id` (MANY-TO-ONE)

**Индексы:**
- INDEX `idx_category_id` (`category_id`)
- INDEX `idx_is_active` (`is_active`)
- INDEX `idx_popularity` (`popularity` DESC, `price` ASC)

---

#### Таблица: `shop_package`
**Описание:** Пакеты услуг

| Атрибут | Тип данных | Ограничения | Описание |
|---------|-----------|-------------|----------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Уникальный идентификатор |
| `name` | VARCHAR(120) | NOT NULL | Название пакета |
| `description` | TEXT | | Описание |
| `price` | DECIMAL(10,2) | NOT NULL, CHECK (price >= 0) | Цена |
| `is_active` | BOOLEAN | DEFAULT TRUE | Активен |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Дата обновления |

**Индексы:**
- INDEX `idx_is_active` (`is_active`)

---

#### Таблица: `shop_order`
**Описание:** Заказы из магазина

| Атрибут | Тип данных | Ограничения | Описание |
|---------|-----------|-------------|----------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Уникальный идентификатор |
| `customer_name` | VARCHAR(120) | NOT NULL | Имя клиента |
| `email` | VARCHAR(254) | NOT NULL | Email |
| `phone` | VARCHAR(40) | NOT NULL | Телефон |
| `description` | TEXT | NOT NULL | Описание |
| `ad_id` | INTEGER | FOREIGN KEY → shop_ad.id, NULL | Реклама (N:1) |
| `package_id` | INTEGER | FOREIGN KEY → shop_package.id, NULL | Пакет (N:1) |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'new', CHECK IN ('new', 'in_progress', 'done', 'cancelled') | Статус |
| `payment_status` | VARCHAR(20) | NOT NULL, DEFAULT 'pending', CHECK IN ('pending', 'paid', 'failed') | Статус оплаты |
| `payment_amount` | DECIMAL(10,2) | CHECK (payment_amount >= 0) | Сумма оплаты |
| `payment_date` | TIMESTAMP | | Дата оплаты |
| `user_id` | INTEGER | FOREIGN KEY → auth_user.id, NULL | Пользователь (N:1) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Дата обновления |

**Связи:**
- `ad_id` → `shop_ad.id` (MANY-TO-ONE)
- `package_id` → `shop_package.id` (MANY-TO-ONE)
- `user_id` → `auth_user.id` (MANY-TO-ONE)

**Индексы:**
- INDEX `idx_user_id` (`user_id`)
- INDEX `idx_status` (`status`)
- INDEX `idx_created_at` (`created_at` DESC)

---

### 1.6. Отзывы

#### Таблица: `reviews_review`
**Описание:** Отзывы пользователей о блоггерах

| Атрибут | Тип данных | Ограничения | Описание |
|---------|-----------|-------------|----------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Уникальный идентификатор |
| `user_id` | INTEGER | FOREIGN KEY → auth_user.id, NOT NULL | Пользователь (N:1) |
| `blogger_id` | INTEGER | FOREIGN KEY → bloggers_blogger.id, NOT NULL | Блоггер (N:1) |
| `offer_id` | INTEGER | FOREIGN KEY → bloggers_adoffer.id, NULL | Предложение (N:1) |
| `rating` | SMALLINT | NOT NULL, DEFAULT 5, CHECK (rating >= 1 AND rating <= 5) | Оценка (1-5) |
| `text` | TEXT | NOT NULL | Текст отзыва |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |

**Связи:**
- `user_id` → `auth_user.id` (MANY-TO-ONE)
- `blogger_id` → `bloggers_blogger.id` (MANY-TO-ONE)
- `offer_id` → `bloggers_adoffer.id` (MANY-TO-ONE)

**Индексы:**
- INDEX `idx_user_id` (`user_id`)
- INDEX `idx_blogger_id` (`blogger_id`)
- INDEX `idx_rating` (`rating`)

**Ограничения:**
- CHECK `rating` BETWEEN 1 AND 5

---

#### Таблица: `shop_review`
**Описание:** Отзывы в магазине

| Атрибут | Тип данных | Ограничения | Описание |
|---------|-----------|-------------|----------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Уникальный идентификатор |
| `user_name` | VARCHAR(120) | NOT NULL | Имя отзывающегося |
| `rating` | SMALLINT | NOT NULL, DEFAULT 5, CHECK (rating >= 1 AND rating <= 5) | Оценка |
| `text` | TEXT | NOT NULL | Текст отзыва |
| `ad_id` | INTEGER | FOREIGN KEY → shop_ad.id, NULL | Реклама (N:1) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Дата обновления |

**Связи:**
- `ad_id` → `shop_ad.id` (MANY-TO-ONE)

**Индексы:**
- INDEX `idx_ad_id` (`ad_id`)
- INDEX `idx_rating` (`rating`)

---

### 1.7. Отчеты и уведомления

#### Таблица: `managers_weeklyreport`
**Описание:** Еженедельные отчеты менеджеров

| Атрибут | Тип данных | Ограничения | Описание |
|---------|-----------|-------------|----------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Уникальный идентификатор |
| `manager_id` | INTEGER | FOREIGN KEY → managers_manager.id, NOT NULL | Менеджер (N:1) |
| `week_start` | DATE | NOT NULL | Начало недели |
| `week_end` | DATE | NOT NULL | Конец недели |
| `total_orders` | INTEGER | DEFAULT 0, CHECK (total_orders >= 0) | Всего заказов |
| `total_revenue` | DECIMAL(12,2) | DEFAULT 0, CHECK (total_revenue >= 0) | Общая выручка |
| `active_services` | INTEGER | DEFAULT 0, CHECK (active_services >= 0) | Активных услуг |
| `pdf_file` | VARCHAR(200) | | Путь к PDF файлу |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |

**Связи:**
- `manager_id` → `managers_manager.id` (MANY-TO-ONE)

**Индексы:**
- INDEX `idx_manager_id` (`manager_id`)
- INDEX `idx_week_start` (`week_start` DESC)

**Ограничения:**
- CHECK `week_end` >= `week_start`

---

#### Таблица: `managers_notification`
**Описание:** Уведомления для менеджеров

| Атрибут | Тип данных | Ограничения | Описание |
|---------|-----------|-------------|----------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Уникальный идентификатор |
| `manager_id` | INTEGER | FOREIGN KEY → managers_manager.id, NOT NULL | Менеджер (N:1) |
| `notification_type` | VARCHAR(20) | NOT NULL, CHECK IN ('service_created', 'service_updated', 'service_deleted', 'order_accepted', 'order_completed', 'report_generated') | Тип уведомления |
| `title` | VARCHAR(200) | NOT NULL | Заголовок |
| `message` | TEXT | NOT NULL | Сообщение |
| `is_read` | BOOLEAN | DEFAULT FALSE | Прочитано |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Дата создания |

**Связи:**
- `manager_id` → `managers_manager.id` (MANY-TO-ONE)

**Индексы:**
- INDEX `idx_manager_id` (`manager_id`)
- INDEX `idx_is_read` (`is_read`)
- INDEX `idx_created_at` (`created_at` DESC)

---

## 2. Связи между таблицами

### 2.1. Связи ONE-TO-ONE

```
auth_user ⟷ accounts_profile (1:1)
auth_user ⟷ managers_manager (1:1)
```

### 2.2. Связи ONE-TO-MANY

```
auth_user → ads_order
auth_user → reviews_review
auth_user → shop_order

managers_manager → bloggers_blogger
managers_manager → managers_adservice
managers_manager → managers_managerorder
managers_manager → managers_weeklyreport
managers_manager → managers_notification

bloggers_blogger → bloggers_adoffer
bloggers_blogger → managers_adservice
bloggers_blogger → reviews_review

bloggers_adoffer → ads_order
bloggers_adoffer → reviews_review

ads_order → managers_managerorder

shop_category → shop_ad
shop_ad → shop_order
shop_ad → shop_review
shop_package → shop_order
```

---

## 3. Типы данных PostgreSQL

| Django тип | PostgreSQL тип | Описание |
|-----------|---------------|----------|
| `CharField(max_length=N)` | `VARCHAR(N)` | Строка фиксированной длины |
| `TextField()` | `TEXT` | Длинный текст |
| `EmailField()` | `VARCHAR(254)` | Email адрес |
| `IntegerField()` | `INTEGER` | Целое число |
| `PositiveIntegerField()` | `INTEGER CHECK (>= 0)` | Неотрицательное целое |
| `SmallIntegerField()` | `SMALLINT` | Маленькое целое |
| `DecimalField()` | `DECIMAL(10,2)` | Десятичное число |
| `BooleanField()` | `BOOLEAN` | Логическое значение |
| `DateTimeField()` | `TIMESTAMP` | Дата и время |
| `DateField()` | `DATE` | Дата |
| `ForeignKey()` | `INTEGER` с FK constraint | Внешний ключ |
| `OneToOneField()` | `INTEGER` с UNIQUE | Один к одному |
| `JSONField()` | `JSONB` | JSON данные |
| `SlugField()` | `VARCHAR(140)` | URL slug |
| `URLField()` | `VARCHAR(200)` | URL |
| `FileField()` | `VARCHAR(200)` | Путь к файлу |

---

## 4. Ограничения целостности (Constraints)

### 4.1. CHECK ограничения

```sql
-- Положительные значения
CHECK (price >= 0)
CHECK (budget >= 0)
CHECK (audience_size >= 0)
CHECK (total_orders >= 0)

-- Диапазоны
CHECK (rating >= 1 AND rating <= 5)
CHECK (birth_year >= 1900)
CHECK (deadline > 0)

-- Даты
CHECK (week_end >= week_start)
```

### 4.2. NOT NULL ограничения

- Все первичные ключи
- Все внешние ключи (кроме опциональных)
- Обязательные поля (`username`, `email`, `password` в `auth_user`)

### 4.3. UNIQUE ограничения

- `auth_user.username`
- `accounts_profile.user_id` (ONE-TO-ONE)
- `managers_manager.user_id` (ONE-TO-ONE)
- `shop_category.name`
- `shop_category.slug`

### 4.4. FOREIGN KEY ограничения

Все внешние ключи имеют ограничения:
- `ON DELETE CASCADE` - каскадное удаление
- `ON DELETE SET NULL` - установка NULL
- `ON DELETE PROTECT` - запрет удаления

---

## 5. Индексы

### 5.1. Первичные ключи

Все таблицы имеют индекс на `id` (создаётся автоматически)

### 5.2. Внешние ключи

Все внешние ключи имеют индекс (создаётся автоматически)

### 5.3. Дополнительные индексы

```sql
-- Часто используемые поля
CREATE INDEX idx_social_network ON bloggers_blogger(social_network);
CREATE INDEX idx_is_active ON bloggers_adoffer(is_active);
CREATE INDEX idx_status ON ads_order(status);
CREATE INDEX idx_created_at ON ads_order(created_at);

-- Составные индексы
CREATE INDEX idx_popularity_price ON shop_ad(popularity DESC, price ASC);

-- UNIQUE индексы
CREATE UNIQUE INDEX idx_name ON shop_category(name);
CREATE UNIQUE INDEX idx_slug ON shop_category(slug);
```

---

## 6. Триггеры и правила

### 6.1. Автоматические timestamp

Django автоматически обновляет `updated_at` при изменении записи

### 6.2. Подсчёт статистики

Вычисляемые свойства через Django ORM:
- `Manager.active_orders_count` - количество активных заказов
- `Manager.managed_bloggers_count` - количество блоггеров

---

## 7. Нормализация

### 7.1. Первая нормальная форма (1NF)

✅ Все таблицы в 1NF - каждый атрибут содержит только атомарные значения

### 7.2. Вторая нормальная форма (2NF)

✅ Все таблицы в 2NF - все неключевые атрибуты полностью зависят от первичного ключа

### 7.3. Третья нормальная форма (3NF)

✅ Все таблицы в 3NF - нет транзитивных зависимостей

---

## 8. Оптимизация

### 8.1. Индексы

- Индексы на внешние ключи
- Индексы на часто используемые поля для фильтрации
- Составные индексы для оптимизации запросов

### 8.2. Файлы и медиа

- Статические файлы хранятся в `/staticfiles`
- Медиа файлы в `/media`
- Управление через Django `FileField`

### 8.3. Кэширование

- Можно добавить Redis для кэширования
- Кэширование популярных запросов к БД

---

## 9. Миграции

Django автоматически создаёт миграции при изменении моделей:

```bash
# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Откат миграций
python manage.py migrate app_name migration_number
```

---

## 10. Бэкап и восстановление

### Создание бэкапа

```bash
# PostgreSQL dump
pg_dump -U sanderstu sanderstu > backup.sql

# Восстановление
psql -U sanderstu sanderstu < backup.sql
```

### Экспорт через Django

```bash
# Экспорт данных
python manage.py dumpdata > fixtures/backup.json

# Импорт данных
python manage.py loaddata fixtures/backup.json
```

---

**Последнее обновление:** 2024  
**Версия модели:** 1.0  
**Статус:** Production ready

