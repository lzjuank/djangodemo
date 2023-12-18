from django.contrib import admin
from .models import NTDdata

# Register your models here.
@admin.register(NTDdata)
class NTDdataAdmin(admin.ModelAdmin):
    pass