from django.core.mail import EmailMessage
from django.urls import reverse_lazy
from django.utils.html import format_html
from django.db import transaction
import django.utils.timezone
from dateutil.relativedelta import relativedelta
from aula.apps.matricula.models import Matricula
from aula.apps.sortides.models import QuotaPagament, Quota, TPV
from aula.apps.alumnes.models import Alumne, Curs
from aula.apps.extPreinscripcio.models import Preinscripcio
from aula.apps.extUntis.sincronitzaUntis import creaGrup
from aula.apps.usuaris.models import OneTimePasswd
from django.conf import settings
import random

def acceptaCondicions(alumne, nany=None):
    '''
    Es considera que ha acceptat les condicions si ha marcat la casella
    Retorna True o False
    '''
    
    if nany:
        mt=Matricula.objects.filter(alumne=alumne, any=nany)
    else:
        mt=Matricula.objects.filter(alumne=alumne, acceptar_condicions=True)
    return (mt and mt[0].acceptar_condicions)

def MatContestada(alumne, nany):
    '''
    ES considerada contestada si ha acceptat les condicions
    Retorna True o False
    '''
    
    mt=Matricula.objects.filter(alumne=alumne, any=nany)
    return (mt and mt[0].acceptar_condicions)

def ConfContestada(alumne, nany):
    '''
    Es considera confirmada o no, si ha donat una resposta
    Retorna True o False
    '''
    mt=Matricula.objects.filter(alumne=alumne, any=nany)
    return mt and bool(mt[0].confirma_matricula) and (mt[0].acceptar_condicions or mt[0].confirma_matricula=='N')

def ConfirmacioActivada(alumne):
    '''
    Retorna True si l'alumne té oberta la confirmació
    '''
    return alumne.grup.curs.confirmacio_oberta and \
        (not alumne.grup.curs.limit_confirmacio or django.utils.timezone.now().date()<=alumne.grup.curs.limit_confirmacio)
    
def FlagMatriculaOberta(alumne, preinscripcio=None):
    '''
    Comprova si es pot fer matrícula segons el curs actual de l'alumne o segons la preinscripció
    Retorna True si és oberta la matrícula
    '''
    if alumne.grup.curs.nivell.matricula_oberta: return True
    if not bool(preinscripcio): return False
    curs=preinscripcio.getCurs()
    return curs.nivell.matricula_oberta
    
def MatriculaOberta(alumne, preinscripcio=None):
    '''
    Comprova si es pot fer matrícula segons el curs actual de l'alumne o segons la preinscripció
    Retorna True si és oberta la matrícula i no ha finalizat el període
    '''
    if FlagMatriculaOberta(alumne, preinscripcio):
        if (not alumne.grup.curs.nivell.limit_matricula or \
            (django.utils.timezone.now().date()<=alumne.grup.curs.nivell.limit_matricula)):
            return True
        if not bool(preinscripcio): return False
        curs=preinscripcio.getCurs()
        return (not curs.nivell.limit_matricula or django.utils.timezone.now().date()<=curs.nivell.limit_matricula)
    return False

def get_url_alumne(usuari):
    '''
    Retorna la url inicial per omplir informació de matrícula:
        Confirmació de matrícula si encara no ha omplert el formulari
        Matrícula si encara no ha acceptat les condicions
    en altre cas retorna None
    '''
    
    try:
        if usuari.alumne:
            nany=django.utils.timezone.now().year
            # situacioMat determina el pas a fer de la matrícula
            info = situacioMat(usuari.alumne, nany)
            if info=='M' and not MatContestada(usuari.alumne, nany):
                return reverse_lazy('matricula:relacio_families__matricula__dades')
            if info=='C' and not ConfContestada(usuari.alumne, nany):
                return reverse_lazy('matricula:relacio_families__matricula__confirma', kwargs={"nany": nany})
        return None
    except Exception:
        return None

def matriculaDoble(alumne, nany):
    '''
    Comprova si l'alumne ja ha fet una matrícula i
    a més a més té una preinscripció per a fer una segona matrícula.
    Si té una matrícula no completada, aleshores l'esborra i la prepara per a 
    la nova matrícula segons la preinscripció.
    Retorna True si té opció de una segona matrícula
    '''
    
    p=Preinscripcio.objects.filter(ralc=alumne.ralc, any=nany, estat='Enviada')
    if p: p=p[0]
    else: p=None
    if not ConfirmacioActivada(alumne) and not MatriculaOberta(alumne, p): return False
    mt=Matricula.objects.filter(alumne=alumne, any=nany)
    if not mt or not p: return False
    mt=mt[0]
    curs=p.getCurs()
    if curs==mt.curs: return False
    #  Curs preinscripció != curs matrícula
    if not mt.acceptar_condicions or mt.confirma_matricula=='N':
        # Matrícula incompleta, es pot modificar
        QuotaPagament.objects.filter(alumne=alumne, quota__any=nany,
                                     quota__tipus__nom__in=[curs.nivell.taxes, settings.CUSTOM_TIPUS_QUOTA_MATRICULA,],
                                     pagament_realitzat=False).delete()
        mt.estat='A'
        mt.curs=curs
        q=Quota.objects.filter(curs=mt.curs, any=nany, tipus__nom=settings.CUSTOM_TIPUS_QUOTA_MATRICULA)
        mt.quota=q[0] if q else None
        mt.acceptar_condicions='False'
        mt.acceptacio_en=None
        mt.confirma_matricula=None
        mt.preinscripcio=p
        mt.save()

        return False
    else:
        # Matrícula ja feta diferent de la preinscripció, curs diferent. 
        return True

