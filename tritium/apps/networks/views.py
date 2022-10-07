from rest_framework import viewsets
from .models import Network
from .serializers import NetworkSerializer
from django_filters import rest_framework as filters


class NetworkViewSet(viewsets.ModelViewSet):
    model = Network
    serializer_class = NetworkSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('nickname','id')
    queryset = Network.objects.all()