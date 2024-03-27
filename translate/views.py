from django.shortcuts import render
from .models import ScrapedURL, TranslatedText
import requests
from bs4 import BeautifulSoup
from googletrans import Translator

def scrape_and_save(request):
    if request.method == 'POST':
        url = request.POST.get('url')

        if not url:
            error_message = 'URL is required.'
            return render(request, 'result.html', {'error_message': error_message})

        try:
            response = requests.get(url)
            response.raise_for_status()  

            content_type = response.headers.get('content-type', '')
            if 'text/html' not in content_type:
                error_message = 'The content of the provided URL is not HTML and cannot be scraped.'
                return render(request, 'result.html', {'error_message': error_message})

            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text()

            translator = Translator()
            translated_text = translator.translate(text_content, src='mr', dest='en').text

            scraped_url_obj, created = ScrapedURL.objects.get_or_create(url=url) 

            translated_text_obj = TranslatedText.objects.create(scraped_url=scraped_url_obj, translated_text=translated_text)

            return render(request, 'result.html', {'url': url, 'scraped_text': text_content, 'translated_text': translated_text})
        
        except requests.RequestException as e:
            error_message = f'Failed to fetch data from the website: {str(e)}'
            return render(request, 'result.html', {'error_message': error_message})
        
        except Exception as e:
            error_message = f'An error occurred: {str(e)}'
            return render(request, 'result.html', {'error_message': error_message})

    return render(request, 'scrape_form.html')



from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph
from .models import TranslatedText

def download_translated_text(request):
    translated_texts = TranslatedText.objects.all()

    if request.method == 'POST':
        selected_text_id = request.POST.get('selected_text_id')

        if selected_text_id:
            try:
                selected_text = TranslatedText.objects.get(pk=selected_text_id)
                
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="translated_text.pdf"'

                pdf = SimpleDocTemplate(response, pagesize=letter)
                styles = getSampleStyleSheet()
                normal_style = styles['Normal']

                content = []

                content.append(Paragraph("Translated Text", styles['Title']))

                paragraphs = selected_text.translated_text.split('\n')
                for paragraph in paragraphs:
                    content.append(Paragraph(paragraph.strip(), normal_style))

                pdf.build(content)

                return response
            except TranslatedText.DoesNotExist:
                error_message = 'Selected translated text does not exist.'
        else:
            error_message = 'Please select a translated text.'

        return render(request, 'select_translated_text.html', {'translated_texts': translated_texts, 'error_message': error_message})

    return render(request, 'select_translated_text.html', {'translated_texts': translated_texts})




