from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from tritium.apps.subscriptions.models import Subscription, SubscribedTransaction
from datetime import datetime, timedelta
from django.db.models import Sum
from .serializers import (
    APICreditSerializer,
    APIKeySerializer,
    UserSerializer
)
from tritium.apps.subscriptions.serializers import SubscribedTransactionSerializer
from .models import CustomUser as User, APICredit, APIKey
from rest_framework import viewsets
from .permissions import IsOwner
from django.utils import timezone


# Create your views here.


class Dashboard(APIView):
    def get(self, request, format=None):
        if not self.request.user.is_authenticated:
            return Response({'error': 'You are not logged in'}, status=401)

        my_subscriptions = Subscription.objects.filter(
            user=self.request.user).exclude(archived_at__lte=timezone.now())

        my_transactions = SubscribedTransaction.objects.filter(
            subscription__user=self.request.user)

        yesterday = timezone.now() - timedelta(days=1)

        my_transactions_today = my_transactions.filter(
            created_at__gte=yesterday)

        total_ether = my_transactions_today.aggregate(Sum('value'))[
            'value__sum']

        total_tokens = my_transactions_today.aggregate(Sum('token_amount'))[
            'token_amount__sum']

        return Response({
            'active_subscriptions': my_subscriptions.count(),
            'transactions_today': my_transactions_today.count(),
            'total_ether': total_ether or 0,
            'total_tokens': total_tokens or 0,
            'transactions': SubscribedTransactionSerializer(my_transactions[:10], many=True).data
        })


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    model = User
    permission_classes = (IsOwner,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class MyAPICredits(APIView):
    def get(self, request, format=None):
        if not self.request.user.is_authenticated:
            return Response({'error': 'You are not logged in'}, status=401)

        total_credits = APICredit.objects.filter(user=self.request.user).aggregate(Sum('amount'))

        return Response({
            'api_credit_balance': total_credits or 0
        })

class APICreditViewSet(viewsets.ReadOnlyModelViewSet):
    model = APICredit
    serializer_class = APICreditSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return APICredit.objects.none()
        return APICredit.objects.filter(user=self.request.user)


class APIKeyViewSet(viewsets.ModelViewSet):
    model = APIKey
    serializer_class = APIKeySerializer

    def get(self, request, format=None):
        if not self.request.user.is_authenticated:
            return Response({'error': 'You are not logged in'}, status=401)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return APIKey.objects.none()
        return APIKey.objects.filter(user=self.request.user)
    

