import os
import django
import schedule
import time
from datetime import timedelta
from Brutarie.tasks import delete_unconfirmed_users, send_newsletter, clean_cache, weekly_offer_cleanup

# Configurarea Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Proiect_Django_Facultate.settings')  # Înlocuiește cu numele proiectului tău
django.setup()

def run_scheduler():
    # Programarea taskurilor
    schedule.every(2).minutes.do(delete_unconfirmed_users)
    schedule.every().monday.at("15:08").do(send_newsletter)
    schedule.every(15).minutes.do(clean_cache)
    schedule.every().monday.at("08:00").do(weekly_offer_cleanup)

    # Rularea taskurilor
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    try:
        run_scheduler()
    except KeyboardInterrupt:
        print("Scheduler oprit manual.")
