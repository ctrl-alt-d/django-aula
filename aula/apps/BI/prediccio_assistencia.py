# This Python file uses the following encoding: utf-8
'''
Created on Mar 24, 2013

@author: dani
'''
from django.conf import settings
from lxml import etree
from aula.utils.tools import unicode

def predictTreeModel( values ):
    
    #Si no hi ha model fem predicció respecte hora anterior:
    if not hasattr(settings, 'PREDICTION_TREE') or settings.PREDICTION_TREE is None:
        if "assistenciaaHoraAnterior" in values and values["assistenciaaHoraAnterior"] == 'Absent':
            return 'Absent', 0.8
        else: 
            return 'Present', 0.5

    #Si hi ha model llavors segons el model.
    predict = None
    
    tree = settings.PREDICTION_TREE
    root = tree.getroot()
    TreeModel = root.find( '{http://www.dmg.org/PMML-4_2}TreeModel' )

    #TODO: check values into MiningField
    
    #Node root de TreeModel. Predicció global
    Node = TreeModel.find( '{http://www.dmg.org/PMML-4_2}Node' )
    predict = Node.get("score")
    pct = 0.5
    n_tot = Node.get("recordCount")
    n_predict = next(  x.get( 'recordCount' ) for x in Node if etree.QName(x).localname == 'ScoreDistribution' and  x.get('value') == predict )
    
    #print 'primera prediccio', predict
    
    #Si node root té fills cal baixar pels fills.
    while True:
        
        try:        
                    
            fill = next( e for e in Node 
                         if etree.QName(e).localname == 'Node' and
                            unicode(values[ e[0].get('field') ]) == e[0].get('value')  )

            try:
                Node = fill
                predict = Node.get("score")
                #print ' seguent prediccio', predict
                n_tot = Node.get("recordCount")
                n_predict = max(  x.get( 'recordCount' ) for x in Node if etree.QName(x).localname == 'ScoreDistribution' and  x.get('value') == predict )
            except IndexError:
                break
            
            try:
                pct = float(n_predict) / float(n_tot)
            except:
                pct = 0.5
        except StopIteration:
            break
        
        
    return  predict, pct 

