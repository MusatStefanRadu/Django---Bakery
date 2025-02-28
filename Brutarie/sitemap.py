from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from .models import Bakery, Product, Promotion, Category, CustomUser, VehicleFleet, Employee

class ProductSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    def items(self):
        # Return all bakery products
        return Product.objects.all()
    def lastmod(self, obj):
        # Returns the last modification date for each product
        return obj.updated_at  
    def location(self, obj):
        # Return the URL of each product
        return reverse('product_detail', args=[obj.product_id])  


# Category sitemap
class CategorySitemap(Sitemap):
    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return reverse('category_detail', args=[obj.category_id])  
    

# Sitemap for promotions
class PromotionSitemap(Sitemap):
    def items(self):
        return Promotion.objects.all()

    def location(self, obj):
        return reverse('promotion_detail', args=[obj.promotion_id])  
    

# Sitemap for bakers
class BakerySitemap(Sitemap):
    def items(self):
        return Bakery.objects.all()

    def location(self, obj):
        return reverse('bakery_detail', args=[obj.bakery_id])  


# Sitemap for static pages ("home", "about", "contact")
class StaticViewSitemap(Sitemap):
    def items(self):
        return [
            'home',
            'contact',
        ]

    def location(self, obj):
        return reverse(obj)

    def changefreq(self, obj):
        return 'monthly'

    def priority(self, obj):
        return 0.5
