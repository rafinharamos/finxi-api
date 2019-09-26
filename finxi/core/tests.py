from django.contrib.auth.models import AnonymousUser, User
import requests
from django.test import RequestFactory, TestCase
from rest_framework.authtoken.models import Token
from .models import Demandas


class SimpleTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        """criando usuário anunciante"""
        self.anunciante = User.objects.create_user(
            username='anuciante', email='anunciante@…', password='anunciante')
        self.token_anunciante = Token.objects.create(user=self.anunciante)

        """criando usuario admin"""
        self.admin = User.objects.create_user(
            username='admin', email='admin@…', password='admin')
        self.token_admin = Token.objects.create(user=self.admin)

        """criando demandas"""
        demanda1 = Demandas.objects.create(descricao="Demanda teste", endereco="endereco teste", contato="contato teste",
                          anunciante=self.anunciante)

        demanda2 = Demandas.objects.create(descricao="Demanda teste 2", endereco="endereco teste 2", contato="contato teste 2",
                          anunciante=self.admin)


    def test_request_home(self):
        response = requests.get('http://0.0.0.0:8000/')
        self.assertEqual(response.status_code, 200)
        assert response.json() == {"demandas": "http://0.0.0.0:8000/demandas/"}

    def test_request_demandas(self):
        response = requests.get('http://0.0.0.0:8000/demandas/')
        self.assertEqual(response.status_code, 401)
        assert response.json() == {"detail": "As credenciais de autenticação não foram fornecidas."}

