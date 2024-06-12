from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.views.generic.edit import UpdateView
from django.views.generic import ListView
from django.urls import reverse_lazy
from django.utils.html import format_html
from django.http import HttpResponseRedirect
import django.utils.timezone
from formtools.wizard.views import SessionWizardView
from aula.utils.decorators import group_required
from aula.apps.matricula.forms import DadesForm1, DadesForm2, DadesForm2b, DadesForm3, \
                                    ConfirmaMat, escollirMat
from aula.apps.matricula.models import Document, Matricula
from aula.apps.sortides.models import QuotaPagament, QuotaCentre, TPV
from aula.apps.alumnes.models import Curs
from aula.apps.extPreinscripcio.models import Preinscripcio
from aula.apps.extUntis.sincronitzaUntis import creaGrup
from django.conf import settings
from aula.apps.matricula.viewshelper import situacioMat, mailMatricula, següentCurs, quotaSegüentCurs, \
        enviaMissatge, gestionaPag, alumne2Mat, updateAlumne, getCanvis, mat_selecciona, next_mat, inforgpd, \
        enviaIniciMat, ResumLlistat

@login_required
@group_required(['direcció','administradors'])
def LlistaMatConf(request):
    '''
    Selecciona els paràmetres per a la verificació de matrícules
    '''
    from aula.apps.matricula.forms import EscollirMatsForm

    if request.method == 'POST':
        form = EscollirMatsForm(request.user, request.POST)
        if form.is_valid():
            idcurs=form.cleaned_data['curs'].id
            nany=form.cleaned_data['year']
            tipus=form.cleaned_data['tipus']
            queryset = Matricula.objects.filter( mat_selecciona(idcurs, nany, tipus) ).order_by('curs__nom_curs_complert', 'cognoms', 'nom')
            if not queryset:
                infos=[]
                infos.append('Sense matrícules pendents de verificació')
                return render(
                            request,
                            'resultat.html', 
                            {'msgs': {'errors': [], 'warnings': [], 'infos': infos} },
                         )
            if tipus=='C':
                pk=queryset[0].pk
                return HttpResponseRedirect(reverse_lazy("matricula:gestio__matricula__llistat", 
                                kwargs={"pk": pk, 'curs':idcurs, 'nany':nany, 'tipus':tipus},
                                ))
            else:
                return HttpResponseRedirect(reverse_lazy("matricula:gestio__matricula__llistat", 
                                kwargs={'curs':idcurs, 'nany':nany, 'tipus':tipus},
                                ))
    else:
        form = EscollirMatsForm(request.user)
    return render(
                request,
                'form.html', 
                {'form': form, 
                 },
            )

class ConfirmaDetail(LoginRequiredMixin, UpdateView):
    '''
    View per editar una Matrícula
    Al finalitzar mostra la següent
    '''
    
    model = Matricula
    template_name='confirma_detail.html'
    fields = ['nom','cognoms','curs','data_naixement','alumne_correu','adreca','localitat','cp',
              'rp1_nom','rp1_telefon','rp1_correu','rp2_nom','rp2_telefon','rp2_correu',
              'confirma_matricula']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titol'] = 'Matrícules confirmades'
        return context
        
    def get_success_url(self):
        pk=self.object.pk
        idcurs=self.kwargs.get('curs', None)
        nany=self.kwargs.get('nany', django.utils.timezone.now().year)
        tipus=self.kwargs.get('tipus', 'C')
        nextpk=next_mat(pk, idcurs, nany, tipus)
        if nextpk:
            return reverse_lazy("matricula:gestio__matricula__llistat", 
                                kwargs={"pk": nextpk, 'curs':idcurs, 'nany':nany, 'tipus':tipus},
                                )
        else:
            return reverse_lazy('matricula:gestio__matricula__llistat')
    
    def get_initial(self):
        base_initial = super().get_initial()
        base_initial['curs'] = següentCurs(self.object.alumne)
        return base_initial
            
    def get_form(self, form_class=None):
        form = super(ConfirmaDetail, self).get_form(form_class)
        modificats=getCanvis(self.object.pk)
        for f in self.fields:
            form.fields[f].widget.attrs['readonly'] = True
            if f in modificats: form.fields[f].widget.attrs.update({'class': 'alert alert-info'})
            else: form.fields[f].widget.attrs.update({'class': 'alert alert-success'})
            form.fields[f].widget.attrs.update({'style': 'padding: 0.5rem 0.5rem'})
        form.fields['confirma_matricula'].widget.attrs.update({'disabled': 'disabled'})
        form.fields['curs'].widget.attrs.pop('class', None)
        form.fields['curs'].widget.attrs['readonly'] = False
        return form
    
    def form_valid(self, form):
        self.object = form.save()
        self.object.estat='F'
        self.object.confirma_matricula='C'
        self.object.save()
        updateAlumne(self.object.alumne, self.object)
        gestionaPag(self.object, 0)
        mailMatricula(self.object.estat, self.object.curs, 
                      self.object.alumne.get_correus_relacio_familia(), self.object.alumne)
        return HttpResponseRedirect(self.get_success_url())

