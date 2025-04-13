from django.db.models import Q
from django.test import TestCase
from django.urls import reverse

from .forms import AdForm
from .models import *
from rest_framework.test import APITestCase
from rest_framework import status
class AdTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.ad_data = {
            'title': 'Test API Ad',
            'description': 'Test API Description',
            'category': 'Electronics',
            'condition': 'new',
        }
    def test_create_ad(self):
        # Входим как тестовый пользователь
        self.client.login(username='testuser', password='testpassword')

        # Подготовка данных для POST-запроса
        data = {
            'title': 'Test Ad',
            'description': 'This is a test ad description',
            'category': 'Electronics',
            'condition': 'new',
            'user': self.user.id,
        }

        # Отправка POST-запроса для создания объявления
        response = self.client.post(reverse('create_ad'), data)

        # Проверка, что ответ содержит статус 302 (перенаправление)
        self.assertEqual(response.status_code, 302)

        # Проверка, что объявление создано в базе данных
        self.assertEqual(Ad.objects.count(), 1)
        self.assertEqual(Ad.objects.get().title, 'Test Ad')
class AdUpdateTests(TestCase):
    def setUp(self):
        # Создаем пользователей
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')

        self.ad = Ad.objects.create(
            title='Test Ad',
            description='Description',
            user=self.user1  # Указываем пользователя
        )

    def test_update_ad(self):
        # Входим как user1
        self.client.login(username='user1', password='password')

        # Подготовка данных для редактирования
        data = {
            'title': 'Updated Test Ad',
            'description': 'Updated Description',
            'category': 'Electronics',
            'condition': 'new',
        }

        # Отправка PUT-запроса для обновления объявления
        response = self.client.post(reverse('update_ad', kwargs={'pk': self.ad.pk}), data)

        # Проверка, что статус ответа 302 (перенаправление)
        self.assertEqual(response.status_code, 302)

        # Проверка, что объявление обновилось
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.title, 'Updated Test Ad')
        self.assertEqual(self.ad.description, 'Updated Description')

    def test_update_ad_other_user(self):
        # Входим как другой пользователь
        self.client.login(username='user2', password='password')
        # Попытка изменить объявление другого пользователя
        data = {
            'title': 'Updated Test Ad',
            'description': 'Updated Description',
            'category': 'Electronics',
            'condition': 'new',
        }
        response = self.client.post(reverse('update_ad', kwargs={'pk': self.ad.pk}), data)
        # Проверка, что статус ответа 403 (Forbidden)
        self.assertEqual(response.status_code, 403)
class AdDeleteTests(TestCase):
    def setUp(self):
        # Создаем пользователя и объявление
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.ad = Ad.objects.create(
            title='Test Ad',
            description='Description',
            user=self.user1
        )

    def test_delete_ad(self):
        # Входим как user1
        self.client.login(username='user1', password='password')

        # Удаление объявления
        response = self.client.post(reverse('delete_ad', kwargs={'pk': self.ad.pk}))

        # Проверка, что статус ответа 302 (перенаправление)
        self.assertEqual(response.status_code, 302)

        # Проверка, что объявление удалено
        self.assertEqual(Ad.objects.count(), 0)
class AdSearchTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.ad1 = Ad.objects.create(title='Test Ad 1', description='Description 1', user=self.user1)
        self.ad2 = Ad.objects.create(title='Test Ad 2', description='Description 2', user=self.user1)

    def test_search_ads(self):
        # Поиск по ключевому слову в заголовке
        response = self.client.get(reverse('ad_list') + '?search=Test Ad 1')
        # Проверка, что возвращается только одно объявление
        self.assertEqual(len(response.context['page_obj']), 1)  # Используем page_obj вместо ads
        # Проверка, что найденное объявление имеет правильный заголовок
        self.assertEqual(response.context['page_obj'][0].title, 'Test Ad 1')


