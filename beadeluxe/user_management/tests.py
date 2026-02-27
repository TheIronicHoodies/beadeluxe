from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Profile
from django.urls import reverse
from django.core import mail

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
    def credentials_valid(self):
        profile = Profile(
            user=self.user,
            fullname="Collin Harper",
            nickname="Collin",
            pronouns="he/him",
            email="collin@example.com",
            mobile_number="+6591258565"
        )
        profile.full_clean()
        profile.save()
        self.assertEqual(profile.fullname, "Collin Harper")
        self.assertEqual(profile.nickname, "Collin")
        self.assertEqual(profile.pronouns, "he/him")
        self.assertEqual(profile.email, "collin@example.com")
        self.assertEqual(profile.mobile_number, "+6591258565")
        self.assertEqual(str(profile), "Collin Harper")
        self.assertEqual(profile.user.username, "collin")

    def credentials_invalid(self):
        profile = Profile(
            user=self.user,
            fullname="Bob Smith",
            nickname="Bob",
            pronouns="he/him",
            email="bob@example.com",
            mobile_number="91258 565"
        )
        with self.assertRaises(ValidationError):
            profile.full_clean() 
            
    def profile_picture_added(self):
        image = SimpleUploadedFile(
            name="test_image.jpg",
            content=b"file_content",
            content_type="image/jpeg"
        )

        profile = Profile.objects.create(
            user=self.user,
            fullname="Collin Harper",
            nickname="Collin",
            pronouns="he/him",
            email="collin@example.com",
            mobile_number="+6591258565",
            profile_picture=image
        )
        self.assertTrue(profile.profile_picture)
        self.assertIn("test_image.jpg", profile.profile_picture.name)

"""Class for testing if password reset flow works as expected"""
class PasswordResetTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="collin",
            email="collin@example.com",
            password="secret123"
        )

    def password_reset_flow(self):
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


