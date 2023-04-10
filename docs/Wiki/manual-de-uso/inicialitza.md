# Inicialització de la base de dades per començar el curs

Cada inici de curs s'ha de preparar el Djau amb les noves dades necessàries.

Es pot fer de vàries maneres:
* [Instal·lació nova](../instalacion-2/instalacion.md) o com a mínim base de dades nova cada curs.
* La mateixa opció anterior i [recuperant dades del curs anterior](../../../canviDeCurs.txt).
* Mantenir la instal·lació i inicialitzar la base de dades, s'explica a continuació.

En aquest apartat s'explica la inicialització des d'Admin/Inicialitza. Aquest procés elimina informació caducada, com el control d’assistència i l’horari.

La inicialització s'ha de fer una vegada ha finalitzat el curs, només pot fer-ho l’usuari administrador.

Abans de fer qualsevol procés de preparació per al curs vinent, es recomanable fer còpia de la base de dades actual.

Es pot fer servir pg_dump -U usuari -f nomfitxer.pgsql nombasedades

Per exemple:

```bash
pg_dump -U djauser -f djau-20230410.pgsql djau
```

També es pot aprofitar per [actualitzar](actualitza.md) el Djau a l'última versió.

## Dades eliminades:

Incidències, expulsions, sancions, assistència, horaris, festius, cartes, tutors, pagaments pendents de l'any anterior, alumnes de baixa i dades relacionades excepte pagaments efectuats. 

La base de dades queda preparada per a fer la càrrega d'horaris i grups d'alumnes, festius, tutors i altres dades específiques del curs entrant.

## Avantatges:

Es mantenen les qualitatives, actuacions i seguiment tutorial.

Es mantenen els usuaris, les famílies no han de canviar d'usuari cada curs.

El professorat manté usuari i dades addicionals.

Es mantenen els grups i l'usuari superuser.

Es mantenen les definicions: tipus d'incidència, tipus de sanció, frases d'incidència, dies de la setmana, franges, aules, assignatures, missatges, accions, grups, cursos, nivells, recursos de material...

Es manté l'històric de pagaments i sortides.

## Procés posterior

Després s’haurà de carregar el nou horari i l’assignació de grups dels alumnes segons el que indica el Saga i Esfera.

Més informació de la càrrega de dades a [Carga inicial de datos](carga-inicial-de-datos/README.md)
