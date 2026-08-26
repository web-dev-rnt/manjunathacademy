from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0056_course_highlights'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='e.g. Section A — Mathematics', max_length=120)),
                ('is_optional', models.BooleanField(default=False, help_text='Students may choose whether to attempt this section.')),
                ('negative_marks', models.DecimalField(decimal_places=2, default=0, help_text='Marks deducted for each incorrect answer in this section.', max_digits=5)),
                ('order', models.PositiveIntegerField(default=0)),
                ('course', models.ForeignKey(limit_choices_to={'course_type': 'test_series'}, on_delete=django.db.models.deletion.CASCADE, related_name='test_sections', to='myapp.course')),
            ],
            options={
                'ordering': ['order', 'id'],
                'unique_together': {('course', 'name')},
            },
        ),
        migrations.AddField(
            model_name='question',
            name='section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='questions', to='myapp.testsection'),
        ),
        migrations.AddField(
            model_name='testattempt',
            name='selected_section_ids',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
