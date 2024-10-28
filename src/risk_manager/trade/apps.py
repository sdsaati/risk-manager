from django.apps import AppConfig


class TradeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trade'

    def ready(self):
        import trade.signals  # Import the signals so they're registered
