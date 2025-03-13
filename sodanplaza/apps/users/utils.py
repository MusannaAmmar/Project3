from django.core.mail import send_mail
from django.conf import settings


def send_email(to,otp):
    subject= 'Your OTP code is'
    message= f'Your OTP code is {otp}'
    from_email= settings.DEFAULT_FROM_EMAIL 
    recipient_list= {to}

    try:
        send_mail(subject,message,from_email,recipient_list, fail_silently=False)
    except Exception as e:
        print(f'error sending email: {e}')
        return ValueError('something went wrong!')