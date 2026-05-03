from django.urls import path
from . import views
from .views import SubscribedArticlesAPIView
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    # home
    path("", views.home, name="home"),
    # Aunthentication
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    # Reader URLs
    path("articles/", views.article_list, name="article_list"),
    path("subscribe/publisher/<int:publisher_id>/", views.subscribe_publisher, name="subscribe_publisher"),
    path("subscribe/journalist/<int:journalist_id>/", views.subscribe_journalist, name="subscribe_journalist"),
    # Journalist URLs
    path("articles/create/", views.create_article, name="create_article"),
    path("articles/<int:article_id>/edit/", views.update_article, name="update_article"),
    path("articles/<int:article_id>/delete/", views.delete_article, name="delete_article"),
    # Article detail
    path("articles/<int:newsletter_id>/", views.article_detail, name="article_detail"),
    # Newsletters
    path("newsletters/", views.newsletter_list, name="newsletter_list"),
    path("newsletters/create/", views.create_newsletter, name="create_newsletter"),
    path("newsletters/<int:newsletter_id>/edit/", views.update_newsletter, name="update_newsletter"),
    path("newsletters/<int:newsletter_id>/delete/", views.delete_newsletter, name="delete_newsletter"),
    path("newsletters/<int:newsletter_id>/", views.newsletter_detail, name="newsletter_detail"),
    # Editor URLs
    path("editor/pending/", views.pending_articles, name="pending_articles"),
    path("editor/approve/<int:article_id>/", views.approve_article, name="approve_article"),
    # APIS
    path("api/subscribed-articles/", SubscribedArticlesAPIView.as_view(), name="subscribed-articles"),
    path("articles/<int:article_id>/tweet/", views.tweet_article_view, name="tweet-article"),

    # token
    path("api/token/", obtain_auth_token, name="api_token"),
]
