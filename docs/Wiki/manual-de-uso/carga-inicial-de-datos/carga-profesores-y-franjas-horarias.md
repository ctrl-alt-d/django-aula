# Carga Profesores y Franjas Horarias

Para la carga de Profes y Franjas Horarias hay que utilizar el mismo fichero que se utilizo para cargar los Grupos del curso, ya que ese fichero también contenía la información que necesitamos ahora.

{% page-ref page="creacion-de-niveles-cursos-y-grupos.md" %}

Nos dirijimos a la URL: [\[URL\_DJANGO\]/extKronowin/sincronitzaKronowin/](https://djau.local/extKronowin/sincronitzaKronowin/)

![](../../.gitbook/assets/image%20%2828%29.png)

Volvemos a subir el fichero generado por Kronowin u otro y deberá salir lo siguiente:

![](../../.gitbook/assets/image%20%287%29.png)

No avisa de que debemos mapear los códigos de las franjas horarias de Kronowin con nuestras propias franjas horarias creadas en la app anteriormente, ademas podemos observar como ha recogido del archivo los Códigos de los profesores del fichero y les ha asignado la contraseña por defecto a "1234".

La salida no lo muestra pero también es necesario mapear de nuevo los grupos que aparecen en Kronowin con nuestros propios Grupos.

Los profesores están ya creados ahora hay que mapear las franjas y los grupos.

Para mapear los grupos de kronowin ir a [\[DJANGO\_URL\]/extKronowin/assignaGrups/](https://djau.local/extKronowin/assignaGrups/) y mapea los grupos tal como hiciste al importar los alumnos del SAGA.

![](../../.gitbook/assets/image%20%2818%29.png)

Finalmente mapeamos las franjas desde [\[URL\_DJANGO\]/extKronowin/assignaFranges/](https://djau.local/extKronowin/assignaFranges/)

![](../../.gitbook/assets/image%20%283%29.png)

Hay que mapear la ID de la franja \(Estas ID se asignan desde el generador de horarios\) contra la franja de la app que coincida en Intervalo de tiempo.

