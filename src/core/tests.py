from rest_framework.test import APITestCase
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from rest_framework import status
from core.models import User


class UserCreateTestCase(APITestCase):
    def test_user_password(self):
        """Проверяем сложность пароля"""
        response = self.client.post(
            reverse('signup'),
            {
                'username': 'test',
                'password': '12345',
                'password_repeat': '12345'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user(self):
        """Проверяем обязательность полей"""
        url = reverse('signup')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(),
                             {'username': ['Обязательное поле.'],
                              'password': ['Обязательное поле.'],
                              'password_repeat': ['Обязательное поле.']

                              })

    def test_double_user(self):
        """Проверяем, что пользователь уже есть"""
        User.objects.create(username='test', password=make_password('test_password'))
        response = self.client.post(
            reverse('signup'),
            {
                'username': 'test',
                'password': 'test12345',
                'password_repeat': 'test12345'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), {'username': ['Пользователь с таким именем уже существует.']})

    def test_email_user(self):
        """Проверяем корректность email"""
        response = self.client.post(
            reverse('signup'),
            {
                'username': 'test',
                'password': 'test12345',
                'password_repeat': 'test12345',
                'email': 'test'
            })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), {'email': ['Введите правильный адрес электронной почты.']})

    def test_error_password(self):
        """Проверяем пароль на совпадение"""
        response = self.client.post(
            reverse('signup'),
            {
                'username': 'test',
                'password': 'test12345',
                'password_repeat': 'test1234577',
            })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), {'non_field_errors': ['Password must match']})

    def test_all_fields_user(self):
        """Проверяем все поля пользователя при создании"""
        response = self.client.post(
            reverse('signup'),
            {
                'username': 'test',
                'email': 'test@mail.ru',
                'first_name': 'test',
                'last_name': 'test',
                'password': 'test12345',
                'password_repeat': 'test12345',
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        new_user = User.objects.last()
        self.assertDictEqual(response.json(),
                             {
                                 'id': new_user.id,
                                 'username': 'test',
                                 'email': 'test@mail.ru',
                                 'first_name': 'test',
                                 'last_name': 'test',
                             })
        self.assertNotEqual(new_user.password, 'test12345')
        self.assertTrue(new_user.check_password('test12345'))


class LoginTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
            email='test@mail.ru',
            password='test1234567',
        )

    def test_invalid_username(self):
        """Проверяем пользователя"""
        response = self.client.post(
            reverse('login'),
            {
                'username': 'test234',
                'password': 'test123456788'
            })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_password(self):
        """Проверяем пароль"""
        response = self.client.post(
            reverse('login'),
            {
                'username': 'test',
                'password': 'test123456788'
            })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ProfileTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
            password='test1234567',
        )

    def test_logout(self):
        self.client.force_login(self.user)
        response = self.client.delete(
            reverse('profile'), )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.cookies['sessionid'].value, '')

    def test_retrieve_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.json(),
                             {
                                 'id': self.user.id,
                                 'username': self.user.username,
                                 'email': self.user.email,
                                 'first_name': self.user.first_name,
                                 'last_name': self.user.last_name,
                             })

    def test_update_user(self):
        """Проверяем изменение пользователя"""
        self.client.force_login(self.user)
        self.assertEqual(self.user.email, '')
        response = self.client.patch(reverse('profile'), {'email': 'teat12@mail.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.json(),
                             {
                                 'id': self.user.id,
                                 'username': self.user.username,
                                 'email': 'teat12@mail.com',
                                 'first_name': self.user.first_name,
                                 'last_name': self.user.last_name,
                             })


class TestUpdatePassword(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user',
            password='test_password'
        )

    def test_auth_user(self):
        response = self.client.patch(reverse('update_password'),
                                     {
                                         'old_password': 'test_password',
                                         'new_password': 'newtest1234567',
                                     })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_old_password(self):
        """Проверяем корректность старого пароля"""
        self.client.force_login(self.user)
        response = self.client.patch(reverse('update_password'),
                                     {
                                         'old_password': 'test_password11',
                                         'new_password': 'newtest1234567',
                                     })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), {'old_password': ['field is incorrect']})

    def test_success(self):
        """Проверяем изменение пароля"""
        self.client.force_login(self.user)
        response = self.client.patch(reverse('update_password'),
                                     {
                                         'old_password': 'test_password',
                                         'new_password': 'newtest1234567',
                                     })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.json(), {})
        self.user.refresh_from_db(fields=('password',))
        self.assertTrue(self.user.check_password('newtest1234567'))
