from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json


def home_page(request):
    return render(request, "shop/home.html")


def buy_ads_page(request):
    return render(request, "shop/buy.html")


def order_ads_page(request):
    return render(request, "shop/order.html")


def my_orders_page(request):
    return render(request, "shop/my_orders.html")


def profile_page(request):
    return render(request, "shop/profile.html")


def search_results_page(request):
    """Страница результатов поиска"""
    query = request.GET.get('q', '')
    context = {
        'query': query,
    }
    return render(request, "shop/search_results.html", context)

def new_admin_page(request):
    """Новая админ-панель"""
    return render(request, "shop/new_admin.html")


def admin_dashboard(request):
    # Проверяем, что пользователь авторизован и является админом
    if not request.user.is_authenticated:
        return redirect('/')
    
    # Проверяем роль админа
    is_admin = (
        request.user.is_staff or 
        request.user.is_superuser or 
        (hasattr(request.user, 'profile') and request.user.profile.role == 'admin')
    )
    
    if not is_admin:
        return redirect('/')
    
    return render(request, "shop/admin_dashboard.html")


MOCK_ADS = [
    {
        "id": 1,
        "title": "Баннер на главной",
        "description": "Размещение баннера 728x90 на главной странице",
        "category": "Баннеры",
        "price": 15000,
        "popularity": 95,
        "image": "/static/shop/img/banner_main.svg",
    },
    {
        "id": 2,
        "title": "Пост в соцсетях",
        "description": "Нативная интеграция в Instagram и Facebook",
        "category": "Соцсети",
        "price": 12000,
        "popularity": 88,
        "image": "/static/shop/img/social_post.svg",
    },
    {
        "id": 3,
        "title": "Реклама в рассылке",
        "description": "Баннер или нативный блок в email-рассылке",
        "category": "Email",
        "price": 9000,
        "popularity": 72,
        "image": "/static/shop/img/email_ad.svg",
    },
]


def _filter_and_sort_ads(query_params):
    keyword = query_params.get("q", "").lower()
    category = query_params.get("category", "").lower()
    sort_by = query_params.get("sort", "").lower()  # price_asc, price_desc, popularity

    filtered = [
        ad
        for ad in MOCK_ADS
        if (not keyword or keyword in ad["title"].lower() or keyword in ad["description"].lower())
        and (not category or category == ad["category"].lower())
    ]

    if sort_by == "price_asc":
        filtered.sort(key=lambda a: a["price"])
    elif sort_by == "price_desc":
        filtered.sort(key=lambda a: -a["price"])
    elif sort_by == "popularity":
        filtered.sort(key=lambda a: -a["popularity"])

    return filtered


def api_ads_list(request):
    data = _filter_and_sort_ads(request.GET)
    return JsonResponse({"results": data})


def api_ads_detail(request, ad_id: int):
    ad = next((a for a in MOCK_ADS if a["id"] == ad_id), None)
    if not ad:
        return JsonResponse({"detail": "Not found"}, status=404)
    return JsonResponse(ad)


@csrf_exempt
@require_http_methods(["POST"])
def api_order_create(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        payload = {}
    return JsonResponse({"status": "ok", "received": payload})


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    return JsonResponse({"status": "ok", "message": "Logged in (mock)"})


@csrf_exempt
@require_http_methods(["POST"])
def api_register(request):
    return JsonResponse({"status": "ok", "message": "Registered (mock)"})

