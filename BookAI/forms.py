from django import forms

class BookRecommendationForm(forms.Form):
    title = forms.CharField(label='Title', required=False)
    author = forms.CharField(label='Author', required=False)
    publishDate = forms.IntegerField(label='Publication Year', required=False)
    description = forms.CharField(label='Description', required=False)
    cover_photo = forms.ImageField(label='Cover Photo', required=False)
