# Carga de Alumnos Fichero SAGA

Hasta ahora tenemos cargados los grupos de nuestro centro ahora es el momento de importar los alumnos.

Recuerda que Django-Aula solo permite la importación de alumnos desde una exportación hecha desde SAGA, el proceso de obtención de esta exportación esta explicado en [TutorialALUMNES_SAGA-ESFER@_a_DJAU.pdf](../../../installacio/TutorialALUMNES_SAGA-ESFER@_a_DJAU.pdf)

Se creará un usuario de acceso individual para cada alumno y responsable. Es necesario informar del DNI de los responsables para poder crear su usuario correspondiente.

Si desde SAGA no esta especificado el grupo al que pertenece el Alumno consultar [IMPORTAR_A_DJAUsense_curs_actualitzat.pdf](../../../installacio/IMPORTAR_A_DJAUsense_curs_actualitzat.pdf)

Vale llego el momento de la verdad, nos dirigimos a esta URL: \[URL\_DJAU\]/extSaga/sincronitzaSaga/ 

![](../../.gitbook/assets/image%20%2813%29.png)

Seleccionamos nuestro fichero SAGA  y presionamos sobre "Upload", si el fichero es correcto nos saldra la siguiente advertencia:

![](../../.gitbook/assets/image%20%2829%29.png)

Nos avisa de que es necesario mapear los grupos que ha leído del CSV con los de la aplicación creados en pasos anteriores.

Vamos a esta URL: \[URL\_DJAU\]/extSaga/assignaGrups/

![](../../.gitbook/assets/image%20%2817%29.png)

A la izquierda aparecen los grupos leídos en el CSV, a la derecha podemos seleccionar uno de nuestros grupos, esto lo que hará es mas tarde meter a los Alumnos de un Grupo X del CSV en el Grupo Y elegido de la aplicación.

Ahora solo hay que volver a subir el fichero del SAGA en la misma URL que antes: \[URL\_DJAU\]/extSaga/sincronitzaSaga/

Si todo va bien nos debería dar la siguiente salida:

![](../../.gitbook/assets/image%20%281%29.png)

Ya tenemos los Alumnos y los Grupos, ya queda menos para empezar a usar la aplicación, animo!!

