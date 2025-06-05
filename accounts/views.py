from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import CandidateProfile
from .forms import CandidateProfileForm
from notifications.models import Notification # For displaying notifications

@login_required
def my_applications(request):
    try:
        # Ensure candidate profile exists, create if not (basic structure)
        # In a real app, profile creation might be a separate step after registration
        candidate_profile, created = CandidateProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'full_name': request.user.get_full_name() or request.user.username,
                'birth_date': '2000-01-01',  # Default value, should be updated by user
                'cpf': '000.000.000-00',     # Default value, should be updated by user
                'rg': '0000000',             # Default value, should be updated by user
                'phone_whatsapp': '(00) 00000-0000',  # Default value
                'address_street': 'Rua Exemplo',      # Default value
                'address_number': '123',              # Default value
                'address_neighborhood': 'Centro',     # Default value
                'address_city': 'São Paulo',          # Default value
                'address_state': 'SP',                # Default value
                'address_zip': '00000-000'            # Default value
            }
        )
        
        if created:
            messages.info(request, _("Perfil criado automaticamente. Por favor, atualize suas informações."))
        
        applications = candidate_profile.applications.select_related(
            "job_vacancy", "job_vacancy__hospital_unit"
        ).order_by("-application_date")
        
        context = {"applications": applications}
        return render(request, "accounts/my_applications.html", context)
    
    except Exception as e:
        # Log the error for debugging
        print(f"Erro ao acessar candidaturas: {str(e)}")
        messages.error(request, _("Ocorreu um erro ao acessar suas candidaturas. Por favor, complete seu perfil antes de continuar."))
        return redirect("accounts:profile_edit")


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

