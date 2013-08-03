# This Python file uses the following encoding: utf-8
# Django settings for aula project.

from dev import *

INSTALLED_APPS += [
                   'aula.apps.demo',
                   ]

NOM_CENTRE = 'Centre de Demo'
LOCALITAT = u"L'Escala"
URL_DJANGO_AULA = r'http://djau.ctrlalt.d.webfactional.com'

#En cas de tenir un arbre de predicció cal posar-lo aquí:
# from lxml import etree  
# PREDICTION_TREE=etree.parse( r'path_fins_el_model' )
PREDICTION_TREE = None