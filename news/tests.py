from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Article, Publisher

User = get_user_model()


class SubscribedArticlesAPITest(APITestCase):
    def setUp(self):
        # Create users
        self.reader = User.objects.create_user(
            username="reader1", password="password123", role="reader"
        )
        self.non_reader = User.objects.create_user(
            username="editor1", password="password123", role="editor"
        )
        self.journalist1 = User.objects.create_user(
            username="journalist1", password="password123", role="journalist"
        )
        self.journalist2 = User.objects.create_user(
            username="journalist2", password="password123", role="journalist"
        )

        # Create tokens
        self.reader_token = Token.objects.create(user=self.reader)
        self.non_reader_token = Token.objects.create(user=self.non_reader)

        # Create publishers
        self.publisher1 = Publisher.objects.create(name="Publisher 1")
        self.publisher2 = Publisher.objects.create(name="Publisher 2")

        # Subscribe the reader
        self.reader.subscribed_publishers.add(self.publisher1)
        self.reader.subscribed_journalists.add(self.journalist1)

        # Create articles
        self.article_pub1 = Article.objects.create(
            title="Publisher1 Article", approved=True, publisher=self.publisher1, journalist=self.journalist1
        )
        self.article_pub2 = Article.objects.create(
            title="Publisher2 Article", approved=True, publisher=self.publisher2, journalist=self.journalist2
        )
        self.article_journalist1 = Article.objects.create(
            title="Journalist1 Article", approved=True, publisher=self.publisher2, journalist=self.journalist1
        )
        self.article_journalist2 = Article.objects.create(
            title="Journalist2 Article", approved=True, publisher=self.publisher1, journalist=self.journalist2
        )
        self.article_unapproved = Article.objects.create(
            title="Unapproved Article", approved=False, publisher=self.publisher1, journalist=self.journalist1
        )

        self.url = "/api/subscribed-articles/"


    def test_reader_sees_only_subscribed_articles(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.reader_token.key}')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        titles = [article["title"] for article in response.data]

        # Articles included because of subscription (approved only)
        expected_titles = [
            self.article_pub1.title,          # Publisher1 (subscribed)
            self.article_journalist1.title,  # Journalist1 (subscribed)
            self.article_journalist2.title   # Publisher1 (subscribed)
        ]
        self.assertCountEqual(titles, expected_titles)

    def test_non_reader_sees_no_articles(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.non_reader_token.key}')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_unauthenticated_user_is_denied(self):
        self.client.credentials()  # remove any credentials
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
