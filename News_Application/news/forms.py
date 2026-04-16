from django import forms
from .models import Article, Newsletter, CustomUser
from django.contrib.auth.forms import UserCreationForm


""" # ******************** REGISTRATION FORMS ********************"""


class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "role", "password1", "password2")


""" # ******************** ARTICLE FORMS ********************"""


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            "title",
            "content",
            "publisher",
        ]


""" # ******************** NEWSLETTER FORMS  ********************"""


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ["title", "content", "publisher"]
