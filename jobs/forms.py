from django import forms
from .models import Job, Order, generate_order_id


class JobForm(forms.ModelForm):
    """
    Form for creating and editing a Job.
    Order ID is automatically generated but can be customized if needed.
    """
    order_id = forms.CharField(
        required=False,
        help_text="Automatically generated if left blank",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-800 focus:border-transparent text-slate-800 placeholder-slate-400 bg-white text-sm',
            'placeholder': 'Auto-generated (e.g. 100001)'
        })
    )

    class Meta:
        model = Job
        fields = ['job_no', 'buyer', 'order_id', 'date', 'status', 'remarks']
        widgets = {
            'job_no': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-800 focus:border-transparent text-slate-800 placeholder-slate-400 bg-white text-sm',
                'placeholder': 'e.g. JOB-1001'
            }),
            'buyer': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-800 focus:border-transparent text-slate-800 placeholder-slate-400 bg-white text-sm',
                'placeholder': 'e.g. Zara, H&M, Levi\'s'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-800 focus:border-transparent text-slate-800 bg-white text-sm'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-800 focus:border-transparent text-slate-800 bg-white text-sm'
            }),
            'remarks': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-800 focus:border-transparent text-slate-800 placeholder-slate-400 bg-white text-sm',
                'placeholder': 'Optional notes, garment style number, or customer instructions...'
            }),
        }


class OrderForm(forms.ModelForm):
    """
    Form for adding or editing an Order item inside a Job.
    Colour and Sizes support tag-like entry (comma-separated or chips).
    """
    order_id = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-800 focus:border-transparent text-slate-800 placeholder-slate-400 bg-white text-sm',
            'placeholder': 'Auto-assigned from Job if blank'
        })
    )

    class Meta:
        model = Order
        fields = ['order_id', 'colour', 'fabric', 'quantity', 'sizes']
        widgets = {
            'colour': forms.HiddenInput(),
            'sizes': forms.HiddenInput(),
            'fabric': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-800 focus:border-transparent text-slate-800 placeholder-slate-400 bg-white text-sm',
                'placeholder': 'e.g. Lycra single jersey, 100% Cotton Pique'
            }),
            'quantity': forms.NumberInput(attrs={
                'min': '1',
                'class': 'w-full px-4 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-800 focus:border-transparent text-slate-800 placeholder-slate-400 bg-white text-sm',
                'placeholder': 'e.g. 500'
            }),
        }
