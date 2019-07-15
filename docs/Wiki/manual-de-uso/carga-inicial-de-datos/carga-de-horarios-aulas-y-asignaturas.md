# Carga de Horarios, Aulas y Asignaturas

Lo único que queda por importar son los horarios, Aulas y Materias para ello utilizaremos de nuevo el fichero proporcionado por Kronowin.

Volvemos otra vez a [\[URL\_DJANGO\]/extKronowin/sincronitzaKronowin/](https://djau.local/extKronowin/sincronitzaKronowin/) y cargamos el mismo fichero de siempre, la salida deberá ser la siguiente:

![](../../.gitbook/assets/image%20%2816%29.png)

{% hint style="info" %}
Dice que ha creado 0 Aulas pero es falso, si que las ha creado, se debe a un pequeño bug de la vista.
{% endhint %}

Ya tenemos todos los activos del centro, el siguiente paso es entrelazar todos los Items para generar el "SuperHorario", pero antes vamos a realizar un par de tareas recomendables.

