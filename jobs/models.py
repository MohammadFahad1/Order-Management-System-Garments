from django.db import models
from django.utils import timezone


def generate_order_id():
    """
    Generate an automatic 6-digit numeric Order ID (e.g. 100001, 100002, 123457).
    Finds the highest existing numeric order ID in Job and Order, and increments by 1.
    """
    start_id = 100001
    max_numeric_id = 0

    # Search through Job order_ids
    for val in Job.objects.values_list('order_id', flat=True):
        if val and val.isdigit():
            num = int(val)
            if num > max_numeric_id:
                max_numeric_id = num

    # Search through Order order_ids
    for val in Order.objects.values_list('order_id', flat=True):
        if val and val.isdigit():
            num = int(val)
            if num > max_numeric_id:
                max_numeric_id = num

    if max_numeric_id >= 100000:
        return str(max_numeric_id + 1)
    elif max_numeric_id > 0:
        return str(max_numeric_id + 1).zfill(6)
    else:
        return str(start_id)


class Job(models.Model):
    """
    Job is at the top of the hierarchy.
    Contains:
      - job_no: A unique identifier for the job (e.g. JOB-1001)
      - buyer: Name of the client/buyer (e.g. Zara, H&M, Nike)
      - order_id: Automatically generated 6-digit order reference number (e.g. 100001)
      - date: Date of the order / job issue
      - status: Current stage (Pending, In Production, Completed, Delivered)
    """

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Production', 'In Production'),
        ('Completed', 'Completed'),
        ('Delivered', 'Delivered'),
    ]

    job_no = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Job Number",
        help_text="Unique job number, e.g. JOB-1001"
    )
    buyer = models.CharField(
        max_length=120,
        verbose_name="Buyer",
        help_text="Name of the buyer/brand, e.g. Zara, H&M"
    )
    order_id = models.CharField(
        max_length=100,
        blank=True,
        default=generate_order_id,
        verbose_name="Order ID",
        help_text="Automatically generated order number, e.g. 100001"
    )
    date = models.DateField(
        default=timezone.now,
        verbose_name="Order Date"
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='In Production',
        verbose_name="Status"
    )
    remarks = models.TextField(
        blank=True,
        null=True,
        verbose_name="Remarks / Notes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = "Job"
        verbose_name_plural = "Jobs"

    def save(self, *args, **kwargs):
        # Ensure order_id is automatically generated if left empty
        if not self.order_id:
            self.order_id = generate_order_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.job_no} | Order #{self.order_id} - {self.buyer}"

    @property
    def total_quantity(self):
        """Calculate total quantity of all orders/items inside this job."""
        return sum(order.quantity for order in self.orders.all())

    @property
    def total_orders(self):
        """Count the number of order items inside this job."""
        return self.orders.count()


class Order(models.Model):
    """
    Each Order belongs to a Job in the hierarchy.
    It contains:
      - colour: Color tags of the garment (e.g. Navy Blue, Black)
      - fabric: Fabric specification (e.g. Lycra single jersey)
      - quantity: Number of pieces ordered (e.g. 500)
      - sizes: Size tags breakdown (e.g. S, M, L, XL)
      - order_id: Automatically inherits Job's order ID if left blank
    """

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Job"
    )
    order_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Order ID",
        help_text="Defaults to parent Job Order ID automatically"
    )
    fabric = models.CharField(
        max_length=150,
        verbose_name="Fabric",
        help_text="e.g. Lycra Single Jersey, 100% Cotton Pique, French Terry"
    )
    colour = models.CharField(
        max_length=200,
        verbose_name="Colour",
        help_text="Comma-separated or tag list of colours (e.g. Navy Blue, Black)"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Quantity (Pieces)",
        help_text="Total pieces for this breakdown"
    )
    sizes = models.CharField(
        max_length=200,
        verbose_name="Sizes",
        help_text="Comma-separated or tag list of sizes (e.g. S, M, L, XL)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def save(self, *args, **kwargs):
        # If order_id is not specified for this item, automatically inherit the Job's order_id
        if not self.order_id and self.job_id:
            self.order_id = self.job.order_id or generate_order_id()
        super().save(*args, **kwargs)

    @property
    def colour_list(self):
        """Returns colours as a clean list of tags for badges/chips."""
        if not self.colour:
            return []
        return [c.strip() for c in self.colour.split(',') if c.strip()]

    @property
    def size_list(self):
        """Returns sizes as a clean list of tags for badges/chips."""
        if not self.sizes:
            return []
        return [s.strip() for s in self.sizes.split(',') if s.strip()]

    def __str__(self):
        effective_id = self.order_id or (self.job.order_id if self.job else "")
        return f"Order #{effective_id}: {self.colour} - {self.fabric} ({self.quantity} pcs)"
