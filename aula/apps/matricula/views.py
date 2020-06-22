from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.views.generic.edit import UpdateView
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
import django.utils.timezone
import random
from formtools.wizard.views import SessionWizardView
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.conf import settings
from aula.utils.decorators import group_required
from aula.apps.matricula.forms import peticioForm, DadesForm1, DadesForm2, DadesForm3, MatriculaForm, \
                EscollirCursForm, PagQuotesForm
from aula.apps.matricula.models import Peticio, Dades
from aula.apps.sortides.models import QuotaPagament, Quota
from aula.apps.alumnes.models import Alumne, Curs
from aula.apps.extPreinscripcio.models import Preinscripcio
from aula.apps.extSaga.models import ParametreSaga
from aula.apps.extUntis.sincronitzaUntis import creaGrup
from aula.apps.usuaris.models import OneTimePasswd

def get_url_alumne(usuari):
    '''
    Si l'usuari és un alumne i té una petició de matrícula acceptada que encara
    no ha omplert les dades retorna la url per omplir la informació
    en altre cas retorna None
    '''
    
    try:
        if usuari.alumne:
            p=Peticio.objects.filter(alumne=usuari.alumne, any=django.utils.timezone.now().year, estat='A')
            if p:
                p=p[0]
                if not p.dades:
                    return reverse_lazy('matricula:relacio_families__matricula__dades')
    except Exception:
        return None
    return None

def autoRalc(ident):
    '''
    Calcula Ralc per a alumnes que no tenen.
    ident identificador de l'alumne, normalment DNI
    Utilitza el paràmetre autoRalc de paràmetres Saga, crea un identificador 
    format per parametre + ident
    Retorna el ralc calculat 
    '''
    autoRalc, _ = ParametreSaga.objects.get_or_create( nom_parametre = 'autoRalc' )
    if bool(autoRalc.valor_parametre):
        ralc= autoRalc.valor_parametre + ident[-9:]
        return ralc
    return ident
    
def alumneExisteix(idalum):
    '''
    Retorna objecte Alumne que correspon a ralc=idalum
    Retorna None si no existeix
    '''
    ralc=idalum
    al=Alumne.objects.filter(ralc=ralc)
    if al:
        return al[0]
    ralc=autoRalc(idalum)
    al=Alumne.objects.filter(ralc=ralc)
    if al:
        return al[0]
    return None

def mailPeticio(estat, idalum, email, alumne=None):
    '''
    Envia email segons l'estat de la petició de matrícula
    estat de la petició ('P', 'R', 'A' o 'F')
    idalum identificador d'alumne
    email  adreça email destinataria
    alumne objecte Alumne si matrícula completada o None
    '''
    if estat=='A':
        #preparo el codi a la bd:
        clau = str( random.randint( 100000, 999999) ) + str( random.randint( 100000, 999999) )
        OneTimePasswd.objects.create(usuari = alumne.get_user_associat(), clau = clau)
        
        #envio missatge:
        urlDjangoAula = settings.URL_DJANGO_AULA
        username=alumne.get_user_associat().username
        url = "{0}/usuaris/recoverPasswd/{1}/{2}".format( urlDjangoAula, username, clau )
    else:
        username=''
        url=''
        
    assumpte = {
        'P': u"Petició de matrícula rebuda - {0}".format(settings.NOM_CENTRE ),
        'R': u"Petició de matrícula incorrecte - {0}".format(settings.NOM_CENTRE ),
        'A': u"Petició de matrícula vàlida - {0}".format(settings.NOM_CENTRE ),
        'F': u"Matrícula completada - {0}".format(settings.NOM_CENTRE ),
        }
    cosmissatge={
        'P': u"Hem rebut la seva petició de matrícula, un cop verificada rebrà un email amb noves instruccions.",
        'R': u"La seva petició de matrícula no correspon a cap preinscripció. No és possible fer el tràmit.",
        'A': u"\n".join(
            [u"El motiu d'aquest correu és el de donar-vos les instruccions per a realitzar la matrícula al nostre centre.",
            u"El primer pas es obtenir la contrasenya:",
            u" * Entreu a {0} on podeu escollir la vostra contrasenya.".format(url),
            u" * Una vegada accediu a l'aplicació podreu continuar la matrícula",
            u"",
            u"Sempre podreu accedir a l'aplicació {0} amb el vostre usuari {1} i la contrasenya escollida".format(settings.URL_DJANGO_AULA, username ),]
            ),
        'F': u"La matrícula de l'alumne {0} ha finalitzat correctament.".format(str(alumne)),
        }
    missatge = [u"Aquest missatge ha estat enviat per un sistema automàtic. No respongui a aquest e-mail, el missatge no serà llegit per ningú.",
                u"",
                u"Benvolgut/da,",
                u"",
                cosmissatge.get(estat),
                u"",
                u"Cordialment,",
                u"",
                settings.NOM_CENTRE,
                ]                        
    fromuser = settings.DEFAULT_FROM_EMAIL
    if settings.DEBUG:
        print (u'Enviant recepció de petició a {0}'.format( idalum ))
    try:
        send_mail(assumpte.get(estat), 
                  u'\n'.join( missatge ), 
                  fromuser,
                  (email,), 
                  fail_silently=False)
    except Exception as e:
        print("Error send_mail petició "+str(e))

