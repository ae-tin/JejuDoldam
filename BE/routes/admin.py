from django.contrib import admin
from .models import Route, RouteDay, RoutePlace

# Register your models here.
admin.site.register(Route)
admin.site.register(RouteDay)
admin.site.register(RoutePlace)