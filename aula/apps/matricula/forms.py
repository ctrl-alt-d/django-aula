from django import forms
from aula.apps.extPreinscripcio.models import Preinscripcio
from aula.apps.matricula.models import Matricula
from aula.apps.sortides.models import QuotaPagament
from aula.apps.alumnes.models import Curs, Nivell
from aula.utils.widgets import DateTextImput
import django.utils.timezone
from django.conf import settings

class DadesForm1(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(DadesForm1, self).__init__(*args, **kwargs)
        #self.fields['data_naixement'].widget=DateTextImput()
        self.fields['nom'].disabled=True
        self.fields['cognoms'].disabled=True
        self.fields['centre_de_procedencia'].disabled=True
        self.fields['data_naixement'].disabled=True
        mat=kwargs['initial'].get('matricula')
        if mat.preinscripcio:        
            self.fields['curs'].disabled=True
        else:
            nivell=self.initial['curs'].nivell
            self.fields['curs'].queryset = Curs.objects.filter(nivell=nivell,
                                                    ).order_by('nom_curs_complert').distinct()
    def clean(self):
        from aula.apps.usuaris.tools import testEmail
        
        cleaned_data = super(DadesForm1, self).clean()
        email=cleaned_data.get('alumne_correu')
        res, email = testEmail(email, False)
        if res<-1:
            self.add_error('alumne_correu','Adreça email no vàlida')
        else: cleaned_data['alumne_correu'] = email
        return cleaned_data
           
    class Meta:
        model=Matricula
        fields = ['curs', 'nom','cognoms', 'centre_de_procedencia','data_naixement','alumne_correu','adreca','localitat','cp',]

class DadesForm2(forms.ModelForm):
    
    def clean(self):
        from aula.apps.usuaris.tools import testEmail
        
        cleaned_data = super(DadesForm2, self).clean()
        email=cleaned_data.get('rp1_correu')
        res, email = testEmail(email, False)
        if res<-1:
            self.add_error('rp1_correu','Adreça email no vàlida')
        else: cleaned_data['rp1_correu'] = email
        email=cleaned_data.get('rp2_correu')
        res, email = testEmail(email, False)
        if res<-1:
            self.add_error('rp2_correu','Adreça email no vàlida')
        else: cleaned_data['rp2_correu'] = email
        return cleaned_data
    
    class Meta:
        model=Matricula
        fields = ['rp1_nom','rp1_telefon','rp1_correu','rp2_nom','rp2_telefon','rp2_correu',]

class DadesForm2b(forms.ModelForm):
    
    llistaufs = forms.CharField(widget=forms.Textarea, required=False)
    
    class Meta:
        model=Matricula
        fields = ['curs_complet', 'quantitat_ufs', 'llistaufs', 'bonificacio', ]

    def __init__(self, *args, **kwargs):
        super(DadesForm2b, self).__init__(*args, **kwargs)
        mat=kwargs['initial'].get('matricula')
        taxes=mat.curs.nivell.taxes
        if not taxes:
            self.fields['bonificacio'].help_text='No s\'apliquen taxes en aquest curs'
            self.fields['bonificacio'].disabled=True
        pag=QuotaPagament.objects.filter(alumne=mat.alumne, quota__any=mat.any, quota__tipus=taxes, pagament_realitzat=True)
        if pag and mat.acceptar_condicions:
            self.fields['curs_complet'].disabled=True
            self.fields['quantitat_ufs'].disabled=True
            self.fields['llistaufs'].disabled=True
            self.fields['bonificacio'].disabled=True
        
    def clean(self):
        cleaned_data = super(DadesForm2b, self).clean()
        complet = cleaned_data.get('curs_complet')
        ufs = cleaned_data.get('quantitat_ufs')
        if not isinstance(ufs,int): ufs=0
        llista = cleaned_data.get('llistaufs')
        if not complet and ufs<=0:
            raise forms.ValidationError("Si no és curs complet, la quantitat de UFs és obligatòria")
        if complet and (ufs!=0 or bool(llista)):
            raise forms.ValidationError("Si curs complet no s'ha d'introduir quantitat de UFs")
        if ufs>0 and not bool(llista):
            raise forms.ValidationError("Indica les UFs a on vols matricular-te")
        return cleaned_data


class CustomClearableFileInput(forms.ClearableFileInput):
    from django.utils.safestring import mark_safe
    
    template_name = 'widgets/uploadfiles.html'
    eliminaFitxers = []
    input_text = mark_safe('<b>Selecciona TOTS els arxius necessaris</b>')

    def value_from_datadict(self, data, files, name):
        upload = super().value_from_datadict(data, files, name)
        checkbox=self.clear_checkbox_name(name)
        pos=len(checkbox)
        self.eliminaFitxers=[]
        for key in data.keys():
            if key.startswith(checkbox):
                num=int(key[pos:])
                self.eliminaFitxers.append(num)
        return upload

class DadesForm3(forms.ModelForm):
    
    quotaMat=forms.CharField(label="Quota Matrícula:", widget = forms.TextInput( attrs={'readonly': True} ), required=False, )
    importTaxes=forms.CharField(label="Import de les taxes:", widget = forms.TextInput( attrs={'readonly': True} ), required=False, )
    #documents=forms.CharField(label="Documents actuals:", widget = forms.Textarea( attrs={'readonly': True, 'files': None} ), required=False, )
    fitxers = forms.FileField(widget=CustomClearableFileInput(attrs={'multiple': True}))

    def __init__(self, *args, **kwargs):
        from django.utils.safestring import mark_safe

        super(DadesForm3, self).__init__(*args, **kwargs)
        self.fields['acceptar_condicions'].required=True
        mat=kwargs['initial'].get('matricula')
        if mat.curs.nivell.nom_nivell=='ESO':
            self.fields['fitxers'].help_text=mark_safe('<b style="color:darkgreen">Targeta sanitària, carnet de vacunacions, \
                            llibre de família, documents identificació ...</b>')
        else:
            self.fields['fitxers'].help_text=mark_safe('<b style="color:darkgreen">Targeta sanitària, documents identificació, \
                            titulació aportada (ESO, Batxillerat, ...), compliment de les bonificacions ...</b>')
        importTaxes = kwargs['initial'].get('importTaxes')
        docs=kwargs['initial'].get('documents')
        self.fields['fitxers'].widget.clear_checkbox_label='Esborra'
        if len(docs)>0:
            self.fields['fitxers'].widget.attrs['files'] = docs
        else:
            self.fields['fitxers'].widget.attrs['files'] = []
        if len(docs)==0 and mat.preinscripcio:
            self.fields['fitxers'].required=True
        else:
            self.fields['fitxers'].required=False
        taxes=mat.curs.nivell.taxes
        pag=QuotaPagament.objects.filter(alumne=mat.alumne, quota__any=mat.any, quota__tipus=taxes, pagament_realitzat=True)
        if not taxes or pag or importTaxes==0:
            self.fields['fracciona_taxes'].disabled=True
            
    def clean(self):
        from django.utils.datastructures import MultiValueDict
        
        cleaned_data = super(DadesForm3, self).clean()
        files = self.files
        if isinstance(files, MultiValueDict):
            for key in files.keys():
                for value in files.getlist(key):
                    if value.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                        self.add_error('fitxers', "Mida màxima de cada fitxer és "+
                                       str(settings.FILE_UPLOAD_MAX_MEMORY_SIZE/1024/1024)+"MB")
        nous = cleaned_data.get('fitxers')
        esborra=self.fields['fitxers'].widget.eliminaFitxers
        antics=self.fields['fitxers'].widget.attrs['files']
        if not nous and len(antics)==len(esborra) and len(antics)>0:
            self.add_error('fitxers', "S'han de pujar els documents demanats.")
        cleaned_data['fitxers']=esborra
        return cleaned_data
    
    class Meta:
        model=Matricula
        fields = ['quotaMat', 'importTaxes', 'fracciona_taxes', 'fitxers', 'acceptar_condicions',]

class ConfirmaMat(forms.ModelForm):
    
    opcions=forms.ChoiceField(  label=u"Continuarà el proper curs a ESO o Batxillerat ?",
                                required=True,
                                choices=Matricula.CONF_CHOICES,
                                widget=forms.RadioSelect())

    class Meta:
        model=Matricula
        fields = ['opcions', 'nom','cognoms', 'data_naixement', 'alumne_correu','adreca','localitat','cp',\
                  'rp1_nom','rp1_telefon','rp1_correu','rp2_nom','rp2_telefon','rp2_correu',\
                  'acceptar_condicions',]
    
    def __init__(self, user, *args, **kwargs):
        super(ConfirmaMat, self).__init__(*args, **kwargs)
        self.fields['acceptar_condicions'].label=""
        self.fields['alumne_correu'].required=True
        self.fields['nom'].widget.attrs['readonly'] = True
        self.fields['cognoms'].widget.attrs['readonly'] = True
        self.fields['data_naixement'].widget.attrs['readonly'] = True
    
    def clean(self):
        from aula.apps.usuaris.tools import testEmail
        
        cleaned_data = super(ConfirmaMat, self).clean()
        opcions = cleaned_data.get('opcions')
        condicions = cleaned_data.get('acceptar_condicions')
        if opcions=='C' and not condicions:
            self.add_error('acceptar_condicions', "És obligatori acceptar les condicions de matrícula")

        email=cleaned_data.get('alumne_correu')
        res, email = testEmail(email, False)
        if res<-1:
            self.add_error('alumne_correu','Adreça email no vàlida')
        else: cleaned_data['alumne_correu'] = email
        
        email=cleaned_data.get('rp1_correu')
        res, email = testEmail(email, False)
        if res<-1:
            self.add_error('rp1_correu','Adreça email no vàlida')
        else: cleaned_data['rp1_correu'] = email
        
        email=cleaned_data.get('rp2_correu')
        if email:
            res, email = testEmail(email, False)
            if res<-1:
                self.add_error('rp2_correu','Adreça email no vàlida')
            else: cleaned_data['rp2_correu'] = email
        
        #  fijar valor definitivo acceptar_condicions
        if opcions=='N' and condicions==None:
            cleaned_data['acceptar_condicions'] = False
        return cleaned_data

class escollirMat(forms.Form):
    
    escollida=forms.ChoiceField(label=u"Selecciona la matrícula que vols fer servir",
                                required=True,
                                widget=forms.RadioSelect())
    
    def __init__(self, user, alumne, nany, *args, **kwargs):
        super().__init__(*args, **kwargs)
        p=Preinscripcio.objects.filter(ralc=alumne.ralc, any=nany, estat='Enviada')
        mt=Matricula.objects.filter(alumne=alumne, any=nany)
        self.fields['escollida'].choices=[
                                    ('M','Matrícula actual a {0}{1}'.format(
                                        mt[0].curs.nivell.nom_nivell,mt[0].curs.nom_curs)
                                    ),
                                    ('P','Fer nova matrícula segons preinscripció a {0}{1} ({2})'.format(
                                        p[0].codiestudis,p[0].curs,p[0].torn)
                                    ),
                                    ]

def year_choices():
    '''
    Retorna choices d'anys possibles de matrícules
    '''
    primer=Matricula.objects.all().order_by('any').first()
    ultim=Matricula.objects.all().order_by('any').last()
    if primer:
        primer = primer.any
    else:
        primer=current_year()
    if ultim:
        ultim = ultim.any
    else:
        ultim=current_year()
    primerCurs=Curs.objects.filter(data_inici_curs__isnull=False).order_by('data_inici_curs').first()
    ultimCurs=Curs.objects.filter(data_fi_curs__isnull=False).order_by('data_fi_curs').last()
    if primerCurs and primerCurs.data_inici_curs.year<primer:
        primer = primerCurs.data_inici_curs.year
    if ultimCurs and ultimCurs.data_fi_curs.year>ultim:
        ultim = ultimCurs.data_fi_curs.year
    return [(r,r) for r in range(primer, ultim+1)]

def current_year():
    '''
    Retorna any de l'última matrícula o any actual
    '''
    import datetime
    ultim=Matricula.objects.all().order_by('any').last()
    if ultim:
        ultim = ultim.any
    else:
        ultim = datetime.date.today().year
    return ultim

class EscollirMatsForm(forms.Form):
    '''
    Permet escollir paràmetres de selecció de matrícules: curs, any i tipus
    '''
    curs = forms.ModelChoiceField(label=u'Curs', queryset=None, required = True,)
    year = forms.TypedChoiceField(label='Any', coerce=int, choices=year_choices, initial=current_year, required = True)
    tipus=forms.ChoiceField(  label=u"Tipus", initial="A", required=True,
                                choices=[('T','Totes'),
                                         ('C','Confirmades'),
                                         ('N','No confirmades'),
                                         ('A','Pendents de finalitzar'),
                                         ('F','Finalitzades'),
                                         ])
    
    def __init__(self, user, *args, **kwargs):
        super(EscollirMatsForm, self).__init__(*args, **kwargs)
        #Mostra cursos amb alumnes
        self.fields['curs'].queryset = Curs.objects.filter(grup__alumne__isnull=False, 
                                                                grup__alumne__data_baixa__isnull=True,
                                                ).order_by('nom_curs_complert').distinct()

class ActivaMatsForm(forms.Form):
    '''
    Permet escollir paràmetres per activació de matrícules: nivell, data i alumnes
    '''
    nivell = forms.ModelChoiceField(label=u'Nivell', queryset=None, required = True,)
    datalimit = forms.DateField(label='Data límit', required = True, widget=DateTextImput())
    tipus=forms.ChoiceField(label='Tipus de matrícules', required = False,
                                choices=[('P','Amb Preinscripció'),
                                         ('C','Confirmacions'),
                                         ('A','Altres'),
                                         ])
    ultimCursNoEmail=forms.BooleanField(label=u'No envia emails a alumnes d\'últim curs',required = False,
                                help_text=u'Sense emails a alumnes d\'últim curs, segurament ja tenen el títol.')
    senseEmails=forms.BooleanField(label=u'No envia emails',required = False,
                                help_text=u'Si ja s\'ha donat la informació directament als alumnes. \
                                Opció adequada si no es pot concretar qui continua, canvia de centre o obté el títol.')
    exclusiu=forms.BooleanField(label=u'Exclusivament preinscripcions',required = False,
                                help_text=u'Només es permet matrícula amb preinscripció. Els alumnes que continuen al centre no podran accedir.')
    
    def __init__(self, user, *args, **kwargs):
        super(ActivaMatsForm, self).__init__(*args, **kwargs)
        self.fields['nivell'].queryset = Nivell.objects.filter(curs__grup__alumne__isnull=False, 
                                                                curs__grup__alumne__data_baixa__isnull=True,
                                                ).order_by('nom_nivell').distinct()

    def clean(self):
        cleaned_data = super(ActivaMatsForm, self).clean()
        datalimit = cleaned_data.get('datalimit')
        if django.utils.timezone.now().date()>datalimit:
            self.add_error('datalimit', "Data és anterior a l'actual")
        return cleaned_data
