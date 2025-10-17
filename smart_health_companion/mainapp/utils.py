import random
from django.core.mail import send_mail
from .models import PasswordResetOTP
from django.conf import settings

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(user):
    otp = generate_otp()
    PasswordResetOTP.objects.create(user=user, otp=otp)
    subject = "Your OTP for Smart Health Companion Password Reset"
    message = (
        f"Hello {user.username},\n\n"
        f"You requested to reset your Smart Health Companion password.\n\n"
        f"Your OTP is: {otp}\n"
        f"It will expire in 5 minutes.\n\n"
        f"If you did not request this, ignore this email.\n\n"
        f"Best regards,\n"
        f"The Smart Health Companion Team"
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
