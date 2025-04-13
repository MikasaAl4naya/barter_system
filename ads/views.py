from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponseForbidden
from .forms import AdForm, ExchangeProposalForm, LoginForm, SignUpForm
from .models import Ad, ExchangeProposal
from .serializers import AdSerializer, ExchangeProposalSerializer
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
# Представление для работы с объявлениями
class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Устанавливаем пользователя, создающего объявление
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        # Проверяем, что только автор может редактировать объявление
        ad = self.get_object()
        if ad.user != request.user:
            return Response({"detail": "You can only edit your own ads."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # Проверяем, что только автор может удалить объявление
        ad = self.get_object()
        if ad.user != request.user:
            return Response({"detail": "You can only delete your own ads."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

# Представление для работы с предложениями обмена
class ExchangeProposalViewSet(viewsets.ModelViewSet):
    queryset = ExchangeProposal.objects.all()
    serializer_class = ExchangeProposalSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Устанавливаем отправителя предложения
        ad_sender = serializer.validated_data['ad_sender']
        serializer.save()

    def update(self, request, *args, **kwargs):
        # Только администратор или инициатор предложения может изменять статус
        proposal = self.get_object()
        if proposal.ad_sender != request.user and not request.user.is_staff:
            return Response({"detail": "You do not have permission to update this proposal."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)


# views.py (дополнение для ad_list)
def ad_list(request):
    search_query = request.GET.get('search', '')
    category = request.GET.get('category', '')
    condition = request.GET.get('condition', '')

    ads = Ad.objects.all()

    if search_query:
        ads = ads.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

    if category:
        ads = ads.filter(category=category)

    if condition:
        ads = ads.filter(condition=condition)

    # Пагинация
    paginator = Paginator(ads, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'ads/ad_list.html', {
        'page_obj': page_obj,
        'categories': Ad.objects.values_list('category', flat=True).distinct(),
        'conditions': [choice[0] for choice in Ad._meta.get_field('condition').choices]
    })


@login_required
def update_proposal(request, pk):
    proposal = get_object_or_404(ExchangeProposal, pk=pk)

    if proposal.ad_receiver.user != request.user:
        messages.error(request, "Вы не можете изменять это предложение")
        return redirect('proposals_list')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(ExchangeProposal.STATUS_CHOICES):
            proposal.status = new_status
            proposal.save()
            messages.success(request, "Статус предложения обновлен")

    return redirect('proposals_list')


@login_required
def proposals_list(request):
    # Фильтрация предложений, только те, которые имеют статус "ожидает"
    proposals = ExchangeProposal.objects.filter(
        (Q(ad_sender__user=request.user) | Q(ad_receiver__user=request.user)),
        status="ожидает"  # Только те предложения, которые еще не были приняты или отклонены
    )

    return render(request, 'ads/proposals_list.html', {
        'proposals': proposals
    })
@login_required
def create_ad(request):
    if request.method == 'POST':
        form = AdForm(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user  # Привязка объявления к текущему пользователю
            ad.save()
            return redirect('ad_list')
    else:
        form = AdForm()
    return render(request, 'ads/create_ad.html', {'form': form})

def update_ad(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    if ad.user != request.user:
        return redirect('ad_list')  # Перенаправление на список объявлений
    if request.method == 'POST':
        form = AdForm(request.POST, instance=ad)
        if form.is_valid():
            ad = form.save()  # Сохраняем изменения
            return redirect('ad_detail', pk=ad.pk)  # Перенаправляем на страницу объявления
    else:
        form = AdForm(instance=ad)  # Заполняем форму данными из объявления
    return render(request, 'ads/update_ad.html', {'form': form, 'ad': ad})


# views.py (исправление delete_ad)
@login_required
def delete_ad(request, pk):
    ad = get_object_or_404(Ad, pk=pk)

    if ad.user != request.user:
        messages.error(request, "Вы не можете удалить это объявление")
        return redirect('ad_list')

    ad.delete()
    messages.success(request, "Объявление успешно удалено")
    return redirect('ad_list')

def ad_detail(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    return render(request, 'ads/ad_detail.html', {'ad': ad})


@login_required
def create_exchange_proposal(request):
    user_ads = Ad.objects.filter(user=request.user)  # Все объявления пользователя
    available_ads = Ad.objects.exclude(user=request.user)  # Объявления других пользователей для обмена

    if request.method == 'POST':
        # Получаем данные из формы
        ad_sender_id = request.POST.get('ad_sender')
        ad_receiver_id = request.POST.get('ad_receiver')
        comment = request.POST.get('comment')

        # Получаем объекты объявлений
        ad_sender = Ad.objects.get(id=ad_sender_id)
        ad_receiver = Ad.objects.get(id=ad_receiver_id)

        # Создаем предложение обмена
        proposal = ExchangeProposal(
            ad_sender=ad_sender,
            ad_receiver=ad_receiver,
            comment=comment,
            status='ожидает',  # начальный статус
        )
        proposal.save()  # Сохраняем предложение обмена

        return redirect('ad_list')  # Перенаправляем на страницу со списком объявлений

    return render(request, 'ads/create_exchange_proposal.html', {
        'user_ads': user_ads,  # Объявления пользователя
        'available_ads': available_ads,  # Объявления других пользователей
    })
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('ad_list')  # Перенаправление на главную страницу
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def login_view(request):
    form = LoginForm(data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                # Перенаправляем на главную страницу через имя URL-шаблона
                return redirect('ad_list')  # Используем имя URL, а не имя шаблона

    return render(request, 'registration/login.html', {'form': form})