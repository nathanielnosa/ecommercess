# Generated by Django 4.0.4 on 2022-05-27 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0005_alter_order_cart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='ref',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]