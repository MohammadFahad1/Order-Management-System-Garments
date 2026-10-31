from django.core.management.base import BaseCommand
from django.utils import timezone
from jobs.models import Job, Order


class Command(BaseCommand):
    help = 'Seeds realistic sample apparel manufacturing jobs and orders.'

    def handle(self, *args, **options):
        sample_jobs = [
            {
                'job_no': 'JOB-1001',
                'buyer': 'Zara Man',
                'order_id': '123456',
                'date': timezone.now().date(),
                'status': 'In Production',
                'remarks': 'Summer Collection - Soft silicone wash required.',
                'items': [
                    {'colour': 'Navy Blue', 'fabric': 'Lycra Single Jersey', 'quantity': 1200, 'sizes': 'S, M, L, XL'},
                    {'colour': 'Black', 'fabric': 'Lycra Single Jersey', 'quantity': 800, 'sizes': 'M, L, XL, XXL'},
                    {'colour': 'White', 'fabric': '100% Cotton Pique', 'quantity': 1500, 'sizes': 'S, M, L, XL'},
                ]
            },
            {
                'job_no': 'JOB-1002',
                'buyer': 'H&M Basic',
                'order_id': '789012',
                'date': timezone.now().date(),
                'status': 'In Production',
                'remarks': 'Export to Sweden. Strict barcode label inspection.',
                'items': [
                    {'colour': 'Melange Grey', 'fabric': 'French Terry 260 GSM', 'quantity': 2400, 'sizes': 'XS, S, M, L, XL'},
                    {'colour': 'Olive Green', 'fabric': 'Lycra Single Jersey', 'quantity': 1100, 'sizes': 'S, M, L, XL'},
                ]
            },
            {
                'job_no': 'JOB-1003',
                'buyer': 'Marks & Spencer',
                'order_id': '345678',
                'date': timezone.now().date(),
                'status': 'Completed',
                'remarks': 'Autumn Polo shirts. Pre-shrunk fabric required.',
                'items': [
                    {'colour': 'Burgundy', 'fabric': 'Cotton Pique 220 GSM', 'quantity': 1800, 'sizes': 'S, M, L, XL, XXL'},
                    {'colour': 'Charcoal', 'fabric': '2x2 Lycra Rib', 'quantity': 950, 'sizes': 'M, L, XL'},
                ]
            },
            {
                'job_no': 'JOB-1004',
                'buyer': 'Nike Athletic',
                'order_id': '901234',
                'date': timezone.now().date(),
                'status': 'Pending',
                'remarks': 'Dri-FIT moisture wicking test report needed.',
                'items': [
                    {'colour': 'Anthracite', 'fabric': 'Polyester Spandex Interlock', 'quantity': 3200, 'sizes': 'S, M, L, XL'},
                    {'colour': 'Volt Lime', 'fabric': 'Micro Mesh 140 GSM', 'quantity': 1600, 'sizes': 'M, L, XL'},
                ]
            },
        ]

        created_count = 0
        for j_data in sample_jobs:
            job, created = Job.objects.get_or_create(
                job_no=j_data['job_no'],
                defaults={
                    'buyer': j_data['buyer'],
                    'order_id': j_data['order_id'],
                    'date': j_data['date'],
                    'status': j_data['status'],
                    'remarks': j_data['remarks'],
                }
            )
            if created:
                created_count += 1
                for item in j_data['items']:
                    Order.objects.create(
                        job=job,
                        order_id=job.order_id,
                        colour=item['colour'],
                        fabric=item['fabric'],
                        quantity=item['quantity'],
                        sizes=item['sizes']
                    )

        self.stdout.write(self.style.SUCCESS(f'Successfully populated {created_count} sample jobs!'))

