from django import forms
from .models import Restaurant, Dish, Cuisine


class RestaurantForm(forms.ModelForm):
    cuisines = forms.ModelMultipleChoiceField(
        queryset=Cuisine.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'cuisine-checkboxes'}),
        required=False,
        help_text="Select one or more cuisines"
    )
    
    class Meta:
        model = Restaurant
        fields = ['name', 'description', 'opening_time', 'closing_time', 'iframe_location', 'image', 'cuisines']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Restaurant Name'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Describe your restaurant...'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'iframe_location': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Paste your embedded map iframe code here...'}),
            'image': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*'}),
        }
        labels = {
            'name': 'Restaurant Name',
            'description': 'Description',
            'opening_time': 'Opening Time',
            'closing_time': 'Closing Time',
            'iframe_location': 'Location (Map Embed)',
            'image': 'Restaurant Image',
            'cuisines': 'Cuisines',
        }


class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ['name', 'description', 'price', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Dish Name'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Describe the dish...'}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
            'image': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*'}),
        }
        labels = {
            'name': 'Dish Name',
            'description': 'Description',
            'price': 'Price',
            'image': 'Dish Image',
        }
