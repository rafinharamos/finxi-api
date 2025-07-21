from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework import viewsets, status


from core.serializers import DemandaSerializer, DemandaCreateSerializer
from .models import Demandas


class DemandasViewSet(viewsets.ModelViewSet):
    serializer_class = DemandaSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
       if self.request.user.is_superuser:
            return Demandas.objects.all()

       return Demandas.objects.filter(anunciante=self.request.user.id)

    def get_serializer_class(self):
        """Return the appropriate serializer class based on the action"""
        if self.action in ['create', 'update', 'partial_update']:
            return DemandaCreateSerializer
        return DemandaSerializer

    def list(self, request, *args, **kwargs):
        return super(DemandasViewSet, self).list(request, *args, **kwargs)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        demanda = Demandas.objects.create(**serializer.validated_data, anunciante=request.user)

        return Response(DemandaSerializer(demanda).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Override update to ensure anunciante is not changed"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Ensure anunciante remains the same
        serializer.save(anunciante=instance.anunciante)
        
        return Response(DemandaSerializer(instance).data)

    def partial_update(self, request, *args, **kwargs):
        """Handle PATCH requests"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