def situacioMat(alumne, nany):
    '''
    Determina quin pas és el següent en el procés de matrícula de l'alumne.
    Retorna un missatge informatiu o una 'C' o una 'M'.
    'C' indica que ha de fer confirmació de matrícula
    'M' indica que ha de fer matrícula amb posible aportacions de documents
    En altre cas es tracta d'un missatge informatiu sobre l'estat de la matrícula, segons
    el diccionari "situacions".
    '''
    url=format_html("<a href='{}'>{}</a>",
                  reverse_lazy('relacio_families__informe__el_meu_informe'),
                  'Activitats/Pagaments')
    situacions={'nomatricula':'No és període de matrícula.',
                'matpendent':'Matrícula en espera de revisió.',
                'matfinal':'Matrícula finalitzada. Procés completat. Gestiona els pagaments des de l\'apartat '+url,
                'confinal':'Confirmació rebuda i completa.',
                'conpendent':'Confirmació rebuda, en espera de revisió.',
                'doblemat':'Doble matrícula. Contacte amb secretaria.',
                }
    if matriculaDoble(alumne, nany):
        return 'D' 
    mt=Matricula.objects.filter(alumne=alumne, any=nany)
    p=Preinscripcio.objects.filter(ralc=alumne.ralc, any=nany)  # Qualsevol preinscripció no permet confirmació
    if alumne.grup.curs.confirmacio_oberta and not p:
        if ConfContestada(alumne, nany):
            if mt[0].estat=='F':
                return situacions.get('confinal')
            else:
                return situacions.get('conpendent')
        else:
            if (mt and not mt[0].preinscripcio or not mt) and (not alumne.grup.curs.limit_confirmacio \
                or django.utils.timezone.now().date()<=alumne.grup.curs.limit_confirmacio): return 'C'
    p=Preinscripcio.objects.filter(ralc=alumne.ralc, any=nany, estat='Enviada') # Només preinscripcions actuals, última tanda
    if p: 
        p=p[0]
        curs=p.getCurs()
    else: 
        p=None
        curs=alumne.grup.curs
    if FlagMatriculaOberta(alumne, p):
        if mt and mt[0].estat=='F':
            return situacions.get('matfinal')
        if MatriculaOberta(alumne, p):
            if (not curs.nivell.preexclusiva or p) and not Preinscripcio.objects.filter(ralc=alumne.ralc, any=nany).exclude(estat='Enviada'):
                return 'M'
        if MatContestada(alumne, nany):
            return situacions.get('matpendent')
    return situacions.get('nomatricula')

def alumneExisteix(idalum):
    '''
    Retorna objecte Alumne que correspon a ralc=idalum
    prova també amb autoRalc si no el troba
    Retorna None si no existeix
    '''
    from aula.apps.extSaga.sincronitzaSaga import autoRalc
    ralc=idalum
    al=Alumne.objects.filter(ralc=ralc)
    if al:
        return al[0]
    ralc=autoRalc(idalum)
    al=Alumne.objects.filter(ralc=ralc)
    if al:
        return al[0]
    return None

def enviamail(subject, message, from_email, to_email, connection=None):
    from aula.apps.relacioFamilies.models import EmailPendent
    r=0
    if isinstance(to_email,str): to_email=[to_email,]
    if isinstance(to_email,tuple): to_email=list(to_email)
    if not isinstance(to_email,list): to_email=[to_email,]
    try:
        if to_email:
            email=EmailMessage(subject, message, from_email, bcc=to_email, connection=connection)
            r=email.send(fail_silently=False)
        if r!=1:
            ep=EmailPendent(subject=subject,message=message,fromemail=from_email,toemail=str(to_email))
            ep.save()
        return r
    except Exception as e:
        ep=EmailPendent(subject=subject,message=message,fromemail=from_email,toemail=str(to_email))
        ep.save()
        return 0

