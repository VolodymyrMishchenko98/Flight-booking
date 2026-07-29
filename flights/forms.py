from django import forms

from .models import Booking


class FlightSearchForm(forms.Form):
    origin = forms.CharField(
        required=False,
        label="From",
        widget=forms.TextInput(attrs={"placeholder": "Kyiv, Warsaw or KBP"}),
    )
    destination = forms.CharField(
        required=False,
        label="To",
        widget=forms.TextInput(attrs={"placeholder": "Paris, London or CDG"}),
    )
    date = forms.DateField(
        required=False,
        label="Date",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    airline = forms.CharField(required=False, widget=forms.HiddenInput())
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ("departure", "Departure time"),
            ("price", "Lowest price"),
            ("-price", "Highest price"),
            ("seats", "Most seats"),
        ],
        initial="departure",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "airline":
                continue
            css_class = "form-select" if name == "sort" else "form-control"
            field.widget.attrs["class"] = css_class


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["full_name", "email", "seats"]
        labels = {
            "full_name": "Full name",
            "email": "Email",
            "seats": "Seats",
        }
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Passenger name"}),
            "email": forms.EmailInput(attrs={"placeholder": "name@example.com"}),
            "seats": forms.NumberInput(attrs={"min": 1}),
        }

    def clean_seats(self):
        seats = self.cleaned_data["seats"]
        if seats < 1:
            raise forms.ValidationError("Book at least one seat.")
        return seats

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
