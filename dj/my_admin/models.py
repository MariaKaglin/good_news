from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django import forms 
from django.forms import ModelForm
from datetime import datetime 

class News(models.Model):
    news_id = models.CharField(max_length=200, primary_key=True)
    author =  models.ManyToManyField(User, blank=True, related_name='news')
    title = models.CharField(max_length=200)
    text = models.TextField()
    published_date = models.FloatField()

    def publish(self):
        self.published_date = datetime.timestamp(datetime.now())
        self.save()

class NewsForm(ModelForm):
    class Meta:
        model = News
        fields = ['title', 'text']

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    # news = models.ManyToManyField(News, blank=True) news_set

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    username = forms.CharField(max_length=200)

    class Meta:
        model = User
        fields = ('username', 'password')
