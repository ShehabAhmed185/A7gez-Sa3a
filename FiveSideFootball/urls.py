from django.urls import path
from .views import FieldAPI,GetFieldAPI

urlpatterns = [
    path('addField/',FieldAPI.as_view()), # POST
    path('getFields/<int:fieldOwner_id>/', GetFieldAPI.as_view(), name='field-detail'),  # GET

]