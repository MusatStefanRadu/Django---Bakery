from django import forms
from .models import Product, Category, CustomUser
from decimal import Decimal
from django.core.exceptions import ValidationError
from datetime import datetime, date 
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import re
import os
import json
import uuid



def validate_text(value):
    if not re.match(r'^[A-Za-z\s]+$', value):  
        raise ValidationError(f'{value} must contain only letters and spaces and the first letter should be a capital one.')
    first_word = value.split()[0]  # Extract the first word
    if not first_word[0].isupper():
        raise ValidationError(f'The first word in "{value}" must start with a capital letter.')


class ContactForm(forms.Form):

    first_name = forms.CharField(max_length=50, required=False, validators=[validate_text])
    last_name = forms.CharField(max_length=50, required=True, validators=[validate_text])
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), #widget for date selection
        label="Birthdate",required=True)
    email = forms.EmailField(required=True)
    confirm_email = forms.EmailField(required=True)
    message_type = forms.ChoiceField(choices=[
        ('complaint', 'Complaint'),
        ('question', 'Question'),
        ('review', 'Review'),
        ('request', 'Request'),
        ('appointment', 'Appointment')
    ], required=True)
    subject = forms.CharField(max_length=200, required=True, validators=[validate_text])
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}), required=True)

    # Specific validation for the "message" field
    def clean_message(self):
        message = self.cleaned_data.get('message')
    # Message preprocessing: remove newlines and merge consecutive spaces
        message = re.sub(r'\s+', ' ', message.replace('\n', ' ')).strip()
        return message

    # Cleanup function for general validations
    def clean(self):

        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        confirm_email = cleaned_data.get('confirm_email')

        # We validate that the email addresses match
        if email and confirm_email and email != confirm_email:
            raise ValidationError("The emails must match.")
        
        # We validate that the user is at least 18 years old
        birth_date = cleaned_data.get('birth_date')
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 18:
                raise ValidationError("You must be at least 18 years old to submit the form.")
        
        # We validate that the message contains between 5 and 100 words
        message = cleaned_data.get('message')
        word_count = len(re.findall(r'\b\w+\b', message))
        if word_count < 5 or word_count > 100:
            raise ValidationError("Message must contain between 5 and 100 words.")
        
        
        # Validate that the message does not contain links
        if re.search(r'https?://', message):
            raise ValidationError("The message cannot contain links.")
        

        # Check if the message ends with the user's full name (signature)
        full_name = f"{cleaned_data.get('first_name')} {cleaned_data.get('last_name')}"
        if not message.strip().endswith(full_name):
            raise ValidationError("Your message must end with your full name (signature).")

        return cleaned_data # Return the cleaned and validated data
    
    def save(self):

        cleaned_data = self.cleaned_data # Get the cleaned data from the form
        birth_date = cleaned_data.get('birth_date')
        today = date.today()

        # Calculate the user's age in years and months
        birth_year = birth_date.year
        birth_month = birth_date.month
        age_years = today.year - birth_year
        age_months = today.month - birth_month
        if today.day < birth_date.day:  # Adjust the month if the birthday has not yet come
            age_months -= 1 
        # We save the age in the format "X years and Y months"
        age = f"{age_years} years and {age_months} months"

        # Process the message to remove multiple spaces and newlines
        message = cleaned_data.get('message')
        message = re.sub(r'\s+', ' ', message.replace('\n', ' ')).strip()


        # Create the 'messages' directory if it doesn't already exist.
        os.makedirs('messages', exist_ok=True)
        
        # Generate a timestamp for the file name
        timestamp = str(int(datetime.combine(date.today(), datetime.min.time()).timestamp()))  # Convert to datetime and get the timestamp
        
        # Prepare the data for the JSON file
        message_data = {
            'first_name': cleaned_data.get('first_name'),
            'last_name': cleaned_data.get('last_name'),
            'birth_date': age,  # We store age instead of birthdate
            'email': cleaned_data.get('email'),
            'message_type': cleaned_data.get('message_type'),
            'subject': cleaned_data.get('subject'),
            'message': message,
        }
        
        # Save the data in a JSON file with a unique timestamp
        with open(f'messages/message_{timestamp}.json', 'w') as f:
            json.dump(message_data, f, indent=4)  # Save the data in a readable format





