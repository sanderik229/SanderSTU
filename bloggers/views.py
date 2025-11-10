from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Blogger, AdOffer
from .serializers import BloggerSerializer, AdOfferSerializer


class BloggerViewSet(viewsets.ModelViewSet):
    queryset = Blogger.objects.all()
    serializer_class = BloggerSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "topic", "social_network"]
    ordering_fields = ["audience_size", "name"]


class AdOfferViewSet(viewsets.ModelViewSet):
    queryset = AdOffer.objects.all()
    serializer_class = AdOfferSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "blogger__name", "blogger__topic", "blogger__social_network"]
    ordering_fields = ["price"]
    
    def list(self, request, *args, **kwargs):
        """Переопределяем list для включения услуг менеджера (AdService)"""
        # Получаем обычные предложения
        response = super().list(request, *args, **kwargs)
        offers_data = response.data['results'] if 'results' in response.data else response.data
        
        # Добавляем услуги менеджеров
        try:
            from managers.models import AdService
            services = AdService.objects.filter(is_active=True)
            
            for service in services:
                offer_data = {
                    'id': f"service_{service.id}",
                    'blogger': {
                        'id': service.blogger.id,
                        'name': service.blogger.name,
                        'social_network': service.social_network,
                        'topic': service.blogger.topic,
                        'audience_size': service.blogger.audience_size
                    },
                    'title': service.name,
                    'description': service.description,
                    'price': float(service.price),
                    'is_active': service.is_active,
                    'service_id': service.id  # Добавляем ID сервиса для идентификации
                }
                offers_data.append(offer_data)
            
            # Если это paginated response, обновляем results
            if 'results' in response.data:
                response.data['results'] = offers_data
                response.data['count'] = len(offers_data)
            else:
                response.data = offers_data
                
        except Exception as e:
            print(f"Error adding AdService to offers: {e}")
            import traceback
            traceback.print_exc()
        
        return response


