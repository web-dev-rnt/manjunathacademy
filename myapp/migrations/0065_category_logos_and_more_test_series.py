from django.db import migrations, models
from django.db.models import Max


CATEGORY_LOGOS = {
    'CBSE': 'school',
    'ICSE': 'school',
    'UP Board': 'school',
    'SSC': 'staff',
    'Railway': 'railway',
    'Banking & Insurance': 'banking',
    'NEET': 'medical',
    'JEE': 'engineering',
}


NEW_CATEGORIES = [
    ('UPSC & Civil Services', 'civil'),
    ('Defence Exams', 'defence'),
    ('Teaching Exams', 'teaching'),
    ('State PSC', 'state'),
    ('Police & Constable', 'police'),
    ('Engineering Entrance', 'engineering'),
]


TEST_SERIES_DATA = [
    {
        'name': 'UPSC Prelims General Studies Mock Test',
        'category': 'UPSC & Civil Services',
        'test_type': 'mock_test',
        'original_price': '599.00',
        'current_price': '299.00',
        'duration_minutes': 120,
        'about': 'A balanced UPSC prelims practice test covering polity, history, economy and general studies.',
        'sections': [
            ('polity', 'Indian Polity', '0.33'),
            ('general', 'General Studies', '0.33'),
        ],
        'questions': [
            ('polity', 'On which date was the Constitution of India adopted?', '15 August 1947', '26 January 1950', '26 November 1949', '2 October 1948', 'C'),
            ('polity', 'Which amendment added Fundamental Duties to the Constitution of India?', '24th Amendment', '42nd Amendment', '44th Amendment', '73rd Amendment', 'B'),
            ('polity', 'Which article is associated with the Right to Constitutional Remedies?', 'Article 14', 'Article 19', 'Article 21', 'Article 32', 'D'),
            ('polity', 'The Goods and Services Tax was enabled by which Constitutional Amendment?', '91st', '97th', '101st', '103rd', 'C'),
            ('general', 'In which year did the Reserve Bank of India begin operations?', '1935', '1947', '1950', '1955', 'A'),
            ('general', 'Which Harappan site is well known for its ancient dockyard?', 'Kalibangan', 'Lothal', 'Rakhigarhi', 'Banawali', 'B'),
            ('general', 'Which is the largest Indian state by area?', 'Madhya Pradesh', 'Maharashtra', 'Rajasthan', 'Uttar Pradesh', 'C'),
            ('general', 'Which mountain range is older than the Himalayas?', 'Aravalli Range', 'Karakoram Range', 'Pir Panjal Range', 'Zanskar Range', 'A'),
        ],
    },
    {
        'name': 'NDA & CDS General Ability Test',
        'category': 'Defence Exams',
        'test_type': 'mock_test',
        'original_price': '499.00',
        'current_price': '249.00',
        'duration_minutes': 120,
        'about': 'Defence entrance practice in general knowledge, English, mathematics and reasoning.',
        'sections': [
            ('ability', 'General Ability', '0.33'),
            ('aptitude', 'Aptitude & English', '0.33'),
        ],
        'questions': [
            ('ability', 'Which body conducts the National Defence Academy examination?', 'Staff Selection Commission', 'Union Public Service Commission', 'National Testing Agency', 'Indian Army', 'B'),
            ('ability', 'Where is the Officers Training Academy located?', 'Chennai', 'Pune', 'Dehradun', 'Kochi', 'A'),
            ('ability', 'What is India\'s highest wartime gallantry award?', 'Ashoka Chakra', 'Maha Vir Chakra', 'Param Vir Chakra', 'Vir Chakra', 'C'),
            ('ability', 'Indian Army Day is observed on which date?', '15 January', '26 January', '4 December', '8 October', 'A'),
            ('aptitude', 'A vehicle travels at 60 km/h for 2 hours. What distance does it cover?', '30 km', '60 km', '90 km', '120 km', 'D'),
            ('aptitude', 'Choose the synonym of "valiant".', 'Brave', 'Careless', 'Silent', 'Weak', 'A'),
            ('aptitude', 'Find the next number: 2, 5, 10, 17, 26, __.', '33', '35', '37', '39', 'C'),
            ('aptitude', 'If 3x + 5 = 20, what is x?', '3', '4', '5', '6', 'C'),
        ],
    },
    {
        'name': 'CTET Paper I Practice Test',
        'category': 'Teaching Exams',
        'test_type': 'practice_test',
        'original_price': '299.00',
        'current_price': '149.00',
        'duration_minutes': 90,
        'about': 'Practice child development, pedagogy, language, mathematics and environmental studies for CTET Paper I.',
        'sections': [
            ('pedagogy', 'Child Development & Pedagogy', '0.00'),
            ('subject', 'Language, Maths & EVS', '0.00'),
        ],
        'questions': [
            ('pedagogy', 'In child-centred education, the learner is primarily viewed as what?', 'A passive listener', 'An active participant', 'A silent observer', 'A note-copying assistant', 'B'),
            ('pedagogy', 'Formative assessment is generally conducted at what stage?', 'Only after the final examination', 'During the teaching-learning process', 'Before admission only', 'Only once each year', 'B'),
            ('pedagogy', 'Inclusive education aims to teach children with diverse needs in which setting?', 'Separate schools only', 'The same classroom with suitable support', 'Home study only', 'No structured setting', 'B'),
            ('pedagogy', 'The Zone of Proximal Development is associated with which psychologist?', 'Jean Piaget', 'B. F. Skinner', 'Lev Vygotsky', 'Sigmund Freud', 'C'),
            ('subject', 'What is three-fourths of 200?', '100', '125', '150', '175', 'C'),
            ('subject', 'What is the HCF of 24 and 36?', '6', '8', '12', '18', 'C'),
            ('subject', 'Choose the synonym of "rapid".', 'Slow', 'Swift', 'Quiet', 'Late', 'B'),
            ('subject', 'Which process changes liquid water into water vapour?', 'Condensation', 'Freezing', 'Evaporation', 'Precipitation', 'C'),
        ],
    },
    {
        'name': 'UPPSC PCS Prelims Mock Test',
        'category': 'State PSC',
        'test_type': 'mock_test',
        'original_price': '499.00',
        'current_price': '249.00',
        'duration_minutes': 120,
        'about': 'A state civil services mock test covering Uttar Pradesh knowledge, polity and aptitude.',
        'sections': [
            ('state', 'Uttar Pradesh General Knowledge', '0.33'),
            ('aptitude', 'Polity & Aptitude', '0.33'),
        ],
        'questions': [
            ('state', 'What is the capital of Uttar Pradesh?', 'Kanpur', 'Lucknow', 'Agra', 'Varanasi', 'B'),
            ('state', 'The principal seat of the Allahabad High Court is in which city?', 'Lucknow', 'Noida', 'Prayagraj', 'Meerut', 'C'),
            ('state', 'Dudhwa National Park is located in which district?', 'Lakhimpur Kheri', 'Jhansi', 'Gorakhpur', 'Mathura', 'A'),
            ('state', 'The confluence of the Ganga, Yamuna and the mythical Saraswati is at which city?', 'Ayodhya', 'Prayagraj', 'Varanasi', 'Mirzapur', 'B'),
            ('aptitude', 'Who appoints the Governor of an Indian state?', 'Prime Minister', 'Chief Minister', 'President of India', 'Chief Justice of India', 'C'),
            ('aptitude', 'Which amendment gave constitutional status to Panchayati Raj institutions?', '42nd', '44th', '73rd', '86th', 'C'),
            ('aptitude', 'What is 15% of 640?', '86', '90', '96', '102', 'C'),
            ('aptitude', 'Find the next number: 4, 9, 16, 25, __.', '30', '32', '36', '49', 'C'),
        ],
    },
    {
        'name': 'Police Constable Recruitment Practice Test',
        'category': 'Police & Constable',
        'test_type': 'practice_test',
        'original_price': '199.00',
        'current_price': '99.00',
        'duration_minutes': 90,
        'about': 'A practical police recruitment set with general awareness, reasoning, mathematics and language.',
        'sections': [
            ('awareness', 'General Awareness', '0.25'),
            ('aptitude', 'Reasoning & Aptitude', '0.25'),
        ],
        'questions': [
            ('awareness', 'What does FIR stand for?', 'First Investigation Record', 'First Information Report', 'Formal Incident Review', 'Federal Inquiry Report', 'B'),
            ('awareness', 'What is India\'s single emergency response support number?', '100', '101', '108', '112', 'D'),
            ('awareness', 'A red traffic signal instructs a driver to do what?', 'Proceed slowly', 'Turn only', 'Stop', 'Sound the horn', 'C'),
            ('awareness', 'Article 21 of the Constitution protects which right?', 'Right to property', 'Life and personal liberty', 'Freedom of religion only', 'Right to vote', 'B'),
            ('aptitude', 'Two numbers are in the ratio 2:3 and total 50. What is the smaller number?', '10', '20', '25', '30', 'B'),
            ('aptitude', 'What is 20% of 450?', '45', '80', '90', '100', 'C'),
            ('aptitude', 'Choose the antonym of "lawful".', 'Legal', 'Valid', 'Unlawful', 'Formal', 'C'),
            ('aptitude', 'If all roses are flowers and some flowers fade quickly, which statement must be true?', 'All flowers are roses', 'All roses are flowers', 'No roses fade', 'No flowers are roses', 'B'),
        ],
    },
    {
        'name': 'JEE Main Physics Chapter Test',
        'category': 'Engineering Entrance',
        'test_type': 'sectional_test',
        'original_price': '399.00',
        'current_price': '199.00',
        'duration_minutes': 60,
        'about': 'A focused JEE Main chapter test covering mechanics, electricity, optics and units.',
        'marks': 4,
        'sections': [
            ('mechanics', 'Mechanics', '1.00'),
            ('electricity', 'Electricity & Optics', '1.00'),
        ],
        'questions': [
            ('mechanics', 'What is the SI unit of force?', 'Joule', 'Newton', 'Pascal', 'Watt', 'B'),
            ('mechanics', 'Ignoring air resistance, the acceleration of a projectile is directed how?', 'Horizontally forward', 'Vertically upward', 'Vertically downward', 'Along its velocity', 'C'),
            ('mechanics', 'Which expression gives the kinetic energy of a body of mass m moving with speed v?', 'mv', 'mv squared', 'one-half mv squared', '2mv squared', 'C'),
            ('mechanics', 'What is the SI unit of linear momentum?', 'kg m/s', 'kg m/s squared', 'N/m', 'J/s', 'A'),
            ('electricity', 'Which equation represents Ohm\'s law?', 'V = IR', 'P = VI', 'F = ma', 'Q = It squared', 'A'),
            ('electricity', 'The power P of a thin lens with focal length f in metres is given by which relation?', 'P = f', 'P = 1/f', 'P = f squared', 'P = 1/f squared', 'B'),
            ('electricity', 'Two resistors of 3 ohm and 5 ohm are connected in series. What is their equivalent resistance?', '1.875 ohm', '2 ohm', '8 ohm', '15 ohm', 'C'),
            ('electricity', 'What is the SI unit of electric current?', 'Volt', 'Ampere', 'Coulomb', 'Ohm', 'B'),
        ],
    },
]


