from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth.models import Group


class CustomSignupForm(SignupForm):
    user_type = forms.ChoiceField(
        choices=[('user', 'User'), ('courier', 'Courier')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='client',
        label='Select a role'
    )

    def save(self, request):
        user = super().save(request)
        user_type = self.cleaned_data['user_type']
        group_name = 'Couriers' if user_type == 'courier' else 'Users'
        group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)
        return user
