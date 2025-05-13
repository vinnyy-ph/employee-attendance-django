from typing import Iterable
from django.db import models
from django.core.exceptions import ValidationError

from apps.employee.card_utils import get_id_card_photo

def validate_image(image):
    if image.file.size > 2 * 1024 * 1024:
        raise ValidationError('Image file too large ( > 2mb )')
    
    # Get the file extension and convert to lowercase for case-insensitive comparison
    extension = image.file.name.split('.')[-1].lower()
    
    # Support both JPEG and PNG as mentioned in the error message
    if extension not in ['jpg', 'jpeg', 'png']:
        raise ValidationError('Image file type not supported. Only JPEG and PNG files are accepted.')

class Employee(models.Model):
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    designation = models.CharField(max_length=50)
    email = models.EmailField(unique=True)  # Keeping email for now as it's required by existing code
    phone = models.CharField(max_length=15)
    photo = models.ImageField(upload_to='employee_photos', validators=[validate_image])
    id_card_photo = models.ImageField(upload_to='employee_id_cards', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    def save(self, *args, **kwargs):
        # Check if this is a new record that needs an ID card
        if self.photo:  # Only proceed if a photo was uploaded
            # Remove previous photo if it exists
            if self.id_card_photo:
                self.id_card_photo.delete(save=False)
                
            # Add id_card_photo to the instance
            try:
                self.id_card_photo.save(
                    f'{self.first_name}_{self.last_name}_id_card.jpg',
                    get_id_card_photo(self),
                    save=False
                )
            except Exception as e:
                # Log the error but don't prevent saving the employee
                print(f"Error generating ID card: {e}")
                # Optionally raise the error if you want to prevent saving without ID card
                # raise
    
        super().save(*args, **kwargs)