from django.urls import path
from gestion_personas import views

urlpatterns = [
    path('listado_base/', views.listado_base, name='listado_base'),
    path('listado_base/consulta/', views.consulta_listado_base, name='consulta_listado_base'),
    path('tablas/', views.lista_tablas, name='lista_tablas'),
    path('tablas/<str:tabla>/', views.campos_tabla, name='campos_tabla'),
    path('guardar_contratista/', views.guardar_contratista, name='guardar_contratista'),
    path('obtener_subgrupos_roles/', views.obtener_subgrupos_roles, name='obtener_subgrupos_roles'),
    path('eliminar_contratista/<int:id_persona>/', views.eliminar_contratista, name='eliminar_contratista'),
    path('agregar_contratista/', views.agregar_contratista, name='agregar_contratista'),  # Agregamos esta línea
]
