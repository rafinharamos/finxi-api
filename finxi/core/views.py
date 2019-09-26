from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework import viewsets


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

    def list(self, request, *args, **kwargs):
        return super(DemandasViewSet, self).list(request, *args, **kwargs)

    def create(self, request):
        serializer = DemandaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        demanda = Demandas.objects.create(**serializer.data, anunciante=request.user)

        return Response(DemandaSerializer(demanda).data)