def seed_categories_and_tests(apps, schema_editor):
    Category = apps.get_model('myapp', 'Category')
    Course = apps.get_model('myapp', 'Course')
    Question = apps.get_model('myapp', 'Question')
    TestSection = apps.get_model('myapp', 'TestSection')

    for name, logo_key in CATEGORY_LOGOS.items():
        Category.objects.filter(name=name).update(logo_key=logo_key)

    category_order = (Category.objects.aggregate(value=Max('order'))['value'] or 0) + 1
    for offset, (name, logo_key) in enumerate(NEW_CATEGORIES):
        category, created = Category.objects.get_or_create(
            name=name,
            defaults={'logo_key': logo_key, 'order': category_order + offset},
        )
        if not created and category.logo_key == 'general':
            category.logo_key = logo_key
            category.save(update_fields=['logo_key'])

    course_order = (
        Course.objects.filter(course_type='test_series').aggregate(value=Max('order'))['value'] or 0
    ) + 1

    for course_offset, content in enumerate(TEST_SERIES_DATA):
        category = Category.objects.get(name=content['category'])
        course, _ = Course.objects.get_or_create(
            course_type='test_series',
            name=content['name'],
            defaults={
                'category': category,
                'test_type': content['test_type'],
                'original_price': content['original_price'],
                'current_price': content['current_price'],
                'duration_minutes': content['duration_minutes'],
                'max_optional_sections': 0,
                'about': content['about'],
                'order': course_order + course_offset,
                'is_active': True,
            },
        )

        sections = {}
        for section_order, (key, section_name, negative_marks) in enumerate(content['sections']):
            section, _ = TestSection.objects.get_or_create(
                course=course,
                name=section_name,
                defaults={
                    'is_optional': False,
                    'negative_marks': negative_marks,
                    'order': section_order,
                },
            )
            sections[key] = section

        for question_order, question_data in enumerate(content['questions']):
            section_key, text, option_a, option_b, option_c, option_d, correct_answer = question_data
            Question.objects.get_or_create(
                course=course,
                text=text,
                defaults={
                    'section': sections[section_key],
                    'question_type': 'single',
                    'option_a': option_a,
                    'option_b': option_b,
                    'option_c': option_c,
                    'option_d': option_d,
                    'correct_answer': correct_answer,
                    'marks': content.get('marks', 1),
                    'order': question_order,
                },
            )


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0064_merge_20260826_2137'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
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
                max_length=20,
            ),
        ),
        migrations.RunPython(seed_categories_and_tests, migrations.RunPython.noop),
    ]