def creaAlumne(idalum, tipus, curs, email):
    '''
    Crea l'alumne, assigna grup sense lletra. Activa l'usuari per a poder fer Login.
    idalum identificador d'alumne
    tipus 'R' Ralc o 'D' DNI
    curs  objecte Curs de l'alumne
    email  adreça email destinataria
    Retorna objecte Alumne
    '''
    
    al=alumneExisteix(idalum)
    if al:
        return al
    al=Alumne()
    if tipus=='D':
        al.ralc=autoRalc(idalum)
    else:
        al.ralc=idalum
    grup , _ = creaGrup(curs.nivell.nom_nivell,curs.nom_curs,'-',None,None)
    al.grup=grup
    al.correu_tutors=email
    al.correu_relacio_familia_pare=email
    al.tutors_volen_rebre_correu=True
    al.save()
    al.user_associat.is_active=True
    al.user_associat.save()
    return al

def creaPagament(alumne, quota):
    '''
    Crea pagament de la quota per a l'alumne
    '''
    
    p=QuotaPagament.objects.filter(alumne=alumne, quota=quota)
    if not p:
        p=QuotaPagament(alumne=alumne, quota=quota)
        p.save()

def peticio(request):
    '''
    View per a fer la petició de matrícula
    Crea Peticio pendent (tipus 'P') amb les dades i envia email de confirmació de recepció.
    Si es una petició repetida, acceptada prèviament, la marca com duplicada 'D'.
    '''
    
    if request.method == 'POST':
        form = peticioForm(request.POST)
        if form.is_valid():
            infos=[]
            errors=[]
            novaPeticio=form.save()
            toaddress = novaPeticio.email
            idalum = novaPeticio.idAlumne
            if novaPeticio.tipusIdent=='R':
                p=Preinscripcio.objects.filter(ralc=idalum, correu=toaddress)
                if not p:
                    estat='P'
                else:
                    estat='A'
            else:
                p=Preinscripcio.objects.filter(identificador=idalum, correu=toaddress)
                if not p:
                    estat='P'
                else:
                    estat='A'
                    idalum=p[0].ralc
            if estat=='A':
                alumne=creaAlumne(idalum, 'R', novaPeticio.curs, toaddress)
                quotacurs=Quota.objects.filter(curs=novaPeticio.curs, any=novaPeticio.any)
                if quotacurs:
                    quotacurs=quotacurs[0]
                    creaPagament(alumne, quotacurs)
                    novaPeticio.quota=quotacurs
                novaPeticio.alumne=alumne
                novaPeticio.estat='A'
                novaPeticio.save()
                mailPeticio('A', idalum, toaddress, alumne)
            else:
                mailPeticio('P', idalum, toaddress)
                    
            p=Peticio.objects.filter(idAlumne=idalum, any=novaPeticio.any, estat__in=('A',))
            if alumneExisteix(idalum) and p:
                # Si ja existeix una petició acceptada
                Peticio.objects.filter(idAlumne=idalum, any=novaPeticio.any, estat__in=('P','R',)).update(estat='D')
            
            infos.append('Petició rebuda, un cop verificada rebrà un email amb noves instruccions.')
            
            return render(
                        request,
                        'resultat.html', 
                        {'msgs': {'errors': errors, 'warnings': [], 'infos': infos} },
                     )
    else:
        form = peticioForm()
    return render(request, 'peticio.html', {'form': form})
    
