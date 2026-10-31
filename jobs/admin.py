from django.contrib import admin
from .models import Job, Order


class OrderInline(admin.TabularInline):
    """
    Shows Order breakdown items inline inside the Job admin page.
    This reinforces the Job -> Order hierarchy in Django admin.
    """
    model = Order
    extra = 1
    fields = ('order_id', 'colour', 'fabric', 'quantity', 'sizes')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('job_no', 'buyer', 'order_id', 'date', 'status', 'get_total_qty', 'get_order_count')
    list_filter = ('date', 'buyer', 'status')
    search_fields = ('job_no', 'buyer', 'order_id', 'orders__fabric', 'orders__colour')
    date_hierarchy = 'date'
    inlines = [OrderInline]

    @admin.display(description="Total Pcs")
    def get_total_qty(self, obj):
        return obj.total_quantity

    @admin.display(description="Items Count")
    def get_order_count(self, obj):
        return obj.total_orders


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'job', 'order_id', 'colour', 'fabric', 'quantity', 'sizes')
    list_filter = ('fabric', 'job__buyer', 'job__date')
    search_fields = ('order_id', 'colour', 'fabric', 'sizes', 'job__job_no', 'job__buyer')
