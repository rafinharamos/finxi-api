"""
Simple test script for the Demandas model.
This script doesn't use Django's test framework, but directly tests the model functionality.
"""

import os
import sys
import django

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finxi.settings')
django.setup()

# Now we can import Django models
from django.contrib.auth.models import User
from core.models import Demandas
from core.views import DemandasViewSet
from core.serializers import DemandaSerializer, DemandaCreateSerializer

def test_demanda_creation():
    """Test creating a demand"""
    # Create a test user
    user = User.objects.create_user(
        username='testuser', 
        email='test@example.com', 
        password='testpassword'
    )
    
    # Create a test demand
    demanda = Demandas.objects.create(
        descricao="Test Demand",
        endereco="Test Address",
        contato="Test Contact",
        anunciante=user
    )
    
    # Check that the demand was created correctly
    assert demanda.descricao == "Test Demand"
    assert demanda.endereco == "Test Address"
    assert demanda.contato == "Test Contact"
    assert demanda.anunciante == user
    assert demanda.finalizado == False
    
    print("✅ test_demanda_creation passed")
    
    # Clean up
    demanda.delete()
    user.delete()

def test_demanda_finalization():
    """Test marking a demand as finalized"""
    # Create a test user
    user = User.objects.create_user(
        username='testuser2', 
        email='test2@example.com', 
        password='testpassword2'
    )
    
    # Create a test demand
    demanda = Demandas.objects.create(
        descricao="Test Demand 2",
        endereco="Test Address 2",
        contato="Test Contact 2",
        anunciante=user
    )
    
    # Check that the demand is not finalized by default
    assert demanda.finalizado == False
    
    # Mark the demand as finalized
    demanda.finalizado = True
    demanda.save()
    
    # Refresh from database
    demanda.refresh_from_db()
    
    # Check that it's now finalized
    assert demanda.finalizado == True
    
    print("✅ test_demanda_finalization passed")
    
    # Clean up
    demanda.delete()
    user.delete()

def test_demanda_filtering():
    """Test filtering demands by anunciante"""
    # Create test users
    user1 = User.objects.create_user(
        username='testuser3', 
        email='test3@example.com', 
        password='testpassword3'
    )
    
    user2 = User.objects.create_user(
        username='testuser4', 
        email='test4@example.com', 
        password='testpassword4'
    )
    
    # Create test demands
    demanda1 = Demandas.objects.create(
        descricao="Test Demand 3",
        endereco="Test Address 3",
        contato="Test Contact 3",
        anunciante=user1
    )
    
    demanda2 = Demandas.objects.create(
        descricao="Test Demand 4",
        endereco="Test Address 4",
        contato="Test Contact 4",
        anunciante=user2
    )
    
    # Filter demands by anunciante
    user1_demands = Demandas.objects.filter(anunciante=user1)
    user2_demands = Demandas.objects.filter(anunciante=user2)
    
    # Check that the filtering works correctly
    assert user1_demands.count() == 1
    assert user2_demands.count() == 1
    assert user1_demands.first() == demanda1
    assert user2_demands.first() == demanda2
    
    print("✅ test_demanda_filtering passed")
    
    # Clean up
    demanda1.delete()
    demanda2.delete()
    user1.delete()
    user2.delete()

def test_viewset_queryset_filtering():
    """Test that the viewset filters queryset based on user"""
    # Create test users
    user1 = User.objects.create_user(
        username='testuser5', 
        email='test5@example.com', 
        password='testpassword5'
    )
    
    user2 = User.objects.create_user(
        username='testuser6', 
        email='test6@example.com', 
        password='testpassword6',
        is_superuser=True
    )
    
    # Create test demands
    demanda1 = Demandas.objects.create(
        descricao="Test Demand 5",
        endereco="Test Address 5",
        contato="Test Contact 5",
        anunciante=user1
    )
    
    demanda2 = Demandas.objects.create(
        descricao="Test Demand 6",
        endereco="Test Address 6",
        contato="Test Contact 6",
        anunciante=user2
    )
    
    # Create viewset instance
    viewset = DemandasViewSet()
    
    # Test regular user (should only see their own demands)
    class MockRequest:
        def __init__(self, user):
            self.user = user
    
    viewset.request = MockRequest(user1)
    queryset = viewset.get_queryset()
    
    assert queryset.count() == 1
    assert queryset.first() == demanda1
    
    # Test superuser (should see all demands)
    viewset.request = MockRequest(user2)
    queryset = viewset.get_queryset()
    
    assert queryset.count() == 2
    
    print("✅ test_viewset_queryset_filtering passed")
    
    # Clean up
    demanda1.delete()
    demanda2.delete()
    user1.delete()
    user2.delete()

def test_serializer():
    """Test the DemandaSerializer"""
    # Create a test user
    user = User.objects.create_user(
        username='testuser7', 
        email='test7@example.com', 
        password='testpassword7'
    )
    
    # Create a test demand
    demanda = Demandas.objects.create(
        descricao="Test Demand 7",
        endereco="Test Address 7",
        contato="Test Contact 7",
        anunciante=user
    )
    
    # Serialize the demand
    serializer = DemandaSerializer(demanda)
    data = serializer.data
    
    # Check that the serialized data is correct
    assert data['id'] == demanda.id
    assert data['descricao'] == "Test Demand 7"
    assert data['endereco'] == "Test Address 7"
    assert data['contato'] == "Test Contact 7"
    assert data['anunciante']['id'] == user.id
    assert data['finalizado'] == False
    
    print("✅ test_serializer passed")
    
    # Clean up
    demanda.delete()
    user.delete()

def test_create_serializer():
    """Test the DemandaCreateSerializer"""
    # Create valid data
    valid_data = {
        'descricao': 'New Demand',
        'endereco': 'New Address',
        'contato': 'New Contact'
    }
    
    # Create a serializer with the data
    serializer = DemandaCreateSerializer(data=valid_data)
    
    # Check that the data is valid
    assert serializer.is_valid()
    
    # Create invalid data (missing required field)
    invalid_data = {
        'endereco': 'New Address',
        'contato': 'New Contact'
    }
    
    # Create a serializer with the invalid data
    serializer = DemandaCreateSerializer(data=invalid_data)
    
    # Check that the data is invalid
    assert not serializer.is_valid()
    assert 'descricao' in serializer.errors
    
    print("✅ test_create_serializer passed")

if __name__ == "__main__":
    # Run the tests
    print("Running tests...")
    test_demanda_creation()
    test_demanda_finalization()
    test_demanda_filtering()
    test_viewset_queryset_filtering()
    test_serializer()
    test_create_serializer()
    print("All tests passed! ✅")