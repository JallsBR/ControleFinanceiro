from rest_framework.exceptions import AuthenticationFailed, APIException
from django.contrib.auth.hashers import check_password

from .models import User

class Authentication:
    def signin(self, email=None, password=None):
        exception_auth = AuthenticationFailed('Credenciais incorretas')

        user_exists = User.objects.filter(email=email).exists()

        if not user_exists:
            raise exception_auth
        
        user = User.objects.filter(email=email).first()

        if not check_password(password, user.password):
            raise exception_auth
        
        return user
    
    def signup(self, username, email, password ):
        if not username or username == '':
            raise APIException('O nome de usuário não deve ser null')
        
        if not email or email == '':
            raise APIException('O email não deve ser null')
        
        if not password or password == '':
            raise APIException('O password não deve ser null') 
        
        user = User
        if user.objects.filter(email=email).exists():
            raise APIException('Este email já existe na plataforma')
        
        if user.objects.filter(username=username).exists():
            raise APIException('Este usuário já existe na plataforma')

        created_user = User.objects.create_user(
            username=username,
            email=email,
            password=password)


        return created_user
    
