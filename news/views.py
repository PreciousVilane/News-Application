from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from .models import Article, Publisher, CustomUser, Newsletter
from .forms import ArticleForm, NewsletterForm, CustomUserCreationForm
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from .serializers import ArticleSerializer


""" # ********************  HOME/LANDING PAGE ********************"""


def home(request):
    """ landing page"""
    return render(request, "news/home.html")


""" # ***************** AUNTHENTICATION FUNCTIONALITY ****************"""
'''
The views is for handling user aunthentication
'''


def register_view(request):
    if request.method == "POST":
        '''Use registration form to create a new user'''
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Assign Django group based on role
            group = Group.objects.get(name=user.role)
            user.groups.add(group)

            login(request, user)
            return redirect("article_list")
    else:
        form = CustomUserCreationForm()

    return render(request, "news/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        ''' Use Django's built-in authentication form to log in the user'''
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("article_list")
        messages.error(request, "Invalid username or password")
    else:
        form = AuthenticationForm()

    return render(request, "news/login.html", {"form": form})


# USER LOGOUT
@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


""" # ******************** READERS FUNCTIONALITY ********************"""


# READERS VIEWING APPROVE ARTICLES + JOURNALST VIEW THEIR ARTICLES,
@login_required
def article_list(request):
    ''' Depending on the user role, show different sets of articles '''
    user = request.user

    if user.role == "journalist":
        # Journalist's independent articles
        articles = request.user.journalist_articles.all()

    elif user.role == "reader":

        articles = Article.objects.filter(approved=True)

    elif user.role == "editor":
        # Editors see all articles
        articles = Article.objects.all()
    else:
        articles = Article.objects.none()

    return render(request, "news/article_list.html", {"articles": articles})


# READERS SUBCRIBING TO PUBLISHERS
@login_required
def subscribe_publisher(request, publisher_id):  # name to identify publisher
    ''' Only readers can subscribe to publishers '''
    if request.user.role != "reader":
        return HttpResponseForbidden()

    publisher = get_object_or_404(Publisher, id=publisher_id)
    if publisher not in request.user.subscribed_publishers.all():
        request.user.subscribed_publishers.add(publisher)
        messages.success(request, f"Subscribed to {publisher.name} successfully!")
    return redirect("article_list")


# READERS SUBCRIBING TO JOURNALIST
@login_required
def subscribe_journalist(request, journalist_id):
    if request.user.role != "reader":
        return HttpResponseForbidden()

    journalist = get_object_or_404(CustomUser, id=journalist_id, role="journalist")
    request.user.subscribed_journalists.add(journalist)
    return redirect("article_list")


""" # ******************** ARTICLES FUNCTIONALITY ********************"""
'''
The views is for handling article, creation, updating, viewing
and deletion
'''


@login_required
@permission_required("news.add_article", raise_exception=True)
def create_article(request):
    ''' Only journalists can create articles '''
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.journalist = request.user
            article.approved = False  # needs approval
            article.save()
            request.user.independent_articles.add(article)
            return redirect("article_list")
    else:
        form = ArticleForm()

    return render(request, "news/article_form.html", {"form": form})


# ARTICLES VIEW IN DETAIL
@login_required
def article_detail(request, article_id):
    ''' All users can view article details, but readers can
        only see approved articles from subscribed publishers/journalists
    '''
    article = get_object_or_404(Article, id=article_id)
    user = request.user

    # Readers can only see approved articles from subscribed
    # publishers/journalists
    if user.role == "reader" and not article.approved:
        return HttpResponseForbidden("This article is not approved.")

    if user.role == "reader":
        if (
            article.publisher not in user.subscribed_publishers.all()
            and article.journalist not in user.subscribed_journalists.all()
        ):
            return HttpResponseForbidden(
                "You are not subscribed to this article's publisher or journalist."
            )

    return render(request, "news/article_detail.html", {"article": article})


# UPDATE ARTICLES ONLY BY JOURNALIST + EDITORS
@login_required
@permission_required("news.change_article", raise_exception=True)
def update_article(request, article_id):
    ''' Journalists can edit only their own articles,
        while editors can edit any article
    '''

    article = get_object_or_404(Article, id=article_id)
    user = request.user

    # Journalists can edit only their own articles
    if user.role == "journalist":
        if article.journalist != user:
            return HttpResponseForbidden("You can only edit your own articles.")

    # Editors can edit ANY article
    elif user.role == "editor":
        pass
    else:
        return HttpResponseForbidden("You cannot edit articles.")

    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return redirect("article_list")
    else:
        form = ArticleForm(instance=article)

    return render(request, "news/article_form.html", {"form": form, "is_edit": True})


# DELETE ARTICLES ONLY BY JOURNALIST + EDITORS
@login_required
@permission_required("news.delete_article", raise_exception=True)
def delete_article(request, article_id):
    ''' Journalists can delete only their own articles,
        while editors can delete any article
    '''
    article = get_object_or_404(Article, id=article_id)
    user = request.user

    # Journalists can delete only their own articles
    if user.role == "journalist":
        if article.journalist != user:
            return HttpResponseForbidden("You can only delete your own articles.")

    # Editors can delete ANY article
    elif user.role == "editor":
        pass
    else:
        return HttpResponseForbidden("You cannot delete articles.")

    if request.method == "POST":
        article.delete()
        return redirect("article_list")

    return render(request, "news/article_confirm_delete.html", {"article": article})


# REVIEW PENDING ARTICLES
@login_required
@permission_required("news.change_article", raise_exception=True)
def pending_articles(request):
    ''' Editors can see all pending articles that need approval '''
    articles = Article.objects.filter(approved=False)
    return render(request, "news/pending_articles.html", {"articles": articles})


# APPROVE ARTICLE
@login_required
@permission_required("news.change_article", raise_exception=True)
def approve_article(request, article_id):
    ''' Editors can approve articles, which sets approved=True '''
    article = get_object_or_404(Article, id=article_id)
    article.approved = True
    article.save()  # triggers signal
    return redirect("pending_articles")


""" # ******************** NEWSLETTERS  CRUD FUNCTIONALITY ********************"""
'''
The views is for handling newsletter, creation, updating, viewing
and deletion
'''


# JOURNALIST CREATES NEWSLETTERS
@login_required
@permission_required("news.add_newsletter", raise_exception=True)
def create_newsletter(request):
    ''' Only journalists can create newsletters '''
    if request.user.role != "journalist":
        return HttpResponseForbidden("Only journalists can create newsletters.")
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            newsletter = form.save()
            # assign to journalist
            request.user.independent_newsletters.add(newsletter)
            return redirect("newsletter_list")
    else:
        form = NewsletterForm()

    return render(request, "news/newsletters_form.html", {"form": form})


# VIEW/ READ NEWSLETTERS
@login_required
def newsletter_list(request):
    ''' Show newsletters based on user role:
        - Journalists see their own newsletters
        - Readers see newsletters from subscribed publishers/journalists
        - Editors see all newsletters
    '''
    user = request.user

    if user.role == "journalist":
        newsletters = user.independent_newsletters.all()
    elif user.role == "reader":
        # show newsletters from subscribed publishers or journalists
        newsletters = Newsletter.objects.filter(
            publisher__in=user.subscribed_publishers.all()
        )
        # | Newsletter.objects.filter(journalist__in=user.subscribed_journalists.all())
    elif user.role == "editor":
        newsletters = Newsletter.objects.all()
    else:
        newsletters = Newsletter.objects.none()

    return render(request, "news/newsletter_list.html", {"newsletters": newsletters})


# VIEW NEWSLETTERS IN DETAIL
@login_required
def newsletter_detail(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)

    user = request.user

    # Readers can only view subscribed newsletters
    if user.role == "reader":
        if (
            newsletter.publisher not in user.subscribed_publishers.all()
            and newsletter.journalist not in user.subscribed_journalists.all()
        ):
            return HttpResponseForbidden("You are not subscribed to this newsletter.")

    return render(request, "news/newsletter_detail.html", {"newsletter": newsletter})


# UPDATE NEWSLETTERS ONLY BY: JOURNALIST + EDITORS
@login_required
@permission_required("news.change_newsletter", raise_exception=True)
def update_newsletter(request, newsletter_id):
    ''' Journalists can edit only their own newsletters,
        while editors can edit any newsletter
    '''
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    user = request.user

    # Journalists can edit only their own newsletters
    if user.role == "journalist":
        if newsletter not in user.independent_newsletters.all():
            return HttpResponseForbidden("You can only edit your own newsletters.")

    # Editors can edit ANY newsletter
    elif user.role == "editor":
        pass

    else:
        return HttpResponseForbidden("You cannot edit newsletters.")

    if request.method == "POST":
        form = NewsletterForm(request.POST, instance=newsletter)
        if form.is_valid():
            form.save()
            return redirect("newsletter_list")
    else:
        form = NewsletterForm(instance=newsletter)

    return render(
        request, "news/newsletters_form.html", {"form": form, "is_edit": True}
    )


# DELETE NEWSLETTERS BY JOURNALIST + EDITORS
@login_required
@permission_required("news.delete_newsletter", raise_exception=True)
def delete_newsletter(request, newsletter_id):
    ''' Journalists can delete only their own newsletters,
        while editors can delete any newsletter
    '''

    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    user = request.user

    if user.role == "journalist":
        if newsletter not in user.independent_newsletters.all():
            return HttpResponseForbidden("You can only delete your own newsletters.")

    elif user.role == "editor":
        pass

    else:
        return HttpResponseForbidden("You cannot delete newsletters.")

    if request.method == "POST":
        newsletter.delete()
        return redirect("newsletter_list")

    return render(
        request, "news/newsletter_confirm_delete.html", {"newsletter": newsletter}
    )


""" # ******************** API FUNCTIONALITY ********************"""
'''
The view is for handling API requests and making a post to twitter
'''


# SUBSCRIBED ARTITICLES API VIEW
class SubscribedArticlesAPIView(ListAPIView):
    ''' API endpoint to get approved articles from
    subscribed publishers/journalists for readers
    '''

    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role != "reader":
            return Article.objects.none()

        publisher_articles = Article.objects.filter(
            approved=True, publisher__in=user.subscribed_publishers.all()
        )

        journalist_articles = Article.objects.filter(
            approved=True, journalist__in=user.subscribed_journalists.all()
        )

        return (publisher_articles | journalist_articles).distinct()


# MAKING A TWEET
def tweet_article_view(request, article_id):
    ''' API endpoint to tweet an approved article '''
    
    article = get_object_or_404(Article, id=article_id)

    if not article.approved:
        return JsonResponse(
            {"error": "Article must be approved before tweeting"},
            status=400
        )

    from .twitter import Tweet
    Tweet.tweet_article(article)

    return JsonResponse({"status": "Tweet sent successfully"})
