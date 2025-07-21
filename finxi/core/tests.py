from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.urls import reverse
from .models import Demandas
from .serializers import DemandaSerializer, DemandaCreateSerializer, AnuncianteSerializer


class DemandaModelTest(TestCase):
    """Test cases for the Demandas model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_demanda_creation(self):
        """Test creating a new demanda"""
        demanda = Demandas.objects.create(
            descricao="Test demanda",
            endereco="Test address",
            contato="Test contact",
            anunciante=self.user
        )
        
        self.assertEqual(demanda.descricao, "Test demanda")
        self.assertEqual(demanda.endereco, "Test address")
        self.assertEqual(demanda.contato, "Test contact")
        self.assertEqual(demanda.anunciante, self.user)
        self.assertFalse(demanda.finalizado)  # Default should be False
        
    def test_demanda_str_method(self):
        """Test the string representation of demanda"""
        demanda = Demandas.objects.create(
            descricao="Test demanda description",
            endereco="Test address",
            contato="Test contact",
            anunciante=self.user
        )
        
        self.assertEqual(str(demanda), "Test demanda description")
        
    def test_demanda_finalizado_default(self):
        """Test that finalizado defaults to False"""
        demanda = Demandas.objects.create(
            descricao="Test demanda",
            endereco="Test address",
            contato="Test contact",
            anunciante=self.user
        )
        
        self.assertFalse(demanda.finalizado)
        
    def test_demanda_finalizado_can_be_set(self):
        """Test that finalizado can be set to True"""
        demanda = Demandas.objects.create(
            descricao="Test demanda",
            endereco="Test address",
            contato="Test contact",
            anunciante=self.user,
            finalizado=True
        )
        
        self.assertTrue(demanda.finalizado)


class DemandaSerializerTest(TestCase):
    """Test cases for Demanda serializers"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user.first_name = "Test"
        self.user.last_name = "User"
        self.user.save()
        
        self.demanda = Demandas.objects.create(
            descricao="Test demanda",
            endereco="Test address",
            contato="Test contact",
            anunciante=self.user
        )
        
    def test_demanda_create_serializer_valid_data(self):
        """Test DemandaCreateSerializer with valid data"""
        data = {
            'descricao': 'New demanda',
            'endereco': 'New address',
            'contato': 'New contact'
        }
        
        serializer = DemandaCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
    def test_demanda_create_serializer_missing_required_field(self):
        """Test DemandaCreateSerializer with missing required field"""
        data = {
            'descricao': 'New demanda',
            'endereco': 'New address'
            # Missing 'contato'
        }
        
        serializer = DemandaCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('contato', serializer.errors)
        
    def test_demanda_serializer_output(self):
        """Test DemandaSerializer output format"""
        serializer = DemandaSerializer(self.demanda)
        data = serializer.data
        
        self.assertEqual(data['id'], self.demanda.id)
        self.assertEqual(data['descricao'], self.demanda.descricao)
        self.assertEqual(data['endereco'], self.demanda.endereco)
        self.assertEqual(data['contato'], self.demanda.contato)
        self.assertEqual(data['finalizado'], self.demanda.finalizado)
        self.assertIn('anunciante', data)
        
    def test_anunciante_serializer(self):
        """Test AnuncianteSerializer output"""
        serializer = AnuncianteSerializer(self.user)
        data = serializer.data
        
        self.assertEqual(data['id'], self.user.id)
        self.assertEqual(data['get_full_name'], self.user.get_full_name())