class PeticioDetail(LoginRequiredMixin, UpdateView):
    '''
    View per editar una Peticio
    Al finalitzar mostra la següent
    '''
    
    model = Peticio
    template_name='peticio_form.html'
    fields = ['idAlumne', 'tipusIdent', 'email', 'curs', 'estat', 'quota']
    
    def get_success_url(self):
        pk=self.object.pk
        queryset = Peticio.objects.filter(pk__gt=pk, estat='P', any=django.utils.timezone.now().year)
        if queryset:
            pk=queryset[0].pk
            return reverse_lazy("matricula:gestio__peticions__pendents", kwargs={"pk": pk})
        else:
            queryset = Peticio.objects.filter(estat='P', any=django.utils.timezone.now().year)
            if queryset:
                pk=queryset[0].pk
                return reverse_lazy("matricula:gestio__peticions__pendents", kwargs={"pk": pk})
            return reverse_lazy('matricula:gestio__peticions__pendents')

    def get_form(self, form_class=None):
        form = super(PeticioDetail, self).get_form(form_class)
        form.fields['curs'].queryset = form.fields['curs'].queryset.order_by('nom_curs_complert')
        form.fields['quota'].required = True
        form.fields['quota'].queryset = form.fields['quota'].queryset.order_by('descripcio')
        form.fields['estat'].choices = [('A','Acceptada'), ('R','Rebutjada'),]
        return form

    def form_valid(self, form):
        '''
        Envia el email amb la resposta a la petició
            si estat R Rebutjada
            si estat A Acceptada
                Crea un Alumne per a la petició
            si estat F Finalitzada
        '''
        
        self.object = form.save()
        estat=self.object.estat
        idalum=self.object.idAlumne
        email=self.object.email
        if estat=='R':
            mailPeticio(estat, idalum, email)
        if estat=='A':
            Peticio.objects.filter(idAlumne=idalum, any=self.object.any, estat__in=('P','R',)).update(estat='D')
            alumne=creaAlumne(idalum, self.object.tipusIdent, self.object.curs, email)
            creaPagament(alumne, self.object.quota)
            self.object.alumne=alumne
            self.object.save()
            mailPeticio(estat, idalum, email, alumne)
        return super().form_valid(form)

@login_required
@group_required(['direcció','administradors'])
def PeticiobyId(request, pk=None):
    return PeticioDetail.as_view()(request, pk=pk)

@login_required
@group_required(['direcció','administradors'])
def PeticioVerifica(request):
    '''
    View que verifica les peticions
    Mostra una petició pendent de verificació
    '''
    
    queryset = Peticio.objects.filter(estat='P', any=django.utils.timezone.now().year)
    if queryset:
        pk=queryset[0].pk
        return PeticioDetail.as_view()(request, pk=pk)
    else:
        infos=[]
        infos.append('Sense peticions pendents de verificació')
        return render(
                    request,
                    'resultat.html', 
                    {'msgs': {'errors': [], 'warnings': [], 'infos': infos} },
                 )

