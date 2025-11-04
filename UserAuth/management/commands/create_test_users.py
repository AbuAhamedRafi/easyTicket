"""
Django management command to create test users for payment integration testing
"""

from django.core.management.base import BaseCommand
from UserAuth.models import User


class Command(BaseCommand):
    help = "Create pre-verified test users for payment integration testing"

    def handle(self, *args, **options):
        self.stdout.write("Creating test users for payment integration...\n")

        # Create admin/organizer user
        admin_email = "admin_payment@test.com"

        if User.objects.filter(email=admin_email).exists():
            self.stdout.write(
                self.style.WARNING(f"Admin user {admin_email} already exists")
            )
            admin_user = User.objects.get(email=admin_email)
        else:
            admin_user = User.objects.create_user(
                email=admin_email,
                password="AdminPass123!",
                first_name="Admin",
                last_name="Payment",
                user_type="organizer",  # This sets is_organizer property
                is_staff=True,
                is_email_verified=True,  # Skip email verification for testing
            )
            self.stdout.write(
                self.style.SUCCESS(f"✓ Created admin user: {admin_email}")
            )

        # Create regular customer user
        customer_email = "customer_payment@test.com"

        if User.objects.filter(email=customer_email).exists():
            self.stdout.write(
                self.style.WARNING(f"Customer user {customer_email} already exists")
            )
            customer_user = User.objects.get(email=customer_email)
        else:
            customer_user = User.objects.create_user(
                email=customer_email,
                password="CustomerPass123!",
                first_name="John",
                last_name="Doe",
                user_type="consumer",
                is_email_verified=True,  # Skip email verification for testing
            )
            self.stdout.write(
                self.style.SUCCESS(f"✓ Created customer user: {customer_email}")
            )

        # Display credentials
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("Test Users Created Successfully!"))
        self.stdout.write("=" * 60)
        self.stdout.write("\nAdmin/Organizer Account:")
        self.stdout.write(f"  Email: {admin_email}")
        self.stdout.write(f"  Password: AdminPass123!")
        self.stdout.write(f"  User Type: organizer")
        self.stdout.write(f"  Staff: Yes")

        self.stdout.write("\nCustomer Account:")
        self.stdout.write(f"  Email: {customer_email}")
        self.stdout.write(f"  Password: CustomerPass123!")
        self.stdout.write(f"  User Type: consumer")

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("Ready for payment integration testing!"))
        self.stdout.write("=" * 60 + "\n")
