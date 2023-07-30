from django import forms
from .models import ProductReview

# Product Review Add Form
class ReviewAdd(forms.ModelForm):
	class Meta:
		model = ProductReview
		fields = ['comment', 'rating']