class AdAPITests(APITestCase):
    def setUp(self):
        # Создаем пользователя
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)

        # Данные для создания объявления через API
        self.ad_data = {
            'title': 'Test Ad',
            'description': 'Test Description',
            'category': 'Electronics',
            'condition': 'new',
            'user': self.user.id
        }

        # Создаем тестовое объявление для теста get_ads_api
        self.test_ad = Ad.objects.create(
            title='Existing Ad',
            description='Existing Description',
            category='Electronics',
            condition='new',
            user=self.user
        )

    def test_create_ad_api(self):
        initial_count = Ad.objects.count()
        response = self.client.post('/api/ads/', self.ad_data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Ad.objects.count(), initial_count + 1)

        created_ad = Ad.objects.last()
        self.assertEqual(created_ad.title, self.ad_data['title'])
        self.assertEqual(created_ad.description, self.ad_data['description'])
        self.assertEqual(created_ad.user, self.user)

    def test_get_ads_api(self):
        response = self.client.get('/api/ads/')



        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) > 0)


class AdFilterAndPaginationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        for i in range(15):  # Создаем 15 объявлений для тестирования пагинации
            Ad.objects.create(
                title=f'Ad {i}',
                description=f'Description {i}',
                category='Electronics' if i % 2 == 0 else 'Books',
                condition='new',
                user=self.user
            )

    def test_filter_by_category(self):
        # Удаляем повторный цикл создания
        response = self.client.get(reverse('ad_list') + '?category=Electronics')
        self.assertEqual(len(response.context['page_obj']), 8)
    def test_pagination(self):
        response = self.client.get(reverse('ad_list'))
        self.assertEqual(len(response.context['page_obj']), 10)  # По умолчанию показывается 10 объявлений


class ExchangeProposalTests(TestCase):
    def setUp(self):
        # Создаем пользователей
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')

        # Создаем объявления
        self.ad1 = Ad.objects.create(
            title='Ad 1',
            description='Description 1',
            category='Electronics',
            condition='new',
            user=self.user1
        )

        self.ad2 = Ad.objects.create(
            title='Ad 2',
            description='Description 2',
            category='Electronics',
            condition='new',
            user=self.user2
        )

    def test_filter_exchange_proposals(self):
        # Создаем предложение обмена
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment='Test proposal',
            status='pending'
        )

        # Входим как user1
        logged_in = self.client.login(username='user1', password='password')
        self.assertTrue(logged_in, "Login failed")  # Проверяем успешность входа

        # Проверяем, что предложение создано
        self.assertEqual(ExchangeProposal.objects.count(), 1, "Proposal was not created")

        # Получаем URL для списка предложений
        url = reverse('proposals_list')

        # Делаем запрос
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, "Response status code is not 200")

        # Проверяем количество предложений
        self.assertEqual(len(response.context['proposals']), 1)

    def test_update_exchange_proposal(self):
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment='Initial comment',
            status='pending'
        )
        self.client.login(username='user2', password='password')
        data = {'status': 'accepted'}
        response = self.client.post(reverse('update_proposal', kwargs={'pk': proposal.pk}), data)
        self.assertEqual(response.status_code, 302)
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, 'accepted')

    def test_filter_exchange_proposals(self):
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment='Pending proposal',
            status='pending'  # Указываем статус
        )
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse('proposals_list'))
        self.assertEqual(len(response.context['proposals']), 1)
class AuthorizationTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.ad = Ad.objects.create(title='Test Ad', description='Description', category='Electronics', condition='new', user=self.user1)

    def test_unauthorized_access(self):
        response = self.client.post(reverse('create_ad'), {})
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа

    def test_forbidden_actions(self):
        self.client.login(username='user2', password='password')
        response = self.client.post(reverse('delete_ad', kwargs={'pk': self.ad.pk}))
        self.assertEqual(response.status_code, 403)  # Запрещено удалять чужое объявление
class ValidationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_invalid_data(self):
        form_data = {
            'title': '',  # Пустое значение должно вызвать ошибку
            'description': 'Test Description',
            'category': 'Electronics',
            'condition': 'new',  # Используйте правильное значение из choices
            'price': '100.00'
        }
        form = AdForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)


class PaginationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        for i in range(15):  # Создаем 15 объявлений
            Ad.objects.create(
                title=f'Ad {i}',
                description=f'Description {i}',
                category='Electronics',
                condition='new',
                user=self.user
            )

    def test_pagination(self):
        response = self.client.get(reverse('ad_list'))
        self.assertEqual(len(response.context['page_obj']), 10)  # По умолчанию показывается 10 объявлений