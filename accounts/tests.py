from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class RegisterViewTest(TestCase):
    def test_register_page(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)

    def test_register_success(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_password_mismatch(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'password1': 'StrongPass123!',
            'password2': 'DifferentPass123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())


class LoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'testpass123')

    def test_login_page(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_invalid(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)


class LogoutViewTest(TestCase):
    def test_logout(self):
        User.objects.create_user('testuser', 'test@test.com', 'testpass123')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('accounts:logout'))
        self.assertIn(response.status_code, [200, 302])


class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'testpass123')
        self.client.force_login(self.user)

    def test_profile_page(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')

    def test_profile_update(self):
        response = self.client.post(reverse('accounts:profile'), {
            'username': 'testuser',
            'email': 'updated@test.com',
            'first_name': 'Test',
            'last_name': 'User',
        })
        self.assertRedirects(response, reverse('accounts:profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@test.com')
        self.assertEqual(self.user.first_name, 'Test')

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)
