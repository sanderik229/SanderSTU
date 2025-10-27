from rest_framework import viewsets, permissions
from .models import Review
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        blogger_id = self.request.query_params.get("blogger")
        if blogger_id:
            qs = qs.filter(blogger_id=blogger_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


