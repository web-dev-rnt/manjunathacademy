from django.db import migrations


def clear_category_icons(apps, schema_editor):
    Category = apps.get_model('myapp', 'Category')
    Category.objects.exclude(icon='').update(icon='')


class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0045_alter_course_test_type'),
    ]

    operations = [
        migrations.RunPython(clear_category_icons, migrations.RunPython.noop),
    ]
