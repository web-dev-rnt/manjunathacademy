from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0055_alter_course_pdf_file_alter_course_thumbnail_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='highlights',
            field=models.TextField(
                blank=True,
                help_text='Used for Video Courses. Add one short highlight per line.',
                verbose_name='Course highlights',
            ),
        ),
    ]