class ProductFilterForm(forms.Form):
    name = forms.CharField(max_length=100, required=False, label="Product Name")
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(), # Show all available categories
        required=False,
        label="Category"
    )    
    min_price = forms.DecimalField(required=False, label="Minimum price")
    max_price = forms.DecimalField(required=False, label="Maximum peice")
    stock = forms.IntegerField(required=False, label="Stock (minimum)")
    description = forms.CharField(max_length=200, required=False, label = "Description contains")
    


class ProductForm(forms.ModelForm):
    # Additional fields
    calories = forms.IntegerField(
        required=True,
        label="Number of Calories",
        help_text="Enter the number of calories per 100g.",
        error_messages={
            'required': "Please specify the number of calories.", # Error if field is empty
            'invalid': "Calories must be a valid number.",  # Error if value is not a valid number
            'min_value': "Calories cannot be negative.", # Error if value is negative
        }
    )
    allergens = forms.CharField(
        required=False,
        label="Allergens",
        help_text="List potential allergens, separated by commas.",
        widget=forms.Textarea(attrs={'rows': 3}), # Display the field as a 3-line Textarea
        error_messages={
            'invalid': "Enter a valid list of allergens.", # Error for an invalid list
        }
    )

    class Meta:
        # Defining the model this form is linked to
        model = Product
        # Defining the fields in the model that will appear in the form
        fields = ["name", "category", "price", "stock", "description"]
        labels = {
            'name': "Product Name",
            'category': "Category",
            'price': "Price",
            'stock': "Stock",
            'description': "Description",
        }
        # Field help messages
        help_texts = {
            'name': "Provide a unique name for the product.", # Product name help
            'price': "Enter the price in your local currency.",  # Price help
            'stock': "Specify the quantity available in stock.", # Stock help
        }
        # Custom error messages for model fields
        error_messages = {
            'name': {
                'required': "Please enter the product name.", # Error if name is missing
                'max_length': "The name must not exceed 100 characters.", # Error if name is too long
            },
            'category': {
                'required': "Please select a category for the product.", # Error if category is missing
            },
            'price': {
                'required': "Please enter the price.",  # Error for missing price
                'invalid': "Price must be a valid decimal number.", # Error for invalid price
            },
            'stock': {
                'required': "Please specify the stock quantity.", # Out of stock error
                'invalid': "Stock must be a positive number.", # Error for invalid stock value
            },
        }

    # Individual validation for calories
    def clean_calories(self):
        calories = self.cleaned_data.get('calories')  # Get the field value
        if calories > 1000:
            raise forms.ValidationError("Calories cannot exceed 1000 per 100g.")
        if calories < 0:
            raise forms.ValidationError("Calories cannot be negative.")
        if calories % 5 != 0:
            raise forms.ValidationError("Calories must be a multiple of 5.") # Additional validation
        return calories

    # Individual validation for allergens
    def clean_allergens(self):
        allergens = self.cleaned_data.get('allergens', '')  # Get the field value
        if len(allergens.split(',')) > 5:
            raise forms.ValidationError("You can specify a maximum of 5 allergens.")
        if allergens and any(char.isdigit() for char in allergens):
            raise forms.ValidationError("Allergens must not contain numbers.")  # Additional validation
        return allergens.strip()
    
    # Individual validation for product name
    def clean_name(self):
        name = self.cleaned_data.get('name')  # Get the value of the 'name' field
        if Product.objects.filter(name=name).exists():  # Check if a product with the same name already exists
            raise forms.ValidationError("A product with this name already exists.")  # Error if name already exists
        if len(name) < 3:
            raise forms.ValidationError("Product name must have at least 3 characters.")  # Additional validation
        if not name.isalpha():
            raise forms.ValidationError("Product name must only contain letters.")  # Additional validation
        return name
    
    # Individual price validation
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        if price == 0:
            raise forms.ValidationError("Price cannot be zero.")
        if price > 1000:
            raise forms.ValidationError("Price cannot exceed 10,00.")  
        return price
    
    # Individual validation for stock
    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock < 0:
            raise forms.ValidationError("Stock quantity cannot be negative.")
        if stock > 1000:
            raise forms.ValidationError("Stock quantity cannot exceed 1000.")  # Additional validation
        return stock
    
    # Form-level validation
    def clean(self):
        cleaned_data = super().clean()
        calories = cleaned_data.get('calories')
        allergens = cleaned_data.get('allergens', '')

        if calories and "nuts" in allergens.lower() and calories > 500:
            raise forms.ValidationError(
                "High-calorie products (>500 kcal) should not include 'nuts' as an allergen."
            )

        return cleaned_data

    def save(self, commit=True):
        product = super().save(commit=False)  # Create the model instance without saving it to the database immediately

        product.calories = self.cleaned_data.get('calories')
        product.allergens = self.cleaned_data.get('allergens')
        product.description = self.cleaned_data.get('description')

        if commit:
            product.save() # save the product if commit is true
        return product




