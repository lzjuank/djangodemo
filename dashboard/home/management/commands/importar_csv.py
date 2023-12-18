# management/commands/importar_csv.py en miapp

import csv
from django.core.management.base import BaseCommand
from home.models import NTDdata

class Command(BaseCommand):
    help = 'Importa datos desde un archivo CSV a la base de datos'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Ruta del archivo CSV')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        with open(csv_file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                NTDdata.objects.create(
                    Date=row['Date'],
                    High=row['High'],
                    Low=row['Low'],
                    Close=row['Close'],
                    # Otros campos del modelo
                )

        self.stdout.write(self.style.SUCCESS('Datos importados exitosamente'))
