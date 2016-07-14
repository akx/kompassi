import pytest
from core.models import *
from programme.models import *
from labour.models import *
from django.db import connection
from django.db.models import Prefetch

@pytest.mark.django_db
def test_spoop(settings):

    org = Organization.objects.create()
    ven = Venue.objects.create()
    event = Event.objects.create(venue=ven, organization=org)
    category = Category.objects.create(event=event)
    pc = PersonnelClass.objects.create(event=event)
    pub_role = Role.objects.create(personnel_class=pc, is_public=True)
    priv_role = Role.objects.create(personnel_class=pc, is_public=False)
    person = Person.objects.create(first_name='teppo', surname='testi')
    for x in range(50):
        prog = Programme.objects.create(category=category)
        for x in range(5):
            FreeformOrganizer.objects.create(programme=prog, text='asd%s' % x)
        ProgrammeRole.objects.create(role=pub_role, person=person, programme=prog)
        ProgrammeRole.objects.create(role=priv_role, person=person, programme=prog)
    settings.DEBUG = True
    for prog in Programme.objects.prefetch_related(
        Prefetch(
            'freeform_organizers',
            to_attr='freeform_organizer_texts',
        ),
        Prefetch(
            'programmerole_set',
            queryset=ProgrammeRole.objects.filter(role__is_public=True).select_related('person'),
            to_attr='public_programme_role_people'
        ),
    ):
        assert prog.formatted_hosts == 'asd0, asd1, asd2, asd3, asd4, teppo testi'
    for q in connection.queries:
        print(q)
    print(len(connection.queries))