def mailMatricula(tipus, curs, email, alumne, connection=None):
    '''
    Envia email segons tipus de matrícula
    tipus de missatge ('P', 'A', 'C', 'F')
        P  matrícula amb Preinscripció
        A  Altres matrícules
        C  Confirmació de matrícula
        F  Finalitza matrícula
    curs a on s'ha de fer la matrícula
    email adreces email destinataries, pot ser una llista.
    alumne objecte Alumne
    connection servidor correu
    Retorna True si correcte, False si error.
    '''
    
    if not email: return False
    username=alumne.get_user_associat().username
    urlDjangoAula = settings.URL_DJANGO_AULA
    if tipus!='F':
        # Prepara recuperació de contrasenya
        clau = str( random.randint( 100000, 999999) ) + str( random.randint( 100000, 999999) )
        OneTimePasswd.objects.create(usuari = alumne.get_user_associat(), clau = clau)
        url = "{0}/usuaris/recoverPasswd/{1}/{2}".format( urlDjangoAula, username, clau )
    
    assumpte = {
        'P': u"Instruccions de matrícula - {0}".format(settings.NOM_CENTRE ),
        'A': u"Instruccions de matrícula - {0}".format(settings.NOM_CENTRE ),
        'C': u"Confirmació de matrícula - {0}".format(settings.NOM_CENTRE ),
        'F': u"Matrícula completada - {0}".format(settings.NOM_CENTRE ),
        }
    
    if curs.nivell.limit_matricula:
        data_mat="La data límit és {0}.".format(curs.nivell.limit_matricula.strftime("%A %-d %B"))
    else:
        data_mat=''
    if curs.limit_confirmacio:
        data_conf="La data límit és {0}.".format(curs.limit_confirmacio.strftime("%A %-d %B"))
    else:
        data_conf=''
    
    cosmissatge={
        'P': "\n".join(
            [
            "El procés de matrícula ja s'ha iniciat, per realitzar la matrícula de l'alumne/a {0}, s'ha d'accedir a l'aplicació ".format(alumne.nom+" "+alumne.cognoms)+ \
            "des de {0} amb l'usuari {1}.".format(settings.URL_DJANGO_AULA, username ),
            data_mat,
            ]
            ),
        'A': "\n".join(
            [
            "El procés de matrícula ja s'ha iniciat, per realitzar la matrícula de l'alumne/a {0}, s'ha d'accedir a l'aplicació ".format(alumne.nom+" "+alumne.cognoms)+ \
            "des de {0} amb l'usuari {1}.".format(settings.URL_DJANGO_AULA, username ),
            data_mat,
            ]
            ),
        'C': "\n".join(
            [
            "Com ja sabeu el curs ja s’està acabant i cal preparar el següent, per això us demanem que confirmeu la plaça si voleu continuar amb nosaltres.",
            "Per realitzar la confirmació de matrícula de l'alumne/a {0}, s'ha d'accedir a l'aplicació ".format(alumne.nom+" "+alumne.cognoms)+ \
            "des de {0} amb l'usuari {1}.".format(settings.URL_DJANGO_AULA, username ),
            data_conf,
            ]
            ),
        'F': "\n".join(
            [
            "La matrícula de l'alumne {0} ha finalitzat correctament.".format(alumne.nom+" "+alumne.cognoms),
            "Sempre podreu accedir a l'aplicació {0} amb el vostre usuari {1}".format(settings.URL_DJANGO_AULA, username),
            "Pugeu una fotografia tipus carnet des de l'opció de paràmetres.",
            ]
            ),
        }
    cos=cosmissatge.get(tipus)
    if tipus=='P':
        if curs.nivell.nom_nivell=='ESO':
            cos="\n".join([cos,"Durant el procés de matrícula serà necessari pujar la documentació requerida:",
            "      DNI alumne/a (si el té)",
            "      DNI del pare, mare o tutors legals",
            "      Llibre de família (pàgina dels pares i pàgina de l’alumne/a)",
            "      Carnet de vacunacions",
            "      Targeta sanitària",
            ])
        else:
            cos="\n".join([cos,"Durant el procés de matrícula serà necessari pujar la documentació requerida:",
            "      DNI alumne/a",
            "      DNI del pare, mare o tutors legals (si alumnat menor d'edat)",
            "      Titulació aportada per accedir als estudis",
            "      Llibre de família (si alumnat menor d'edat)",
            "      Targeta sanitària",
            "      Carnet família nombrosa/monoparental si s’escau",
            "      Carnet discapacitat si s’escau",
            "      Credencial de beca si s’escau",
            ])
    if tipus!='F':
        cos="\n".join([cos,"","Si encara no ha obtingut la contrasenya, entreu a {0} per escollir-la.".format(url), ])
    missatge = [u"",
                u"Benvolgut/da,",
                u"",
                cos,
                u"",
                u"Cordialment,",
                u"",
                settings.NOM_CENTRE,
                u"",
                u"Aquest missatge ha sigut enviat per un sistema automàtic. No respongui a aquest e-mail, el missatge no serà llegit per ningú.",
                ]                        
    fromuser = settings.DEFAULT_FROM_EMAIL
    if settings.DEBUG:
        print (u'Enviant comunicació sobre la matrícula a {0}'.format(alumne.nom+" "+alumne.cognoms))
    try:
        r=enviamail(assumpte.get(tipus), 
                  u'\n'.join( missatge ), 
                  fromuser,
                  email, 
                  connection=connection)
        if r!=1:
            return False
        return True
    except Exception as e:
        print("Error enviant mail matrícula "+str(e))
        return False

