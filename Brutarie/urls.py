from django.urls import path
from . import views
from .sitemap import ProductSitemap, CategorySitemap, PromotionSitemap, BakerySitemap, StaticViewSitemap
from django.contrib.sitemaps.views import sitemap


sitemaps = {
    'products': ProductSitemap,
    'categories': CategorySitemap,
    'promotions': PromotionSitemap,
    'bakeries': BakerySitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [    

    path('home/', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('success/', views.success_view, name='success'),
    path('add-product/', views.add_product, name='add_product'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('confirm_email/<str:cod>/', views.confirm_email, name='confirm_email'),

    path('products/', views.product_list, name='product_list'),
    path('promotions/', views.promotion_list, name='promotion_list'),
    path('bakeries/', views.bakery_list, name='bakery_list'),
    path('categories/', views.category_list, name='category_list'),

    path('claim_offer/', views.claim_offer, name='claim_offer'),
    path('banner/', views.banner_view, name='banner'),
    path('offer_page/', views.offer_view, name='offer_page'),

    path('error_403/', views.error_403_view, name='error_403'),

    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('promotion/<int:promotion_id>/', views.promotion_detail, name='promotion_detail'),
    path('bakery/<int:bakery_id>/', views.bakery_detail, name='bakery_detail'),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]