class DadesView(LoginRequiredMixin, SessionWizardView):
    form_list = [DadesForm1, DadesForm2, DadesForm3]
    template_name = 'dades_form.html'
    file_storage = FileSystemStorage(location=settings.PRIVATE_STORAGE_ROOT)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titol'] = self.kwargs.get('titol', None)
        context['pagfet'] = self.kwargs.get('pagfet', None)=='True'
        return context

    def done(self, form_list, **kwargs):
        data=self.get_all_cleaned_data()
        if 'pk' in kwargs:
            iddata = kwargs['pk']
            item = Dades.objects.get(pk=iddata)
        else:
            item = Dades()
        for field, value in iter(data.items()):
            setattr(item, field, value)

        item.save()
        p=Peticio.objects.filter(alumne=self.request.user.alumne, estat='A', any=django.utils.timezone.now().year)[0]
        p.dades=item
        p.save()
        infos=[]
        if "quota" in self.request.POST:
            # redirect pagament online
            pagament=QuotaPagament.objects.filter(alumne=p.alumne, quota=p.quota)[0]
            return (HttpResponseRedirect(reverse_lazy('sortides__sortides__pago_on_line',
                                        kwargs={'pk': pagament.id})+'?next=/')) #'?next='+str(self.request.get_full_path())))
        else:
            pagament=QuotaPagament.objects.filter(alumne=p.alumne, quota=p.quota)
            if not pagament or not pagament[0].pagament_realitzat:
                infos.append('Dades completades, falta el pagament de la quota.')
            else:
                infos.append('Dades completades, rebrà un mail amb el resultat.')
                
        return render(
                    self.request,
                    'resultat.html', 
                    {'msgs': {'errors': [], 'warnings': [], 'infos': infos} },
                 )

def dadesAntigues(alumne):
    d=Dades()
    p=Preinscripcio.objects.filter(ralc=alumne.ralc)
    if p:
        p=p[0]
        d.nom=p.nom
        d.cognoms=p.cognoms
        d.centre_de_procedencia=p.centreprocedencia
        d.data_naixement=p.naixement
        d.alumne_correu=p.correu
        d.adreca=p.adreça
        d.localitat=p.localitat
        d.cp=p.cp
        d.rp1_nom=p.nomtut1+" "+p.cognomstut1
        d.rp1_telefon1=p.telefon
        d.rp1_correu=p.correu
        d.rp2_nom=p.nomtut2+" "+p.cognomstut2
    else:
        d.nom=alumne.nom
        d.cognoms=alumne.cognoms
        d.centre_de_procedencia=alumne.centre_de_procedencia
        d.data_naixement=alumne.data_neixement
        d.alumne_correu=alumne.correu
        d.adreca=alumne.adreca
        d.localitat=alumne.localitat
        d.cp=alumne.cp
        d.rp1_nom=alumne.rp1_nom
        d.rp1_telefon1=alumne.rp1_mobil if alumne.rp1_mobil else alumne.rp1_telefon
        d.rp1_correu=alumne.rp1_correu
        d.rp2_nom=alumne.rp2_nom
        d.rp2_telefon1=alumne.rp2_mobil if alumne.rp2_mobil else alumne.rp2_telefon
        d.rp2_correu=alumne.rp2_correu
    return d

def updateAlumne(alumne, dades):
    alumne.nom=dades.nom
    alumne.cognoms=dades.cognoms
    alumne.centre_de_procedencia=dades.centre_de_procedencia if dades.centre_de_procedencia else ''
    alumne.data_neixement=dades.data_naixement
    alumne.correu=dades.alumne_correu
    alumne.adreca=dades.adreca
    alumne.localitat=dades.localitat
    alumne.cp=dades.cp
    alumne.rp1_nom=dades.rp1_nom
    alumne.rp1_telefon=dades.rp1_telefon1
    alumne.rp1_correu=dades.rp1_correu
    alumne.rp2_nom=dades.rp2_nom if dades.rp2_nom else ''
    alumne.rp2_telefon=dades.rp2_telefon1 if dades.rp2_telefon1 else ''
    alumne.rp2_correu=dades.rp2_correu if dades.rp2_correu else ''
    alumne.correu_relacio_familia_pare = alumne.rp1_correu
    alumne.correu_relacio_familia_mare = alumne.rp2_correu
    alumne.save()

