from django.urls import path
from .views import formulario
from .views import carregarbanco
from .views import visualizar_partitura
from . import views


urlpatterns = [
    path('formulario/', formulario, name='formulario'),
    path('inicio/', carregarbanco, name='carregarbanco'),
    path('excluir/<int:partitura_id>/', views.excluir_partitura, name='excluir_partitura'),
    path('partitura/<int:id>/', visualizar_partitura, name='visualizar_partitura'),
    path('processar_partitura/', views.processar_partitura, name='processar_partitura'),
    path('selecionar_notas/', views.selecionar_notas, name='selecionar_notas'),
    path('processando/', views.loading_page, name='loading_page'),
    path('loading/', views.loading, name='loading'),
    path('processar_rois/', views.processar_rois, name='processar_rois'),
    #path('visualizar_rois/', views.visualizar_rois, name='visualizar_rois'),
    path('visualizar_imagem_rois/', views.visualizar_imagem_rois, name='visualizar_imagem_rois'),
    path('partitura_final/', views.partitura_final, name='partitura_final'),
    path('Início/', views.carregarbanco_logado, name='carregarbanco_logado'),
    path('visualizando_partitura/<int:partitura_id>/', views.visualizar_partitura_logado, name='visualizar_partitura_logado'),
    path('processando_partitura/', views.processar_partitura_logado, name='processar_partitura_logado'),
    path('selecionando_notas/', views.selecionar_notas_logado, name='selecionar_notas_logado'),
    path('carregando_partitura/', views.loading_logado, name='loading_logado'),
    path('partitura_finalizada/', views.partitura_final_logado, name='partitura_final_logado'),
] 