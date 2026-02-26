from django.test import TestCase
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

# Create your tests here.

User = get_user_model()

class AccountsTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.register_url = "/api/accounts/register/"
        self.login_url = "/api/accounts/login/"

        self.user_data = {
            "username": "arvind",
            "email": "arvind@test.com",
            "password": "testpass123",
            "role": "CUSTOMER",
            "phone_number": "9999999999"
        }

    # ✅ REGISTRATION SUCCESS
    def test_user_registration_success(self):
        response = self.client.post(self.register_url, self.user_data, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["username"], "arvind")
        self.assertEqual(User.objects.count(), 1)

    # ✅ REGISTRATION VALIDATION ERROR
    def test_user_registration_missing_fields(self):
        response = self.client.post(self.register_url, {
            "username": "test"
        }, format="json")

        self.assertEqual(response.status_code, 400)

    # ✅ LOGIN SUCCESS (JWT)
    def test_login_success(self):
        User.objects.create_user(
            username="arvind",
            email="arvind@test.com",
            password="testpass123"
        )

        response = self.client.post(self.login_url, {
            "username": "arvind",
            "password": "testpass123"
        }, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    # ❌ LOGIN FAIL – WRONG PASSWORD
    def test_login_wrong_password(self):
        User.objects.create_user(
            username="arvind",
            email="arvind@test.com",
            password="correctpass"
        )

        response = self.client.post(self.login_url, {
            "username": "arvind",
            "password": "wrongpass"
        }, format="json")

        self.assertEqual(response.status_code, 401)

    # ❌ LOGIN FAIL – USER NOT FOUND
    def test_login_user_not_found(self):
        response = self.client.post(self.login_url, {
            "username": "ghost",
            "password": "nopass"
        }, format="json")

        self.assertEqual(response.status_code, 401)

    # ✅ PASSWORD IS HASHED
    def test_password_is_hashed(self):
        self.client.post(self.register_url, self.user_data, format="json")

        user = User.objects.first()

        self.assertNotEqual(user.password, "testpass123")
        self.assertTrue(user.check_password("testpass123"))