def següentCurs(alumne):
    c=alumne.grup.curs
    try:
        ncurs=str(int(c.nom_curs)+1)
        seg=Curs.objects.filter(nivell=c.nivell, nom_curs=ncurs)
        if seg:
            return seg[0]
        return None
    except:
        return None

def quotaSegüentCurs(nomtipus, nany, alumne):
    '''
    Selecciona una quota del tipus i any adequada per al següent curs de l'alumne
    Exemple:
      Si l'alumne fa ESO-2 retorna la quota d'ESO-3
      Si l'alumne fa ESO-4 no selecciona cap.
    Si no troba cap, farà servir per defecte una quota del mateix tipus si només n'hi ha una possible.
    '''
    c=alumne.grup.curs
    try:
        ncurs=str(int(c.nom_curs)+1)
        quotacurs=Quota.objects.filter(curs__nivell=c.nivell, curs__nom_curs=ncurs, any=nany, tipus__nom=nomtipus)
    except:
        quotacurs=None
    if not quotacurs:
        # No troba una quota adequada, comprova si existeixen altres quotes del mateix tipus
        quotacurs=Quota.objects.filter(any=nany, tipus__nom=nomtipus)
        if quotacurs.count()!=1:
            # Si troba varies no selecciona cap, si només troba una aleshores la fa servir per defecte
            quotacurs=None
    
    if quotacurs:
        quotacurs=quotacurs[0]
    else:
        quotacurs=None
    return quotacurs

def creaAlumne(preinscripcio):
    '''
    Crea l'alumne si no existeix.
    Si crea l'alumne li assigna les dades segons la preinscripció i amb grup sense lletra.
    Activa l'usuari per a poder fer Login.
    preinscripcio: amb les dades que s'assignen a l'alumne
    Retorna objecte Alumne
    '''
    
    al=alumneExisteix(preinscripcio.ralc)
    if not al:
        al=Alumne(ralc=preinscripcio.ralc)
        curs=preinscripcio.getCurs()
        grup , _ = creaGrup(curs.nivell.nom_nivell,curs.nom_curs,'-',None,None)
        al.grup = grup
        al.nom = preinscripcio.nom
        al.cognoms = preinscripcio.cognoms
        al.data_neixement = preinscripcio.naixement
    al.correu_relacio_familia_pare = preinscripcio.correu if al.primer_responsable==0 else al.correu_relacio_familia_pare
    al.correu_relacio_familia_mare = preinscripcio.correu if al.primer_responsable==1 else al.correu_relacio_familia_mare
    al.correu = preinscripcio.correu
    activaAlumne(al)
    return al

def activaAlumne(al):
    '''
    Activa l'usuari per a poder fer Login.
    '''
    
    al.estat_sincronitzacio = 'MAN'
    al.motiu_bloqueig = ''
    al.tutors_volen_rebre_correu = True
    if not al.data_alta or al.data_baixa: 
        al.data_alta = django.utils.timezone.now()
        al.data_baixa = None
    al.relacio_familia_darrera_notificacio = None
    al.periodicitat_faltes = 7
    al.periodicitat_incidencies = True
    al.save()
    al.user_associat.is_active=True
    al.user_associat.save()

def creaPagament(matricula, quota=None, fracciona=False):
    '''
    Crea pagament de la quota per a l'alumne
    '''
    
    if not quota: quota=matricula.quota
    if not quota: return
    alumne=matricula.alumne
    p=QuotaPagament.objects.filter(alumne=alumne, quota=quota)
    if not p and quota:
        dataLimit=matricula.curs.nivell.limit_matricula + relativedelta(weeks=+3)
        if not quota.dataLimit:
            quota.dataLimit=dataLimit
            quota.save()
        else:
            if dataLimit<quota.dataLimit:
                dataLimit=quota.dataLimit
        with transaction.atomic():
            if fracciona and quota.importQuota!=0:
                import1=round(float(quota.importQuota)/2.00,2)
                import2=float(quota.importQuota)-import1
                p=QuotaPagament(alumne=alumne, quota=quota, fracciona=True, importParcial=import1, dataLimit=dataLimit)
                p.save()
                p=QuotaPagament(alumne=alumne, quota=quota, fracciona=True, importParcial=import2, 
                                dataLimit=dataLimit + relativedelta(months=+1))
                p.save()
            else:
                p=QuotaPagament(alumne=alumne, quota=quota, dataLimit=dataLimit)
                p.save()

