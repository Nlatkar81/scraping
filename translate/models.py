from django.db import models

# Create your models here.

class ScrapedURL(models.Model):
    url = models.URLField(unique=True)

class TranslatedText(models.Model):
    scraped_url = models.ForeignKey(ScrapedURL, on_delete=models.CASCADE)
    translated_text = models.TextField()

    def __str__(self):
        return f"Translated text for {self.scraped_url.url}"
