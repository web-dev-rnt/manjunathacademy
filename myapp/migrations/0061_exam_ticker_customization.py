from django.db import migrations, models


def seed_exam_ticker(apps, schema_editor):
    ExamTickerSettings = apps.get_model('myapp', 'ExamTickerSettings')
    ExamTickerItem = apps.get_model('myapp', 'ExamTickerItem')

    ExamTickerSettings.objects.get_or_create(
        pk=1,
        defaults={
            'heading': "India's Most Competitive Exams in One Platform",
            'animation_duration': 20,
            'is_active': True,
        },
    )

    items = [
        ('SSC & Railway Combo', '🏛️', '#popular-courses'),
        ('Banking Complete Pack', '💰', '#popular-courses'),
        ('NEET Foundation Pack', '🧬', '#popular-courses'),
        ('UPSC Civil Services', '📜', '#test-series'),
        ('JEE Engineering Prep', '⚙️', '#test-series'),
        ('Defence Exams', '🛡️', '#test-series'),
        ('Teaching Exams', '🍎', '#test-series'),
        ('State PSC', '🗺️', '#test-series'),
        ('Police & Constable', '👮', '#test-series'),
    ]
    for order, (label, icon, link) in enumerate(items):
        ExamTickerItem.objects.get_or_create(
            label=label,
            defaults={
                'icon': icon,
                'link': link,
                'order': order,
                'is_active': True,
            },
        )


def unseed_exam_ticker(apps, schema_editor):
    ExamTickerItem = apps.get_model('myapp', 'ExamTickerItem')
    ExamTickerSettings = apps.get_model('myapp', 'ExamTickerSettings')
    labels = [
        'SSC & Railway Combo',
        'Banking Complete Pack',
        'NEET Foundation Pack',
        'UPSC Civil Services',
        'JEE Engineering Prep',
        'Defence Exams',
        'Teaching Exams',
        'State PSC',
        'Police & Constable',
    ]
    ExamTickerItem.objects.filter(label__in=labels).delete()
    ExamTickerSettings.objects.filter(pk=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0060_result_integrity_snapshots'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExamTickerSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(default="India's Most Competitive Exams in One Platform", max_length=180)),
                ('animation_duration', models.PositiveIntegerField(default=20, help_text='Seconds for one full ticker loop. A lower number moves faster.')),
                ('is_active', models.BooleanField(default=True, verbose_name='Show exam ticker on homepage')),
            ],
            options={
                'verbose_name': 'Exam ticker settings',
                'verbose_name_plural': 'Exam ticker settings',
            },
        ),
        migrations.CreateModel(
            name='ExamTickerItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=120)),
                ('icon', models.CharField(blank=True, help_text='Emoji or a short symbol shown before the label.', max_length=20)),
                ('link', models.CharField(blank=True, help_text='Optional website path, page anchor, or full URL.', max_length=500)),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['order', 'id'],
            },
        ),
        migrations.RunPython(seed_exam_ticker, unseed_exam_ticker),
    ]
