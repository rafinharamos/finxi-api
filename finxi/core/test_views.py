from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.authtoken.models import Token

from .models import Demandas
from .views import DemandasViewSet
from .serializers import DemandaSerializer, DemandaCreateSerializer


class DemandasModelTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create users
        self.anunciante = User.objects.create_user(
            username='anunciante', email='anunciante@example.com', password='anunciante')
        self.token_anunciante = Token.objects.create(user=self.anunciante)
        
        self.admin = User.objects.create_user(
            username='admin', email='admin@example.com', password='admin', is_superuser=True)
        self.token_admin = Token.objects.create(user=self.admin)
        
        # Create test demands
        self.demanda1 = Demandas.objects.create(
            descricao="Demanda teste 1", 
            endereco="Endereco teste 1", 
            contato="Contato teste 1",
            anunciante=self.anunciante
        )
        
        self.demanda2 = Demandas.objects.create(
            descricao="Demanda teste 2", 
            endereco="Endereco teste 2", 
            contato="Contato teste 2",
            anunciante=self.admin
        )
    
    def test_demanda_creation(self):
        """Test that a demand can be created"""
        self.assertEqual(self.demanda1.descricao, "Demanda teste 1")
        self.assertEqual(self.demanda1.endereco, "Endereco teste 1")
        self.assertEqual(self.demanda1.contato, "Contato teste 1")
        self.assertEqual(self.demanda1.anunciante, self.anunciante)
        self.assertFalse(self.demanda1.finalizado)
    
    def test_demanda_str_representation(self):
        """Test the string representation of a demand"""
        self.assertEqual(str(self.demanda1), "Demanda teste 1")
    
    def test_demanda_finalization(self):
        """Test that a demand can be marked as finished"""
        self.assertFalse(self.demanda1.finalizado)
        self.demanda1.finalizado = True
        self.demanda1.save()
        self.assertTrue(self.demanda1.finalizado)
    
    def test_demanda_filtering_by_anunciante(self):
        """Test that demands can be filtered by anunciante"""
        anunciante_demands = Demandas.objects.filter(anunciante=self.anunciante)
        self.assertEqual(anunciante_demands.count(), 1)
        self.assertEqual(anunciante_demands.first(), self.demanda1)
        
        admin_demands = Demandas.objects.filter(anunciante=self.admin)
        self.assertEqual(admin_demands.count(), 1)
        self.assertEqual(admin_demands.first(), self.demanda2)


class DemandasSerializerTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.anunciante = User.objects.create_user(
            username='anunciante', email='anunciante@example.com', password='anunciante')
        
        self.demanda = Demandas.objects.create(
            descricao="Demanda teste", 
            endereco="Endereco teste", 
            contato="Contato teste",
            anunciante=self.anunciante
        )
        
        self.serializer = DemandaSerializer(instance=self.demanda)
    
    def test_serializer_contains_expected_fields(self):
        """Test that the serializer contains the expected fields"""
        data = self.serializer.data
        self.assertIn('id', data)
        self.assertIn('descricao', data)
        self.assertIn('endereco', data)
        self.assertIn('contato', data)
        self.assertIn('anunciante', data)
        self.assertIn('finalizado', data)
    
    def test_serializer_field_content(self):
        """Test that the serializer fields contain the expected values"""
        data = self.serializer.data
        self.assertEqual(data['descricao'], "Demanda teste")
        self.assertEqual(data['endereco'], "Endereco teste")
        self.assertEqual(data['contato'], "Contato teste")
        self.assertEqual(data['anunciante']['id'], self.anunciante.id)
        self.assertFalse(data['finalizado'])


class DemandaCreateSerializerTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.valid_data = {
            'descricao': 'Nova demanda',
            'endereco': 'Novo endereco',
            'contato': 'Novo contato'
        }
        
        self.invalid_data = {
            'descricao': '',  # Empty description should be invalid
            'endereco': 'Novo endereco',
            'contato': 'Novo contato'
        }
        
        self.valid_serializer = DemandaCreateSerializer(data=self.valid_data)
        self.invalid_serializer = DemandaCreateSerializer(data=self.invalid_data)
    
    def test_valid_serializer(self):
        """Test that the serializer validates valid data"""
        self.assertTrue(self.valid_serializer.is_valid())
    
    def test_invalid_serializer(self):
        """Test that the serializer invalidates invalid data"""
        self.assertFalse(self.invalid_serializer.is_valid())
        self.assertIn('descricao', self.invalid_serializer.errors)
    
    def test_serializer_fields(self):
        """Test that the serializer contains the expected fields"""
        self.valid_serializer.is_valid()
        self.assertIn('id', self.valid_serializer.fields)
        self.assertIn('descricao', self.valid_serializer.fields)
        self.assertIn('endereco', self.valid_serializer.fields)
        self.assertIn('contato', self.valid_serializer.fields)


class DemandasViewSetTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create users
        self.anunciante = User.objects.create_user(
            username='anunciante', email='anunciante@example.com', password='anunciante')
        
        self.admin = User.objects.create_user(
            username='admin', email='admin@example.com', password='admin', is_superuser=True)
        
        # Create test demands
        self.demanda1 = Demandas.objects.create(
            descricao="Demanda teste 1", 
            endereco="Endereco teste 1", 
            contato="Contato teste 1",
            anunciante=self.anunciante
        )
        
        self.demanda2 = Demandas.objects.create(
            descricao="Demanda teste 2", 
            endereco="Endereco teste 2", 
            contato="Contato teste 2",
            anunciante=self.admin
        )
        
        # Set up the viewset
        self.viewset = DemandasViewSet()
    
    def test_get_queryset_for_admin(self):
        """Test that admin users can see all demands"""
        # Mock the request
        self.viewset.request = type('obj', (object,), {
            'user': self.admin
        })
        
        queryset = self.viewset.get_queryset()
        self.assertEqual(queryset.count(), 2)
    
    def test_get_queryset_for_anunciante(self):
        """Test that anunciante users can only see their own demands"""
        # Mock the request
        self.viewset.request = type('obj', (object,), {
            'user': self.anunciante
        })
        
        queryset = self.viewset.get_queryset()
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.demanda1)