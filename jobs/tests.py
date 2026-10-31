from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from .models import Job, Order, generate_order_id


class JobOrderModelTest(TestCase):
    def setUp(self):
        # Create Job with explicit order_id
        self.job = Job.objects.create(
            job_no='JOB-2001',
            buyer='Zara',
            order_id='123456',
            date=timezone.now().date(),
            status='In Production'
        )
        self.order1 = Order.objects.create(
            job=self.job,
            colour='Navy Blue, Black',
            fabric='Lycra single jersey',
            quantity=500,
            sizes='S, M, L, XL'
        )
        self.order2 = Order.objects.create(
            job=self.job,
            colour='White',
            fabric='100% Cotton Pique',
            quantity=300,
            sizes='M, L'
        )

    def test_job_hierarchy_and_totals(self):
        """Test Job relationship to Orders and aggregate properties."""
        self.assertEqual(self.job.orders.count(), 2)
        self.assertEqual(self.job.total_quantity, 800)
        self.assertEqual(self.job.total_orders, 2)

    def test_order_id_inheritance(self):
        """Test that Order automatically inherits parent Job order_id if blank."""
        self.assertEqual(self.order1.order_id, '123456')
        self.assertEqual(self.order2.order_id, '123456')

    def test_auto_generate_order_id_when_blank(self):
        """Test that Job generates an automatic order ID if not provided."""
        auto_job = Job.objects.create(
            job_no='JOB-AUTO-01',
            buyer='H&M',
            order_id='',  # left blank
            date=timezone.now().date()
        )
        self.assertTrue(bool(auto_job.order_id))
        self.assertTrue(auto_job.order_id.isdigit())
        self.assertEqual(len(auto_job.order_id), 6)

    def test_colour_and_size_tag_properties(self):
        """Test that comma-separated colours and sizes are returned as clean tag lists."""
        self.assertEqual(self.order1.colour_list, ['Navy Blue', 'Black'])
        self.assertEqual(self.order1.size_list, ['S', 'M', 'L', 'XL'])
        self.assertEqual(self.order2.colour_list, ['White'])
        self.assertEqual(self.order2.size_list, ['M', 'L'])


class JobViewsAndFilteringTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.today = timezone.now().date()
        self.yesterday = self.today - timedelta(days=1)

        # Job 1: Zara, Order 123456, Today
        self.job1 = Job.objects.create(
            job_no='JOB-101',
            buyer='Zara',
            order_id='123456',
            date=self.today,
            status='In Production'
        )
        Order.objects.create(
            job=self.job1,
            colour='Navy Blue',
            fabric='Lycra single jersey',
            quantity=600,
            sizes='S, M, L'
        )

        # Job 2: H&M, Order 789012, Yesterday
        self.job2 = Job.objects.create(
            job_no='JOB-102',
            buyer='H&M',
            order_id='789012',
            date=self.yesterday,
            status='Completed'
        )
        Order.objects.create(
            job=self.job2,
            colour='Heather Grey',
            fabric='French Terry',
            quantity=400,
            sizes='M, L, XL'
        )

    def test_job_list_view_renders(self):
        response = self.client.get(reverse('jobs:job_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'JOB-101')
        self.assertContains(response, 'JOB-102')
        self.assertContains(response, 'Lycra single jersey')

    def test_filter_by_buyer(self):
        response = self.client.get(reverse('jobs:job_list'), {'buyer': 'Zara'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'JOB-101')
        self.assertNotContains(response, 'JOB-102')

    def test_filter_by_order(self):
        response = self.client.get(reverse('jobs:job_list'), {'order': '123456'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'JOB-101')
        self.assertNotContains(response, 'JOB-102')

    def test_filter_by_date(self):
        response = self.client.get(reverse('jobs:job_list'), {'date': self.today.strftime('%Y-%m-%d')})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'JOB-101')
        self.assertNotContains(response, 'JOB-102')

    def test_job_create_view_with_auto_order_id_and_tags(self):
        post_data = {
            'job_no': 'JOB-999',
            'buyer': 'Uniqlo',
            'order_id': '',  # left blank to test auto-generation
            'date': self.today.strftime('%Y-%m-%d'),
            'status': 'In Production',
            'item_colour[]': ['Olive Green, Black'],
            'item_fabric[]': ['Lycra single jersey'],
            'item_quantity[]': ['1000'],
            'item_sizes[]': ['S, M, L, XL'],
            'item_order_id[]': [''],
        }
        response = self.client.post(reverse('jobs:job_create'), post_data)
        self.assertEqual(response.status_code, 302)
        new_job = Job.objects.get(job_no='JOB-999')
        self.assertEqual(new_job.buyer, 'Uniqlo')
        self.assertTrue(bool(new_job.order_id))
        self.assertEqual(new_job.total_quantity, 1000)
        
        created_order = new_job.orders.first()
        self.assertEqual(created_order.fabric, 'Lycra single jersey')
        self.assertEqual(created_order.colour_list, ['Olive Green', 'Black'])
        self.assertEqual(created_order.size_list, ['S', 'M', 'L', 'XL'])
        # Order should inherit the Job's auto-generated order_id
        self.assertEqual(created_order.order_id, new_job.order_id)
