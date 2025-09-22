from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='destacado',
            field=models.BooleanField(default=False),
        ),
    ]
