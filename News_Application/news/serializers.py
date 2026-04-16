from rest_framework import serializers
from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    publisher = serializers.StringRelatedField()
    journalist = serializers.StringRelatedField()

    class Meta:
        model = Article
        fields = ["id", "title", "content", "publisher", "journalist", "approved", "created_at",
        ]
