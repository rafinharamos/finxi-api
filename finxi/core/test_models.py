import unittest
from django.contrib.auth.models import User
from .models import Demandas


class TestDemandas(unittest.TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='testpassword'
        )
        
        # Create a test demand
        self.demanda = Demandas.objects.create(
            descricao="Test Demand",
            endereco="Test Address",
            contato="Test Contact",
            anunciante=self.user
        )
    
    def test_demanda_creation(self):
        """Test that a demand is created with the correct attributes"""
        self.assertEqual(self.demanda.descricao, "Test Demand")
        self.assertEqual(self.demanda.endereco, "Test Address")
        self.assertEqual(self.demanda.contato, "Test Contact")
        self.assertEqual(self.demanda.anunciante, self.user)
        self.assertFalse(self.demanda.finalizado)
    
    def test_demanda_string_representation(self):
        """Test the string representation of a demand"""
        self.assertEqual(str(self.demanda), "Test Demand")
    
    def test_demanda_finalization(self):
        """Test that a demand can be marked as finalized"""
        self.assertFalse(self.demanda.finalizado)
        
        # Mark the demand as finalized
        self.demanda.finalizado = True
        self.demanda.save()
        
        # Refresh from database
        self.demanda.refresh_from_db()
        
        # Check that it's now finalized
        self.assertTrue(self.demanda.finalizado)
    
    def tearDown(self):
        # Clean up after each test
        self.demanda.delete()
        self.user.delete()


if __name__ == '__main__':
    unittest.main()