def enviaMissatge(missatge):
    from aula.apps.missatgeria.models import Missatge
    from django.contrib.auth.models import User, Group
    
    tipus_de_missatge = 'ADMINISTRACIO'
    usuari_notificacions, new = User.objects.get_or_create( username = 'TP')
    if new:
        usuari_notificacions.is_active = False
        usuari_notificacions.first_name = u"Usuari Tasques Programades"
        usuari_notificacions.save()
    msg = Missatge(
                remitent= usuari_notificacions,
                text_missatge = missatge,
                tipus_de_missatge = tipus_de_missatge)
    importancia = 'VI'
    destinataris, _ = Group.objects.get_or_create( name = 'administradors' )
    msg.envia_a_grup( destinataris , importancia=importancia)

def gestionaPag(matricula, importTaxes):
    '''
    Crea els pagaments corresponents a la matrícula i
    segons l'import de les taxes.
    Si existeixen altres pagaments pendents diferents, esborra els antics.
    Si els pagaments existents ja s'han pagat, no fa canvis
    '''
    
    # Determina la quota de taxes i si es fracciona
    taxes=matricula.curs.nivell.taxes
    if taxes and importTaxes>0:
        quotatax=Quota.objects.filter(importQuota=importTaxes, any=matricula.any, tipus=taxes)
        if quotatax:
            quotatax=quotatax[0]
        else:
            #  Es crea la quota de taxes
            quotatax=Quota(importQuota=importTaxes, 
                  dataLimit=matricula.curs.nivell.limit_matricula + relativedelta(weeks=+3),
                  any=matricula.any, 
                  descripcio='Taxes', 
                  tpv=TPV.objects.get(nom='centre'), 
                  curs=None, 
                  tipus=taxes)
            quotatax.save()
    else:
        quotatax=None
    fracciona=matricula.fracciona_taxes
    
    # Determina la quota de matrícula
    if matricula.confirma_matricula=='C' and matricula.estat=='A':
        if not matricula.quota:
            quotamat=quotaSegüentCurs(settings.CUSTOM_TIPUS_QUOTA_MATRICULA, matricula.any, matricula.alumne)
        else:
            quotamat=matricula.quota
    else:
        quotamat=Quota.objects.filter(curs=matricula.curs, any=matricula.any, tipus__nom=settings.CUSTOM_TIPUS_QUOTA_MATRICULA)
        if quotamat:
            quotamat=quotamat[0]
        else:
            quotamat=None
    
    matricula.quota=quotamat
    matricula.save()
    pag=QuotaPagament.objects.filter(alumne=matricula.alumne, quota__any=matricula.any, 
                                     quota__tipus__nom=settings.CUSTOM_TIPUS_QUOTA_MATRICULA)
    if pag:
        # existeix pagament de quota de matrícula
        if (pag[0].quota!=quotamat and not pag.filter(pagament_realitzat=True)):
            # esborra antiga si no s'ha pagat, crea nova
            enviaMissatge("Canvi de quota. Matrícula:{0} {1} {2}. Quota anterior {3}. Quota actual {4}.".format(
                str(matricula.alumne), str(matricula.curs), matricula.any, str(pag[0].quota), str(quotamat)))
            pag.delete()
            creaPagament(matricula)
        else:
            if pag[0].quota!=quotamat and pag.filter(pagament_realitzat=True):
                # quota canviada i antiga pagada ???
                if pag[0].quota and quotamat and pag[0].quota.importQuota!=quotamat.importQuota:
                    # incompatible
                    enviaMissatge("Quota pagada no correspon. Matrícula:{0}-{1}".format(matricula.idAlumne, matricula.any))
                else:
                    # compatible, fer canvi
                    pag.update(quota=quotamat)
    else:
        creaPagament(matricula)
    
    # Quota taxes
    if not quotatax: return
    
    pag=QuotaPagament.objects.filter(alumne=matricula.alumne, quota__any=matricula.any, 
                                     quota__tipus=taxes)
    if pag:
        if (pag[0].quota!=quotatax and not pag.filter(pagament_realitzat=True)) or \
            (pag[0].quota==quotatax and not pag.filter(pagament_realitzat=True) and \
             pag[0].fracciona!=fracciona):        
            # esborra antiga, crea nova
            pag.delete()
            creaPagament(matricula, quotatax, fracciona)
        else:
            if pag[0].quota!=quotatax and pag.filter(pagament_realitzat=True):
                # taxes canviades i antigues pagades
                enviaMissatge("Taxes pagades no corresponen. Matrícula:{0}-{1}".format(matricula.idAlumne, matricula.any))
    else:
        creaPagament(matricula, quotatax, fracciona)

