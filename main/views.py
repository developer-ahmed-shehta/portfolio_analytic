import os

from django.conf import settings
from django.http import FileResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

#This makes sure the CSRF cookie is always set when the homepage is loaded — even in incognito mode and even if you’re not using a form.
@method_decorator(ensure_csrf_cookie, name='dispatch')
class HomeView(TemplateView):
    template_name = 'portofio.html'


def download_cv(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'Ahmed Shehta CV.pdf')
    return FileResponse(open(file_path, 'rb'), as_attachment=True)