@login_required
@group_required(['direcció','administradors'])
def VerificaConfirma(request, pk, curs, nany, tipus):
    return ConfirmaDetail.as_view()(request, pk=pk, curs=curs, nany=nany, tipus=tipus)

@login_required
def Confirma(request, nany):
    user=request.user
    infos=[]
    try:
        if user.alumne:
            nany=django.utils.timezone.now().year
            info = situacioMat(user.alumne, nany)
            if info=='D':
                return HttpResponseRedirect(reverse_lazy('matricula:relacio_families__matricula__escollir'))
            if info=='M':
                return HttpResponseRedirect(reverse_lazy('matricula:relacio_families__matricula__dades'))
            if info=='C':
                mat=alumne2Mat(user.alumne, nany)
                mat.save()
                if request.method == 'POST':
                    form = ConfirmaMat(request.user, request.POST, instance=mat)
                    if form.is_valid():
                        infos=[]
                        item=form.save()
                        item.confirma_matricula=form.cleaned_data['opcions']
                        item.acceptacio_en=django.utils.timezone.now()
                        item.quota=quotaSegüentCurs(settings.CUSTOM_TIPUS_QUOTA_MATRICULA, nany, user.alumne)
                        item.save()
                        if item.confirma_matricula=='C' and item.quota:
                            gestionaPag(item, 0)
                            url=format_html("<a href='{}'>{}</a>",
                                            reverse_lazy('relacio_families__informe__el_meu_informe'),
                                            'Activitats/Pagaments')            
                            infos.append('Dades guardades correctament. '\
                                         'Una vegada siguin revisades per secretaria rebrà un missatge. ' \
                                         'Gestioni els pagaments des de l\'apartat '+url)
                        else:
                            infos.append('Dades guardades correctament. ' \
                                         'Una vegada siguin revisades per secretaria rebrà un missatge.')
                        return render(
                                    request,
                                    'resultat.html', 
                                    {'msgs': {'errors': [], 'warnings': [], 'infos': infos} },
                                 )
                else:
                    form = ConfirmaMat(request.user, instance=mat, 
                                       initial={'acceptar_condicions':False,
                                                'opcions':mat.confirma_matricula,
                                                })
                return render(request, 'confirma_form.html', {'form': form, 'curs':mat.curs, 'quota':mat.quota, 
                                                              'rgpd':inforgpd(), })
            else:
                infos.append(info)
        else:
            infos.append('Sense necessitat de dades.')
        
    except Exception as e:
        print(str(e))
        infos.append('Error en la confirmació de matrícula: '+str(e))
        
    return render(
                request,
                'resultat.html', 
                {'msgs': {'errors': [], 'warnings': [], 'infos': infos} },
             )

@login_required
@group_required(['direcció','administradors'])
def changeEstat(request, pk, tipus):
    '''
    Modifica estat a F.
    Envia email de confirmació a la família
    '''
    mat=Matricula.objects.get(pk=pk)
    if not mat.acceptar_condicions and mat.confirma_matricula!='N':
        # No hauria de passar mai, però per si la llei de Murphy
        errors=[]
        errors.append('No es pot finalitzar matrícula que no té acceptades les condicions')
        enviaMissatge('No es pot finalitzar matrícula:{0}-{1}. No té acceptades les condicions.'.format(mat.idAlumne,mat.any))
        return render(
                        request,
                        'resultat.html', 
                        {'msgs': {'errors': errors, 'warnings': [], 'infos': []} },
                     )
    if not mat.acceptacio_en and mat.confirma_matricula!='N':
        mat.acceptacio_en=django.utils.timezone.now()
    mat.estat='F'
    mat.save()
    updateAlumne(mat.alumne, mat)
    if mat.confirma_matricula!='N':
        mailMatricula(mat.estat, mat.alumne.grup.curs, mat.alumne.get_correus_relacio_familia(), mat.alumne)
    return HttpResponseRedirect(reverse_lazy("matricula:gestio__matricula__llistat", 
                                kwargs={'curs':mat.curs.id, 'nany':mat.any, 'tipus':tipus},
                                ))

