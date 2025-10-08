import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gisenails.settings')
django.setup()
from django.db import connection

with connection.cursor() as c:
    c.execute("DROP TABLE IF EXISTS `reserva_reserva`;")
    c.execute("DROP TABLE IF EXISTS `reserva_horariodisponible`;")
    print('Dropped reserva_reserva and reserva_horariodisponible (if they existed)')
