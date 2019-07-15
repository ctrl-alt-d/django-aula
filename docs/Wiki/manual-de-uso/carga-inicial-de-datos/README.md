# Carga Inicial de datos

### Introducción

Se puede decir que este es el paso mas critico de la puesta en marcha de Django-Aula, es en este paso donde deberemos cargar todos los alumnos, profesores, aulas, asignaturas, grupos, horarios...

La aplicación tiene una serie de módulos para importar todos estos datos  desde diferentes fuentes CSV, esto permite una carga masiva de datos, una carga manual de datos es teóricamente posible pero el proceso se vuelve titanico y nada recomendable.

Si no sabes mucho del tema te preguntaras una cosa, "¿De donde obtengo todos esos datos en un CSV?"

Para la importación masiva de **alumnos** django-aula reconoce el formato de salida que ofrece el software  **SAGA.**

SAGA es un software ofrecido por la **La Generalitat de Cataluña** que permite gestionar y centralizar a nivel Autonomico la historia académica de un Alumno y cualquier centro educativo tiene acceso a este portal y a sus alumnos.

Una de las exportaciones de SAGA permite obtener una serie de alumnos junto a toda su información su aspecto es el siguiente:

{% code-tabs %}
{% code-tabs-item title="Saga\_Export\_Sample\_fakedata.csv" %}
```text
"#","00_IDENTIFICADOR DE L'ALUMNE/A","01_NOM","02_DATA NAIXEMENT","03_RESPONSABLE 1","04_TELÈFON RESP. 1","05_MÒBIL RESP. 1","06_ADREÇA ELECTR. RESP. 1","07_RESPONSABLE 2","08_TELÈFON RESP. 2","09_MÒBIL RESP. 2","10_ADREÇA ELECTR. RESP. 2","11_ADREÇA","12_LOCALITAT","13_CORREU ELECTRÒNIC","14_ALTRES TELÈFONS","15_CENTRE PROCEDÈNCIA","16_GRUPSCLASSE""1","92483170093","Torrent Ortiz, Marta","27/11/1998","Salvador Segura, Xavi","+34 XXXXXXX","+34 XXXXXXX","c/ del General Martina Dominguez Llorens","+34 XXXXXYYY","+34 XXXXZZZZ","+34 XXXXLLL","xavi@mailintaor.com","c/ de l'aviador Martina Dominguez Llorens","L'Armentera","marta@mailintaor.com","","La Salle","ESO1A""1","13450532361","Camacho Blanco, Pau","12/12/1990","Aranda Montoya, Carlota","+34 XXXXXXX","+34 XXXXXXX","c/ del General Aitana Guzman Colomer","+34 XXXXXYYY","+34 XXXXZZZZ","+34 XXXXLLL","carlota@mailintaor.com","c/ de l'aviador Aitana Guzman Colomer","L'Armentera","pau@mailintaor.com","","La Salle","ESO1A""1","74944249961","Bautista Mesa, Ana","27/07/1997","Paredes Quesada, Lluc","+34 XXXXXXX","+34 XXXXXXX","c/ del General Mariona Rius Bermudez","+34 XXXXXYYY","+34 XXXXZZZZ","+34 XXXXLLL","lluc@mailintaor.com","c/ de l'aviador Mariona Rius Bermudez","L'Armentera","ana@mailintaor.com","","La Salle","ESO1A"
```
{% endcode-tabs-item %}
{% endcode-tabs %}

Tutorial exportación de SAGA aquí.

{% page-ref page="../../anexos/exportacion-saga.md" %}

Básicamente el CSV  necesita una primera linea con las cabeceras de los campos y después lineas de Alumnos y sus datos.

Ahora bien, con lo explicado tenemos cubiertos a los alumnos, pero que pasa con los demás activos de un centro \(Profesores, Grupos, Asignaturas, Horarios..\).

