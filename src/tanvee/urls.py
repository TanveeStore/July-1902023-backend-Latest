"""tanvee URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
#from django.conf.urls.static import static
from django.conf import settings


# Dajngo Admin Customization
admin.site.site_title = "Tanvee Mobile Admin"
admin.site.site_header = "Tanvee Admin Site"
admin.site.index_title = "Tanvee Mobile Admin"


from django.shortcuts import render
def websiteHomeView(request):
    context ={}
    return render(request, "index.html", context)
def websitePrivacyPolicyView(request):
    context ={}
    return render(request, "privacy-policy.html", context)
def websiteTermsConditionsView(request):
    context ={}
    return render(request, "terms-conditions.html", context)
def websiteReturnCancellationPolicyView(request):
    context ={}
    return render(request, "return-cancellation-policy.html", context)


urlpatterns = [
    path("", websiteHomeView),
    path("privacy-policy/", websitePrivacyPolicyView),
    path("terms-conditions/", websiteTermsConditionsView),
    path("return-cancellation-policy/", websiteReturnCancellationPolicyView),
    path('admin/', admin.site.urls),
    path("api/", include("common.app_urls", namespace="common_urls")),
]

  # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  # + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)