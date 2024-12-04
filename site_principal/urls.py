from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name="home"),
    path('sobre-nos/', views.sobrenos, name='sobre-nos'),
    path('cadastro/', views.cadastro_view, name="cadastro"),
    path('login/', views.login_view, name='login'),
    path('perfil/', views.user_profile_view, name='perfil'),
    path('logout/', views.logout_view, name='logout'),
    path('excluir/<int:partitura_id>/', views.excluir_partitura_logado, name='excluir_partitura_logado'),
    path('Home/', views.home_logado, name="home_logado"),
    path('Sobre_nos/', views.sobre_nos_logado, name='sobre-nos_logado'),
]