@login_required
def condicions(request):
    '''
    Mostra les condicions de Matricula segons settings.CONDICIONS_MATRICULA 
    '''
    f = open(settings.CONDICIONS_MATRICULA, 'r', encoding='UTF-8')
    file_content = f.read()
    f.close()
    file_content = "<br />".join(file_content.split("\n"))
    return render(
                request,
                'file_form.html', 
                {'dat': file_content },
             )

class MatriculesList(LoginRequiredMixin, ListView):
    '''
    Mostra les matrícules segons curs, nany i tipus
    '''
    
    model = Matricula
    template_name='dades_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tipus=self.kwargs.get('tipus', 'A')
        opcions={'T':'','C':'confirmades','N':'no confirmades', 'A':'pendents de finalitzar', 'F':'finalitzades'}
        context['titol'] = 'Matrícules '+opcions.get(tipus)
        context['tipus'] = tipus
        return context
        
    def get_queryset(self):
        idcurs=self.kwargs.get('curs', None)
        nany=self.kwargs.get('nany', django.utils.timezone.now().year)
        tipus=self.kwargs.get('tipus', 'A')
        tipusfiltre = mat_selecciona(idcurs, nany, tipus)
        return Matricula.objects.filter(tipusfiltre).order_by('curs__nom_curs_complert', 'cognoms', 'nom')

@login_required
@group_required(['direcció','administradors'])
def LlistaMatFinals(request, curs, nany, tipus):
    return MatriculesList.as_view()(request, curs=curs, nany=nany, tipus=tipus)

