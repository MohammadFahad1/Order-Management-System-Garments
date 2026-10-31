from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import datetime

from .models import Job, Order, generate_order_id
from .forms import JobForm, OrderForm


def job_list(request):
    """
    Main View: Displays the hierarchy of Jobs and their Orders.
    Supports filtering by:
      1. date (exact date)
      2. buyer (buyer name)
      3. order (order ID like 123456, matched on Job or Order Item)
    """
    # Start with all jobs, prefetching related orders for fast database queries
    jobs = Job.objects.prefetch_related('orders').all()

    # Get filter parameters from GET request
    filter_buyer = request.GET.get('buyer', '').strip()
    filter_order = request.GET.get('order', '').strip()
    filter_date = request.GET.get('date', '').strip()
    filter_status = request.GET.get('status', '').strip()

    # 1. Filter by Buyer (e.g. Zara, H&M)
    if filter_buyer:
        jobs = jobs.filter(buyer__icontains=filter_buyer)

    # 2. Filter by Order ID (e.g. 123456)
    # Checks either the main Job order_id OR the individual Order items order_id
    if filter_order:
        jobs = jobs.filter(
            Q(order_id__icontains=filter_order) | 
            Q(orders__order_id__icontains=filter_order)
        ).distinct()

    # 3. Filter by Date (e.g. 2026-10-31)
    if filter_date:
        try:
            parsed_date = datetime.strptime(filter_date, '%Y-%m-%d').date()
            jobs = jobs.filter(date=parsed_date)
        except ValueError:
            pass  # If invalid date format, ignore quietly

    # Optional status filter
    if filter_status:
        jobs = jobs.filter(status=filter_status)

    # Calculate overall summary metrics for the dashboard
    total_jobs_count = jobs.count()
    all_order_items = Order.objects.filter(job__in=jobs)
    total_quantity = all_order_items.aggregate(total=Sum('quantity'))['total'] or 0
    total_order_items_count = all_order_items.count()

    # Collect list of distinct buyers for the filter dropdown
    available_buyers = Job.objects.values_list('buyer', flat=True).distinct().order_by('buyer')

    # Check if any filter is actively applied
    has_active_filters = bool(filter_buyer or filter_order or filter_date or filter_status)

    context = {
        'jobs': jobs,
        'filter_buyer': filter_buyer,
        'filter_order': filter_order,
        'filter_date': filter_date,
        'filter_status': filter_status,
        'has_active_filters': has_active_filters,
        'available_buyers': available_buyers,
        'total_jobs_count': total_jobs_count,
        'total_quantity': total_quantity,
        'total_order_items_count': total_order_items_count,
    }
    return render(request, 'jobs/job_list.html', context)


def job_detail(request, pk):
    """
    Detailed View: View a single Job and all its nested Orders.
    Also provides a clean form with tag support to add new Order items directly.
    """
    job = get_object_or_404(Job.objects.prefetch_related('orders'), pk=pk)
    
    # Form with auto-filled parent Order ID
    order_form = OrderForm(initial={'order_id': job.order_id})

    context = {
        'job': job,
        'orders': job.orders.all(),
        'order_form': order_form,
    }
    return render(request, 'jobs/job_detail.html', context)