class CustomUserCreationForm(UserCreationForm):
    # Additional fields defined in the CustomUser model
    birth_date = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    phone_number = forms.CharField(max_length=15, required=False)
    sex = forms.ChoiceField(choices=CustomUser.SEX_CHOICES, required=True)
    country = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=100, required=False)
    city = forms.CharField(max_length=100, required=False)
    address = forms.CharField(max_length=100, required=False)

    class Meta:
        model = CustomUser
        fields = (
            'username', 'first_name', 'last_name', 'email', 
            'password1', 'password2', 'birth_date', 'phone_number', 
            'sex', 'country', 'state', 'city', 'address'
        )

    # Phone number validation
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number:
            raise ValidationError("This field cannot be left blank.")
        if not re.match(r'^\+?[0-9]{10,15}$', phone_number):
            raise ValidationError("Invalid phone number format.")
        return phone_number

    # Username validation
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9._]+$', username):
            raise ValidationError("The username can only contain letters, numbers, underscores (_), and dots (.)")
        return username

    # Validation for first_name
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[a-zA-Z\s-]+$', first_name):
            raise ValidationError("The first name can only contain letters.")
        return first_name

    # Validation for last_name
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not re.match(r'^[a-zA-Z]+$', last_name):
            raise ValidationError("The last name can only contain letters.")
        return last_name

    # Validation for address
    def clean_address(self):
        address = self.cleaned_data.get('address')
        if not address:
            raise ValidationError("This field cannot be left blank.")
        if len(address) < 5:
            raise ValidationError("The address must be at least 5 characters long.")
        return address

    # Validation for country
    def clean_country(self):
        country = self.cleaned_data.get('country')
        if not country:
            raise ValidationError("This field cannot be left blank.")
        return country
    
    # Validation for states
    def clean_state(self):
        state = self.cleaned_data.get('state')
        if not state:
            raise ValidationError("This field cannot be left blank.")
        return state

    # Validation for city
    def clean_city(self):
        city = self.cleaned_data.get('city')
        if not city:
            raise ValidationError("This field cannot be left blank.")
        return city

    # Email validation
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("This field cannot be left blank.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)

        user.cod = str(uuid.uuid4())  # Unique code generated with UUID
        user.email_confirmat = False  # Initially, the email is not confirmed

        if commit:
            user.save()  # Save the user in the database
            #self.send_confirmation_email(user) # Sending confirmation email
        return user