def alumne2Mat(alumne, nany=None, p=None):
    '''
    Busca la Matricula amb les dades de l'alumne per l'any indicat o l'any actual.
    Si no existeix, agafa les dades de la preinscripció o de l'alumme si no té preinscripció.
    Retorna la Matricula trobada o crea una nova.
    '''
    if not nany:
        nany=django.utils.timezone.now().year
    mat=Matricula.objects.filter(alumne=alumne, any=nany)
    if mat:
        mat=mat[0]
    else:
        mat=Matricula()
        mat.alumne=alumne
        mat.idAlumne=alumne.ralc
        mat.any=nany
        mat.estat='A'
        mat.acceptar_condicions=False
        if p:
            p=p[0]
            mat.nom=p.nom
            mat.cognoms=p.cognoms
            mat.centre_de_procedencia=p.centreprocedencia
            mat.data_naixement=p.naixement
            mat.alumne_correu=p.correu
            mat.adreca=p.adreça
            mat.localitat=p.localitat if p.localitat else p.municipi
            mat.cp=p.cp
            mat.rp1_nom=p.nomtut1+" "+p.cognomstut1 if p.nomtut1 and p.cognomstut1 else ''
            mat.rp1_telefon=p.telefon
            mat.rp1_correu=p.correu
            mat.rp2_nom=p.nomtut2+" "+p.cognomstut2 if p.nomtut2 and p.cognomstut2 else ''
            mat.preinscripcio=p
            curs=p.getCurs()
            mat.curs=curs
        else:
            mat.nom=alumne.nom
            mat.cognoms=alumne.cognoms
            mat.centre_de_procedencia=alumne.centre_de_procedencia[0:50]
            mat.data_naixement=alumne.data_neixement
            mat.alumne_correu=alumne.correu
            mat.adreca=alumne.adreca
            mat.localitat=alumne.localitat if alumne.localitat else alumne.municipi
            mat.cp=alumne.cp
            mat.rp1_nom=alumne.rp1_nom
            mat.rp1_telefon=alumne.rp1_mobil if alumne.rp1_mobil else alumne.rp1_telefon
            mat.rp1_correu=alumne.correu_relacio_familia_pare if alumne.primer_responsable==0 else alumne.correu_relacio_familia_mare
            mat.rp2_nom=alumne.rp2_nom
            mat.rp2_telefon=alumne.rp2_mobil if alumne.rp2_mobil else alumne.rp2_telefon
            mat.rp2_correu=alumne.correu_relacio_familia_mare if alumne.primer_responsable==0 else alumne.correu_relacio_familia_pare
            mat.curs=alumne.grup.curs  # Curs actual
    return mat

def updateAlumne(alumne, mat):
    '''
    Actualitza les dades de l'alumne amb les dades de la Matricula mat.
    '''
    alumne.nom=mat.nom
    alumne.cognoms=mat.cognoms
    if mat.centre_de_procedencia and not alumne.centre_de_procedencia:
        alumne.centre_de_procedencia=mat.centre_de_procedencia
    alumne.data_neixement=mat.data_naixement
    alumne.correu=mat.alumne_correu
    alumne.adreca=mat.adreca
    alumne.localitat=mat.localitat
    alumne.cp=mat.cp
    alumne.rp1_nom=mat.rp1_nom
    alumne.rp1_telefon=mat.rp1_telefon
    alumne.rp1_correu=mat.rp1_correu
    alumne.rp2_nom=mat.rp2_nom if mat.rp2_nom else ''
    alumne.rp2_telefon=mat.rp2_telefon if mat.rp2_telefon else ''
    alumne.rp2_correu=mat.rp2_correu if mat.rp2_correu else ''
    alumne.correu_relacio_familia_pare = alumne.rp1_correu
    alumne.correu_relacio_familia_mare = alumne.rp2_correu
    alumne.save()

def diferents(dada1, dada2):
    '''
    Retorna True si dada1 i dada2 són diferents.
    Retorna False si iguals o les dues són None
    '''

    if (not dada1 and not dada2) or dada1==dada2: return False
    return True

def getCanvis(idMat):
    '''
    Crea una llista amb tots el camps que tenen diferències entre
    les dades de la matrícula i les de l'alumne corresponent.
    Retorna la llista
    '''
    mat=Matricula.objects.get(pk=idMat)
    alumne=mat.alumne
    
    llista=[]
    if diferents(alumne.correu, mat.alumne_correu): llista.append('alumne_correu')
    if diferents(alumne.adreca, mat.adreca): llista.append('adreca')
    if diferents(alumne.localitat, mat.localitat): llista.append('localitat')
    if diferents(alumne.cp, mat.cp): llista.append('cp')
    if diferents(alumne.rp1_nom, mat.rp1_nom): llista.append('rp1_nom')
    if diferents(alumne.rp1_telefon, mat.rp1_telefon): llista.append('rp1_telefon')
    if diferents(alumne.rp1_correu, mat.rp1_correu): llista.append('rp1_correu')
    if diferents(alumne.rp2_nom, mat.rp2_nom): llista.append('rp2_nom')
    if diferents(alumne.rp2_telefon, mat.rp2_telefon): llista.append('rp2_telefon')
    if diferents(alumne.rp2_correu, mat.rp2_correu): llista.append('rp2_correu')
    return llista

