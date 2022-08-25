import random
from django.shortcuts import render, redirect
from django import forms
from django.urls import reverse
from django.http import HttpResponse
from markdown2 import Markdown
from . import util


# Class for editing entries:
class EditForm(forms.Form):
    text = forms.CharField(label='', widget=forms.Textarea(attrs={
        "class": 'form-control col-md-8',
        "placeholder": "Enter Page Content using Github Markdown"
    }))

# Class for creating new entries:
class CreateForm(forms.Form):
    title = forms.CharField(label='', widget=forms.TextInput(attrs={
        "class": 'form-control col-md-8',
        "placeholder": "Page Entry"
    }))
    text = forms.CharField(label='', widget=forms.Textarea(attrs={
        "class": 'form-control col-md-8',
        "placeholder": "Enter Page Content using Github Markdown"
    }))

# Class for search bar:
class SearchForm(forms.Form):
    title = forms.CharField(label='', widget=forms.TextInput(attrs={
        "class": "search",
        "placeholder": "Search wiki"
    }))

# Home page - function that displays all available entries:
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "search_form": SearchForm()
    })

# Function that loads requested title page if it exists, else displays search results:
def search(request):

    # If search page reached by submitting search form:
    if request.method == "POST":
        form = SearchForm(request.POST)

        # If form is valid try to search for title:
        if form.is_valid():
            title = form.cleaned_data["title"]
            entry_md = util.get_entry(title)
    
            print('search request: ', title)

            if entry_md:
                # If entry exists, redirect to entry view:
                return redirect(reverse('entry', args=[title]))
            else:
                # Otherwise display relevant search results:
                related_titles = util.related_titles(title)

                return render(request, "encyclopedia/search.html", {
                "title": title,
                "related_titles": related_titles,
                "search_form": SearchForm()
                })

    # Otherwise form not posted or form not valid, return to index page:
    return redirect(reverse('index'))

# Takes user to a random encyclopedia entry:
def random_title(request):

    #get list of titles, pick one at random:
    titles = util.list_entries()
    title = random.choice(titles)

    #Redirect to selected page:
    return redirect(reverse('entry', args=[title]))

# Entry page - function displays the requested entry page, if it exists:
def entry(request, title):

    entry_md = util.get_entry(title)

    if entry_md != None:
        # If entry with given title exists, function converts md to HTML and return rendered template:
        entry_HTML = Markdown().convert(entry_md)
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "entry": entry_HTML,
            "search_form": SearchForm(),
        })
    else:
        # If page does not exist, return links for similar titles:
        related_titles = util.related_titles(title)

        return render(request, "encyclopedia/error.html", {
            "title": title,
            "related_titles": related_titles,
            "search_form": SearchForm()
        })

# Lets users create a new page on the wiki:
def create(request):
    # If reached via link, display the form:
    if request.method == "GET":
        return render(request, "encyclopedia/create.html", {
            "create_form": CreateForm(),
            "search_form": SearchForm()
        })
    
    # Otherwise if reached by form submission:
    elif request.method == "POST":
        form = CreateForm(request.POST)

        # If form is valid, process the form:
        if form.is_valid():
            title = form.cleaned_data["title"]
            text = form.cleaned_data["text"]
        else:
            return render(request, "encyclopedia/create.html", {
                "create_form": form,
                "search_form": SearchForm()
            })
        
        # Check that title does not already exist:
        if util.get_entry(title):
            return render(request, "encyclopedia/create.html", {
                "create_form": form,
                "search_form": SearchForm()
            })
        
        # Otherwise save new title file to disk, take user to new page:
        else:
            util.save_entry(title, text)
            return redirect(reverse('entry', args=[title]))

    # Lets users edit an already existing page on the wiki:   
def edit(request, title):

    # If reached via editing link, return form with post to edit:
    if request.method == "GET":
        text = util.get_entry(title)

        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "edit_form": EditForm(initial={'text':text}),
            "search_form": SearchForm()
        })
    
    # If reached via posting form , updated page and redirect to page:
    elif request.method == "POST":

        form = EditForm(request.POST)

        # If clicked on submit button:
        if 'submit' in request.POST:
            if form.is_valid():
                text = form.cleaned_data['text']
                util.save_entry(title, text)
                return redirect(reverse('entry', args=[title]))

            else:
                return render(request, "encyclopedia/edit.html", {
                    "title": title,
                    "edit_form": form,
                    "search_form": SearchForm()
                })
       
        # If clicked on delete button, deletes entry from database and redirects to the Home Page:
        if 'delete' in request.POST:
            util.delete_entry(title)
            return redirect(reverse('index'))  


      