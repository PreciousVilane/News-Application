from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.contrib.auth.models import AbstractUser, Group

'''
The model is for handling user roles
'''


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("reader", "Reader"),
        ("journalist", "Journalist"),
        ("editor", "Editor"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Reader-specific fields
    subscribed_publishers = models.ManyToManyField(
        "Publisher", blank=True, related_name="subscribed_readers"
    )
    subscribed_journalists = models.ManyToManyField(
        "self", blank=True, symmetrical=False, related_name="subscribers"
    )

    # Journalist-specific fields
    independent_articles = models.ManyToManyField(
        "Article", blank=True, related_name="owning_journalists"
    )
    independent_newsletters = models.ManyToManyField(
        "Newsletter", blank=True, related_name="owning_journalists"
    )

    def save(self, *args, **kwargs):
        # Save the user first
        super().save(*args, **kwargs)

        # Auto-assign group based on role
        group_name = self.role.capitalize()  # 'reader' to 'Reader'
        try:
            group = Group.objects.get(name=group_name)
            self.groups.clear()  # remove previous groups
            self.groups.add(group)
        except Group.DoesNotExist:
            pass  # group may not exist yet (e.g., before migrations)

        # Enforce role separation
        if self.role == "reader":
            self.independent_articles.clear()
            self.independent_newsletters.clear()

        elif self.role == "journalist":
            self.subscribed_publishers.clear()
            self.subscribed_journalists.clear()


'''
The model is for handling publisher name
'''


# PUBLISHER MODEL
class Publisher(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


'''
The model is for handling articles data
'''


# ARTICLE MODEL
class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    approved = models.BooleanField(default=False)
    publisher = models.ForeignKey(
        Publisher, on_delete=models.CASCADE, related_name="articles"
    )
    journalist = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="journalist_articles"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

'''
The model is for handling newsletter data
'''


# NEWSLETTERS MODEL
class Newsletter(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    publisher = models.ForeignKey(
        Publisher, on_delete=models.CASCADE, related_name="newsletters"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