class DadesView(LoginRequiredMixin, SessionWizardView):
    '''
    Omple les dades de la Matrícula
    '''
    #form_list = [DadesForm1, DadesForm2, DadesForm2b, DadesForm3]
    template_name = 'dades_form.html'
    file_storage = FileSystemStorage(location=settings.PRIVATE_STORAGE_ROOT)

    
    def process_step_files(self, form):
        """
        This method is used to postprocess the form files. By default, it
        returns the raw `form.files` dictionary.
        """
        import unicodedata
        
        files = form.files
        pk = self.kwargs.get('pk', None)
        mat=Matricula.objects.get(pk=pk)
        for key in files.keys():
            for value in files.getlist(key):
                # Elimina accents
                newname=unicodedata.normalize('NFKD',value.name).encode('ascii','ignore').decode('UTF-8')
                if value.name!=newname:
                    value.name=newname
                file_instance = Document(fitxer=value)
                file_instance.matricula=mat
                file_instance.save()
        return self.get_form_step_files(form)
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titol'] = self.kwargs.get('titol', None)
        pk = self.kwargs.get('pk', None)
        mat=Matricula.objects.get(pk=pk)
        pagament=QuotaPagament.objects.filter(alumne=mat.alumne, quota=mat.quota).order_by('dataLimit')
        context['pagament'] = pagament[0] if pagament else None
        context['matricula'] = mat
        context['rgpd']=inforgpd()
        return context

    def get_form_initial(self, step):
        pk = self.kwargs.get('pk', None)
        mat=Matricula.objects.get(pk=pk)
        dictf0=self.initial_dict.get(step, {})
        dictf0['matricula']=mat
        if step == '3' or (step == '2' and self.steps.count==3):
            total=0
            if step == '3': 
                step2data = self.get_cleaned_data_for_step('2')
                if step2data:
                    complet = step2data.get('curs_complet', False)
                    ufs = step2data.get('quantitat_ufs', 0)
                    bonif = step2data.get('bonificacio', '0')
                    taxes=mat.curs.nivell.taxes
                    tcomplet=QuotaCentre.objects.filter(any=mat.any, tipus__nom='taxcurs')
                    tuf=QuotaCentre.objects.filter(any=mat.any, tipus__nom='uf')
                    total=0
                    if complet and taxes and tcomplet:
                        total=tcomplet[0].importQuota
                    else:
                        if taxes and tuf and ufs>0:
                            total=ufs*tuf[0].importQuota
                            if total>tcomplet[0].importQuota:
                                total=tcomplet[0].importQuota
                    if bonif=='5':
                        total=total/2
                    if bonif=='1':
                        total=0
            step0data = self.get_cleaned_data_for_step('0')
            if step0data:
                curs = step0data.get('curs', None)
                quotamat=QuotaCentre.objects.filter(curs=curs, any=mat.any, tipus__nom=settings.CUSTOM_TIPUS_QUOTA_MATRICULA)
                if quotamat: quotamat=quotamat[0]
            else:
                quotamat=None
            dictf3=self.initial_dict.get(step, {})
            dictf3['importTaxes']=total
            dictf3['quotaMat']=quotamat.importQuota if quotamat else None
            dictf3['matricula']=mat
            docs=list(Document.objects.filter(matricula=mat).order_by('pk').values_list('fitxer', flat=True))
            files=[]
            for d in docs:
                files.append(d)
            dictf3['documents']=files
            return dictf3
        return dictf0
   
    def done(self, form_list, **kwargs):
        from decimal import Decimal
        
        data=self.get_all_cleaned_data()
        
        esborra=data.get('fitxers',[])
        pk = self.kwargs.get('pk', None)
        fitxers=Document.objects.filter(matricula__id=pk).order_by('pk')
        for n in esborra[::-1]:
            f=fitxers[n-1]
            f.fitxer.delete()
            f.delete()
        
        if 'pk' in kwargs:
            pk = kwargs['pk']
            mat=Matricula.objects.get(pk=pk)
        else:
            mat=Matricula()
        
        ac=data.get('acceptar_condicions',False)
        if ac and not mat.acceptar_condicions:
            mat.acceptacio_en=django.utils.timezone.now()
                
        for field, value in iter(data.items()):
            setattr(mat, field, value)
        
        if mat.curs_complet:
            mat.quantitat_ufs=0
            mat.llistaufs=None
        mat.save()

        importTaxes=Decimal(data.get('importTaxes',''))
        infos=[]
        url_next=[]
        gestionaPag(mat, importTaxes)
        grup , _ = creaGrup(mat.curs.nivell.nom_nivell,mat.curs.nom_curs,'-',None,None)
        mat.alumne.grup=grup
        mat.alumne.save()
        url=format_html("<a href='{}'>{}</a>",
                  reverse_lazy('relacio_families__informe__el_meu_informe'),
                  'Activitats/Pagaments')            
        infos.append('Dades completades, una vegada siguin revisades per secretaria rebrà un missatge. Es poden afegir més documents tornant a l\'opció de Matrícula. '\
                     'Gestioni els pagaments des de l\'apartat '+url)
            
        return render(
                    self.request,
                    'resultat.html', 
                    {'msgs': {'errors': [], 'warnings': [], 'infos': infos, 'url_next':url_next} },
                 )

