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


from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email', '')
        message = request.POST.get('message')

        # Basic validation
        if not name or not message:
            messages.error(request, 'Name and message are required fields.')
            return redirect('contact')  # Assuming 'contact' is your URL name

        try:
            # Send email
            send_mail(
                subject=f'New contact from {name}',
                message=f"From: {name}\nEmail: {email}\n\nMessage:\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=False,
            )

            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('contact')

    return render(request, 'contact.html')