class DemandaAPITest(APITestCase):
    """Test cases for Demanda API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create regular user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_superuser=True
        )
        self.admin_token = Token.objects.create(user=self.admin_user)
        
        # Create test demandas
        self.user_demanda = Demandas.objects.create(
            descricao="User demanda",
            endereco="User address",
            contato="User contact",
            anunciante=self.user
        )
        
        self.admin_demanda = Demandas.objects.create(
            descricao="Admin demanda",
            endereco="Admin address",
            contato="Admin contact",
            anunciante=self.admin_user
        )
        
    def test_list_demandas_unauthenticated(self):
        """Test that unauthenticated users cannot access demandas"""
        url = reverse('demandas-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_list_demandas_regular_user(self):
        """Test that regular users only see their own demandas"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('demandas-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.user_demanda.id)
        
    def test_list_demandas_admin_user(self):
        """Test that admin users see all demandas"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        url = reverse('demandas-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
    def test_create_demanda_authenticated(self):
        """Test creating a demanda as authenticated user"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('demandas-list')
        data = {
            'descricao': 'New test demanda',
            'endereco': 'New test address',
            'contato': 'New test contact'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['descricao'], data['descricao'])
        self.assertEqual(response.data['anunciante']['id'], self.user.id)
        
        # Verify demanda was created in database
        demanda = Demandas.objects.get(id=response.data['id'])
        self.assertEqual(demanda.anunciante, self.user)
        
    def test_create_demanda_unauthenticated(self):
        """Test that unauthenticated users cannot create demandas"""
        url = reverse('demandas-list')
        data = {
            'descricao': 'New test demanda',
            'endereco': 'New test address',
            'contato': 'New test contact'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_create_demanda_invalid_data(self):
        """Test creating demanda with invalid data"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('demandas-list')
        data = {
            'descricao': '',  # Empty description should be invalid
            'endereco': 'New test address',
            'contato': 'New test contact'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_retrieve_own_demanda(self):
        """Test retrieving user's own demanda"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('demandas-detail', kwargs={'pk': self.user_demanda.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user_demanda.id)
        
    def test_retrieve_other_user_demanda_as_regular_user(self):
        """Test that regular users cannot retrieve other users' demandas"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('demandas-detail', kwargs={'pk': self.admin_demanda.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_retrieve_any_demanda_as_admin(self):
        """Test that admin users can retrieve any demanda"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        url = reverse('demandas-detail', kwargs={'pk': self.user_demanda.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user_demanda.id)


class DemandaViewSetTest(TestCase):
    """Test cases for DemandasViewSet methods"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_superuser=True
        )
        
        self.user_demanda = Demandas.objects.create(
            descricao="User demanda",
            endereco="User address",
            contato="User contact",
            anunciante=self.user
        )
        
        self.admin_demanda = Demandas.objects.create(
            descricao="Admin demanda",
            endereco="Admin address",
            contato="Admin contact",
            anunciante=self.admin_user
        )
        
    def test_get_queryset_regular_user(self):
        """Test get_queryset for regular user"""
        from .views import DemandasViewSet
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/demandas/')
        request.user = self.user
        
        viewset = DemandasViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.user_demanda)
        
    def test_get_queryset_admin_user(self):
        """Test get_queryset for admin user"""
        from .views import DemandasViewSet
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/demandas/')
        request.user = self.admin_user
        
        viewset = DemandasViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        
        self.assertEqual(queryset.count(), 2)
        self.assertIn(self.user_demanda, queryset)
        self.assertIn(self.admin_demanda, queryset)


class DemandaModelValidationTest(TestCase):
    """Test cases for Demanda model validation and edge cases"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_demanda_max_length_validation(self):
        """Test that model respects max_length constraints"""
        # Test descricao max_length (150 chars)
        long_description = "x" * 151
        demanda = Demandas(
            descricao=long_description,
            endereco="Test address",
            contato="Test contact",
            anunciante=self.user
        )
        
        # This should raise a validation error when full_clean is called
        with self.assertRaises(Exception):
            demanda.full_clean()
            
    def test_demanda_required_fields(self):
        """Test that required fields are enforced"""
        # Test missing anunciante
        demanda = Demandas(
            descricao="Test demanda",
            endereco="Test address",
            contato="Test contact"
        )
        
        with self.assertRaises(Exception):
            demanda.full_clean()
            
    def test_demanda_cascade_delete(self):
        """Test that demandas are deleted when user is deleted"""
        demanda = Demandas.objects.create(
            descricao="Test demanda",
            endereco="Test address",
            contato="Test contact",
            anunciante=self.user
        )
        
        demanda_id = demanda.id
        self.assertTrue(Demandas.objects.filter(id=demanda_id).exists())
        
        # Delete the user
        self.user.delete()
        
        # Demanda should be deleted due to CASCADE
        self.assertFalse(Demandas.objects.filter(id=demanda_id).exists())


class DemandaSerializerEdgeCasesTest(TestCase):
    """Test edge cases for serializers"""
    
    def test_demanda_create_serializer_empty_strings(self):
        """Test serializer with empty strings"""
        data = {
            'descricao': '',
            'endereco': '',
            'contato': ''
        }
        
        serializer = DemandaCreateSerializer(data=data)
        # Empty strings should be invalid for required fields
        self.assertFalse(serializer.is_valid())
        
    def test_demanda_create_serializer_whitespace_only(self):
        """Test serializer with whitespace-only strings"""
        data = {
            'descricao': '   ',
            'endereco': '   ',
            'contato': '   '
        }
        
        serializer = DemandaCreateSerializer(data=data)
        # Whitespace-only strings should be invalid (Django considers them blank)
        self.assertFalse(serializer.is_valid())
        self.assertIn('descricao', serializer.errors)
        self.assertIn('endereco', serializer.errors)
        self.assertIn('contato', serializer.errors)
        
    def test_anunciante_serializer_with_no_name(self):
        """Test AnuncianteSerializer with user having no first/last name"""
        user = User.objects.create_user(
            username='noname',
            email='noname@example.com',
            password='testpass123'
        )
        # first_name and last_name are empty by default
        
        serializer = AnuncianteSerializer(user)
        data = serializer.data
        
        self.assertEqual(data['id'], user.id)
        self.assertEqual(data['get_full_name'], '')  # Should be empty string


class DemandaAPIEdgeCasesTest(APITestCase):
    """Test edge cases for API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        
    def test_create_demanda_with_extra_fields(self):
        """Test creating demanda with extra fields that should be ignored"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('demandas-list')
        data = {
            'descricao': 'Test demanda',
            'endereco': 'Test address',
            'contato': 'Test contact',
            'finalizado': True,  # This should be ignored
            'anunciante': 999,   # This should be ignored
            'extra_field': 'should be ignored'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # finalizado should be False (default), not True from request
        self.assertFalse(response.data['finalizado'])
        # anunciante should be the authenticated user, not 999
        self.assertEqual(response.data['anunciante']['id'], self.user.id)
        
    def test_update_demanda_put(self):
        """Test updating demanda with PUT"""
        demanda = Demandas.objects.create(
            descricao="Original demanda",
            endereco="Original address",
            contato="Original contact",
            anunciante=self.user
        )
        
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('demandas-detail', kwargs={'pk': demanda.pk})
        data = {
            'descricao': 'Updated demanda',
            'endereco': 'Updated address',
            'contato': 'Updated contact'
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['descricao'], 'Updated demanda')
        
    def test_partial_update_demanda_patch(self):
        """Test partially updating demanda with PATCH"""
        demanda = Demandas.objects.create(
            descricao="Original demanda",
            endereco="Original address",
            contato="Original contact",
            anunciante=self.user
        )
        
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('demandas-detail', kwargs={'pk': demanda.pk})
        data = {
            'descricao': 'Partially updated demanda'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['descricao'], 'Partially updated demanda')
        self.assertEqual(response.data['endereco'], 'Original address')  # Should remain unchanged
        
    def test_delete_demanda(self):
        """Test deleting a demanda"""
        demanda = Demandas.objects.create(
            descricao="To be deleted",
            endereco="Test address",
            contato="Test contact",
            anunciante=self.user
        )
        
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('demandas-detail', kwargs={'pk': demanda.pk})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Demandas.objects.filter(id=demanda.id).exists())
        
    def test_invalid_token_authentication(self):
        """Test API access with invalid token"""
        self.client.credentials(HTTP_AUTHORIZATION='Token invalid_token_here')
        url = reverse('demandas-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_malformed_token_authentication(self):
        """Test API access with malformed token header"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)  # Wrong format
        url = reverse('demandas-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

