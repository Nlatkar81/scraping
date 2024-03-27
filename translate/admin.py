from django.contrib import admin
from .models import ScrapedURL, TranslatedText

# Register your models here.
admin.site.register(ScrapedURL)
admin.site.register(TranslatedText)