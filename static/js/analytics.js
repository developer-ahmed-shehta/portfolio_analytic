// Track page views
document.addEventListener('DOMContentLoaded', function() {
    // Send pageview to your analytics endpoint
    fetch('/analytics/track-pageview/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            url: window.location.href,
            referrer: document.referrer
        })
    });

    // Track clicks on important elements
    document.querySelectorAll('[data-track]').forEach(element => {
        element.addEventListener('click', function() {
            const eventType = this.getAttribute('data-track');
            trackEvent(eventType, this.textContent.trim());
        });
    });

    // Track form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            trackEvent('form_submit', form.id || 'contact_form');
        });
    });
});

function trackEvent(eventType, elementText = '') {
    fetch('/analytics/track-event/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            event_type: eventType,
            element_text: elementText.substring(0, 100),
            page_url: window.location.href
        })
    });
}
