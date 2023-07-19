from django.contrib.auth.models import User
from django.db import models

from django.contrib.auth.models import User

class Source(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    link = models.URLField()
    pub_date = models.DateTimeField()
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class ViewedArticle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} viewed "{self.article.title}"'

    class Meta:
        verbose_name_plural = 'Viewed Articles'



