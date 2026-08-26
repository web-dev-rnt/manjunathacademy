from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0047_coursevideo'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('pdf_file', models.FileField(help_text='Upload a PDF document.', upload_to='elibrary_pdfs/collection/')),
                ('pages', models.PositiveIntegerField(blank=True, null=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('course', models.ForeignKey(limit_choices_to={'course_type': 'elibrary'}, on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='myapp.course')),
            ],
            options={'ordering': ['order', 'id']},
        ),
    ]
