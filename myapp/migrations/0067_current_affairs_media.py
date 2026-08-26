from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0066_exam_ticker_vector_logos'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyupdatepost',
            name='thumbnail',
            field=models.ImageField(
                blank=True,
                help_text='Compact image used on the homepage and Current Affairs listing. Falls back to the main image.',
                null=True,
                upload_to='daily_updates/posts/thumbnails/',
            ),
        ),
        migrations.AddField(
            model_name='dailyupdatepost',
            name='video_url',
            field=models.URLField(
                blank=True,
                help_text='Optional direct video URL (.mp4, .webm or .ogg), or an external video page URL.',
                max_length=500,
            ),
        ),
        migrations.AddField(
            model_name='dailyupdatepost',
            name='youtube_url',
            field=models.URLField(
                blank=True,
                help_text='Optional YouTube watch, Shorts, youtu.be or embed link.',
                max_length=500,
            ),
        ),
        migrations.AlterField(
            model_name='dailyupdatepost',
            name='image',
            field=models.ImageField(
                blank=True,
                help_text='Main image shown on the full Current Affairs article.',
                null=True,
                upload_to='daily_updates/posts/',
            ),
        ),
    ]
