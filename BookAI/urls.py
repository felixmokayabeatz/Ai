from django.urls import path
from .views import recommend_books  # Correct import statement

urlpatterns = [
    path('', recommend_books, name='book_recommendation'),  # Correct function name
]
