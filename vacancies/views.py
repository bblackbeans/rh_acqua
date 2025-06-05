from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.forms import (Form, CharField, EmailField, ChoiceField, BooleanField,
                        FileField, DateField, IntegerField, FloatField, Textarea,
                        Select, CheckboxInput, FileInput, DateInput, NumberInput,
                        MultipleChoiceField, CheckboxSelectMultiple, ValidationError,
                        ModelForm, DateTimeInput)
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.contrib.auth.models import User
import json
from datetime import date

from .models import JobVacancy, JobApplication, JobVacancyType, Interview
from accounts.models import CandidateProfile
# Import Notification and ActivityLog models
from notifications.models import Notification, ActivityLog

# --- Helper Functions (build_dynamic_form, clean_data_for_json) remain the same ---
# (Assuming they are in the same file or imported)

# Helper function to build a Django form dynamically based on field_config
def build_dynamic_form(field_config, data=None, files=None, initial=None):
    fields = {}

    # --- Dynamic Fields based on field_config ---

    # Personal Data Section
    personal_data_config = field_config.get("personal_data", {})
    if personal_data_config.get("pis", {}).get("show", False):
        required = personal_data_config["pis"].get("required", False)
        fields["pis"] = CharField(label=_("PIS"), required=required, max_length=20)

    if personal_data_config.get("race", {}).get("show", False):
        required = personal_data_config["race"].get("required", False)
        race_choices = [("", "---------"), ("INDIGENA", _("Indígena")), ("BRANCA", _("Branca")), ("PRETA", _("Preta")), ("AMARELA", _("Amarela")), ("PARDA", _("Parda"))]
        fields["race"] = ChoiceField(label=_("Raça/Cor"), choices=race_choices, required=required)

    # Professional Council Section
    prof_council_config = field_config.get("professional_council", {})
    if prof_council_config.get("show", False):
        required = prof_council_config.get("required", False)
        council_types = prof_council_config.get("council_types", [])
        council_choices = [("", "---------")] + [(c, c) for c in council_types]
        fields["professional_council_type"] = ChoiceField(label=_("Conselho Regional"), choices=council_choices, required=required)
        fields["professional_council_number"] = CharField(label=_("Número de Registro"), required=required, max_length=50)
        fields["professional_council_validity"] = DateField(label=_("Validade do Registro"), required=required, widget=DateInput(attrs={"type": "date"}))

    # PCD Details Section
    pcd_config = field_config.get("pcd_details", {})
    if pcd_config.get("ask_if_pcd", False):
        fields["is_pcd"] = ChoiceField(label=_("Você é pessoa com deficiência?"), choices=[("", "-"), ("True", _("Sim")), ("False", _("Não"))], required=True, widget=Select)
        # Note: Conditional requirement logic (if is_pcd is True) needs handling in clean() or JS
        cid_required = pcd_config.get("require_cid_if_yes", False)
        fields["pcd_cid"] = CharField(label=_("CID"), required=False, max_length=10, help_text=_("Obrigatório se PCD") if cid_required else "")
        laudo_required = pcd_config.get("require_laudo_if_yes", False)
        fields["pcd_laudo_file"] = FileField(label=_("Laudo Médico Comprobatório"), required=False, widget=FileInput, help_text=_("Obrigatório se PCD") if laudo_required else "")
        adaptation_required = pcd_config.get("ask_adaptation_needs", False)
        fields["pcd_adaptation_needs"] = CharField(label=_("Necessita de adaptações durante o processo? Se sim, qual?"), required=False, widget=Textarea(attrs={"rows": 3}), help_text=_("Obrigatório se PCD") if adaptation_required else "")

    # Specific Questions Section
    specific_questions = field_config.get("specific_questions", [])
    for i, q in enumerate(specific_questions):
        q_id = q.get("id", f"specific_q_{i}")
        q_label = q.get("label", "")
        q_type = q.get("type", "text")
        q_required = q.get("required", False)
        q_options = q.get("options", [])

        # Handle conditional requirement (e.g., required if another field is 'yes')
        # This basic implementation sets required based on the config directly.
        # More complex logic needs handling in clean() or JS.
        conditional_required = isinstance(q_required, str) # e.g., "if_exp_area_yes"
        actual_required = q_required if not conditional_required else False # Set False initially if conditional

        if q_type == "boolean":
            fields[q_id] = ChoiceField(label=q_label, choices=[("", "-"), ("True", _("Sim")), ("False", _("Não"))], required=actual_required, widget=Select)
        elif q_type == "textarea":
            fields[q_id] = CharField(label=q_label, required=actual_required, widget=Textarea(attrs={"rows": 4}))
        elif q_type == "select" and q_options:
            choices = [("", "---------")] + [(opt, opt) for opt in q_options]
            fields[q_id] = ChoiceField(label=q_label, choices=choices, required=actual_required)
        elif q_type == "checkbox_multiple" and q_options:
             choices = [(opt, opt) for opt in q_options]
             fields[q_id] = MultipleChoiceField(label=q_label, choices=choices, required=actual_required, widget=CheckboxSelectMultiple)
        else: # Default to CharField
            fields[q_id] = CharField(label=q_label, required=actual_required, max_length=255)

        # Store conditional requirement info for later use in clean() if needed
        if conditional_required:
            fields[q_id].widget.attrs["data-conditional-required"] = q_required

    # Emotional Skills Section
    emotional_config = field_config.get("emotional_skills", {})
    if emotional_config.get("show", False):
        required = emotional_config.get("required", False)
        options = emotional_config.get("options", [])
        max_selection = emotional_config.get("max_selection", None)
        choices = [(opt, opt) for opt in options]
        fields["emotional_skills"] = MultipleChoiceField(
            label=_("Habilidades Emocionais (Selecione até %s)") % max_selection if max_selection else _("Habilidades Emocionais"),
            choices=choices,
            required=required,
            widget=CheckboxSelectMultiple,
            help_text=_("Selecione as %s habilidades que melhor o/a representam.") % max_selection if max_selection else ""
        )
        # Store max_selection for validation in clean()
        if max_selection:
            fields["emotional_skills"].widget.attrs["data-max-selection"] = max_selection

    # Availability Section
    availability_config = field_config.get("availability", {})
    if availability_config.get("ask_schedule", False):
        required = availability_config.get("required", False)
        options = availability_config.get("schedule_options", [])
        choices = [(opt, opt) for opt in options]
        fields["availability_schedule"] = MultipleChoiceField(label=_("Disponibilidade de Horário"), choices=choices, required=required, widget=CheckboxSelectMultiple)
    if availability_config.get("ask_immediate_start", False):
        required = availability_config.get("required", False)
        fields["availability_immediate"] = ChoiceField(label=_("Disponibilidade para início imediato?"), choices=[("", "-"), ("True", _("Sim")), ("False", _("Não"))], required=required, widget=Select)

    # Relatives Section
    relatives_config = field_config.get("relatives", {})
    if relatives_config.get("ask_if_relative", False):
        fields["has_relative"] = ChoiceField(label=_("Possui parentes na instituição?"), choices=[("", "-"), ("True", _("Sim")), ("False", _("Não"))], required=True, widget=Select)
        # Conditional requirement
        details_required = relatives_config.get("require_details_if_yes", False)
        relative_choices = [
            ("", "---------"), ("AVO", _("Avô(ó)")), ("PAI", _("Pai")), ("MAE", _("Mãe")), ("FILHO", _("Filho(a)")), ("IRMAO", _("Irmão(ã)")),
            ("TIO", _("Tio(a)")), ("SOBRINHO", _("Sobrinho(a)")), ("PRIMO", _("Primo(a)")), ("CONJUGE", _("Cônjuge")),
            ("ENTEADO", _("Enteado(a)")), ("SOGRO", _("Sogro(a)")), ("GENRO", _("Genro")), ("NORA", _("Nora")), ("NETO", _("Neto(a)")),
            ("CUNHADO", _("Cunhado(a)"))
        ]
        fields["relative_relationship"] = ChoiceField(label=_("Grau de Parentesco"), choices=relative_choices, required=False, help_text=_("Obrigatório se possuir parente") if details_required else "")
        fields["relative_name_dept"] = CharField(label=_("Nome do Parente e Setor"), required=False, widget=Textarea(attrs={"rows": 2}), help_text=_("Obrigatório se possuir parente") if details_required else "")

    # --- Declarations --- (Always required)
    fields["declaration_truthful"] = BooleanField(label=_("Declaro que todas as informações fornecidas neste formulário são verdadeiras. Estou ciente de que falsidades ou omissões podem resultar em desclassificação do processo."), required=True)
    fields["declaration_read_terms"] = BooleanField(label=_("Declaro que li e estou de acordo com os termos do edital (se aplicável)."), required=True)
    fields["declaration_data_usage"] = BooleanField(label=_("Autorizo o uso dos meus dados para fins do processo seletivo, conforme a Política de Privacidade."), required=True)

    # --- Custom Form Class with Validation ---
    class DynamicApplicationForm(Form):
        def __init__(self, *args, **kwargs):
            self._field_config = kwargs.pop('field_config', {}) # Store config for clean method
            super().__init__(*args, **kwargs)
            # Add field attributes or initial values if needed
            for field_name, field in self.fields.items():
                 # Add Bootstrap classes or other attributes
                 if not isinstance(field.widget, (CheckboxInput, CheckboxSelectMultiple, FileInput)):
                     field.widget.attrs.update({"class": "form-control"})
                 elif isinstance(field.widget, CheckboxSelectMultiple):
                     # Bootstrap 5 needs custom styling for checkbox groups
                     field.widget.attrs.update({"class": "form-check-input"})
                 elif isinstance(field.widget, Select):
                     field.widget.attrs.update({"class": "form-select"})

        def clean(self):
            cleaned_data = super().clean()
            pcd_config = self._field_config.get("pcd_details", {})
            relatives_config = self._field_config.get("relatives", {})
            specific_questions = self._field_config.get("specific_questions", [])
            emotional_config = self._field_config.get("emotional_skills", {})

            # --- Conditional Validation Examples ---
            is_pcd_str = cleaned_data.get("is_pcd")
            is_pcd = is_pcd_str == "True"

            if pcd_config.get("require_cid_if_yes", False) and is_pcd and not cleaned_data.get("pcd_cid"):
                self.add_error("pcd_cid", ValidationError(_("CID é obrigatório para PCD.")))

            # Use self.files for file validation
            if pcd_config.get("require_laudo_if_yes", False) and is_pcd and "pcd_laudo_file" not in self.files and not (self.initial and self.initial.get("pcd_laudo_file")):
                 # Check initial data too if form is for update
                 self.add_error("pcd_laudo_file", ValidationError(_("Laudo médico é obrigatório para PCD.")))

            if pcd_config.get("ask_adaptation_needs", False) and is_pcd and not cleaned_data.get("pcd_adaptation_needs"):
                 self.add_error("pcd_adaptation_needs", ValidationError(_("Informe se necessita de adaptações.")))

            # Validate specific questions conditional requirement
            for i, q in enumerate(specific_questions):
                q_id = q.get("id", f"specific_q_{i}")
                q_required = q.get("required", False)
                if isinstance(q_required, str) and q_required.startswith("if_"):
                    condition_parts = q_required.split("_eq_")
                    condition_field_id = condition_parts[0].replace("if_", "") # e.g., "exp_area"
                    expected_value = condition_parts[1] # e.g., "True"
                    condition_value_str = cleaned_data.get(condition_field_id)
                    # Adjust condition check based on expected value type (e.g., 'True' for boolean)
                    if condition_value_str == expected_value and not cleaned_data.get(q_id):
                        self.add_error(q_id, ValidationError(_("Este campo é obrigatório.")))

            # Validate max selections for emotional skills
            if "emotional_skills" in cleaned_data and emotional_config.get("max_selection"):
                max_selection = int(emotional_config["max_selection"])
                if len(cleaned_data["emotional_skills"]) > max_selection:
                    self.add_error("emotional_skills", ValidationError(_("Selecione no máximo %s habilidades.") % max_selection))

            # Validate relative details
            has_relative_str = cleaned_data.get("has_relative")
            if relatives_config.get("require_details_if_yes", False) and has_relative_str == "True":
                if not cleaned_data.get("relative_relationship"):
                    self.add_error("relative_relationship", ValidationError(_("Grau de parentesco é obrigatório.")))
                if not cleaned_data.get("relative_name_dept"):
                    self.add_error("relative_name_dept", ValidationError(_("Nome e setor do parente são obrigatórios.")))

            return cleaned_data

    # Add the dynamically generated fields to the form class
    DynamicApplicationForm.base_fields = fields
    DynamicApplicationForm.declared_fields = fields

    return DynamicApplicationForm(data=data, files=files, initial=initial, field_config=field_config)