@login_required
def OmpleDades(request, pk=None):
    user=request.user
    infos=[]
    try:
        if user.alumne:
            p=Peticio.objects.filter(alumne=user.alumne, any=django.utils.timezone.now().year).exclude(estat='D')
            if p:
                p=p[0]
                if p.estat=='A':
                    pagament=QuotaPagament.objects.filter(alumne=p.alumne, quota=p.quota)[0]
                    pagfet=str(pagament.pagament_realitzat)
                    if p.dades:
                        item=p.dades
                    else:
                        item=dadesAntigues(p.alumne)
                        item.rp1_correu=p.email
                    nomAlumne=(item.nom+" "+item.cognoms) if item.nom or item.cognoms else p.idAlumne
                    titol="Dades de matrícula de "+nomAlumne+" a "+p.curs.nom_curs_complert
                    #get the initial data to include in the form
                    fields0 = ['nom','cognoms','centre_de_procedencia','data_naixement','alumne_correu','adreca','localitat','cp',]
                    fields1 = ['rp1_nom','rp1_telefon1','rp1_correu','rp2_nom','rp2_telefon1','rp2_correu',]
                    fields2 = ['acceptar_condicions','files',]
                    initial = {'0': dict([(f,getattr(item,f)) for f in fields0]),
                               '1': dict([(f,getattr(item,f)) for f in fields1]),
                               '2': dict([(f,getattr(item,f)) for f in fields2]),
                    }
                    initial['2']['acceptar_condicions']=False
                    if item.pk:
                        return DadesView.as_view(initial_dict=initial)(request, pk=item.pk, titol=titol, pagfet=pagfet)
                    else:
                        return DadesView.as_view(initial_dict=initial)(request, titol=titol, pagfet=pagfet)
                else:
                    if p.estat=='F':
                        infos.append('Matrícula finalitzada. No fan falta més dades.')
                    else:
                        infos.append('Petició pendent de verificació.')
            else:
                infos.append('Sense dades necessàries')
        else:
            infos.append('Sense dades necessàries')
    except Exception as e:
        print(str(e))
        infos.append('Error a l\'accedir a les dades de matrícula: '+str(e))
        
    return render(
                request,
                'resultat.html', 
                {'msgs': {'errors': [], 'warnings': [], 'infos': infos} },
             )

class DadesShow(LoginRequiredMixin, DetailView):
    model = Dades
    template_name='dades_detail.html'
    fields = '__all__'

@login_required
@group_required(['direcció','administradors'])
def DadesbyId(request, pk=None):
    return DadesShow.as_view()(request, pk=pk)

@login_required
@group_required(['direcció','administradors'])
def changeEstat(request, pk):
    p=Peticio.objects.get(pk=pk)
    p.estat='F'
    p.save()
    updateAlumne(p.alumne, p.dades)
    mailPeticio(p.estat, p.idAlumne, p.email)
    return HttpResponseRedirect(reverse_lazy('matricula:gestio__confirma__matricula'))

@login_required
def condicions(request):
    f = open(settings.CONDICIONS_MATRICULA, 'r', encoding='UTF-8')
    file_content = f.read()
    f.close()
    file_content = "<br />".join(file_content.split("\n"))
    return render(
                request,
                'file_form.html', 
                {'dat': file_content },
             )

