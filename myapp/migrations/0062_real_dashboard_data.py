from django.db import migrations, models
from django.db.models import F


def backfill_payment_timestamps(apps, schema_editor):
    CourseEnrollment = apps.get_model('myapp', 'CourseEnrollment')
    StoreOrder = apps.get_model('myapp', 'StoreOrder')

    # Preserve the best available historical payment timestamp for old records.
    CourseEnrollment.objects.filter(
        is_paid=True,
        amount_paid__gt=0,
        paid_at__isnull=True,
    ).update(paid_at=F('enrolled_at'))
    StoreOrder.objects.filter(
        status__in=['paid', 'shipped', 'delivered'],
        paid_at__isnull=True,
    ).update(paid_at=F('created_at'))


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0061_exam_ticker_customization'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseenrollment',
            name='paid_at',
            field=models.DateTimeField(blank=True, help_text='When a paid course payment was confirmed.', null=True),
        ),
        migrations.AddField(
            model_name='storeorder',
            name='paid_at',
            field=models.DateTimeField(blank=True, help_text='When payment for this order was confirmed.', null=True),
        ),
        migrations.RunPython(backfill_payment_timestamps, migrations.RunPython.noop),
    ]
