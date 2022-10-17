# Generated by Django 4.1 on 2022-10-09 17:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("goals", "0003_create_new_objects"),
    ]

    operations = [
        migrations.AlterField(
            model_name="goalcategory",
            name="board",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="categories",
                to="goals.board",
                verbose_name="Доска",
            ),
        ),
    ]
