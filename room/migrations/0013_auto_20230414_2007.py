# Generated by Django 3.1.4 on 2023-04-14 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0012_auto_20230414_1955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='rate',
            field=models.IntegerField(choices=[(1, '1 star'), (2, '2 stars'), (3, '3 stars'), (4, '4 stars'), (5, '5 stars')]),
        ),
    ]