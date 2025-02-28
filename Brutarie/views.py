from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
from .forms import ContactForm, ProductForm, ProductFilterForm, CustomUserCreationForm
from .models import  Product, Category, Promotion, Bakery, CustomUser
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login, logout, update_session_auth_hash
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.mail import EmailMessage
import uuid, random, logging
from django.template.loader import render_to_string
from django.conf import settings  
from django.contrib.auth.models import Permission
from django.utils import timezone  
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in

logger = logging.getLogger(__name__)


def success_view(request):
    return HttpResponse("Thank you for your message!")


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')
        else:
            return render(request, 'contact.html', {'form': form})
    else:
        form = ContactForm()
        return render(request, 'contact.html', {'form': form})
    


# Viewing details for a product
def product_detail(request, product_id):
    product = Product.objects.get(pk=product_id)# Retrieve the product or return 404 if it doesn't exist
    return render(request, 'model_detail/product_detail.html', {'product': product}) # Returns a product details page

# Viewing details for a category
def category_detail(request, category_id):
    category = Category.objects.get(pk=category_id)
    return render(request, 'model_detail/category_detail.html', {'category': category})

# View details for a promotion
def promotion_detail(request, promotion_id):
    promotion = Promotion.objects.get(pk=promotion_id)
    return render(request, 'model_detail/promotion_detail.html', {'promotion': promotion})

# Viewing details for a bakery
def bakery_detail(request, bakery_id):
    bakery = Bakery.objects.get(pk=bakery_id)
    return render(request, 'model_detail/bakery_detail.html', {'bakery': bakery})


# Static pages
def home(request):
    return render(request, 'home.html')


# Viewing the category list
def category_list(request):
    categories = Category.objects.all() # Retrieve all categories
    return render(request, 'category_list.html', {'categories': categories})

# Function for bakery list
def bakery_list(request):
    bakeries = Bakery.objects.all()
    return render(request, 'bakery_list.html', {'bakeries': bakeries})

# Promotion list function
def promotion_list(request):
    promotions = Promotion.objects.all()
    return render(request, 'promotion_list.html', {'promotions': promotions})

def product_list(request):
    form = ProductFilterForm(request.POST or None)
    products = Product.objects.all() # we select all possible products
    if request.method == 'POST':

        if form.is_valid():
            name = form.cleaned_data.get('name') if form.is_valid() else None
            category = form.cleaned_data.get('category') if form.is_valid() else None
            min_price = form.cleaned_data.get('min_price') if form.is_valid() else None
            max_price = form.cleaned_data.get('max_price') if form.is_valid() else None
            stock = form.cleaned_data.get('stock') if form.is_valid() else None
            description_contains = form.cleaned_data.get('description_contains') if form.is_valid() else None

            if name:
                products = products.filter(name__icontains=name) #filters products whose names contain the substring in the name variable. Ignores uppercase letters   
            if category:
                products = products.filter(category=category) #Search for products where the category exactly matches the value specified in the category variable
            if min_price:
                products = products.filter(price__gte=min_price) #Filter products that have a price greater than or equal to the value specified in min_price
            if max_price:
                products = products.filter(price__lte=max_price) #Filter products that have a price lower than or equal to the value specified in max_price
            if stock:
                products = products.filter(stock__gte=stock) #Filter products that have a price greater than or equal to the value specified in min_price
            if description_contains:
                products = products.filter(description__icontains=description_contains) #Filters products whose names contain the substring in the name variable. Ignores uppercase letters
    

    paginator = Paginator(products, 10) #we divide the product list into 10 per page 
    page_number = request.GET.get('page')   #Get the current page number from the request URL
    page_obj = paginator.get_page(page_number) #Get the objects for the current page

    context = {
        'form': form,
        'page_obj': page_obj,
    }
    return render(request, 'product_form.html', context)


def error_403_view(request):
    context = {
        'title': "Error 403 - Forbidden",
        'username': request.user.username if request.user.is_authenticated else "Guest",
        'message': "You do not have permission to access this resource.",
    }
    return HttpResponseForbidden(render(request, '403_error.html', context))


