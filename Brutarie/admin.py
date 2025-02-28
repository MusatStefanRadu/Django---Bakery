from django.contrib import admin
from .models import Category, Product, Bakery, Promotion, Employee, VehicleFleet, CustomUser
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import ProgrammingError, OperationalError
from django.contrib.auth import get_user_model

# Configuration for admin panel
admin.site.site_header = "Bakery Admin Panel"  # Change the top header
admin.site.site_title = "Bakery Management"    # Change the title in the browser tab
admin.site.index_title = "Welcome to Bakery Admin"  # Change the title on the main page

# ===============================
# Admin Classes
# ===============================

class CategoryAdmin(admin.ModelAdmin):
    
    fields = ('name', 'description')
    search_fields = ['name']
    list_filter = ['name']
    list_display = ('category_id', 'name', 'description')  
    ordering = ('name',)


class PromotionAdmin(admin.ModelAdmin):
    list_filter = ['discount', 'products'] 
    fieldsets =(
        ("Information about the discount", 
         {
             'fields' : ('discount', 'products')
         }),
         ("Information about the date", {
             'fields':('start_date', 'end_date')
         }),
    )
    search_fields = ['promotion_id', 'discount', 'products__name']  
    list_per_page = 5  
    

class ProductAdmin(admin.ModelAdmin):
    exclude = ('updated_at',)  
    fields = ['category', 'name', 'price', 'stock', 'description',]

    list_filter = ['category', 'name', 'price', 'stock']  
    search_fields = ['name', 'category__name',]  
    list_per_page = 10  
    ordering = ('name',) 
    list_display = ('product_id', 'name', 'category', 'price', 'stock', 'updated_at')  


class VehicleFleetAdmin(admin.ModelAdmin):  
    search_fields = ('brand',)
    list_filter = ('bakery',)
    list_display = ('vehicle_id', 'brand', 'bakery', 'manufacture_year')
    ordering = ('brand',)


class EmployeeAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_filter = ('bakery',)
    list_display = ('employee_id', 'name', 'bakery', 'age')
    ordering = ('name','age')
    list_per_page = 10  


class BakeryAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_filter = ('location',)
    list_display = ('bakery_id', 'name', 'location')
    ordering = ('name',)


class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'first_name', 'last_name', 'sex', 'birth_date', 
        'phone_number', 'country', 'state', 'city', 'address', 'email','cod','blocat',      
    )

    # Fields to filter by in the list view
    list_filter = ('sex', 'country', 'state', 'city', 'groups')  # You can filter by sex, country, state, and city
    
    # Fields to be used for searching users in the admin
    search_fields = ('first_name', 'last_name', 'email', 'phone_number', 'address')  # Include address in search
    
    # Sort order by default
    ordering = ('first_name',)  # Sort users by their first name by default
    
    # Number of users to show per page in the list view
    list_per_page = 10  # Display 10 users per page
    
    # Optionally, you can specify which fields should appear in the form for adding/editing users
    fieldsets = (
        (None, {
            'fields': ('username', 'first_name', 'last_name', 'email', 'password', 'birth_date', 'sex', 'groups', 'blocat', )
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'country', 'state', 'city', 'address'),
        }),
        )
    
    add_fieldsets = (
        (None, {
            'fields': ('username', 'first_name', 'last_name', 'email', 'password', 'birth_date', 'sex', 'groups','blocat', )  # Added 'groups' here
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'country', 'state', 'city', 'address', 'cod', 'email_confirm'),
        }),
    )

    filter_horizontal = ('groups',)

# ===============================
# Logica pentru Grupuri si Permisiuni
# ===============================

try:
    Administratori_produse, created = Group.objects.get_or_create(name='Administratori_produse')
    moderatori_group, created = Group.objects.get_or_create(name='Moderatori')

    product_content_type = ContentType.objects.get_for_model(Product)
    user_content_type = ContentType.objects.get_for_model(CustomUser)

    add_product_right = Permission.objects.get(codename='add_product', content_type=product_content_type)
    change_product_right = Permission.objects.get(codename='change_product', content_type=product_content_type)
    delete_product_right = Permission.objects.get(codename='delete_product', content_type=product_content_type)
    view_product_right = Permission.objects.get(codename='view_product', content_type=product_content_type)

    Administratori_produse.permissions.add(add_product_right) 
    Administratori_produse.permissions.add(change_product_right)
    Administratori_produse.permissions.add(delete_product_right)
    Administratori_produse.permissions.add(view_product_right)

    utilizator = CustomUser.objects.get(username='lab8')
    utilizator.groups.add(Administratori_produse)


    permission_view_user = Permission.objects.get(codename='view_user', content_type=ContentType.objects.get_for_model(CustomUser))
    permission_change_first_name = Permission.objects.get(codename='change_first_name', content_type=ContentType.objects.get_for_model(CustomUser))
    permission_change_last_name = Permission.objects.get(codename='change_last_name', content_type=ContentType.objects.get_for_model(CustomUser))
    permission_change_email = Permission.objects.get(codename='change_email', content_type=ContentType.objects.get_for_model(CustomUser))
    permission_change_blocat = Permission.objects.get(codename='change_blocat', content_type=ContentType.objects.get_for_model(CustomUser))


    moderatori_group.permissions.add(permission_view_user)
    moderatori_group.permissions.add(permission_change_first_name)
    moderatori_group.permissions.add(permission_change_last_name)
    moderatori_group.permissions.add(permission_change_email)
    moderatori_group.permissions.add(permission_change_blocat)
    
    user = CustomUser.objects.get(username='Moderator_Mihnea')  
    user.groups.add(moderatori_group)
   

except (ProgrammingError, OperationalError, ObjectDoesNotExist) as e:
    print(f"Warning: Unable to configure permissions/groups - {e}")


# ===============================
# Inregistrarea claselor admin
# ===============================

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Bakery, BakeryAdmin)
admin.site.register(Promotion, PromotionAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(VehicleFleet, VehicleFleetAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
