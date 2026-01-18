# Carga De Niveles, Cursos y Grupos

Llego el momento de hacer una de las primeras cargas de datos, es el momento de crear la estructura de cursos de nuestro centro, para ello utilizaremos la exportación de datos que nos ha proporcionado Kronowin, si no lo recuerdas lee [esto](../README.md)

Este paso no es necesario con la importación desde Untis, solamente se deberían repasar las fechas de inicio y final de curso en la consola de administrador. 

Te recuerdo que el formato que debe de tener el fichero es el siguiente:



"**TUT**","**M7**","**ESO1C**","M","**ESO**","**1**","C","**246**","unk2","**1**","**1**","unk3"

* TUT=Código Asignatura
* M7=Código Tutor
* ESO1C=Código Grupo
* ESO=Código Nivel
* 1=Código Curso
* 246=Código Aula
* 1=Día de la semana \(1=Lunes\)
* 1=Código de franja horaria

Nos dirigimos a \[URL\_DJAU\]/extKronowin/creaNivellCursGrupDesDeKronowin/

Veremos la siguiente ventana

![](../../.gitbook/assets/image%20%289%29.png)

Desde esta ventana seleccionamos el fichero CSV y tenemos que indicar la fecha de inicio y final de los cursos que vamos a crear, este intervalo de tiempo se colocara por defecto en todos los cursos, mas tarde habrá que ir una por una y colocar las fechas correctamente.

El formato de la fecha debe ser  **DD/MM/AAAA**

Si no ha habido errores podemos comprobar desde aquí \[URL\_DJAU\]/admin/alumnes/ si se ha creado la estructura de Cursos del centro.

![](../../.gitbook/assets/image%20%2826%29.png)

Ahora si queremos cambiar las fechas de inicio y fin de un curso tan solo hay que seleccionarlo y editarlo como con los otros módulos.

![](../../.gitbook/assets/image%20%2814%29.png)

![](../../.gitbook/assets/image%20%2825%29.png)