def register(request):
    if request.method == 'POST':
        # Define the registration form with the received data
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) #save the user in the database
            user.email_confirm = False  # By default, the email is not confirmed
            user.cod = str(uuid.uuid4())  # Create a unique code for confirmation
            user.save()

            send_confirmation_email(user)

            messages.success(request, "Please confirm your email address to complete registration.")
            return redirect('login')  # Redirect to the login page
        else:
            # If the form is invalid, send it back with errors
            return render(request, 'register.html', {'form' : form})
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form}) #render the registration page with the form


def login_view(request):
    if request.method == 'POST':
        # Define the authentication form with the received data
        form = AuthenticationForm(request, data=request.POST)
        remember_me = request.POST.get('remember_me')  # Check if the "Remember me" checkbox is checked
        if form.is_valid():
            #if the form is valid we authenticate the user
            user = form.get_user()
            if user.blocat:
                messages.error(request, "Your account has been blocked. Contact the administrator for more information.")
                return redirect('login')  # Redirect back to the login page
            
            if not user.email_confirm:
                messages.error(request, "Please confirm your email first.")
                return redirect('login')
            login(request, user)

            if remember_me:
                request.session.set_expiry(86400)  # Expires in 1 day
            else:
                request.session.set_expiry(0)  # Expires when browser is closed

            # Saving user data in session
            request.session['user_data'] = {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
            messages.success(request, "You have been logged in with succes!")
            return redirect('profile')  # Redirect to profile page
    else:
        # Create an empty login form
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


@login_required  # Make sure the user is authenticated
def add_product(request):
    # Check if the user has permission to add products
    if not request.user.has_perm('Brutarie.add_product'):
        # If it doesn't have permission, return a response of type HttpResponseForbidden
        return HttpResponseForbidden(
            render(request, '403_error.html', {
                'title': 'Error adding products',
                'message': 'You are not allowed to add products.',
                'username': request.user.username
            })
        )

    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            # Save the product, including additional fields, using save() in the form
            form.save()
            return redirect('product_list')  # Redirect to the product list
    else:
        form = ProductForm()

    return render(request, 'add_product.html', {'form': form})


@login_required
def logout_view(request):
    try:
        # We are looking for the 'view_offer' permission
        permission = Permission.objects.get(codename='view_offer')
        
        # We check if the user has the permission and remove it
        if request.user.is_authenticated and permission in request.user.user_permissions.all():
            request.user.user_permissions.remove(permission)
            request.user.save()  # Save the changes
    except Permission.DoesNotExist:
            messages.debug(request, "The required permission does not exist.")

    # Log out the user
    logout(request)
    messages.info(request, "You have been logged out successfully.") # Display an information message
    # Redirect to the login page
    return redirect('login')


@login_required
def profile_view(request):
    user_data = request.session.get('user_data', {})  # User session data
    return render(request, 'profile.html', {'user_data': user_data})

@login_required
def change_password(request):
    if request.method == 'POST':
        # Create a form to change the current user's password
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save() # Save the new password
            update_session_auth_hash(request, user)  # Prevent automatic logout
            messages.success(request, "Your password was successfully updated!")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # Create a blank password change form
        form = PasswordChangeForm(request.user)

    return render(request, 'change_password.html', {'form': form})


def send_confirmation_email(user):

    if user.email_confirm:
        print(f"User {user.username} already confirmed their email.")
        return  # Stop sending email if email is already confirmed
    
    confirmation_link = f"http://127.0.0.1:8000/Brutarie/confirm_email/{user.cod}/"

    context = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
        'confirmation_link': confirmation_link,
    }

    email_html = render_to_string('confirmation_email.html', context) #load a template and populate it with the data from the context

    email = EmailMessage(
        subject='Confirm Your Email Address',
        body=email_html,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.content_subtype = "html"
    email.send()
    print(f"Confirmation link: {confirmation_link}")



def confirm_email(request, cod):
    try:
        user = CustomUser.objects.get(cod=cod)
        if user.email_confirm:
            messages.info(request, "Your email is already confirmed.")
        else:
            user.email_confirm = True
            user.save()
            messages.success(request, "Your email has been successfully confirmed!")

        return redirect('login')

    except CustomUser.DoesNotExist:
        messages.error(request, "Invalid confirmation link.")
        return redirect('register')

    
def create_product(request):
    if not request.user.has_perm('app.add_product'):
        return render(request, '403_error.html', {
            'username': request.user.username if request.user.is_authenticated else 'Anonymous',
            'title': 'Error Adding Product',
            'message': 'You do not have permission to add products.'
        }, status=403)

    # Logic for adding a product
    if request.method == "POST":
        # Creating a product
        pass

    return render(request, 'create_product.html')  # Template for the product add form  



def home(request):
    # Get all products
    products = Product.objects.all()
    logger.info("Fetched all products for the homepage.")

    # Check if there are active offers
    active_promotion = Promotion.objects.filter(start_date__lte=timezone.now(), end_date__gte=timezone.now()).first()

    if active_promotion:
        logger.info(f"Active promotion found: {active_promotion}")
    else:
        logger.info("No active promotions found.")

    # Check if the user is authenticated
    if request.user.is_authenticated:
        # If the user is authenticated, we use first_name if it exists
        first_name = request.user.first_name if request.user.first_name else "User"
        logger.info(f"Authenticated user: {request.user.username}")

        context = {
            'message': f'Welcome, {first_name}!',
            'products': products,
            'active_promotion': active_promotion
        }
    else:
        logger.info("Unauthenticated user accessed the homepage.")
        context = {
            'message': 'Welcome!',
            'products': products,
            'active_promotion': active_promotion
        }

    return render(request, 'home.html', context)


# Function to display the banner
@login_required
def banner_view(request):
    # 30% probability to display the banner
    show_banner = random.random() < 0.3 #random.random() generates a number between 0 and 1
    if show_banner:
        messages.info(request, "Special offer banner is displayed! Click to claim.")
    else:
        messages.debug(request, "Banner hidden due to random probability.")
    return render(request, 'banner.html', {'show_banner': show_banner})


# Function for receiving the offer
@login_required
def claim_offer(request):
    try:
       
        permission = Permission.objects.get(codename='view_offer') # Get 'view_offer' permission
       
        request.user.user_permissions.add(permission) # Add the logged in user permission

        messages.success(request, "Offer claimed successfully! You can now access the special offer page.")
        logger.info(f"User {request.user.username} claimed the offer.")  
        return JsonResponse({'success': True}) # Returns a successful JSON response
    
    except Permission.DoesNotExist:  # If the permission does not exist, return error
        messages.error(request, "Unable to claim the offer: required permission not found.")
        logger.error("Permission 'view_offer' not found. Offer claim failed.")
        return JsonResponse({'success': False, 'error': 'Permission not found.'})
    
    except Exception as e: # Return any other error
        messages.warning(request, f"An unexpected error occurred: {str(e)}")
        logger.exception(f"Unexpected error while {request.user.username} tried to claim the offer: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})
    

# Function for displaying the offer page
def offer_view(request):
    # Check if the user has permission to view the offer
    if not request.user.has_perm('Brutarie.view_offer'):
        logger.warning(f"User {request.user.username} attempted to access the offer page without permission.")
        # If it doesn't have permission, return error 403
        return HttpResponseForbidden(render(request, '403_error.html', {
            'title': "Error Displaying Offer",
            'username': request.user.username,
            'message': "You are not authorized to view the special offer."
        }))
    
    # If allowed, display the offer page
    logger.info(f"User {request.user.username} accessed the offer page.")
    return render(request, 'oferta.html', {'message': "Congratulations! You have unlocked the special offer!"})


def csrf_failure(request, reason=""):
    logger.error(f"CSRF failure for user: {request.user.username if request.user.is_authenticated else 'Guest'}. Reason: {reason}")
    return render(request, '403_error.html', {
        'title': 'Error Displaying Offer',
        'username': request.user.username if request.user.is_authenticated else "Guest",
        'message': "You are not authorized to view this offer."
    }, status=403)


@login_required
def offer_page(request):
    # Check if the user has the 'view_offer' permission
    if not request.user.has_perm('Brutarie.view_offer'):
        messages.error(request, "You do not have the required permissions to view the offer.")
        # If it doesn't have permission, display error 403
        return HttpResponseForbidden(render(request, '403_error.html', {
            'title': "Error Displaying Offer",
            'username': request.user.username,
            'message': "You are not authorized to view the special offer."
        }))
    
    # If allowed, display the offer page
    messages.success(request, "Welcome to the special offer page!")
    logger.info(f"User {request.user.username} accessed the special offer page.")
    return render(request, 'oferta.html', {'message': "Congratulations! You have unlocked the special offer!"})

