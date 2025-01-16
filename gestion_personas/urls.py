from django.urls import path
from gestion_personas import views
from .views import obtener_subgrupos_roles


urlpatterns = [
    path('listado_base/', views.listado_base, name='listado_base'),
    path('listado_base/consulta/', views.consulta_listado_base, name='consulta_listado_base'),
    path('tablas/', views.lista_tablas, name='lista_tablas'),
    path('tablas/<str:tabla>/', views.campos_tabla, name='campos_tabla'),
    path('guardar_contratista/', views.guardar_contratista, name='guardar_contratista'),
    path('obtener_subgrupos_roles/', views.obtener_subgrupos_roles, name='obtener_subgrupos_roles'),
    path('eliminar/<int:id_persona>/', views.eliminar_contratista, name='eliminar_contratista'),
    path('actualizar/<int:id_persona>/', views.actualizar_contratista, name='actualizar_contratista'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('obtener_subgrupos_roles/', obtener_subgrupos_roles, name='obtener_subgrupos_roles'),
]
