from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.core import mail
from django.contrib.auth import get_user_model
User = get_user_model()

"""Class for testing registration of user"""
class RegistrationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="collin",
            password="secret123"
        )
    def test_user_is_registered(self):
        user_count = User.objects.filter(username="collin").count()
        self.assertEqual(user_count, 1)
        self.assertEqual(self.user.username, "collin")
        self.assertTrue(self.user.check_password("secret123"))

"""Class for testing if credentials are properly validated"""
class CredentialTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="collin",
            password="secret123"
        )

    def test_credentials_valid(self):
        user = User(
            username="collin2",
            fullname="Collin Harper",
            nickname="Collin",
            pronouns="he/him",
            email="collin@example.com",
            mobile_number="+6591258565"
        )
        user.full_clean()
        user.save()
        self.assertEqual(user.fullname, "Collin Harper")
        self.assertEqual(user.nickname, "Collin")
        self.assertEqual(user.pronouns, "he/him")
        self.assertEqual(user.email, "collin@example.com")
        self.assertEqual(user.mobile_number, "+6591258565")
        self.assertEqual(str(user), "Collin Harper")

    def test_credentials_invalid(self):
        user = User(
            username="bobsmith",
            fullname="Bob Smith",
            nickname="Bob",
            pronouns="he/him",
            email="bob@example.com",
            mobile_number="91258 565"  # invalid format
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_profile_picture_added(self):
        image = SimpleUploadedFile(
            name="test_image.jpg",
            content=b"file_content",
            content_type="image/jpeg"
        )
        user = User.objects.create(
            username="collin3",
            fullname="Collin Harper",
            nickname="Collin",
            pronouns="he/him",
            email="collin@example.com",
            mobile_number="+6591258565",
            profile_picture=image
        )
        self.assertTrue(user.profile_picture)
        self.assertIn("test_image.jpg", user.profile_picture.name)


"""Class for testing if password reset flow works as expected"""
class PasswordResetTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="collin",
            email="collin@example.com",
            password="secret123"
        )

    def test_password_reset_flow(self):
        response = self.client.post(
            reverse("password_reset"),
            {"email": "collin@example.com"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("collin@example.com", mail.outbox[0].to)

        reset_link = [line for line in mail.outbox[0].body.splitlines() if "/reset/" in line][0]

        response = self.client.get(reset_link, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter your new password")

        response = self.client.post(reset_link, {
            "new_password1": "newsecret123",
            "new_password2": "newsecret123",
        })
        self.assertEqual(response.status_code, 302)

        login_success = self.client.login(username="collin", password="newsecret123")
        self.assertTrue(login_success)


class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="collin",
            password="secret123",
            fullname="Collin Harper",
            nickname="Collin",
            pronouns="he/him",
            email="collin@example.com",
            mobile_number="+6591258565"
        )

    def test_profile_view(self):
        self.client.login(username="collin", password="secret123")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Collin Harper")
        self.assertContains(response, "Collin")
        self.assertContains(response, "he/him")
        self.assertContains(response, "collin@example.com")
        self.assertContains(response, "+6591258565")

        
