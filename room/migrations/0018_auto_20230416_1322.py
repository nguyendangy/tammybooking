# Generated by Django 3.1.4 on 2023-04-16 13:22

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0017_auto_20230416_1320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='room_include',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('Breakfast', 'Breakfast'), ('Bar', 'Bar'), ('Free WiFi', 'Free WiFi'), ('Room service', 'Room service'), ('Private Bathroom', 'Private Bathroom')], max_length=200),
        ),
    ]