import logging
import pandas as pd
import requests
from django.http import JsonResponse
from django.shortcuts import render
from .forms import BookRecommendationForm

#Felix Mokaya 
# Disable NLTK downloader information
nltk_logger = logging.getLogger('nltk')
nltk_logger.setLevel(logging.ERROR)

def recommend_books(request):
    if request.method == 'GET':
        # Assuming you have a form to collect user preferences
        form = BookRecommendationForm()
        return render(request, 'input_form.html', {'form': form})

    try:
        if request.method == 'POST':
            form = BookRecommendationForm(request.POST)
            if form.is_valid():
                # Handle rating separately to avoid conversion issues
                rating = form.cleaned_data['rating']
                try:
                    rating = float(rating)
                except (ValueError, TypeError):
                    rating = 0.0

                # Search for books based on the user's attributes using Open Library API
                search_url = "https://openlibrary.org/search.json"
                search_params = {
                    "title": form.cleaned_data['title'] or '',
                    "author": form.cleaned_data['author'] or '',
                    "subject": form.cleaned_data['genre'] or '',
                    "publish_date": form.cleaned_data['publishDate'] or '',
                    "first_sentence": form.cleaned_data['description'] or '',
                    "limit": 10  # Limit the number of results to 10
                }

                #print(f"Search Parameters: {search_params}")

                search_response = requests.get(search_url, params=search_params)

                #print(f"Open Library API Response: {search_response.text}")

                if search_response.status_code == 200:
                    search_data = search_response.json()
                    num_found = search_data.get("num_found", 0)
                    print(f"Number of books found: {num_found}")

                    if num_found > 0:
                        # Extract relevant information from the search results
                        books_data = search_data.get("docs", [])

                        # Prepare a list of dictionaries for rendering in the template
                        recommended_books_list = []
                        for row in books_data[:10]:  # Only take the top 10 books
                            book_info = {
                                'title': row.get('title', ''),
                                'author': row.get('author_name', ''),
                                'genres': ', '.join(row['subject'] if 'subject' in row else ''),
                                'publishDate': ', '.join(row['publish_date'] if 'publish_date' in row else ''),
                                'rating': row.get('average_rating', ''),
                                'description': row.get('first_sentence', ''),
                                'cover_i': f"https://covers.openlibrary.org/b/id/{row.get('cover_i', 0)}-L.jpg",
                                # Add more fields as needed
                            }
                            recommended_books_list.append(book_info)

                        # Add all details to the response
                        response_data = {
                            'success': True,
                            'message': 'Books found based on the given criteria',
                            'totalBooksFound': num_found,
                            'data': recommended_books_list,
                        }

                        return JsonResponse(response_data)
                    else:
                        print(f"No books found based on the given criteria.")
                        return JsonResponse({'success': True, 'message': 'No books found based on the given criteria'})
                else:
                    print(f"Error: Unable to fetch data from Open Library API. Status Code: {search_response.status_code}")
                    return JsonResponse({'success': False, 'message': 'Unable to fetch data from Open Library API'})
            else:
                print(f"Form is not valid. Errors: {form.errors}")
                return JsonResponse({'success': False, 'message': 'Form is not valid'})

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})
