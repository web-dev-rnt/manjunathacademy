from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0062_real_dashboard_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='bundle',
            name='image',
            field=models.ImageField(blank=True, help_text='Optional. Replaces the emoji on bundle cards. Recommended size: 800×450px.', max_length=500, null=True, upload_to='bundles/'),
        ),
    ]
