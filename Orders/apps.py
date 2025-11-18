from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Orders"

    def ready(self):
        """Import signals when app is ready"""
        import Orders.signals