En resumen la segunda parte critica de la carga de datos es importar el horario escolar de tu centro, a grandes rasgos un horario es una tabla con franjas horarias divididas por los días de la semana, donde en cada día de sus diferentes **franjas** toca una **asignatura** que la imparte un **profesor** en un **aula** a un **grupo** determinado.

![Ejemplo de horario de un grupo a la izquierda podemos observar las franjas horarias](../../.gitbook/assets/1a6bfd5a-1e4e-459a-a620-db33d8d12a72.jpg)



Ahora hay que que imaginarse un Horario Gigantesco que cubriera todos los grupos de tu centro nada mas pensar de hacerlo manualmente se me quitan las ganas de seguir escribiendo :\)

Con lo que si consiguiéramos importar  el concepto Superhorario de una sola vez, importaríamos también Profesores, grupos..etc.

Si estas implantando Django-aula ya deberías saber que existen una serie de software que permite programar de forma eficiente el año escolar, si los desconoces deberías empezar a mirar como funcionan antes de seguir leyendo. Aquí te dejo una [lista](https://www.educaciontrespuntocero.com/recursos/herramientas-elaborar-horarios/34971.html).

Bien si sigues aquí decirte que Django-Aula esta preparado para la importación masiva de datos de una exportación hecha por el software Kronowin, si no utilizas Kronowin no te asustes, la mayoría de estos programas ofrecen muchismas opciones de exportación de datos, la elegida por django-aula es un CSV lo mas básico posible, para que si usas otro software de generación de horarios puedas adaptarte a su formato.

El formato que acepta django-aula es el siguiente:

{% code-tabs %}
{% code-tabs-item title="Export\_Krono\_fakedata.csv" %}
```text
"TUT","M7","ESO1C","M","ESO","1","C","246","unk2","1","1","unk3"
"MA","M2","ESO1A","M","ESO","1","A","285","unk2","1","1","unk3"
"TUT","M6","ESO1B","M","ESO","1","B","135","unk2","1","1","unk3"
"OP1","M0","ESO2B","M","ESO","2","B","291","unk2","1","1","unk3"
"TUT","M3","ESO3A","M","ESO","3","A","310","unk2","1","1","unk3"
"GYM","M5","ESO3B","M","ESO","3","B","145","unk2","1","1","unk3"
```
{% endcode-tabs-item %}
{% endcode-tabs %}

{% hint style="info" %}
Para generar esta salida con Kronowin, elegir en las opciones de exportacion:

"**Archivo de Intercambio Kronowin**"
{% endhint %}

Donde teniendo como ejemplo la primera linea:

"**TUT**","**M7**","**ESO1C**","M","**ESO**","**1**","C","**246**","unk2","**1**","**1**","unk3"

* TUT=Código Asignatura
* M7=Código Tutor
* ESO1C=Código Grupo
* ESO=Código Nivel
* 1=Código Curso
* 246=Código Aula
* 1=Día de la semana \(1=Lunes\)
* 1=Código de franja horaria \(Mas adelante de entenderá\)

Según esta entrada, si suponemos que la primera franja horaria es de 9 a 10, El lunes de 9 a 10 tocara la asignatura TUT con el profesor M7 en el aula 246 al grupo ESO1C.

{% hint style="warning" %}
Los campos que no están en negrita no se utilizan por el programa, pero es como lo exporta Kronowin, pero deben estar allí porque la aplicación espera recibir 12 Campos.

Si usas otro programa tendrá una opción de exportación a CSV muy parecida a esta, no importa si en la salida salen campos diferentes a este, lo importante es que hayan 12 campos y que los campos que están en negrita estén en el orden correcto.

Si no te convence el tener que adaptar los CSV, tu única opción es forkear el proyecto y cambiar el parser de CSV adaptándolo a tus necesidades, no dudes en contactar con los desarrolladores para obtener un poco de ayuda.

Este documento es solo de introducción, en las siguientes paginas se explicara a fondo cada paso.
{% endhint %}





