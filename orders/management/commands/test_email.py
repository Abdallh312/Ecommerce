from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Test email functionality'

    def add_arguments(self, parser):
        parser.add_argument('--to', type=str, required=True, help='Recipient email address')

    def handle(self, *args, **options):
        recipient_email = options['to']
        
        try:
            send_mail(
                subject='Test Email from Pilot',
                message='This is a test email to verify SMTP configuration is working correctly.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS(f'Test email sent successfully to {recipient_email}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to send email: {str(e)}')
            )
