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
                search_params = {}
                title = form.cleaned_data.get('title')
                if title:
                    search_params['title'] = title
                author = form.cleaned_data.get('author')
                if author:
                    search_params['author'] = author
                publish_date = form.cleaned_data.get('publishDate')
                if publish_date:
                    search_params['publish_date'] = publish_date
                description = form.cleaned_data.get('description')
                if description:
                    search_params['first_sentence'] = description
                search_params['limit'] = 10
                
                # Check if any search parameters were provided
                if search_params:
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
                                    'publishDate': ', '.join(book.get('publish_date', [])),
                                    'description': book.get('first_sentence', ''),
                                    'link': f"https://openlibrary.org{book.get('key', '')}",
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
                        return JsonResponse({'success': False, 'message': f'Unable to fetch data from Open Library API.'})
                else:
                    return JsonResponse({'success': True, 'message': 'No search parameters provided.'})
            else:
                return JsonResponse({'success': False, 'message': 'Form is not valid.'})
        else:
            form = BookRecommendationForm()
            return render(request, 'input_form.html', {'form': form})
    except Exception as e:
        logging.error(f'An error occurred: {e}')
        return JsonResponse({'success': False})
