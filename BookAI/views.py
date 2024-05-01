import logging
import requests
from django.http import JsonResponse
from django.shortcuts import render
from .forms import BookRecommendationForm

# Disable NLTK downloader information
nltk_logger = logging.getLogger('nltk')
nltk_logger.setLevel(logging.ERROR)

def recommend_books(request):
    try:
        if request.method == 'POST':
            form = BookRecommendationForm(request.POST)
            if form.is_valid():
                rating = float(form.cleaned_data.get('rating', 0.0))
                search_params = {
                    'title': form.cleaned_data.get('title', ''),
                    'author': form.cleaned_data.get('author', ''),
                    'subject': form.cleaned_data.get('genre', ''),
                    'publish_date': form.cleaned_data.get('publishDate', ''),
                    'first_sentence': form.cleaned_data.get('description', ''),
                    'limit': 10
                }
                search_response = requests.get('https://openlibrary.org/search.json', params=search_params)
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    num_found = search_data.get('num_found', 0)
                    if num_found > 0:
                        books_data = search_data.get('docs', [])[:10]
                        recommended_books_list = []
                        for book in books_data:
                            book_info = {
                                'title': book.get('title', ''),
                                'author': book.get('author_name', ''),
                                # 'genres': ', '.join(book.get('subject', [])),
                                'publishDate': ', '.join(book.get('publish_date', [])),
                                # 'rating': book.get('average_rating', ''),
                                'description': book.get('first_sentence', ''),
                                'cover_i': f"https://covers.openlibrary.org/b/id/{book.get('cover_i', 0)}-L.jpg",
                            }
                            recommended_books_list.append(book_info)
                        return JsonResponse({
                            'success': True,
                            'message': 'Books found based on the given criteria',
                            'totalBooksFound': num_found,
                            'data': recommended_books_list,
                        })
                    else:
                        return JsonResponse({'success': True, 'message': 'No books found based on the given criteria'})
                else:
                    return JsonResponse({'success': False, 'message': f'Unable to fetch data from Open Library API. Status Code: {search_response.status_code}'})
            else:
                return JsonResponse({'success': False, 'message': 'Form is not valid', 'errors': form.errors})
        else:
            form = BookRecommendationForm()
            return render(request, 'input_form.html', {'form': form})
    except Exception as e:
        logging.error(f'An error occurred: {e}')
        return JsonResponse({'success': False, 'error': str(e)})
