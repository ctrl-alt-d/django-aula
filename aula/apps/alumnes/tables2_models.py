import django_tables2 as tables


class HorariAlumneTable(tables.Table):
    hora = tables.Column()
    aula = tables.Column()
    professor = tables.Column()
    assignatura = tables.Column()
    class Meta:
         # add class="paleblue" to <table> tag
         attrs = {"class": "paleblue table table-striped"}
         template = 'bootable2.html'

