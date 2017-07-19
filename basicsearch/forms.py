from django import forms


class SearchForm(forms.Form):
    search_term = forms.CharField(label="search_term", max_length=50)
