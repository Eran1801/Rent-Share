import os
import django
from django.utils import timezone
from Users.models import PasswordResetCode


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TelAviv.settings")
django.setup()


def delete_old_verification_codes():
    # Calculate the cutoff time
    cutoff_time = timezone.now() - timezone.timedelta(minutes=5)

    # Query to find records older than 5 minutes
    old_records = PasswordResetCode.objects.filter(created_at__lt=cutoff_time)

    # Count old records before deleting, for logging
    records_deleted = old_records.count()

    # Delete the records
    old_records.delete()

    print(f"Deleted {records_deleted} old verification code(s).")

if __name__ == "__main__":
    delete_old_verification_codes()
