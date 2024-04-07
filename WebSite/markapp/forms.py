from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, Group

from .models import Profile, Achievement, Task, GroupProfile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput)
    first_name = forms.CharField(max_length=40)
    last_name = forms.CharField(max_length=40)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['user', 'bio', 'score', 'rank', 'profile_pic']


class ProfileEditForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['profile_pic', 'bio']


class AchievementForm(forms.ModelForm):

    class Meta:
        model = Achievement
        fields = ['title', 'description', 'weight', 'ach_img']


class GroupTaskAchievementForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ['achievement']  # Ensure this is correct based on your model
        widgets = {
            'achievement': forms.Select(attrs={'class': 'form-control'}),
        }


class TaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'current_group', 'user']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'current_group': forms.Select(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.none()

        if 'current_group' in self.data:
            try:
                group_id = int(self.data.get('current_group'))
                self.fields['user'].queryset = GroupProfile.objects.get(
                    id=group_id).group.user_set.all()
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields[
                'user'].queryset = self.instance.current_group.group.user_set.all(
                )


class GroupProfileForm(forms.ModelForm):

    class Meta:
        model = GroupProfile
        fields = ['group', 'creator']
        widgets = {
            'group': forms.Select(attrs={'class': 'form-control'}),
            'creator': forms.Select(attrs={'class': 'form-control'}),
        }


class GroupCreationForm(forms.ModelForm):
    user_email = forms.EmailField(
        required=False,
        help_text='Enter the email of the user you want to add to the group.')

    class Meta:
        model = Group
        fields = ['name']

    def clean_user_email(self):
        email = self.cleaned_data.get('user_email')
        if email:
            try:
                user = User.objects.get(email=email)
                print('user', user)
            except User.DoesNotExist:
                print('failll')
                raise ValidationError("No user with this email exists.")
            return email
        return None


class AddUsersToGroupForm(forms.Form):
    emails = forms.CharField(widget=forms.Textarea,
                             help_text='Enter each email on a new line.')

    def clean_emails(self):
        emails_str = self.cleaned_data.get('emails')
        emails_list = emails_str.split()
        users = []
        non_existing_emails = []

        for email in emails_list:
            try:
                user = User.objects.get(email=email.strip())
                users.append(user)
            except User.DoesNotExist:
                non_existing_emails.append(email)

        if non_existing_emails:
            raise ValidationError(
                f"No users found for the following emails: {', '.join(non_existing_emails)}"
            )

        return users
