from django.db import migrations, models
import django.db.models.deletion


def populate_answer_snapshots(apps, schema_editor):
    TestAnswer = apps.get_model('myapp', 'TestAnswer')
    for answer in TestAnswer.objects.select_related('question', 'question__section').iterator():
        question = answer.question
        if not question:
            continue
        answer.question_text_snapshot = question.text
        answer.correct_answer_snapshot = question.correct_answer
        answer.section_name_snapshot = question.section.name if question.section else 'General'
        answer.question_marks_snapshot = question.marks
        answer.save(update_fields=[
            'question_text_snapshot',
            'correct_answer_snapshot',
            'section_name_snapshot',
            'question_marks_snapshot',
        ])


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0059_seed_test_series_sections_and_questions'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyquizattempt',
            name='answer_details',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='testanswer',
            name='correct_answer_snapshot',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AddField(
            model_name='testanswer',
            name='question_marks_snapshot',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
        migrations.AddField(
            model_name='testanswer',
            name='question_text_snapshot',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='testanswer',
            name='section_name_snapshot',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.RunPython(populate_answer_snapshots, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='testanswer',
            name='question',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='myapp.question',
            ),
        ),
    ]