# --- Helper for JSON Serialization ---
def clean_data_for_json(data):
    cleaned = {}
    for key, value in data.items():
        if isinstance(value, date):
            cleaned[key] = value.isoformat()
        elif isinstance(value, bool): # Keep booleans
             cleaned[key] = value
        elif value == "True": # Convert string bools from ChoiceFields
            cleaned[key] = True
        elif value == "False":
            cleaned[key] = False
        elif key.endswith("_file"): # Skip file fields in JSON
            continue
        else:
            cleaned[key] = value
    return cleaned

# --- Candidate Views ---

@login_required
def apply_for_vacancy(request, vacancy_id):
    vacancy = get_object_or_404(JobVacancy, pk=vacancy_id, status=JobVacancy.StatusChoices.OPEN)
    vacancy_type = vacancy.vacancy_type
    try:
        candidate_profile = request.user.candidate_profile
    except CandidateProfile.DoesNotExist:
        messages.error(request, _("Você precisa completar seu perfil de candidato antes de se candidatar."))
        # return redirect("accounts:profile_edit") # Assuming a profile edit URL
        raise Http404 # Or handle profile creation flow

    # Check if already applied
    if JobApplication.objects.filter(candidate=candidate_profile, job_vacancy=vacancy).exists():
        messages.info(request, _("Você já se candidatou para esta vaga."))
        # return redirect("vacancies:list") # Redirect to vacancy list
        return render(request, "vacancies/already_applied.html", {"vacancy": vacancy})

    field_config = vacancy_type.field_config

    if request.method == "POST":
        form = build_dynamic_form(field_config, data=request.POST, files=request.FILES)
        if form.is_valid():
            submitted_data_raw = form.cleaned_data
            pcd_laudo_file = form.files.get("pcd_laudo_file", None)

            # Clean data for JSON storage
            submitted_data_json = clean_data_for_json(submitted_data_raw)

            # Create the application
            application = JobApplication.objects.create(
                candidate=candidate_profile,
                job_vacancy=vacancy,
                submitted_data=submitted_data_json,
                pcd_medical_report_file=pcd_laudo_file
            )
            messages.success(request, _("Candidatura enviada com sucesso!"))

            # Create Notification for Candidate
            Notification.objects.create(
                recipient=request.user,
                message=_(f"Sua candidatura para a vaga ") + f"\"{vacancy.title}\"" + _(" foi recebida."),
                notification_type=Notification.NotificationTypeChoices.APPLICATION_RECEIVED,
                related_application=application
            )
            # TODO: Notify Recruiters? (Requires identifying relevant recruiters)

            # Create Activity Log
            ActivityLog.objects.create(
                actor=request.user,
                verb=_("candidatou-se para a vaga"),
                target_application=application,
                target_vacancy=vacancy,
                target_candidate=candidate_profile
            )

            return render(request, "vacancies/application_success.html", {"vacancy": vacancy, "application": application})
        else:
             messages.error(request, _("Por favor, corrija os erros no formulário."))
    else:
        initial_data = {}
        form = build_dynamic_form(field_config, initial=initial_data)

    context = {
        "vacancy": vacancy,
        "form": form,
    }
    return render(request, "vacancies/apply_form.html", context)

