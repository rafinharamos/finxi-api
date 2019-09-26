# Generated by Django 2.2.5 on 2019-09-25 13:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Demandas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descricao', models.CharField(max_length=150, verbose_name='Descrição')),
                ('endereco', models.CharField(max_length=60, verbose_name='endereço')),
                ('contato', models.CharField(max_length=150, verbose_name='Contato')),
                ('finalizado', models.BooleanField(default=False)),
                ('anunciante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Demanda',
                'verbose_name_plural': 'Demandas',
            },
        ),
    ]
