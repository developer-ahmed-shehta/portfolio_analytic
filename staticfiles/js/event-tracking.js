document.addEventListener('DOMContentLoaded', function () {
    document.body.addEventListener('click', function (e) {
        const element = e.target.closest('[data-track-event]');
        if (element) {
            const eventType = element.getAttribute('data-track-event');
            const elementId = element.id || null;
            const elementClass = element.classList ? [...element.classList].join(' ') : element.className;
            const elementText = element.textContent?.trim().substring(0, 100) || null;
            const metadata = {
                href: element.href || null,
            };

            // Delay if CSRF not yet set
            if (!getCookie('csrftoken')) {
                setTimeout(() => {
                    if (getCookie('csrftoken')) {
                        trackEvent(eventType, elementId, elementClass, elementText, metadata);
                    } else {
                        console.warn('CSRF token not available; event not tracked.');
                    }
                }, 300);
            } else {
                trackEvent(eventType, elementId, elementClass, elementText, metadata);
            }
        }
    });
});


function trackEvent(eventType, elementId, elementClass, elementText, metadata) {
    fetch('/analytics/track-event/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            event_type: eventType,
            page_url: window.location.href,
            elementId: elementId,
            elementClass: elementClass,
            elementText: elementText,
            metadata: metadata
        })
    }).catch(error => console.error('Error tracking event:', error));
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

