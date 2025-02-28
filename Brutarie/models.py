from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from datetime import date
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError



# The "Category" model
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

# "Product" model
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    stock = models.PositiveBigIntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    calories = models.IntegerField(null=True, blank=True)  # Calories
    allergens = models.TextField(null=True, blank=True)    # Allergens
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# The "Bakery" model
class Bakery(models.Model):
    bakery_id = models.AutoField(primary_key=True)
    location = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    opened_at = models.DateField(default=timezone.now)  

    def __str__(self):
        return self.name

# The "Promotion" model
class Promotion(models.Model):
    promotion_id = models.AutoField(primary_key=True)
    products = models.ManyToManyField('Product', related_name='promotions')
    start_date = models.DateField()
    end_date = models.DateField()
    discount = models.DecimalField(max_digits=5, decimal_places=2)

    def clean(self):
        if self.discount <= 0 or self.discount > 100:
            raise ValidationError("The discount must be between 0% and 100%.")
        if self.start_date >= self.end_date:
            raise ValidationError("The start date must be earlier than the end date.")
    
    class Meta:
         permissions = [
            ("view_offer", "Can view special offer"),
        ]
         
    def __str__(self):
        return f"Promotion {self.promotion_id} ({self.start_date} to {self.end_date})"

# The "Employee" model
class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    bakery = models.ForeignKey(Bakery, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.IntegerField(validators=[MinValueValidator(18), MaxValueValidator(70)])  # Age constraint 
    job_title = models.CharField(max_length=100, blank=True, null=True)  # The employee's function or role (e.g. salesperson, merchandise handler, etc.)


    def __str__(self):
        return self.name

# "VehicleFleet" model
class VehicleFleet(models.Model):
    vehicle_id = models.AutoField(primary_key=True)
    bakery = models.ForeignKey(Bakery, on_delete=models.CASCADE)
    brand = models.CharField(max_length=100)
    manufacture_year = models.IntegerField(validators=[MinValueValidator(1900), MaxValueValidator(date.today().year)])
    purchase_date = models.DateField(null=True, blank=True)  


    def __str__(self):
        return f"{self.brand} ({self.manufacture_year})"


class CustomUser(AbstractUser): 
    # Define two possible variables for MALE and FEMALE   
    MALE = 'M'
    FEMALE = 'F'
    
    # a list of tuples indicating gender
    SEX_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    ]
    birth_date = models.DateField(null=True, blank=False)    
    phone_number = models.CharField(max_length=15, blank=False)
    sex = models.CharField(
        max_length=1,  # We only store 'M' or 'F'
        choices=SEX_CHOICES, # We define the options
        default=MALE, # Default value
    )
    country = models.CharField(max_length=100, blank=False)
    state = models.CharField(max_length=100, blank=False)
    city = models.CharField(max_length=100, blank=False)
    address = models.CharField(max_length=100, blank=False)

    cod = models.CharField(max_length=100, unique=True, null=True, blank=True) # Unique code for confirmation
    email_confirm = models.BooleanField(default=False) # Default unconfirmed email
    blocat = models.BooleanField(default=False)

    class Meta:
        permissions = [
            ("view_user", "Can view user"),  # User view permission
            ("change_first_name", "Can change first name"),  # Name change permission
            ("change_last_name", "Can change last name"),  # Permission to change first name
            ("change_email", "Can change email"),  # Permission to change email
            ("change_blocat", "Can block/unblock users")  # Lock/unlock permission
        ]

    def __str__(self):
        return self.username

    