@login_required
def vacancy_list(request):
    # Add filtering logic based on request.GET parameters
    # Example filters:
    query = request.GET.get('q')
    unit_id = request.GET.get('unit')
    city = request.GET.get('city')
    state = request.GET.get('state')

    vacancies = JobVacancy.objects.filter(status=JobVacancy.StatusChoices.OPEN).select_related("hospital_unit", "vacancy_type")

    if query:
        vacancies = vacancies.filter(models.Q(title__icontains=query) | models.Q(description__icontains=query))
    if unit_id:
        vacancies = vacancies.filter(hospital_unit_id=unit_id)
    if city:
        vacancies = vacancies.filter(hospital_unit__city__icontains=city)
    if state:
        vacancies = vacancies.filter(hospital_unit__state=state)

    context = {"vacancies": vacancies}
    # Add filter options to context if needed
    return render(request, "vacancies/vacancy_list.html", context)

@login_required
def vacancy_detail(request, vacancy_id):
    vacancy = get_object_or_404(JobVacancy.objects.select_related("hospital_unit", "department", "vacancy_type"), pk=vacancy_id)
    # Check if candidate already applied
    already_applied = False
    if hasattr(request.user, 'candidate_profile'):
        already_applied = JobApplication.objects.filter(candidate=request.user.candidate_profile, job_vacancy=vacancy).exists()

    context = {
        "vacancy": vacancy,
        "already_applied": already_applied
    }
    return render(request, "vacancies/vacancy_detail.html", context)

