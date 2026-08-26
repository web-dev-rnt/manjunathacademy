from django.db import migrations


DUMMY_QUESTION_TEXTS = {
    'Which of the following is a prime number?',
    'Which of the following are even numbers?',
    'What is 15% of 200?',
    'The sum of angles in a triangle is 180 degrees.',
    'The capital of India is ______.',
    'Choose the correctly spelled word.',
    'Which of these letters are vowels?',
    'If a train travels 60 km in 1.5 hours, what is its speed in km/h?',
    'Water boils at 100 degrees Celsius at sea level.',
    'The national bird of India is the ______.',
}


TEST_SERIES_CONTENT = {
    'SSC CGL Tier 1 Mock Test Series': {
        'sections': [
            ('reasoning', 'General Intelligence & Reasoning', False, '0.25'),
            ('quantitative', 'Quantitative Aptitude', False, '0.25'),
            ('english', 'English Language', True, '0.25'),
            ('awareness', 'General Awareness', True, '0.25'),
        ],
        'questions': [
            ('reasoning', 'Choose the odd one out.', 'Cat', 'Dog', 'Cow', 'Sparrow', 'D'),
            ('reasoning', 'Find the next number in the series: 2, 6, 12, 20, __.', '24', '28', '30', '32', 'C'),
            ('reasoning', 'If every letter is moved one step forward, how is SOUTH coded?', 'TPVUI', 'TPUTH', 'RNTSG', 'UQWVI', 'A'),
            ('quantitative', 'What is 25% of 480?', '100', '110', '120', '125', 'C'),
            ('quantitative', 'Two numbers are in the ratio 3:5 and their sum is 64. What is the smaller number?', '18', '24', '30', '40', 'B'),
            ('quantitative', 'Find the simple interest on Rs. 1,000 at 10% per annum for 2 years.', 'Rs. 100', 'Rs. 150', 'Rs. 200', 'Rs. 220', 'C'),
            ('english', 'Choose the synonym of “Brief”.', 'Lengthy', 'Short', 'Difficult', 'Late', 'B'),
            ('english', 'Choose the correctly spelled word.', 'Accomodation', 'Acommodation', 'Accommodation', 'Accommadation', 'C'),
            ('awareness', 'On which date was the Constitution of India adopted?', '15 August 1947', '26 January 1950', '26 November 1949', '2 October 1948', 'C'),
            ('awareness', 'Which is the largest planet in the Solar System?', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'C'),
        ],
    },
    'Railway RRB NTPC Practice Sets': {
        'sections': [
            ('maths', 'Mathematics', False, '0.33'),
            ('reasoning', 'General Intelligence & Reasoning', False, '0.33'),
            ('awareness', 'General Awareness', True, '0.33'),
            ('science', 'General Science', True, '0.33'),
        ],
        'questions': [
            ('maths', 'Convert 72 km/h into metres per second.', '18 m/s', '20 m/s', '22 m/s', '24 m/s', 'B'),
            ('maths', 'What is the LCM of 12 and 18?', '24', '30', '36', '48', 'C'),
            ('maths', 'If 15 workers complete a job in 12 days, how many days will 20 workers take at the same rate?', '8', '9', '10', '16', 'B'),
            ('reasoning', 'Find the next number: 3, 8, 15, 24, 35, __.', '44', '46', '48', '50', 'C'),
            ('reasoning', 'A is the brother of B, and B is the sister of C. How is A related to C?', 'Brother', 'Sister', 'Father', 'Cousin', 'A'),
            ('reasoning', 'A person faces north, turns right twice, and stops. Which direction is the person facing?', 'East', 'West', 'North', 'South', 'D'),
            ('awareness', 'India’s first passenger train ran between which two places?', 'Delhi and Agra', 'Mumbai and Thane', 'Kolkata and Howrah', 'Chennai and Arakkonam', 'B'),
            ('awareness', 'Article 21 of the Indian Constitution protects which right?', 'Right to equality', 'Freedom of religion', 'Life and personal liberty', 'Right to education only', 'C'),
            ('science', 'What is the SI unit of force?', 'Joule', 'Pascal', 'Newton', 'Watt', 'C'),
            ('science', 'Deficiency of vitamin C causes which disease?', 'Rickets', 'Scurvy', 'Beriberi', 'Night blindness', 'B'),
        ],
    },
    'Banking Reasoning Sectional Tests': {
        'sections': [
            ('reasoning', 'Reasoning Ability', False, '0.25'),
            ('quantitative', 'Quantitative Aptitude', False, '0.25'),
            ('english', 'English Language', True, '0.25'),
            ('banking', 'Banking Awareness', True, '0.25'),
        ],
        'questions': [
            ('reasoning', 'Find the next number: 5, 11, 23, 47, __.', '71', '89', '95', '97', 'C'),
            ('reasoning', 'If BANK is coded by moving every letter one step forward, what is the code?', 'CBOL', 'CAML', 'AZMJ', 'DBPM', 'A'),
            ('reasoning', 'In a row of 30 people, Riya is 12th from the left. What is her position from the right?', '18th', '19th', '20th', '21st', 'B'),
            ('quantitative', 'What is 18% of 500?', '80', '85', '90', '95', 'C'),
            ('quantitative', 'What is the compound interest on Rs. 1,000 at 10% per annum for 2 years?', 'Rs. 200', 'Rs. 210', 'Rs. 220', 'Rs. 240', 'B'),
            ('quantitative', 'Find the average of 18, 22, 25 and 15.', '18', '19', '20', '21', 'C'),
            ('english', 'Choose the synonym of “Prudent”.', 'Careless', 'Cautious', 'Noisy', 'Generous', 'B'),
            ('english', 'Choose the antonym of “Scarce”.', 'Rare', 'Limited', 'Abundant', 'Small', 'C'),
            ('banking', 'The repo rate is the rate at which the RBI lends money to whom?', 'Customers', 'Commercial banks', 'State governments only', 'Insurance companies only', 'B'),
            ('banking', 'What does NEFT stand for?', 'National Electronic Funds Transfer', 'New Exchange Finance Transaction', 'National Equity Fund Trade', 'Net Enabled Finance Tool', 'A'),
        ],
    },
    'CBSE Class 10 Sample Papers': {
        'sections': [
            ('maths', 'Mathematics', False, '0.00'),
            ('science', 'Science', False, '0.00'),
            ('social', 'Social Science', True, '0.00'),
            ('english', 'English', True, '0.00'),
        ],
        'questions': [
            ('maths', 'What are the roots of x² − 5x + 6 = 0?', '1 and 6', '2 and 3', '−2 and −3', '3 and 5', 'B'),
            ('maths', 'What is the slope of the line y = 2x + 3?', '2', '3', '−2', '1/2', 'A'),
            ('maths', 'What is the value of sin 30°?', '0', '1/2', '√3/2', '1', 'B'),
            ('science', 'Which cell organelle is called the powerhouse of the cell?', 'Nucleus', 'Ribosome', 'Mitochondrion', 'Vacuole', 'C'),
            ('science', 'What is the pH of a neutral solution at room temperature?', '0', '5', '7', '14', 'C'),
            ('science', 'Which relation represents Ohm’s law?', 'V = IR', 'P = VI', 'F = ma', 'E = mc²', 'A'),
            ('social', 'Which constitutional amendment gave constitutional status to Panchayati Raj institutions?', '42nd', '44th', '73rd', '86th', 'C'),
            ('social', 'Which treaty formally ended the First World War?', 'Treaty of Paris', 'Treaty of Versailles', 'Treaty of Vienna', 'Treaty of Tordesillas', 'B'),
            ('english', 'Identify the figure of speech in “as brave as a lion”.', 'Metaphor', 'Personification', 'Simile', 'Alliteration', 'C'),
            ('english', 'Choose the correct passive form of “They completed the work.”', 'The work completed them.', 'The work was completed by them.', 'They were completed by the work.', 'The work is completed by them.', 'B'),
        ],
    },
    'NEET Previous Year Papers (2016-2025)': {
        'sections': [
            ('physics', 'Physics', False, '1.00'),
            ('chemistry', 'Chemistry', False, '1.00'),
            ('biology', 'Biology', False, '1.00'),
        ],
        'questions': [
            ('physics', 'What is the SI unit of electric field?', 'N/C', 'C/N', 'J·s', 'W/m', 'A'),
            ('physics', 'The slope of a velocity-time graph represents which quantity?', 'Displacement', 'Acceleration', 'Momentum', 'Force', 'B'),
            ('physics', 'Which lens is used to correct myopia?', 'Convex lens', 'Concave lens', 'Cylindrical lens', 'Bifocal lens only', 'B'),
            ('chemistry', 'What is the atomic number of oxygen?', '6', '7', '8', '16', 'C'),
            ('chemistry', 'The pH of gastric acid is closest to which value?', '2', '7', '9', '12', 'A'),
            ('chemistry', 'What is the approximate value of Avogadro’s constant?', '6.022 × 10²³', '3.0 × 10⁸', '9.8 × 10²', '1.6 × 10⁻¹⁹', 'A'),
            ('biology', 'Which cell structure is the main site of protein synthesis?', 'Lysosome', 'Ribosome', 'Golgi apparatus', 'Centriole', 'B'),
            ('biology', 'What is the functional unit of the kidney?', 'Neuron', 'Alveolus', 'Nephron', 'Villus', 'C'),
            ('biology', 'Which hormone lowers blood glucose level?', 'Glucagon', 'Adrenaline', 'Insulin', 'Thyroxine', 'C'),
            ('biology', 'Who proposed the double-helix model of DNA?', 'Darwin and Wallace', 'Watson and Crick', 'Mendel and Morgan', 'Meselson and Stahl', 'B'),
        ],
        'marks': 4,
    },
}


