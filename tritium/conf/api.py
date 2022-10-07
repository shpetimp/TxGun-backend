from tritium.apps.subscriptions.views import SubscriptionViewSet, TransactionViewSet
from tritium.apps.users.views import UserViewSet, APICreditViewSet, APIKeyViewSet
from rest_framework.routers import DefaultRouter
from tritium.apps.networks.views import NetworkViewSet

router = DefaultRouter()
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'users', UserViewSet, basename='user')
router.register(r'api_credits', APICreditViewSet, basename='api_credit')
router.register(r'api_keys', APIKeyViewSet, basename='api_key')
router.register(r'networks', NetworkViewSet, basename='network')

urlpatterns = router.urls