@login_required
def OmpleDades(request):
    '''
    Omple la Matrícula de l'alumne
    '''
    user=request.user
    infos=[]
    try:
        if user.alumne:
            nany=django.utils.timezone.now().year
            info = situacioMat(user.alumne, nany)
            if info=='D':
                return HttpResponseRedirect(reverse_lazy('matricula:relacio_families__matricula__escollir'))
            if info=='C':
                return HttpResponseRedirect(reverse_lazy('matricula:relacio_families__matricula__confirma',kwargs={'nany':nany}))
            if info=='M':
                # Matrícula segons preinscripcio o de continuitat
                p=Preinscripcio.objects.filter(ralc=user.alumne.ralc, any=nany, estat='Enviada')
                mat=alumne2Mat(user.alumne, nany, p)
                mat.save()
                if mat.estat=='A':
                    nomAlumne=(mat.nom+" "+mat.cognoms) if mat.nom and mat.cognoms else mat.idAlumne
                    titol="Dades de matrícula de "+nomAlumne+" a "+mat.curs.nivell.nom_nivell+ \
                                               (("("+mat.preinscripcio.torn+")") if mat.preinscripcio else '')
                    #get the initial data to include in the form
                    fields0 = ['curs','nom','cognoms','centre_de_procedencia','data_naixement','alumne_correu','adreca','localitat','cp',]
                    fields1 = ['rp1_nom','rp1_telefon','rp1_correu','rp2_nom','rp2_telefon','rp2_correu',]
                    fields2 = ['curs_complet', 'quantitat_ufs', 'bonificacio', 'llistaufs',]
                    fields3 = ['fracciona_taxes', 'acceptar_condicions',]
                    if mat.curs.nivell.nom_nivell in settings.CUSTOM_NIVELLS['CICLES']:
                        form_list = [DadesForm1, DadesForm2, DadesForm2b, DadesForm3]
                        initial = {'0': dict([(f,getattr(mat,f)) for f in fields0]),
                                   '1': dict([(f,getattr(mat,f)) for f in fields1]),
                                   '2': dict([(f,getattr(mat,f)) for f in fields2]),
                                   '3': dict([(f,getattr(mat,f)) for f in fields3]),
                                   }
                    else:
                        form_list = [DadesForm1, DadesForm2, DadesForm3]
                        initial = {'0': dict([(f,getattr(mat,f)) for f in fields0]),
                                   '1': dict([(f,getattr(mat,f)) for f in fields1]),
                                   '3': dict([(f,getattr(mat,f)) for f in fields3]),
                                   }
                    initial['3']['acceptar_condicions']=False
                    return DadesView.as_view(initial_dict=initial, form_list=form_list)(request, pk=mat.pk, titol=titol)
            else:
                infos.append(info)
        else:
            infos.append('Sense necessitat de dades.')
    except Exception as e:
        print(str(e))
        infos.append('Error accedint a les dades de matrícula: '+str(e))
        
    return render(
                request,
                'resultat.html', 
                {'msgs': {'errors': [], 'warnings': [], 'infos': infos} },
             )

@login_required
def matDobleview(request):
    user=request.user
    infos=[]
    if user.alumne:
        nany=django.utils.timezone.now().year
        info = situacioMat(user.alumne, nany)
        if info=='D':
            if request.method == 'POST':
                form = escollirMat(request.user, user.alumne, nany, request.POST)
                if form.is_valid():
                    escollida=form.cleaned_data['escollida']
                    if escollida=='M':
                        Preinscripcio.objects.filter(ralc=user.alumne.ralc, any=nany, estat='Enviada').update(estat='Caducada')
                    else:
                        p=Preinscripcio.objects.get(ralc=user.alumne.ralc, any=nany, estat='Enviada')
                        mt=Matricula.objects.get(alumne=user.alumne, any=nany)
                        curs=p.getCurs()
                        QuotaPagament.objects.filter(alumne=user.alumne, quota__any=nany,
                             quota__tipus__nom__in=[curs.nivell.taxes, settings.CUSTOM_TIPUS_QUOTA_MATRICULA,],
                             pagament_realitzat=False).delete()
                        mt.estat='A'
                        mt.curs=curs
                        q=QuotaCentre.objects.filter(curs=mt.curs, any=nany, tipus__nom=settings.CUSTOM_TIPUS_QUOTA_MATRICULA)
                        mt.quota=q[0] if q else None
                        mt.acceptar_condicions='False'
                        mt.acceptacio_en=None
                        mt.confirma_matricula=None
                        mt.preinscripcio=p
                        mt.save()
                    return HttpResponseRedirect(reverse_lazy('matricula:relacio_families__matricula__dades'))
            else:
                form = escollirMat(request.user, user.alumne, nany)
            return render(request, 'form.html', {'form': form, 'head': u'Selecciona la matrícula' ,})
        else:
            return HttpResponseRedirect(reverse_lazy('matricula:relacio_families__matricula__dades'))
    else:
        infos.append('Sense necessitat de dades.')
        
    return render(
                request,
                'resultat.html', 
                {'msgs': {'errors': [], 'warnings': [], 'infos': infos} },
             )

