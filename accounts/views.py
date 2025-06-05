from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import CandidateProfile
from .forms import CandidateProfileForm
from notifications.models import Notification # For displaying notifications

@login_required
def my_applications(request):
    # Ensure candidate profile exists, create if not (basic structure)
    # In a real app, profile creation might be a separate step after registration
    candidate_profile, created = CandidateProfile.objects.get_or_create(user=request.user)

    applications = candidate_profile.applications.select_related(
        "job_vacancy", "job_vacancy__hospital_unit"
    ).order_by("-application_date")

    context = {"applications": applications}
    return render(request, "accounts/my_applications.html", context)

@login_required
def profile_view(request):
    candidate_profile = get_object_or_404(CandidateProfile, user=request.user)
    context = {
        "profile": candidate_profile
    }
    return render(request, "accounts/profile_view.html", context)

@login_required
def profile_edit(request):
    candidate_profile, created = CandidateProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = CandidateProfileForm(request.POST, request.FILES, instance=candidate_profile)
        if form.is_valid():
            form.save()
            messages.success(request, _("Perfil atualizado com sucesso!"))
            return redirect("accounts:profile_view")
        else:
            messages.error(request, _("Erro ao atualizar o perfil. Verifique os dados."))
    else:
        form = CandidateProfileForm(instance=candidate_profile)

    context = {
        "form": form
    }
    return render(request, "accounts/profile_edit.html", context)

# Add views for registration, login, logout if not using django.contrib.auth.urls