@login_required
def application_success(request):
    # This view might need the application ID passed or retrieved from session
    # For simplicity, just rendering the template
    return render(request, "vacancies/application_success.html")

# --- Recruiter Views ---

def is_recruiter(user):
    # Check if the user belongs to the 'Recruiter' group or has specific permissions
    return user.is_authenticated and (user.is_staff or user.groups.filter(name='Recrutadores').exists())

@user_passes_test(is_recruiter)
def recruiter_dashboard(request):
    # Simple dashboard for recruiters
    # List vacancies they manage or all vacancies if admin
    # TODO: Filter vacancies based on recruiter permissions if needed
    vacancies = JobVacancy.objects.all().order_by('-created_at')
    context = {
        'vacancies': vacancies
    }
    return render(request, 'vacancies/recruiter_dashboard.html', context)

@user_passes_test(is_recruiter)
def recruiter_applications_list(request, vacancy_id):
    vacancy = get_object_or_404(JobVacancy, pk=vacancy_id)
    # Add filtering/sorting based on request.GET
    status_filter = request.GET.get('status')
    sort_by = request.GET.get('sort', '-application_date') # Default sort by date desc

    applications = JobApplication.objects.filter(job_vacancy=vacancy).select_related('candidate', 'candidate__user').order_by(sort_by)

    if status_filter and status_filter in JobApplication.StatusChoices.values:
        applications = applications.filter(status=status_filter)

    context = {
        'vacancy': vacancy,
        'applications': applications,
        'status_choices': JobApplication.StatusChoices.choices,
        'current_status_filter': status_filter,
        'current_sort': sort_by,
    }
    return render(request, 'vacancies/recruiter_applications_list.html', context)

