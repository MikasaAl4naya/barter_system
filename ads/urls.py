from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from rest_framework import permissions
from rest_framework.schemas import get_schema_view
from drf_yasg.views import get_schema_view as yasg_get_schema_view
from drf_yasg import openapi
router = DefaultRouter()
router.register(r'ads', AdViewSet)
router.register(r'proposals', ExchangeProposalViewSet)

schema_view = yasg_get_schema_view(
    openapi.Info(
        title="Barter System API",
        default_version='v1',
        description="Документация API для системы обмена товарами",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@barter.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [

    path('docs/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('create-ad/', create_ad, name='create_ad'),
    path('update-ad/<int:pk>/', update_ad, name='update_ad'),
    path('delete-ad/<int:pk>/', delete_ad, name='delete_ad'),
    path('', ad_list, name='ad_list'),
    path('ad/<int:pk>/', ad_detail, name='ad_detail'),
    path('create-exchange-proposal/', create_exchange_proposal, name='create_exchange_proposal'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('proposals/', proposals_list, name='proposals_list'),
    path('proposals/<int:pk>/update/', update_proposal, name='update_proposal'),
    path('api/', include(router.urls)),
]