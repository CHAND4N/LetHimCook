from django import forms
from .models import Restaurant, Dish, Cuisine


class RestaurantForm(forms.ModelForm):
    cuisines = forms.ModelMultipleChoiceField(
        queryset=Cuisine.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'cuisine-checkboxes'}),
        required=False,
        help_text="Select one or more cuisines"
    )

    new_cuisines = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Add new cuisines (comma separated)'}),
        label="Add New Cuisines"
    )
    
    class Meta:
        model = Restaurant
        fields = [
            'name', 'description', 'opening_time', 'closing_time',
            'iframe_location', 'image', 'cuisines', 'new_cuisines', 'featured', 'location'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Restaurant Name'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Describe your restaurant...'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'iframe_location': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Paste your embedded map iframe code here...'}),
            'image': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City or Address'}),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['cuisines'].initial = self.instance.cuisines.all()


class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ['name', 'description', 'price', 'image', 'featured']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Dish Name'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Describe the dish...'}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
            'image': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
        labels = {
            'name': 'Dish Name',
            'description': 'Description',
            'price': 'Price',
            'image': 'Dish Image',
        }
