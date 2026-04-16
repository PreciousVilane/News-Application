from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Article, Publisher, Newsletter


# ************** CUSTOMERUSER  ADMIN **************
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = ("username", "email", "role", "is_staff")
    list_filter = ("role",)

    fieldsets = UserAdmin.fieldsets + (
        (
            "Role Information",
            {
                "fields": (
                    "role",
                    "subscribed_publishers",
                    "subscribed_journalists",
                    "independent_articles",
                    "independent_newsletters",
                )
            },
        ),
    )

    filter_horizontal = (
        "subscribed_publishers",
        "subscribed_journalists",
        "independent_articles",
        "independent_newsletters",
    )


# ************** ARTICLE  ADMIN **************
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "publisher", "approved", "created_at")
    list_filter = ("approved", "publisher")
    search_fields = ("title", "content")
    list_editable = ("approved",)
    actions = ["approve_articles"]

    def approve_articles(self, request, queryset):
        queryset.update(approved=True)

    approve_articles.short_description = "Approve selected articles"

    def get_readonly_fields(self, request, obj=None):
        if request.user.role != "editor":
            return ("approved",)
        return ()


# ************** PUBLISHER  ADMIN **************
@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


# ************** NEWSLETTERS  ADMIN **************
@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("title", "publisher", "created_at")
    search_fields = ("title", "content")
