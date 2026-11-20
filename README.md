
# ⚡ VOLTIX — Electronics E-commerce

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Django](https://img.shields.io/badge/Django-6.1.1-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-blue)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)
![Tests](https://img.shields.io/badge/Tests-49%20Passed-brightgreen)
![Deployment](https://img.shields.io/badge/Deployment-Render-purple)

## 📖 Про проєкт

**VOLTIX** — повнофункціональний інтернет-магазин
електроніки, розроблений на Django.

Проєкт створений як фінальна робота курсу GoITeens.
Його мета — реалізація сучасної e-commerce платформи
з повним циклом розробки: від проєктування бази даних
до розгортання у хмарному середовищі.

## 🌐 Live Demo

🔗 [Відкрити VOLTIX](https://voltix-lr6g.onrender.com/)

> Сайт розміщений на безкоштовному тарифі Render,
> тому перший запуск може займати певний час.

## 🚀 Основний функціонал

### Каталог товарів
- Категорії та підкатегорії
- Пошук товарів
- Фільтрація та сортування
- Детальні сторінки товарів
- Хіти продажу
- Галерея фотографій
- Нещодавно переглянуті товари

### Система користувачів
- Реєстрація та авторизація
- Кастомна модель користувача
- Особистий кабінет
- Список бажань (Wishlist)

### Кошик та замовлення
- Додавання товарів у кошик
- Зміна кількості товарів
- Оформлення замовлень
- Промокоди та знижки
- Історія замовлень
- Відстеження статусу замовлення

### Додаткові можливості
- Відгуки та оцінки товарів
- Django Admin
- REST API
- Адаптивний дизайн
- Django Messages

## 🛠 Технологічний стек

| Компонент | Технології |
|---|---|
| Backend | Python, Django |
| Frontend | HTML, CSS, JavaScript, Bootstrap |
| Database | SQLite, PostgreSQL |
| Cache | Redis (локальне середовище) |
| API | Django REST Framework |
| Media Storage | Cloudinary |
| Web Server | Gunicorn |
| Static Files | WhiteNoise |
| Containerization | Docker, Docker Compose |
| Deployment | Render |
| Version Control | Git, GitHub |

## ⚡ Оптимізація

- Оптимізація SQL-запитів
- Використання select_related та prefetch_related
- Усунення N+1 запитів на перевірених сторінках
- Кешування
- Django Debug Toolbar
- Оптимізація статичних файлів через WhiteNoise

## 🔐 Безпека

- Змінні середовища (.env)
- Production settings
- CSRF-захист
- Базовий захист від XSS
- Django ORM для захисту від SQL Injection
- Rate limiting
- HTTPS
- DEBUG=False у production

## 🧪 Тестування

Проєкт містить 49 автоматичних тестів.

| Середовище | Результат |
|---|---|
| SQLite | 49/49 Passed |
| PostgreSQL | 49/49 Passed |

Запуск тестів:

```bash
python manage.py test
```

## 📁 Структура проєкту

```text
Voltix/
├── accounts/
├── cart/
├── config/
├── docker/
├── orders/
├── reviews/
├── store/
├── wishlist/
├── static/
├── templates/
├── Dockerfile
├── compose.yaml
├── manage.py
├── requirements.txt
└── README.md
```

## 💻 Локальне встановлення

### 1. Клонування репозиторію

```bash
git clone https://github.com/ivanfoya09-source/Voltix.git
cd Voltix
```

### 2. Створення віртуального середовища

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Встановлення залежностей

```bash
python -m pip install -r requirements.txt
```

### 4. Налаштування середовища

Створіть файл `.env` у корені проєкту.

```dotenv
DEBUG=True
DJANGO_SECRET_KEY=your-local-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
USE_CLOUDINARY=False
```

### 5. Застосування міграцій

```bash
python manage.py migrate
```

### 6. Створення адміністратора

```bash
python manage.py createsuperuser
```

### 7. Запуск сервера

```bash
python manage.py runserver
```

Сайт буде доступний за адресою:

http://127.0.0.1:8000/

## 🐳 Запуск через Docker

```bash
docker compose up --build
```

Зупинка контейнерів:

```bash
docker compose down
```

## ☁️ Production Deployment

Проєкт розгорнуто на Render з використанням:

- Docker
- Gunicorn
- PostgreSQL
- Cloudinary
- WhiteNoise
- Environment Variables
- HTTPS

## 📊 Статистика проєкту

- 45 товарів на момент першого deployment
- 13 категорій
- 49 автоматичних тестів
- 6 основних Django-додатків

## 👨‍💻 Автор

**Ivan Foya**

Junior Web Developer / GoITeens Student

- GitHub: [ivanfoya09-source](https://github.com/ivanfoya09-source)

---

⚡ VOLTIX — Final Project | 2026
