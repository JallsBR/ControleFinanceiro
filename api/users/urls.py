from users.views.signin import Signin
from users.views.signup import Signup
from users.views.user import GetUser
from users.views.logout import Logout
from users.views.token_refresh import TokenRefreshViewDefaultDB

from django.urls import path

urlpatterns = [
    path('signin', Signin.as_view()),
    path('signup', Signup.as_view()),
    path('token/refresh/', TokenRefreshViewDefaultDB.as_view(), name='token_refresh'),
    path('user', GetUser.as_view(), name='user'),
    path('logout', Logout.as_view(), name='logout'),

    
]