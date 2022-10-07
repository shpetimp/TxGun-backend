from rest_framework.authentication import TokenAuthentication
from .models import APIKey
 
class APIKeyAuthentication(TokenAuthentication):
    
    model = APIKey
