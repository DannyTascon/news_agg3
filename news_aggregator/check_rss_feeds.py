import os
import django
import sys

# Add your project to sys.path
project_home = '/Projects/Max/news_agg3/news_aggregator'  # Use your actual path
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_aggregator.settings')

django.setup()

from aggregator.views import is_valid_rss

def check_rss(urls):
    for url in urls:
        if is_valid_rss(url):
            print(f"The URL {url} is a valid RSS feed.")
        else:
            print(f"The URL {url} is NOT a valid RSS feed.")

# Replace with the URLs you want to check
urls = [
    "https://www.huffingtonpost.com/section/front-page/feed",
    "http://rss.cnn.com/rss/edition.rss",
    "https://news.google.com/news/rss",
    "https://www.huffingtonpost.com/section/politics/feed",
    "http://rss.cnn.com/rss/edition_politics.rss",
    "https://news.google.com/news/rss/headlines/section/topic/POLITICS.en_us/Politics?ned=us&hl=en&gl=US",
    "https://rss.app/feeds/XO3uX9ijcndRC6sM.xml",
    "https://rss.app/feeds/yBZmRluraCVp7I9U.xml",
    "https://rss.app/feeds/ToSfPKaoCV3l95uS.xml",
    "https://rss.app/feeds/voRl0jEvJpbcFm2X.xml",
]
check_rss(urls)
