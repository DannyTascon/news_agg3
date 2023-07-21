from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordResetForm, SetPasswordForm, UserCreationForm,
)
from django.contrib.auth import (
    authenticate, get_user_model, login as auth_login, logout as auth_logout,
)
from django.contrib.auth.models import User  # Add this line
from django.shortcuts import render, redirect
import feedparser
from .models import Article, Source, ViewedArticle
from dateutil import parser as date_parser
from django.utils import timezone
from django.db import transaction
from django.http import Http404
from datetime import timedelta
from .utils import fetch_viewed_articles
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site


def home(request):
    fetch_news_data(request, 'latest')
    articles = Article.objects.filter(category='Latest').order_by('-pub_date')[:5]
    context = {'articles': articles}
    return render(request, 'home.html', context)


def politics(request):
    fetch_news_data(request, 'politics')
    articles = Article.objects.filter(category='Politics').order_by('-pub_date')[:5]
    context = {'articles': articles}
    return render(request, 'politics.html', context)


def entertainment(request):
    fetch_news_data(request, 'entertainment')
    articles = Article.objects.filter(category='Entertainment').order_by('-pub_date')[:5]
    context = {'articles': articles}
    return render(request, 'entertainment.html', context)


def sports(request):
    fetch_news_data(request, 'sports')
    articles = Article.objects.filter(category='Sports').order_by('-pub_date')[:5]
    context = {'articles': articles}
    return render(request, 'sports.html', context)


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
def user_logout(request):
    auth_logout(request)
    return redirect('home')


@login_required
def profile(request):
    user = request.user
    past_week = timezone.now() - timedelta(days=7)

    viewed_articles_latest = []
    viewed_articles_politics = []
    viewed_articles_entertainment = []
    viewed_articles_sports = []

    if user.is_authenticated:
        viewed_articles_latest = fetch_viewed_articles(user, 'Latest', past_week, 4)
        viewed_articles_politics = fetch_viewed_articles(user, 'Politics', past_week, 4)
        viewed_articles_entertainment = fetch_viewed_articles(user, 'Entertainment', past_week, 4)
        viewed_articles_sports = fetch_viewed_articles(user, 'Sports', past_week, 4)

    context = {
        'viewed_articles_latest': viewed_articles_latest,
        'viewed_articles_politics': viewed_articles_politics,
        'viewed_articles_entertainment': viewed_articles_entertainment,
        'viewed_articles_sports': viewed_articles_sports,
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
    elif category == 'sports':
        feed_urls = [
            "https://rss.app/feeds/ca0hzIf5cvOSzv5Y.xml",
        ]
    else:
        raise Http404("Invalid category")

    for url in feed_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            # Process each news article
            title = entry.title
            description = entry.summary if 'summary' in entry else 'No description available'
            source_name = entry.source.title if 'source' in entry and 'title' in entry.source else "Unknown"
            source, created = Source.objects.get_or_create(name=source_name)
            link = entry.link
            pub_date_string = entry.published
            if " -" in pub_date_string:
                pub_date
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
                        viewed_article.save()

    if category == 'politics':
        articles = Article.objects.filter(category='Politics').order_by('-pub_date')[:5]
        template_name = 'politics.html'
    elif category == 'entertainment':
        articles = Article.objects.filter(category='Entertainment').order_by('-pub_date')[:5]
        template_name = 'entertainment.html'
    elif category == 'sports':
        articles = Article.objects.filter(category='Sports').order_by('-pub_date')[:5]
        template_name = 'sports.html'
    else:
        articles = Article.objects.all().order_by('-pub_date')[:5]
        template_name = 'home.html'

    context = {'articles': articles}
    return render(request, template_name, context)

def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            
            # Generate the password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build the password reset URL
            current_site = get_current_site(request)
            reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            reset_url = f'{request.scheme}://{current_site.domain}{reset_url}'
            
            # Render the password reset email template
            subject = 'Reset your password'
            message = render_to_string('password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })
            
            # Send the password reset email
            send_mail(subject, message, 'noreply@example.com', [email])
            
            return redirect('password_reset_done')
    else:
        form = PasswordResetForm()
    
    return render(request, 'password_reset.html', {'form': form})


def password_reset_done(request):
    return render(request, 'password_reset_done.html')


def password_reset_confirm(request, uidb64, token):
    try:
        uid = str(urlsafe_base64_decode(uidb64), 'utf-8')
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            # Process the password reset form
            # Update the user's password and log them in
            
            return redirect('password_reset_complete')
    else:
        return render(request, 'password_reset_invalid.html')


def password_reset_complete(request):
    return render(request, 'password_reset_complete.html')