def job_create(request):
    """
    Create a new Job with automatically generated Order ID and interactive tags.
    Allows creating the Job along with initial order items in one clean form.
    """
    if request.method == 'POST':
        job_form = JobForm(request.POST)
        if job_form.is_valid():
            new_job = job_form.save(commit=False)
            # If user left order_id blank, automatically generate it
            if not new_job.order_id:
                new_job.order_id = generate_order_id()
            new_job.save()

            # Process dynamic order breakdown rows
            colours = request.POST.getlist('item_colour[]')
            fabrics = request.POST.getlist('item_fabric[]')
            quantities = request.POST.getlist('item_quantity[]')
            sizes = request.POST.getlist('item_sizes[]')
            sub_order_ids = request.POST.getlist('item_order_id[]')

            # Loop through rows and create Order items
            for i in range(len(fabrics)):
                fabric_val = fabrics[i].strip() if i < len(fabrics) else ''
                colour_val = colours[i].strip() if i < len(colours) else ''
                qty_raw = quantities[i].strip() if i < len(quantities) else '0'
                sizes_val = sizes[i].strip() if i < len(sizes) else ''
                sub_id_val = sub_order_ids[i].strip() if i < len(sub_order_ids) else new_job.order_id

                if fabric_val or colour_val or sizes_val:
                    try:
                        qty_val = int(qty_raw) if qty_raw else 1
                    except ValueError:
                        qty_val = 1
                    Order.objects.create(
                        job=new_job,
                        order_id=sub_id_val or new_job.order_id,
                        fabric=fabric_val or "Single Jersey",
                        colour=colour_val or "Standard",
                        quantity=max(1, qty_val),
                        sizes=sizes_val or "S, M, L"
                    )

            messages.success(request, f"Job '{new_job.job_no}' created with Order #{new_job.order_id}!")
            return redirect('jobs:job_detail', pk=new_job.pk)
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        # Generate default suggested Job number and auto Order ID
        last_job = Job.objects.order_by('-id').first()
        next_job_no = f"JOB-{1001 + (last_job.id if last_job else 0)}"
        auto_order_id = generate_order_id()

        job_form = JobForm(initial={
            'job_no': next_job_no,
            'order_id': auto_order_id,
            'date': timezone.now().date(),
            'status': 'In Production'
        })

    context = {
        'job_form': job_form,
        'title': 'Create New Job',
    }
    return render(request, 'jobs/job_form.html', context)


def job_edit(request, pk):
    """
    Edit an existing Job.
    """
    job = get_object_or_404(Job, pk=pk)

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            updated_job = form.save(commit=False)
            if not updated_job.order_id:
                updated_job.order_id = generate_order_id()
            updated_job.save()
            messages.success(request, f"Job '{job.job_no}' updated successfully!")
            return redirect('jobs:job_detail', pk=job.pk)
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = JobForm(instance=job)

    context = {
        'job_form': form,
        'job': job,
        'title': f"Edit Job {job.job_no}",
    }
    return render(request, 'jobs/job_form.html', context)


def job_delete(request, pk):
    """
    Delete a Job and all its associated Orders.
    """
    job = get_object_or_404(Job, pk=pk)

    if request.method == 'POST':
        job_no = job.job_no
        job.delete()
        messages.success(request, f"Job '{job_no}' and its order items were deleted.")
        return redirect('jobs:job_list')

    context = {
        'job': job,
    }
    return render(request, 'jobs/job_confirm_delete.html', context)


def order_create(request, job_pk):
    """
    Add a new Order item to an existing Job.
    """
    job = get_object_or_404(Job, pk=job_pk)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.job = job
            # Automatically assign Job's order_id if blank
            if not order.order_id:
                order.order_id = job.order_id
            order.save()
            messages.success(request, f"Added order item ({order.colour} - {order.fabric}) to Job {job.job_no}.")
            return redirect('jobs:job_detail', pk=job.pk)
        else:
            messages.error(request, "Could not add order item. Please check the fields.")
    else:
        form = OrderForm(initial={'order_id': job.order_id})

    context = {
        'form': form,
        'job': job,
        'title': f"Add Order Item to Job {job.job_no}",
    }
    return render(request, 'jobs/order_form.html', context)


def order_edit(request, pk):
    """
    Edit an individual Order item.
    """
    order = get_object_or_404(Order, pk=pk)
    job = order.job

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            updated_order = form.save(commit=False)
            if not updated_order.order_id:
                updated_order.order_id = job.order_id
            updated_order.save()
            messages.success(request, "Order item updated successfully.")
            return redirect('jobs:job_detail', pk=job.pk)
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = OrderForm(instance=order)

    context = {
        'form': form,
        'job': job,
        'order': order,
        'title': f"Edit Order Item #{order.id}",
    }
    return render(request, 'jobs/order_form.html', context)


def order_delete(request, pk):
    """
    Delete an individual Order item.
    """
    order = get_object_or_404(Order, pk=pk)
    job_pk = order.job.pk

    if request.method == 'POST':
        order.delete()
        messages.success(request, "Order item removed.")
        return redirect('jobs:job_detail', pk=job_pk)

    context = {
        'order': order,
        'job': order.job,
    }
    return render(request, 'jobs/order_confirm_delete.html', context)


def seed_data(request):
    """
    Convenient helper view to seed sample apparel jobs & order items.
    """
    from jobs.management.commands.seed_data import Command
    cmd = Command()
    cmd.handle()
    messages.success(request, "Sample jobs with realistic orders populated successfully!")
    return redirect('jobs:job_list')