def seed_test_series_content(apps, schema_editor):
    Course = apps.get_model('myapp', 'Course')
    Question = apps.get_model('myapp', 'Question')
    TestSection = apps.get_model('myapp', 'TestSection')

    for course_name, content in TEST_SERIES_CONTENT.items():
        course = Course.objects.filter(course_type='test_series', name=course_name).first()
        if not course:
            continue

        has_optional = any(section[2] for section in content['sections'])
        desired_limit = 1 if has_optional else 0
        if course.max_optional_sections != desired_limit:
            course.max_optional_sections = desired_limit
            course.save(update_fields=['max_optional_sections'])

        sections = {}
        for position, (key, name, is_optional, negative_marks) in enumerate(content['sections']):
            section = TestSection.objects.filter(course=course, name=name).first()
            if not section and position == 0:
                generic = TestSection.objects.filter(course=course, name__in=['Section A', 'Section - A']).first()
                if generic and not Question.objects.filter(section=generic).exists():
                    generic.name = name
                    generic.is_optional = is_optional
                    generic.negative_marks = negative_marks
                    generic.order = position
                    generic.save(update_fields=['name', 'is_optional', 'negative_marks', 'order'])
                    section = generic
            if not section:
                section = TestSection.objects.create(
                    course=course,
                    name=name,
                    is_optional=is_optional,
                    negative_marks=negative_marks,
                    order=position,
                )
            sections[key] = section

        placeholders = list(
            Question.objects.filter(course=course, text__in=DUMMY_QUESTION_TEXTS).order_by('order', 'id')
        )
        question_marks = content.get('marks', 1)
        for order, question_data in enumerate(content['questions']):
            section_key, text, option_a, option_b, option_c, option_d, correct_answer = question_data
            question = Question.objects.filter(course=course, text=text).first()
            if not question:
                question = placeholders.pop(0) if placeholders else Question(course=course)
                question.text = text
                question.question_type = 'single'
                question.option_a = option_a
                question.option_b = option_b
                question.option_c = option_c
                question.option_d = option_d
                question.correct_answer = correct_answer
                question.marks = question_marks
            question.section = sections[section_key]
            question.order = order
            question.save()


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0058_course_max_optional_sections'),
    ]

    operations = [
        migrations.RunPython(seed_test_series_content, migrations.RunPython.noop),
    ]
