import schedule
import time
import os
import django
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Proiect_Django_Facultate.settings')  # Replace with your project name
django.setup()

from Brutarie.models import Promotion, CustomUser


# Task 1: Delete all users who do not have a confirmed email in 2 minutes 
def delete_unconfirmed_users():
    expiration_time = timezone.now() - timedelta(minutes=2)  # Expiration time (2 minutes)
    
    # Exclude the superuser
    users_to_delete = CustomUser.objects.filter(email_confirm=False, date_joined__lte=expiration_time)
    users_to_delete = users_to_delete.exclude(is_superuser=True)  # Exclude the superuser

    # delete users who have not confirmed their email
    deleted_count, _ = users_to_delete.delete()
    
    print(f"{deleted_count} utilizatori au fost stersi la {timezone.now()}")



# Task 2: Sending a newsletter (every day, Monday at 12:00)
def send_newsletter():
    time_limit = timezone.now() - timedelta(minutes=60)
    users_to_send = CustomUser.objects.filter(date_joined__lte=time_limit)
    
    successful_sends = 0
    for user in users_to_send:
        try:
            send_mail(
                subject='Newsletter',
                message='Check out our new discount offer!',
                from_email='musatstefan2004@gmail.com',
                recipient_list=[user.email],
                fail_silently=False,
            )
            successful_sends += 1
        except Exception as e:
            print(f"Failed to send email to {user.email}: {e}")

    print(f"Newsletter sent to {successful_sends} customers at {timezone.now()}")



# Task 3: Clearing the cache (every 15 minutes)
def clean_cache():
    from django.core.cache import cache
    cache.clear()
    print(f"Cache-ul a fost curățat la {timezone.now()}")


# Task 4: Deleting expired promotions
def weekly_offer_cleanup():
    # We filter expired offers
    expired_promotions = Promotion.objects.filter(end_date__lt=timezone.now(), is_active=True)

    # We deactivate expired offers
    for promo in expired_promotions:
        promo.is_active = False
        promo.save()
    
    # We notify administrators about expired offers
    admin_emails = CustomUser.objects.filter(is_superuser=True).values_list('email', flat=True)
    if expired_promotions.exists():
        try:
            send_mail(
                subject="Weekly Promotion Cleanup Report",
                message=f"The following promotions have been deactivated:\n" +
                        "\n".join([f"{promo.name} (ended on {promo.end_date})" for promo in expired_promotions]),
                from_email='musatstefan2004@gmail.com',
                recipient_list=list(admin_emails),  # Convert to list, if needed
                fail_silently=False,
            )
            print(f"Notification email sent to admins at {timezone.now()}")
        except Exception as e:
            print(f"Failed to send notification email: {e}")

    print(f"Deactivated {len(expired_promotions)} expired promotions at {timezone.now()}")



schedule.every().monday.at("15:08").do(send_newsletter)
schedule.every(2).minutes.do(delete_unconfirmed_users) # Task scheduled to run every 2 minutes
schedule.every(15).minutes.do(clean_cache)
schedule.every().monday.at("08:00").do(weekly_offer_cleanup)

try:
    while True:
        schedule.run_pending()
        time.sleep(1)  # 1 second pause between task checks
except KeyboardInterrupt:
    print("Scheduler oprit manual.")