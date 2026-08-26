from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0057_test_sections'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='max_optional_sections',
            field=models.PositiveIntegerField(
                default=1,
                help_text='Maximum optional sections a student may choose before starting a Test Series exam.',
            ),
        ),
    ]
