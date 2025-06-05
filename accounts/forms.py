from django import forms
from django.utils.translation import gettext_lazy as _
from .models import CandidateProfile

class CandidateProfileForm(forms.ModelForm):
    class Meta:
        model = CandidateProfile
        # Include fields relevant for the candidate to edit
        fields = [
            "full_name",
            "cpf",
            "birth_date",
            "phone_whatsapp",
            "address_street",
            "address_number",
            "address_complement",
            "address_neighborhood",
            "address_city",
            "address_state",
            "address_zip",
            "cv_file",
            # Add other fields like education, experience if they are added to the model
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
            "cv_file": forms.ClearableFileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make CPF read-only if it shouldn't be changed after creation
        # self.fields["cpf"].widget.attrs["readonly"] = True
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.FileInput)):
                 field.widget.attrs.update({"class": "form-control"})
            elif isinstance(field.widget, forms.Select):
                 field.widget.attrs.update({"class": "form-select"})
            elif isinstance(field.widget, forms.ClearableFileInput):
                 field.widget.attrs.update({"class": "form-control"})

