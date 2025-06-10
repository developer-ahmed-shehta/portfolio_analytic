import json
import os

from django.conf import settings
from django.http import FileResponse
from django.views.generic import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.utils.decorators import method_decorator

from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.http import require_POST

#This makes sure the CSRF cookie is always set when the homepage is loaded — even in incognito mode and even if you’re not using a form.
@method_decorator(ensure_csrf_cookie, name='dispatch')
class HomeView(TemplateView):
    template_name = 'portofio.html'


def download_cv(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'Ahmed Shehta CV.pdf')
    return FileResponse(open(file_path, 'rb'), as_attachment=True)



@csrf_exempt  # Only for development - use proper CSRF protection in production
def send_message(request):
    if request.method == 'POST':
        try:
            form_data = json.loads(request.body.decode('utf-8'))
            name = form_data.get('name', '')
            message = form_data.get('message', '')

            send_mail(
                f'New message from {name}',
                message,
                'ahmedshehta0123@gmail.com',  # From email
                ['ahmedshehta0123@gmail.com'],  # To email
                fail_silently=False,
            )

            return JsonResponse({'status': 'success', 'message': 'Message sent successfully!'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)