from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0046_clear_category_icons'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('video_file', models.FileField(help_text='Upload an MP4 or other browser-supported video file.', upload_to='course_videos/playlist/')),
                ('duration_minutes', models.PositiveIntegerField(blank=True, null=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('course', models.ForeignKey(limit_choices_to={'course_type': 'video_course'}, on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='myapp.course')),
            ],
            options={'ordering': ['order', 'id']},
        ),
    ]
