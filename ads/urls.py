from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from django.contrib.auth.views import LogoutView
router = DefaultRouter()
router.register(r'ads', AdViewSet)
router.register(r'proposals', ExchangeProposalViewSet)

urlpatterns = [

    # Для веб-страниц
    path('create-ad/', create_ad, name='create_ad'),
    path('update-ad/<int:pk>/', update_ad, name='update_ad'),
    path('delete-ad/<int:pk>/', delete_ad, name='delete_ad'),
    path('ad_list/', ad_list, name='ad_list'),
    path('ad/<int:pk>/', ad_detail, name='ad_detail'),
    path('create-exchange-proposal/', create_exchange_proposal, name='create_exchange_proposal'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='ad_list'), name='logout'),
    path('proposals/', proposals_list, name='proposals_list'),
    path('proposals/<int:pk>/update/', update_proposal, name='update_proposal'),
    path('api/', include(router.urls)),
]