class MatriculesView(LoginRequiredMixin, ListView):
    model = Dades
    template_name='dades_list.html'
    form_class = MatriculaForm
    #paginate_by = 3
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titol'] = 'Matrícules pendents de confirmació'
        return context
    
    def get_queryset(self):
        return Dades.objects.filter(peticio__any=django.utils.timezone.now().year, peticio__estat='A', acceptar_condicions=True).order_by('peticio__curs', 'cognoms')
    
@login_required
@group_required(['direcció','administradors'])
def LlistaMat(request):
    return MatriculesView.as_view()(request)

class MatriculesList(LoginRequiredMixin, ListView):
    model = Dades
    template_name='dades_list.html'
    form_class = MatriculaForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titol'] = 'Matrícules'
        return context
        
    def get_queryset(self):
        return Dades.objects.filter(peticio__any=django.utils.timezone.now().year).order_by('peticio__curs', 'cognoms')

@login_required
@group_required(['direcció','administradors'])
def LlistaMatFinals(request):
    return MatriculesList.as_view()(request)

@login_required
@group_required(['direcció','administradors'])
def assignaQuotes(request):
    if request.method == 'POST':
        form = EscollirCursForm(request.POST)
        if form.is_valid():
            curs=form.cleaned_data['curs_list']
            return HttpResponseRedirect(reverse_lazy("matricula:gestio__assigna__quotes", kwargs={"curs": curs.id}))
    else:
        form = EscollirCursForm()
    return render(
                request,
                'form.html', 
                {'form': form, 
                 },
                )

@login_required
@group_required(['direcció','administradors'])
def quotesCurs( request, curs ):
    #Mateix sistema que alumnes.views.assignaTutors 
    formset = []
    if request.method == "POST":

        for a in Alumne.objects.filter(grup__curs__id=curs).exclude(grup__nom_grup='-').order_by('grup', 'cognoms', 'nom'):
            form=PagQuotesForm(request.POST,
                               prefix=str( a.pk )
                            )
            formset.append( form )
            if form.is_valid():
                quota = form.cleaned_data['quota']
                if quota:
                    fet_act=False
                    pagament=a.get_pagamentQuota
                    if pagament:
                        fet_act=pagament.pagament_realitzat
                    if not fet_act:
                        p=QuotaPagament.objects.filter(alumne=a, quota__id=quota.pk)
                        QuotaPagament.objects.filter(alumne=a, quota__any=django.utils.timezone.now().year).exclude(quota__id=quota.pk).exclude(pagament_realitzat=True).delete()
                        if not p:
                            quota=Quota.objects.get(pk=quota.pk)
                            p=QuotaPagament(alumne=a, quota=quota)
                            p.save()
     
    else:
        c=Curs.objects.get(id=curs)
        try:
            ncurs=str(int(c.nom_curs)+1)
            quotacurs=Quota.objects.filter(curs__nivell=c.nivell, curs__nom_curs=ncurs, any=django.utils.timezone.now().year)
        except:
            quotacurs=None
        if quotacurs:
            quotacurs=quotacurs[0]
        else:
            quotacurs=None
        for a in Alumne.objects.filter(grup__curs__id=curs).exclude(grup__nom_grup='-').order_by('grup', 'cognoms', 'nom'):
            pagament=a.get_pagamentQuota
            if pagament:
                quota=pagament.quota
                fet=pagament.pagament_realitzat
                estat='Ja pagat' if fet else 'Pendent'
            else:
                quota=quotacurs
                fet=False
                estat='No assignat'
            form=PagQuotesForm(
                                    prefix=str( a.pk ),
                                    initial={'cognoms': a.cognoms,
                                             'nom':  a.nom ,
                                             'grup': a.grup,
                                             'correu': a.correu_relacio_familia_pare,
                                             'quota':quota,
                                             'pagament': fet,
                                             'estat': estat
                                             } )            
            formset.append( form )
            
    return render(
                    request,
                  "formsetgrid.html", 
                  { "formset": formset,
                    "head": "Assignació quotes",
                   }
                )
