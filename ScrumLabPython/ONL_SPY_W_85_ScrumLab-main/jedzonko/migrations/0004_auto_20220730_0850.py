# Generated by Django 2.2.6 on 2022-07-30 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jedzonko', '0003_auto_20220729_1009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dayname',
            name='day_name',
            field=models.CharField(choices=[('PON', 'Poniedziałek'), ('WTO', 'Wtorek'), ('SRO', 'Środa'), ('CZW', 'Czwartek'), ('PIA', 'Piątek'), ('SOB', 'Sobota'), ('NIE', 'Niedziela')], max_length=3, unique=True),
        ),
        migrations.AlterField(
            model_name='recipeplan',
            name='meal_name',
            field=models.CharField(max_length=64),
        ),
    ]
