from django.urls import path
from .views import FieldAPI

urlpatterns = [
    path('addField/',FieldAPI.as_view()), # POST
    path('getFields/<int:fieldOwner_id>/', FieldAPI.as_view(), name='field-detail'),  # GET

]