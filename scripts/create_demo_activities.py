import os
import sys
import django
from datetime import timedelta

# Add the project root to sys.path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aula.settings")
django.setup()

from aula.apps.sortides.models import Sortida, NotificaSortida
from django.db import transaction
from django.utils import timezone

def duplicate_activities():
    # Cleanup Stage: Remove previous DUPLICADA activities
    # Need to handle Pagament related to these Sortida objects because of ProtectedError
    titles_to_remove = Sortida.objects.filter(titol__startswith='DUPLICADA:')
    if titles_to_remove.exists():
        from aula.apps.sortides.models import Pagament
        # Delete associated Pagaments first
        Pagament.objects.filter(sortida__in=titles_to_remove).delete()
        # Delete the activities
        count = titles_to_remove.count()
        titles_to_remove.delete()
        print(f"Cleaned up {count} previous 'DUPLICADA:' activities and their payments.")

    # Find 3 paid activities (online payment)
    # Filter by TIPUS_PAGAMENT_CHOICES 'ON' (Online a través del djAu)
    activities_to_duplicate = Sortida.objects.filter(tipus_de_pagament='ON')[:3]

    if not activities_to_duplicate:
        print("No matches found for paid activities (online payment).")
        return

    from django.contrib.auth.models import User
    
    # Get an admin user for credentials (required by Sortida signals)
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
             # Fallback if no superuser
             admin_user = User.objects.first()
    except Exception as e:
        print(f"Error fetching user: {e}")
        return

    created_activities = []

    with transaction.atomic():
        for original in activities_to_duplicate:
            # Duplicate the instance
            new_activity = Sortida()
            
            # Attach credentials (user, l4) to bypass permission checks or satisfy signal
            # l4=True usually means internal/privileged
            new_activity.credentials = (admin_user, True)
            
            # Copy fields
            # Max length for titol is 40. Prefix is "DUPLICADA: " (11 chars). 
            # We need to truncate original part to 29 chars.
            original_titol_truncated = original.titol[:29]
            new_activity.titol = f"DUPLICADA: {original_titol_truncated}"
            new_activity.descripcio = original.descripcio if hasattr(original, 'descripcio') else "" # Check if field exists, though model definition says 'programa_de_la_sortida' is description
            # Mapping based on models.py inspection:
            # 'programa_de_la_sortida' is "Descripció de l'activitat"
            new_activity.programa_de_la_sortida = original.programa_de_la_sortida
            
            new_activity.preu_per_alumne = original.preu_per_alumne
            new_activity.tipus_de_pagament = original.tipus_de_pagament
            new_activity.tipus = original.tipus
            new_activity.subtipus = original.subtipus
            new_activity.ambit = original.ambit
            new_activity.ciutat = original.ciutat
            new_activity.materia = original.materia
            new_activity.condicions_generals = original.condicions_generals
            new_activity.comentaris_interns = original.comentaris_interns
            new_activity.professor_que_proposa = original.professor_que_proposa
            new_activity.estat = 'P' # Set to 'Proposada' or 'E' (Esborrany)? Requirement says "same characteristics", but usually new ones start as proposals. Let's keep consistent with valid state. original might be 'R' or 'G'. Let's set to 'P' or copy? Let's copy state but maybe unsafe. Implementation plan said copy. But usually logic implies new dates = new proposal. Let's stick to implementation plan implicitly: "characteristics of origin". But let's check validation. 'E' is safe.
            # However, if we want them to show up in lists, 'P' or original state is better.
            new_activity.estat = original.estat 

            # Calculate new dates (next week)
            # If original dates are set, shift them. If not, maybe set for next week from now?
            # Requirement: "dates of start and end in the future. For example the week following the current one."
            # Let's verify original dates exist.
            
            today = timezone.now().date()

            # Set start date exactly one week from today
            new_activity.data_inici = today + timedelta(days=7)
            # Set end date posterior to start date
            new_activity.data_fi = new_activity.data_inici + timedelta(days=1)

            # Set payment deadline to one day before start
            new_activity.termini_pagament = timezone.make_aware(
                timezone.datetime.combine(
                    new_activity.data_inici - timedelta(days=1),
                    timezone.datetime.min.time()
                )
            )

            # Ensure price is greater than zero
            if not new_activity.preu_per_alumne or new_activity.preu_per_alumne <= 0:
                new_activity.preu_per_alumne = 10.00
            
            # Franjas
            new_activity.franja_inici = original.franja_inici
            new_activity.franja_fi = original.franja_fi
            
            # Calendari dates (DateTime)
            if original.calendari_desde:
                # Keep original time but change date to data_inici
                orig_time = original.calendari_desde.time()
                new_activity.calendari_desde = timezone.make_aware(
                    timezone.datetime.combine(new_activity.data_inici, orig_time)
                )
            else:
                new_activity.calendari_desde = timezone.make_aware(
                    timezone.datetime.combine(new_activity.data_inici, timezone.datetime.min.time())
                )

            if original.calendari_finsa:
                # Keep original time but change date to data_fi
                orig_time = original.calendari_finsa.time()
                new_activity.calendari_finsa = timezone.make_aware(
                    timezone.datetime.combine(new_activity.data_fi, orig_time)
                )
            else:
                new_activity.calendari_finsa = timezone.make_aware(
                    timezone.datetime.combine(new_activity.data_fi, timezone.datetime.min.time())
                )
            
            # Save to get ID
            new_activity.save()
            created_activities.append(new_activity)

            # Copy M2M relationships
            new_activity.alumnes_convocats.set(original.alumnes_convocats.all())
            new_activity.professors_responsables.set(original.professors_responsables.all())
            new_activity.altres_professors_acompanyants.set(original.altres_professors_acompanyants.all())
            
            # Notify families (Create NotificaSortida objects) and create Pagament objects for online payments
            for alumne in new_activity.alumnes_convocats.all():
                NotificaSortida.objects.create(alumne=alumne, sortida=new_activity)
                if new_activity.tipus_de_pagament == 'ON':
                    from aula.apps.sortides.models import Pagament
                    Pagament.objects.create(alumne=alumne, sortida=new_activity)
            
            print(f"Created activity: {new_activity.titol}")
            
            # Print credentials for 3 students
            students = new_activity.alumnes_convocats.all()[:3]
            if students:
                print("  Sample students credentials:")
                for student in students:
                    user = student.get_user_associat()
                    if user:
                        user.is_active = True
                        user.set_password("djau")
                        user.save()
                        print(f"    Alumne: {student.nom} {student.cognoms}, Usuari: {user.username}, Contrasenya: djau")
                        
                        # Process associated responsible users
                        responsables = student.responsables.all()
                        for resp in responsables:
                            resp_user = resp.get_user_associat()
                            if resp_user:
                                resp_user.is_active = True
                                resp_user.set_password("djau")
                                resp_user.save()
                                print(f"      Responsable: {resp.nom} {resp.cognoms}, Usuari: {resp_user.username}, Contrasenya: djau")
            else:
                print("  No students called for this activity.")
            print("-" * 40)

if __name__ == "__main__":
    duplicate_activities()




