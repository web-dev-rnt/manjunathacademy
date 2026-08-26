from django.db import migrations, models


TICKER_LOGOS = {
    'SSC & Railway Combo': 'railway',
    'Banking Complete Pack': 'banking',
    'NEET Foundation Pack': 'medical',
    'UPSC Civil Services': 'civil',
    'JEE Engineering Prep': 'engineering',
    'Defence Exams': 'defence',
    'Teaching Exams': 'teaching',
    'State PSC': 'state',
    'Police & Constable': 'police',
}


def map_existing_ticker_logos(apps, schema_editor):
    ExamTickerItem = apps.get_model('myapp', 'ExamTickerItem')
    for label, logo_key in TICKER_LOGOS.items():
        ExamTickerItem.objects.filter(label=label).update(logo_key=logo_key)


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0065_category_logos_and_more_test_series'),
    ]

    operations = [
        migrations.AddField(
            model_name='examtickeritem',
            name='logo_key',
            field=models.CharField(
                choices=[
                    ('general', 'General exams'),
                    ('school', 'School education'),
                    ('staff', 'Staff selection'),
                    ('railway', 'Railway'),
                    ('banking', 'Banking'),
                    ('medical', 'Medical'),
                    ('engineering', 'Engineering'),
                    ('civil', 'Civil services'),
                    ('defence', 'Defence'),
                    ('teaching', 'Teaching'),
                    ('state', 'State exams'),
                    ('police', 'Police'),
                ],
                default='general',
                help_text='Vector logo displayed beside this exam category.',
                max_length=20,
            ),
        ),
        migrations.RunPython(map_existing_ticker_logos, migrations.RunPython.noop),
    ]
