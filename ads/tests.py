from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Ad
from rest_framework.test import APITestCase
from rest_framework import status

class AdTests(TestCase):
    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(username='testuser', password='testpassword')

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

        # Создаем объявление от имени пользователя 1
        self.ad = Ad.objects.create(
            title='Test Ad',
            description='Description',
            user=self.user1
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
        self.assertEqual(len(response.context['ads']), 1)

        # Проверка, что найденное объявление имеет правильный заголовок
        self.assertEqual(response.context['ads'][0].title, 'Test Ad 1')
class AdAPITests(APITestCase):
    def setUp(self):
        # Создаём пользователя для теста
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        # Данные для создания объявления
        self.ad_data = {
            'title': 'Test API Ad',
            'description': 'Test API Description',
            'category': 'Electronics',
            'condition': 'new',
        }

        # Создаём тестовое объявление
        self.ad = Ad.objects.create(
            title='Test Ad 1',
            description='Test Description 1',
            category='Electronics',
            condition='new',
            user=self.user  # Привязываем к созданному пользователю
        )

    def test_create_ad_api(self):
        response = self.client.post('/api/ads/', self.ad_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test API Ad')

    def test_get_ads_api(self):
        response = self.client.get('/api/ads/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)  # Убедимся, что хотя бы одно объявление вернулось
