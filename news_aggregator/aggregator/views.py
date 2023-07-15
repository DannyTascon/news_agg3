from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
import feedparser
from .models import Article, Source, ViewedArticle
from dateutil import parser as date_parser
from django.utils import timezone
from django.db.models import Q
from django.db import transaction
from django.http import Http404
from datetime import timedelta

def home(request):
    fetch_news_data(request, 'latest')
    articles = Article.objects.filter(category='Latest').order_by('-pub_date')[:20]
    context = {'articles': articles}
    return render(request, 'home.html', context)


def politics(request):
    fetch_news_data(request, 'politics')
    articles = Article.objects.filter(category='Politics').order_by('-pub_date')[:20]
    context = {'articles': articles}
    return render(request, 'politics.html', context)


def entertainment(request):
    fetch_news_data(request, 'entertainment')
    articles = Article.objects.filter(category='Entertainment').order_by('-pub_date')[:20]
    context = {'articles': articles}
    return render(request, 'entertainment.html', context)



def shopping(request):
    return render(request, 'shopping.html')


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('profile')
    else:
        form = AuthenticationForm(request)
    return render(request, 'login.html', {'form': form})


@login_required
def logout(request):
    auth_logout(request)
    return redirect('home')


from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    user = request.user
    past_week = timezone.now() - timedelta(days=7)

    viewed_articles_latest = []
    viewed_articles_politics = []
    viewed_articles_entertainment = []

    if user.is_authenticated:
        viewed_articles_latest = ViewedArticle.objects.filter(user=user, article__category='Latest', viewed_at__gte=past_week)[:10]
        viewed_articles_politics = ViewedArticle.objects.filter(user=user, article__category='Politics', viewed_at__gte=past_week)[:10]
        viewed_articles_entertainment = ViewedArticle.objects.filter(user=user, article__category='Entertainment', viewed_at__gte=past_week)[:10]

    context = {
        'viewed_articles_latest': viewed_articles_latest,
        'viewed_articles_politics': viewed_articles_politics,
        'viewed_articles_entertainment': viewed_articles_entertainment
    }
    return render(request, 'profile.html', context)



def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def sources(request):
    return render(request, 'sources.html')


def is_valid_rss(url):
    feed = feedparser.parse(url)
    if feed.bozo:
        return False
    elif 'title' in feed.feed:
        return True
    return False


def fetch_news_data(request, category):
    category = category.lower()
    excluded_sources = []
    feed_urls = []

    viewed_articles = []

    # Fetch news data based on category
    if category == 'latest':
        feed_urls = [
            "https://news.google.com/news/rss",
        ]
    elif category == 'politics':
        feed_urls = [
            "https://rss.app/feeds/jw5KcQzuWUEOoXe0.xml",
        ]
    elif category == 'entertainment':
        feed_urls = [
            "https://rss.app/feeds/voRl0jEvJpbcFm2X.xml",
        ]
    else:
        raise Http404("Invalid category")

    for url in feed_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            # Process each news article
            title = entry.title
            description = entry.summary
            source_name = entry.source.title if 'source' in entry and 'title' in entry.source else "Unknown"
            source, created = Source.objects.get_or_create(name=source_name)
            link = entry.link
            pub_date_string = entry.published
            if " -" in pub_date_string:
                pub_date_string = pub_date_string.rsplit(" -", 1)[0]
            elif " +" in pub_date_string:
                pub_date_string = pub_date_string.rsplit(" +", 1)[0]

            pub_date = date_parser.parse(pub_date_string)

            if pub_date.tzinfo is None or pub_date.tzinfo.utcoffset(pub_date) is None:
                pub_date = timezone.make_aware(pub_date)

            category = category.capitalize()

            with transaction.atomic():
                existing_article = Article.objects.filter(title=title, source=source, link=link).first()
                if existing_article:
                    if (
                        existing_article.description != description
                        or existing_article.pub_date != pub_date
                        or existing_article.category != category
                    ):
                        existing_article.description = description
                        existing_article.pub_date = pub_date
                        existing_article.category = category
                        existing_article.save()

                    if request.user.is_authenticated:
                        viewed_article = ViewedArticle.objects.filter(user=request.user, article=existing_article).first()
                        if not viewed_article:
                            viewed_article = ViewedArticle(user=request.user, article=existing_article)
                            viewed_articles.append(viewed_article)
                else:
                    article = Article.objects.create(
                        title=title,
                        description=description,
                        source=source,
                        link=link,
                        pub_date=pub_date,
                        category=category,
                    )

                    if request.user.is_authenticated:
                        viewed_article = ViewedArticle(user=request.user, article=article)
                        viewed_articles.append(viewed_article)

    if category == 'politics':
        articles = Article.objects.filter(category='politics').order_by('-pub_date')[:20]
        template_name = 'politics.html'
    elif category == 'entertainment':
        articles = Article.objects.filter(category='entertainment').order_by('-pub_date')[:20]
        template_name = 'entertainment.html'
    else:
        articles = Article.objects.all().order_by('-pub_date')[:20]
        template_name = 'home.html'

    context = {'articles': articles}
    return render(request, template_name, context)

    # Rest of the code

def fetch_viewed_articles(request):
    if request.user.is_authenticated:
        user = request.user
        past_week = timezone.now() - timedelta(days=7)

        viewed_articles_latest = ViewedArticle.objects.filter(user=user, article__category='Latest', viewed_at__gte=past_week)[:5]
        viewed_articles_politics = ViewedArticle.objects.filter(user=user, article__category='Politics', viewed_at__gte=past_week)[:5]
        viewed_articles_entertainment = ViewedArticle.objects.filter(user=user, article__category='Entertainment', viewed_at__gte=past_week)[:5]

        viewed_articles = []
        viewed_articles.extend(viewed_articles_latest)
        viewed_articles.extend(viewed_articles_politics)
        viewed_articles.extend(viewed_articles_entertainment)

        return viewed_articles
    else:
        return []



