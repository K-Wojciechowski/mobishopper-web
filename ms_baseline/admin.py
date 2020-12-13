"""Django admin views for ms_baseline."""
from django.contrib import admin

from ms_baseline.models import MsUser

admin.site.register(MsUser)
