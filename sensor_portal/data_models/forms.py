from django.forms import ModelForm, PasswordInput

from .models import Device


# Class to make sure password input is displayed correctly
class DeviceForm(ModelForm):
    class Meta:
        model = Device
        widgets = {
            'password': PasswordInput(),
        }
        exclude = []
