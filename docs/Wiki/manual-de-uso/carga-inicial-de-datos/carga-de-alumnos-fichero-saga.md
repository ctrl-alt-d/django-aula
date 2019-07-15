# Carga de Alumnos Fichero SAGA

Hasta ahora tenemos cargados los los grupos de nuestro centro ahora es el momento de importar los alumnos.

Recuerda que Django-Aula solo permite la importación de alumnos desde una exportación hecha desde SAGA, el proceso de obtención de esta exportación esta explicado aquí:

{% page-ref page="../../anexos/exportacion-saga.md" %}

Una vez tenemos el fichero con los alumnos comprobamos que tiene la siguiente estructura:

{% code-tabs %}
{% code-tabs-item title="Saga\_Export\_Sample\_fakedata.csv" %}
```text
"#","00_IDENTIFICADOR DE L'ALUMNE/A","01_NOM","02_DATA NAIXEMENT","03_RESPONSABLE 1","04_TELÈFON RESP. 1","05_MÒBIL RESP. 1","06_ADREÇA ELECTR. RESP. 1","07_RESPONSABLE 2","08_TELÈFON RESP. 2","09_MÒBIL RESP. 2","10_ADREÇA ELECTR. RESP. 2","11_ADREÇA","12_LOCALITAT","13_CORREU ELECTRÒNIC","14_ALTRES TELÈFONS","15_CENTRE PROCEDÈNCIA","16_GRUPSCLASSE""1","92483170093","Torrent Ortiz, Marta","27/11/1998","Salvador Segura, Xavi","+34 XXXXXXX","+34 XXXXXXX","c/ del General Martina Dominguez Llorens","+34 XXXXXYYY","+34 XXXXZZZZ","+34 XXXXLLL","xavi@mailintaor.com","c/ de l'aviador Martina Dominguez Llorens","L'Armentera","marta@mailintaor.com","","La Salle","ESO1A""1","13450532361","Camacho Blanco, Pau","12/12/1990","Aranda Montoya, Carlota","+34 XXXXXXX","+34 XXXXXXX","c/ del General Aitana Guzman Colomer","+34 XXXXXYYY","+34 XXXXZZZZ","+34 XXXXLLL","carlota@mailintaor.com","c/ de l'aviador Aitana Guzman Colomer","L'Armentera","pau@mailintaor.com","","La Salle","ESO1A"
```
{% endcode-tabs-item %}
{% endcode-tabs %}

{% hint style="warning" %}
Si desde SAGA no esta especificado el grupo al que pertenece el Alumno y solo contiene el Nivel y Curso, lamentablemente habría que modificar el fichero a mano o a través de un script custom para asignarle un grupo. \(Me refiero al campo 16 del CSV\).
{% endhint %}

Vale llego el momento de la verdad, nos dirigimos a esta URL: [\[DJANGO\_URL\]/extSaga/sincronitzaSaga/](https://djau.local/extSaga/sincronitzaSaga/) 

![](../../.gitbook/assets/image%20%2813%29.png)

Seleccionamos nuestro fichero SAGA  y presionamos sobre "Upload", si el fichero es correcto nos saldra la siguiente advertencia:

![](../../.gitbook/assets/image%20%2829%29.png)

Nos avisa de que es necesario mapear los grupos que ha leído del CSV con los de la aplicación creados en pasos anteriores.

Vamos a esta URL: [\[URL\_DJANGO\]/extSaga/assignaGrups/](https://djau.local/extSaga/assignaGrups/)

![](../../.gitbook/assets/image%20%2817%29.png)

A la izquierda aparecen los grupos leídos en el CSV, a la derecha podemos seleccionar uno de nuestros grupos, esto lo que hará es mas tarde meter a los Alumnos de un Grupo X del CSV en el Grupo Y elegido de la aplicación.

Ahora solo hay que volver a subir el fichero del SAGA en la misma URL que antes: [\[DJANGO\_URL\]/extSaga/sincronitzaSaga/](https://djau.local/extSaga/sincronitzaSaga/) 

Si todo va bien nos debería dar la siguiente salida:

![](../../.gitbook/assets/image%20%281%29.png)

Ya tenemos los Alumnos y los Grupos, ya queda menos para empezar a usar la aplicación, animo!!

