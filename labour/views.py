# encoding: utf-8

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_http_methods

from core.helpers import initialize_form, url
from core.models import Event

from .forms import SignupForm
from .helpers import labour_admin_required
from .models import LabourEventMeta, Qualification, PersonQualification, Signup


@login_required
@require_http_methods(['GET', 'POST'])
def labour_signup_view(request, event):
    event = get_object_or_404(Event, slug=event)

    # TODO should the user be allowed to change their registration after the registration period is over?
    if not event.laboureventmeta.is_registration_open:
        messages.error(request, u'Ilmoittautuminen tähän tapahtumaan ei ole avoinna.')
        return redirect('core_event_view', event.slug)

    signup = event.laboureventmeta.get_signup_for_person(request.user.person)
    signup_extra = signup.signup_extra
    SignupExtraForm = event.laboureventmeta.signup_extra_model.get_form_class()
    signup_form = initialize_form(SignupForm, request, instance=signup, prefix='signup')
    signup_extra_form = initialize_form(SignupExtraForm, request, instance=signup_extra, prefix='extra')

    if request.method == 'POST':
        if signup_form.is_valid() and signup_extra_form.is_valid():
            if signup.pk is None:
                message = u'Kiitos ilmoittautumisestasi!'
            else:
                message = u'Ilmoittautumisesi on päivitetty.'

            signup = signup_form.save()
            signup_extra.signup = signup
            signup_extra_form.save()

            messages.success(request, message)
            return redirect('core_event_view', event.slug)
        else:
            messages.error(request, u'Ole hyvä ja korjaa virheelliset kentät.')

    vars = dict(
        event=event,
        signup_form=signup_form,
        signup_extra_form=signup_extra_form,
    )

    return render(request, 'labour_signup_view.jade', vars)


@login_required
def labour_qualifications_view(request):
    person_qualifications = request.user.person.personqualification_set.all()
    qualification_pks = [q.qualification.pk for q in person_qualifications]
    available_qualifications = Qualification.objects.exclude(pk__in=qualification_pks)

    vars = dict(
        person_qualifications=person_qualifications,
        available_qualifications=available_qualifications
    )

    return render(request, 'labour_qualifications_view.jade', vars)


@login_required
@require_http_methods(['GET', 'POST'])
def labour_person_qualification_view(request, qualification):
    person = request.user.person
    qualification = get_object_or_404(Qualification, slug=qualification)

    try:
        person_qualification = qualification.personqualification_set.get(person=person)
    except PersonQualification.DoesNotExist:
        person_qualification = PersonQualification(
            person=person,
            qualification=qualification
        )

    QualificationExtra = qualification.qualification_extra_model
    if QualificationExtra:
        QualificationExtraForm = QualificationExtra.get_form_class()
        qualification_extra = person_qualification.qualification_extra
        form = initialize_form(QualificationExtraForm, request, instance=qualification_extra)
    else:
        qualification_extra = None
        form = None

    if request.method == 'POST':
        form_valid = not form or (form and form.is_valid())
        if form_valid:
            person_qualification.save()

            if form:
                qualification_extra.personqualification = person_qualification
                form.save()

            messages.success(request, u'Pätevyys tallennettiin.')
            return redirect('labour_qualifications_view')
        else:
            messages.error(request, u'Ole hyvä ja korjaa lomakkeen virheet.')

    vars = dict(
        person_qualification=person_qualification,
        form=form
    )

    return render(request, 'labour_person_qualification_view.jade', vars)

@login_required
def labour_person_qualify_view(request, qualification):
    person = request.user.person
    qualification = get_object_or_404(Qualification, slug=qualification)

    if qualification.qualification_extra_model:
        return redirect('labour_person_qualification_view', qualification.slug)

    person_qualification, created = PersonQualification.objects.get_or_create(
        person=person,
        qualification=qualification
    )

    if created:
        messages.success(request, u"Pätevyys lisättiin.")

    return redirect('labour_qualifications_view')

@login_required
def labour_person_disqualify_view(request, qualification):
    person = request.user.person
    qualification = get_object_or_404(Qualification, slug=qualification)

    try:
        person_qualification = get_object_or_404(PersonQualification,
            person=person, qualification=qualification)
        person_qualification.delete()
        messages.success(request, u"Pätevyys poistettiin.")
    except:
        pass

    return redirect('labour_qualifications_view')


@labour_admin_required
def labour_admin_dashboard_view(request, vars, event):
    return render(request, 'labour_admin_dashboard_view.jade', vars)


@labour_admin_required
def labour_admin_signup_view(request, vars, event, person):
    signup = get_object_or_404(Signup, person=int(person), event=event)

    vars.update(
        signup=signup,
    )

    return render(request, 'labour_admin_signup_view.jade', vars)


@labour_admin_required
def labour_admin_signups_view(request, vars, event):
    signups = event.signup_set.all()

    vars.update(
        signups=signups,
    )

    return render(request, 'labour_admin_signups_view.jade', vars)


def labour_profile_menu_items(request):
    qualifications_url = url('labour_qualifications_view')
    qualifications_active = request.path.startswith(qualifications_url)
    qualifications_text = u"Pätevyydet"

    return [(qualifications_active, qualifications_url, qualifications_text)]


def labour_admin_menu_items(request, event):
    dashboard_url = url('labour_admin_dashboard_view', event.slug)
    dashboard_active = request.path == dashboard_url
    dashboard_text = u"Kojelauta"

    signups_url = url('labour_admin_signups_view', event.slug)
    signups_active = request.path.startswith(signups_url)
    signups_text = u"Tapahtumaan ilmoittautuneet henkilöt"

    return [
        (dashboard_active, dashboard_url, dashboard_text),
        (signups_active, signups_url, signups_text),
    ]



def labour_event_box_context(request, event):
    if request.user.is_authenticated():
        is_signed_up = event.laboureventmeta.is_person_signed_up(request.user.person)
        is_labour_admin = event.laboureventmeta.is_user_admin(request.user)
    else:
        is_signed_up = False
        is_labour_admin = False

    return dict(
        is_signed_up=is_signed_up,
        is_labour_admin=is_labour_admin,
    )


__all__ = [
    'labour_admin_dashboard_view',
    'labour_admin_menu_items',
    'labour_admin_signup_view',
    'labour_admin_signups_view',
    'labour_event_box_context',
    'labour_person_disqualify_view',
    'labour_person_qualification_view',
    'labour_person_qualify_view',
    'labour_profile_menu_items',
    'labour_qualifications_view',
    'labour_signup_view',
]