def mat_selecciona(idcurs, nany, tipus):
    '''
    Prepara filtre per seleccionar Matricula segons id del curs, nany i tipus d'estat
    tipus: 'T', 'C', 'N', 'A', 'F'
    '''
    from django.db.models import Q
    
    # Segons l'any
    escollides = Q( any=nany )
    # Acceptar condicions True si totes, confirmades o pendents de confirmació
    if tipus!='N' and tipus!='F': escollides = Q( escollides  & Q(acceptar_condicions=True))
    # Confirmades
    if tipus=='C': escollides = Q( escollides & Q( confirma_matricula = tipus) & Q(estat = 'A' ) )
    # No Confirmades
    if tipus=='N': escollides = Q( escollides & Q( confirma_matricula = tipus) )
    # Segons estat
    if tipus=='A' or tipus=='F': escollides = Q( escollides & Q( estat = tipus) )
    # Segons el curs
    if idcurs: escollides = Q( escollides & Q( curs__id=idcurs ))
    return escollides

def next_mat(pk, idcurs, nany, tipus):
    '''
    A partir de la Matricula amb id=pk, selecciona següent Matricula segons idcurs,nany,tipus.
    Retorna id de la següent Matricula segons ordre: 'curs__nom_curs_complert', 'cognoms', 'nom'
    Retorna None si no queda cap.
    '''
    from django.db.models import Q

    matricules = Matricula.objects.filter(Q(mat_selecciona(idcurs, nany, tipus) | Q(pk=pk))).order_by('curs__nom_curs_complert', 'cognoms', 'nom')
    object_ids = list(matricules.values_list('id', flat=True))
    current_pos = object_ids.index(pk)
    if current_pos < len(object_ids) - 1:
        next_id = object_ids[current_pos + 1]
    else:
        next_id = object_ids[0]
    if next_id==pk:
        matricules=Matricula.objects.filter(mat_selecciona(idcurs, nany, tipus)).order_by('curs__nom_curs_complert', 'cognoms', 'nom')
        if not matricules: return None
    return next_id

def inforgpd():
    '''
    Retorna info sobre RGPD
    '''
    if not hasattr(settings, 'INFORGPD') or not bool(settings.INFORGPD): return ''
    try:
        f = open(settings.INFORGPD, 'r', encoding='UTF-8')
        file_content = f.read()
        f.close()
    except:
        file_content = 'Fitxer '+settings.INFORGPD+' no disponible'
    file_content = "<br />".join(file_content.split("\n"))
    return file_content

def taxesPagades(matricula):
    # Determina si ha pagat quota de taxes
    # return True si ha pagat taxes.
    taxes=matricula.curs.nivell.taxes
    if not taxes: return False
    # Quota taxes
    pag=QuotaPagament.objects.filter(alumne=matricula.alumne, quota__any=matricula.any, 
                                     quota__tipus=taxes, pagament_realitzat=True)
    return pag.exists()

def enviaIniciMat(nivell, tipus, nany, ultimCursNoEmail=False, senseEmails=False):
    '''
    Envia emails als alumnes amb instruccions de matrícula
    nivell  dels alumnes escollits
    tipus matrícula
        P  matrícula amb Preinscripció
        A  Altres matrícules
        C  Confirmació de matrícula
    nany any inici curs
    ultimCursNoEmail si True NO envia mail als alumnes d'últim curs. 
            Djau no té les qualificacions i no podem saber si l'alumne ha obtingut títol.
    senseEmails si True NO envia mail a cap alumne. 
            Adequat si alguns alumnes continuen, altres abandonen, altres obtenen el títol.
    '''
    
    from django.core import mail
    
    connection = mail.get_connection()
    # Obre la connexió
    connection.open()
    if tipus=='P':
        for p in Preinscripcio.objects.filter(codiestudis=nivell.nom_nivell, any=nany, estat='Assignada', 
                                              naixement__isnull=False):
            alumne=creaAlumne(p)
            curs=p.getCurs()
            if not senseEmails: mailMatricula(tipus, curs, p.correu, alumne, connection)
            p.estat='Enviada'
            p.save()
    if tipus=='A' or tipus=='C':
        for a in Alumne.objects.filter(grup__curs__nivell=nivell, data_baixa__isnull=True):
            activaAlumne(a)
            correus=a.get_correus_relacio_familia()
            if not correus: correus=a.get_correus_tots()
            if següentCurs(a) or not ultimCursNoEmail:
                if not senseEmails: mailMatricula(tipus, a.grup.curs, correus, a, connection)
    # tanca la connexió
    if connection: connection.close()