@login_required
@group_required(['administradors'])
def ActivaMatricula(request):
    '''
    Selecciona els paràmetres per a l'activació de matrícules
    '''
    from aula.apps.matricula.forms import ActivaMatsForm
    from aula.apps.missatgeria.missatges_a_usuaris import tipusMissatge, ACTIVACIO_MATRICULA_FINALITZADA
    from aula.apps.missatgeria.models import Missatge
    from django.contrib.auth.models import Group
    from aula.utils import tools
    
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials
    
    infos=[]
    if request.method == 'POST':
        form = ActivaMatsForm(request.user, request.POST)
        if form.is_valid():
            nivell=form.cleaned_data['nivell']
            datalimit=form.cleaned_data['datalimit']
            tipus=form.cleaned_data['tipus']
            ultimCursNoEmail=form.cleaned_data['ultimCursNoEmail']
            senseEmails=form.cleaned_data['senseEmails']
            preexclusiva=form.cleaned_data['exclusiu']
            nany=django.utils.timezone.now().year
            if tipus=='P':
                llista = Preinscripcio.objects.filter(codiestudis=nivell.nom_nivell, any=nany, estat='Assignada', naixement__isnull=False)
                if not llista:
                    infos.append('Sense preinscripcions per fer matrícula.')
                    return render(
                                request,
                                'resultat.html', 
                                {'msgs': {'errors': [], 'warnings': [], 'infos': infos} },
                                 )
                # Marca Preinscripcions d'estat 'Enviada', del mateix nivell, com a 'Caducada'
                # Així s'evita que preinscripcions, de matrícules activades anteriorment, puguin continuar la matrícula
                Preinscripcio.objects.filter(estat='Enviada', codiestudis=nivell.nom_nivell, any=nany).update(estat='Caducada')
                nivell.limit_matricula=datalimit
                nivell.matricula_oberta=True
                nivell.preexclusiva=preexclusiva
                if preexclusiva:
                    Curs.objects.filter(nivell=nivell).update(limit_confirmacio=None, confirmacio_oberta=False)
                nivell.save()
            if tipus=='C':
                Curs.objects.filter(nivell=nivell).update(limit_confirmacio=datalimit, confirmacio_oberta=True)
                nivell.preexclusiva=False
                nivell.save()
            if tipus=='A':
                nivell.limit_matricula=datalimit
                nivell.matricula_oberta=True
                nivell.preexclusiva=False
                Curs.objects.filter(nivell=nivell).update(limit_confirmacio=None, confirmacio_oberta=False)
                nivell.save()
                
            enviaIniciMat(nivell, tipus, nany, ultimCursNoEmail, senseEmails)
            definicions={'P': 'preinscripció', 'A': 'altres', 'C': 'confirmació'}
            infomat='Matrícula activada de tipus {0} per {1} amb data límit {2}'.format(definicions.get(tipus,''), nivell.nom_nivell, 
                                                            datalimit.strftime('%d/%m/%Y'))
            if senseEmails:
                infos.append(infomat+'.')
            else:
                infos.append(infomat+', emails enviats.')
            missatge = ACTIVACIO_MATRICULA_FINALITZADA
            tipus_de_missatge = tipusMissatge(missatge)
            msg = Missatge(
                        remitent= user,
                        text_missatge = missatge,
                        tipus_de_missatge = tipus_de_missatge)
            msg.afegeix_infos(infos)
            importancia = 'IN'
            grupDireccio =  Group.objects.get( name = 'direcció' )
            msg.envia_a_grup( grupDireccio , importancia=importancia)
            return render(
                        request,
                        'resultat.html', 
                        {'msgs': {'errors': [], 'warnings': [], 'infos': infos} },
                         )
    else:
        if not hasattr(settings, 'CUSTOM_TIPUS_QUOTA_MATRICULA') or not bool(settings.CUSTOM_TIPUS_QUOTA_MATRICULA) \
                or not TPV.objects.filter(nom='centre').exists():
            return render(
                        request,
                        'resultat.html', 
                        {'msgs': {'errors': ["Falta definir CUSTOM_TIPUS_QUOTA_MATRICULA o el TPV 'centre'",], 'warnings': [], 'infos': infos} },
                         )
        form = ActivaMatsForm(request.user)
    return render(
                request,
                'form.html', 
                {'form': form, 
                 },
            )

@login_required
@group_required(['direcció','administradors'])
def blanc( request ):
    return render(
                request,
                'blanc.html',
                    {},
                )

@login_required
@group_required(['professors'])
def ResumConfirmacions( request ):
    from django.http import HttpResponse

    nany=django.utils.timezone.now().year
    output=ResumLlistat(nany)
    output.seek(0)
    filename = 'confirmacions-{0}.xlsx'.format(nany)
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename

    return response