@user_passes_test(is_recruiter)
def recruiter_application_detail(request, application_id):
    application = get_object_or_404(JobApplication.objects.select_related(
        'candidate', 'candidate__user', 'job_vacancy', 'job_vacancy__vacancy_type'
    ), pk=application_id)
    # TODO: Add candidate profile details (education, experience) to context
    candidate_profile = application.candidate
    interviews = application.interviews.all().order_by('scheduled_time')

    context = {
        'application': application,
        'candidate': candidate_profile,
        'submitted_data': application.submitted_data, # Already a dict
        'interviews': interviews,
        'status_choices': JobApplication.StatusChoices.choices,
    }
    return render(request, 'vacancies/recruiter_application_detail.html', context)

@user_passes_test(is_recruiter)
def recruiter_change_application_status(request, application_id):
    application = get_object_or_404(JobApplication, pk=application_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in JobApplication.StatusChoices.values:
            old_status_display = application.get_status_display()
            application.status = new_status
            application.save()
            new_status_display = application.get_status_display()

            # Create Activity Log
            ActivityLog.objects.create(
                actor=request.user,
                verb=_("atualizou o status da candidatura de '%(status_antigo)s' para '%(status_novo)s'") % {
                    'status_antigo': old_status_display,
                    'status_novo': new_status_display
                },
                target_application=application,
                target_candidate=application.candidate,
                details={'old_status': old_status_display, 'new_status': new_status_display}
            )

            # Create Notification for Candidate
            Notification.objects.create(
                recipient=application.candidate.user,
                message=_(f"O status da sua candidatura para ") + f"\"{application.job_vacancy.title}\"" + _(" foi atualizado para: %s.") % new_status_display,
                notification_type=Notification.NotificationTypeChoices.STATUS_UPDATE,
                related_application=application
            )

            messages.success(request, _(f"Status da candidatura de {application.candidate.full_name} atualizado para {new_status_display}."))
        else:
            messages.error(request, _("Status inválido."))
        return redirect('vacancies:recruiter_application_detail', application_id=application.id)
    else:
        # GET request not allowed or redirect
        return redirect('vacancies:recruiter_application_detail', application_id=application.id)

class InterviewForm(ModelForm):
    class Meta:
        model = Interview
        fields = ['scheduled_time', 'interviewer', 'interview_type', 'location_details', 'status']
        widgets = {
            'scheduled_time': DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit interviewer choices to staff/recruiters
        self.fields['interviewer'].queryset = User.objects.filter(is_staff=True)
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, CheckboxInput):
                 field.widget.attrs.update({'class': 'form-control'})
            if isinstance(field.widget, Select):
                 field.widget.attrs.update({'class': 'form-select'})

@user_passes_test(is_recruiter)
def recruiter_schedule_interview(request, application_id):
    application = get_object_or_404(JobApplication, pk=application_id)
    if request.method == 'POST':
        form = InterviewForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = application
            # Ensure interviewer is set if not provided in form (e.g., default to current user)
            if not interview.interviewer:
                 interview.interviewer = request.user # Or handle appropriately
            interview.save()

            # Create Activity Log
            ActivityLog.objects.create(
                actor=request.user,
                verb=_("agendou uma entrevista (%(tipo)s) para %(data)s") % {
                    'tipo': interview.interview_type or 'Entrevista',
                    'data': interview.scheduled_time.strftime('%d/%m/%Y %H:%M')
                },
                target_application=application,
                target_candidate=application.candidate,
                details={'interview_id': interview.id, 'type': interview.interview_type, 'time': interview.scheduled_time.isoformat()}
            )

            # Create Notification for Candidate
            Notification.objects.create(
                recipient=application.candidate.user,
                message=_(f"Uma entrevista para a vaga ") + f"\"{application.job_vacancy.title}\"" + _(" foi agendada para %s. Detalhes: %s") % (interview.scheduled_time.strftime('%d/%m/%Y às %H:%M'), interview.location_details or ''),
                notification_type=Notification.NotificationTypeChoices.INTERVIEW_SCHEDULED,
                related_application=application
            )
            # Create Notification for Interviewer (if different from scheduler)
            if interview.interviewer != request.user:
                 Notification.objects.create(
                    recipient=interview.interviewer,
                    message=_(f"Você foi agendado para entrevistar {application.candidate.full_name} para a vaga ") + f"\"{application.job_vacancy.title}\"" + _(" em %s. Detalhes: %s") % (interview.scheduled_time.strftime('%d/%m/%Y às %H:%M'), interview.location_details or ''),
                    notification_type=Notification.NotificationTypeChoices.INTERVIEW_SCHEDULED,
                    related_application=application
                 )

            messages.success(request, _(f"Entrevista agendada para {application.candidate.full_name}."))
            return redirect('vacancies:recruiter_application_detail', application_id=application.id)
        else:
             messages.error(request, _("Erro ao agendar entrevista. Verifique os dados."))
    else:
        form = InterviewForm(initial={'application': application, 'interviewer': request.user})

    context = {
        'form': form,
        'application': application,
    }
    return render(request, 'vacancies/recruiter_schedule_interview.html', context)

# --- Views from other apps needed by templates ---
# Move my_applications to accounts/views.py
# from accounts.views import my_applications