def totalsAlumnes(nany):
    from django.db.models import Q, Count, F
    import datetime
    
    mes=datetime.timedelta(days=30)
    quantitats=Curs.objects.filter(grup__alumne__isnull=False, data_inici_curs__isnull=False).distinct().order_by('nom_curs_complert') \
                .annotate(inici=Count('grup__alumne', 
                            filter=Q(
                                (Q(grup__alumne__data_baixa__isnull=True) | Q(grup__alumne__data_baixa__gt=(F('data_inici_curs') + mes))) &
                                Q(grup__alumne__data_alta__lte=(F('data_inici_curs') + mes))
                                      ),
                            distinct=True
                            )) \
                .annotate(ara=Count('grup__alumne', 
                            filter=Q(Q(grup__alumne__data_baixa__isnull=True) & 
                                     Q(grup__alumne__data_alta__lt=F('data_fi_curs'))),
                            distinct=True
                            )) \
                .annotate(conf=Count('grup__alumne', 
                                    filter=Q(Q(grup__alumne__matricula__any=nany) & 
                                             Q(grup__alumne__matricula__confirma_matricula='C')),
                                    distinct=True)) \
                .annotate(noconf=Count('grup__alumne', 
                                    filter=Q(Q(grup__alumne__matricula__any=nany) & 
                                             Q(grup__alumne__matricula__confirma_matricula='N')),
                                    distinct=True))
    return quantitats

def ResumLlistat(nany):
    '''
    Retorna un full de càlcul xlsx amb les llistes d'alumnes que confirmen plaça o no
    '''
    
    import xlsxwriter
    import io
    
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    
    worksheet = workbook.add_worksheet(u'Totals')
    cap=['Curs', 'Alumnes inicials', 'Alumnes ara', 'Confirmades', 'No confirmades']
    worksheet.set_column(0, 0, 10)
    worksheet.set_column(1, 4, 15)
    date=django.utils.timezone.now()
    worksheet.write_string(0,0,'Dades a '+date.strftime('%d/%m/%Y %H:%M'))
    worksheet.write_row(1,0,cap)
    quantitats=totalsAlumnes(nany)
    fila=2
    for q in quantitats:
        worksheet.write_string(fila,0,str(q))
        worksheet.write_number(fila,1,q.inici)
        worksheet.write_number(fila,2,q.ara)
        worksheet.write_number(fila,3,q.conf)
        worksheet.write_number(fila,4,q.noconf)
        fila=fila+1
    
    cursos=Curs.objects.filter(confirmacio_oberta=True).distinct().order_by('nom_curs_complert')
    for c in cursos:
        worksheet = workbook.add_worksheet((u'{0}-Confirmades'.format( str( c ) ))[:31])
        cap=['RALC', 'Cognoms', 'Nom', 'Grup actual', 'Curs Mat.', 'Resposta']
        worksheet.set_column(0, 0, 25)
        worksheet.set_column(1, 3, 15)
        worksheet.write_row(0,0,cap)
        alumConf=Alumne.objects.filter(grup__curs=c, data_baixa__isnull=True, matricula__any=nany, matricula__confirma_matricula='C')\
                .order_by('grup__nom_grup', 'cognoms', 'nom')
        fila=1
        for a in alumConf:
            worksheet.write_string(fila,0,a.ralc)
            worksheet.write_string(fila,1,a.cognoms)
            worksheet.write_string(fila,2,a.nom)
            worksheet.write_string(fila,3,str(a.grup))
            worksheet.write_string(fila,4,str(a.matricula.get(any=nany).curs) if ConfContestada(a,nany) else '')
            worksheet.write_string(fila,5,a.matricula.get(any=nany).get_confirma_matricula_display() if ConfContestada(a,nany) else 'Sense resposta')
            fila=fila+1
        
        worksheet = workbook.add_worksheet((u'{0}-No confirmades'.format( str( c ) ))[:31])
        cap=['RALC', 'Cognoms', 'Nom', 'Grup actual', 'Curs Mat.', 'Resposta']
        worksheet.set_column(0, 0, 25)
        worksheet.set_column(1, 3, 15)
        worksheet.write_row(0,0,cap)
        alumNoConf=Alumne.objects.filter(grup__curs=c, data_baixa__isnull=True).order_by('grup__nom_grup', 'cognoms', 'nom')
        fila=1
        for a in alumNoConf:
            if not ConfContestada(a,nany) or a.matricula.get(any=nany).confirma_matricula!='C':
                worksheet.write_string(fila,0,a.ralc)
                worksheet.write_string(fila,1,a.cognoms)
                worksheet.write_string(fila,2,a.nom)
                worksheet.write_string(fila,3,str(a.grup))
                worksheet.write_string(fila,4,str(a.matricula.get(any=nany).curs) if ConfContestada(a,nany) else '')
                worksheet.write_string(fila,5,a.matricula.get(any=nany).get_confirma_matricula_display() if ConfContestada(a,nany) else 'Sense resposta')
                fila=fila+1
        
    workbook.close()
    return output
