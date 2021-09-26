from django.contrib import admin
from core.models import *
# Register your models here.

admin.site.register(customer)
admin.site.register(category)
admin.site.register(product)
admin.site.register(orderitem)
admin.site.register(order)
admin.site.register(CheckoutAddress)