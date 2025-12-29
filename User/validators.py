from django.core.exceptions import ValidationError


class PasswordValidator:
  def __init__(self, min_length=6, max_length=20):
    self.min_length = min_length
    self.max_length = max_length

  def validate(self, password, account=None):
    if len(password)<self.min_length:
      raise ValidationError(f"Password must be at least {self.min_length} characters!")
    
    if len(password)>self.max_length:
      raise ValidationError(f"Password is limited at {self.max_length} characters!")
    
    if not any(c.isdigit() for c in password):
      raise ValidationError("Password must have at least 1 number!")
    
  def get_help_text(self):
    return f"Password must contain at least 1 number and have length from {self.min_length} to {self.max_length} characters!"
  