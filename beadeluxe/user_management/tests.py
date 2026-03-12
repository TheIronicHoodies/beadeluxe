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
    # Check if the user is registered successfully with correct credentials
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
    # Check if all credentials are valid and saved correctly
    def test_credentials_valid(self):
        user = User(
            username="collin2",
            fullname="Collin Harper",
            nickname="Collin",
            pronouns="he/him",
            email="collin@example.com",
            mobile_number="+6591258565"
        )
        user.set_password("secret123")
        user.full_clean()
        user.save()
        self.assertEqual(user.fullname, "Collin Harper")
        self.assertEqual(user.nickname, "Collin")
        self.assertEqual(user.pronouns, "he/him")
        self.assertEqual(user.email, "collin@example.com")
        self.assertEqual(user.mobile_number, "+6591258565")
        self.assertEqual(str(user), "Collin Harper")

    # In the case that the format is invalid, a ValidationError should be raised
    def test_credentials_invalid(self):
        user = User(
            username="bobsmith",
            fullname="Bob Smith",
            nickname="Bob",
            pronouns="he/him",
            email="bob@example.com",
            mobile_number="91258 565"  # Invalid format since the mobile number should start with a + and contain no spaces
        )
        with self.assertRaises(ValidationError):
            user.full_clean()
            
    # Check if profile picture is added and saved correctly
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
        self.assertTrue(user.profile_picture.name.endswith(".jpg"))
        self.assertIn("test_image", user.profile_picture.name)


"""Class for testing if password reset flow works as expected"""
class PasswordResetTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="collin",
            email="collin@example.com",
            password="secret123"
        )

    # Test the entire password reset flow from requesting a reset to setting a new password and verifying that the password has been updated successfully
    def test_password_reset_flow(self):
        # Request password reset
        response = self.client.post(reverse("password_reset"), {"email": "collin@example.com"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)

        # Extract reset link from email
        email_body = mail.outbox[0].body
        reset_link = [line for line in email_body.splitlines() if "http://testserver" in line][0]

        # GET reset link (redirects to set-password form)
        response = self.client.get(reset_link)
        self.assertEqual(response.status_code, 302)  # redirect expected
        self.assertIn("/set-password/", response.url)

        # Follow redirect to set-password form
        response = self.client.get(reset_link, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "New password")

        # POST new password to set-password form
        set_password_url = response.request["PATH_INFO"]
        response = self.client.post(set_password_url, {
            "new_password1": "NewSecret123!",
            "new_password2": "NewSecret123!",
        })
        self.assertRedirects(response, reverse("password_reset_complete"))

        # Verify password updated inside the database
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewSecret123!"))

        # Check logins with old and new passwords
        self.assertTrue(self.client.login(username="collin", password="NewSecret123!"))
        self.assertFalse(self.client.login(username="collin", password="secret123"))

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

    # Test that the profile view displays the correct user information when accessed by a logged-in user
    def test_profile_view(self):
        self.client.login(username="collin", password="secret123")
        response = self.client.get(reverse("user_management:profile-view", args=["collin"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Collin Harper")
        self.assertContains(response, "Collin")
        self.assertContains(response, "he/him")
        self.assertContains(response, "collin@example.com")
        self.assertContains(response, "+6591258565")

        

        
