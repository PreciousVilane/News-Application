from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Article, CustomUser, Newsletter
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


@receiver(post_migrate)
def create_groups_and_permissions(sender, **kwargs):
    # Create groups
    reader_group, _ = Group.objects.get_or_create(name="reader")
    editor_group, _ = Group.objects.get_or_create(name="editor")
    journalist_group, _ = Group.objects.get_or_create(name="journalist")

    # Get content types
    article_ct = ContentType.objects.get_for_model(Article)
    newsletter_ct = ContentType.objects.get_for_model(Newsletter)

    # Get permissions
    article_perms = Permission.objects.filter(content_type=article_ct)
    newsletter_perms = Permission.objects.filter(content_type=newsletter_ct)

    # Reader: view only
    reader_group.permissions.set(
        article_perms.filter(codename__startswith="view")
        | newsletter_perms.filter(codename__startswith="view")
    )

    # Editor: everything except add
    editor_group.permissions.set(
        article_perms.exclude(codename__startswith="add")
        | newsletter_perms.exclude(codename__startswith="add")
    )

    # Journalist: full access
    journalist_group.permissions.set(
        article_perms | newsletter_perms
    )


@receiver(post_save, sender=Article)
def article_approved_signal(sender, instance, created, **kwargs):

    # Only act when approved
    if not instance.approved:
        return

    # Prevent duplicate execution
    if getattr(instance, "_signal_processed", False):
        return

    instance._signal_processed = True

    # ---- EMAIL ----
    readers_by_publisher = CustomUser.objects.filter(
        role="reader",
        subscribed_publishers=instance.publisher
    )

    readers_by_journalist = CustomUser.objects.filter(
        role="reader",
        subscribed_journalists=instance.journalist
    )

    subscribers = (readers_by_publisher | readers_by_journalist).distinct()
    email_list = [u.email for u in subscribers if u.email]

    if email_list:
        send_mail(
            subject=f"New Article Published: {instance.title}",
            message=instance.content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=email_list,
            fail_silently=True,
        )

    #  TWEET
    from .twitter import Tweet  # adjust import path if needed
    Tweet.tweet_article(instance)