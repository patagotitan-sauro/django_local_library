from django.db import models
from django.urls import reverse

from django.db.models.functions import Lower
from django.db.models import UniqueConstraint


# Create your models here.
class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""

    #Fields
    title = models.CharField(max_length=200, help_text="Enter book title")
    author = models.ForeignKey('Author', on_delete=models.RESTRICT, null= True)
    summary = models.TextField(max_length=1000, help_text="""Enter a brief
    description of the book""")
    isbn = models.CharField('ISBN',max_length=13, unique=True, help_text="""
    13 Character <a href="https://www.isbn-international.org/content/what-isbn">
    ISBN number</a>""")
    genre = models.ManyToManyField('Genre', help_text="Select a genre for this book")
    language = models.ForeignKey('Language', on_delete=models.RESTRICT, null=True)
    digital_book = None # implement an Yes/No

    #Metadata
    class Meta:
        ordering = ["title", "author"]
        #verbose_name = "BookTitle"

    #Methods
    def get_absolute_url(self):
        """Returns the URL to access a detail record for this book."""
        return reverse('book-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return self.title

class Author(models.Model):
    """Model representing a Autor """
    #Fields
    first_name = models.CharField(max_length = 100)
    last_name = models.CharField(max_length = 100)
    class Meta:
        ordering = ['-last_name', 'first_name']


    #Methods
    def __str__(self):
        return f"{self.last_name}{self.first_name}"

    def get_absolute_url(self):
        """Returns the URL to access a particular author instance."""
        return reverse('author-detail', args=[str(self.id)])


class Genre(models.Model):
    """Model representing a book genre."""
    #Fields
    name = models.CharField(max_length=200, unique=True, help_text="Enter a book genre (e.g. Science Fiction, French Poetry etc.)")
    # ver a possibilidade de criar uma lista de Genre para não variar

    #Methods
    def __str__(self):
        """String for representing the Model object."""
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a particular genre instance."""
        return reverse('genre-detail', args=[str(self.id)])
    class Meta:
        constraints = [
        UniqueConstraint(
                Lower('name'),
                name='genre_name_case_insensitive_unique',
                violation_error_message = "Genre already exists (case insensitive match)"
            ),
        ]

class Language(models.Model):
    """Model representing language"""
    #Field
    name= models.CharField(max_length = 100, unique = True)

    #Methods
    def get_absolute_url(self):
        """Returns the url to access a particular genre instance."""
        return reverse('language-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return self.name

    class Meta:
        constraints = [
        UniqueConstraint(
                Lower('name'),
                name='language_name_case_insensitive_unique',
                violation_error_message = "Language already exists (case insensitive match)"
            ),
        ]


