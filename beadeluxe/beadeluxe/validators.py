from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomPasswordValidator:
    def __init__(self):
        self.forbidden = ['/', '\\', '(', ')', '[', ']', '{', '}', '<', '>', '*', '.', ';', ':', ',', '"', "'"]
        
    def validate(self, password, user=None):
        for char in self.forbidden:
            if char in password:
                raise ValidationError(
                    _("Password cannot contain the following characters: / \\ ( ) [ ] { } < > * . ; : , \" '"),
                    code='invalid_password',
                )
    
    def get_help_text(self):
        return _("Your password cannot contain the following characters: / \\ ( ) [ ] { } < > * . ; : , \" '")