from django.core.management.base import BaseCommand
from django.db import transaction

from myapp.models import Category, Course, Question


# Each bank is 5 real, curriculum-appropriate questions: (question_text, [A, B, C, D], correct_letter)
QUESTION_BANKS = {
    'class10_maths': [
        ('What are the roots of the quadratic equation x² − 5x + 6 = 0?', ['2, 3', '1, 6', '-2, -3', '2, -3'], 'A'),
        ('The sum of the first 10 natural numbers is:', ['45', '55', '50', '60'], 'B'),
        ('If the discriminant of a quadratic equation is negative, the equation has:', ['Two distinct real roots', 'Two equal real roots', 'No real roots', 'Infinite roots'], 'C'),
        ('The value of √225 is:', ['13', '15', '25', '12'], 'B'),
        ('In a right triangle, if one angle is 90° and another is 30°, the third angle is:', ['90°', '45°', '60°', '30°'], 'C'),
    ],
    'class10_science': [
        ('The chemical formula of common salt is:', ['NaCl', 'CaCO3', 'NaHCO3', 'KCl'], 'A'),
        ('Which gas is essential for photosynthesis?', ['Oxygen', 'Nitrogen', 'Carbon dioxide', 'Hydrogen'], 'C'),
        ('The SI unit of electric current is:', ['Volt', 'Ampere', 'Ohm', 'Watt'], 'B'),
        ('Which organ of the human body is primarily responsible for pumping blood?', ['Lungs', 'Heart', 'Liver', 'Kidney'], 'B'),
        ('The process by which plants lose water in the form of vapour is called:', ['Transpiration', 'Respiration', 'Photosynthesis', 'Excretion'], 'A'),
    ],
    'class10_social_science': [
        ('Who was the first Prime Minister of India?', ['Mahatma Gandhi', 'Jawaharlal Nehru', 'Sardar Patel', 'Dr. Rajendra Prasad'], 'B'),
        ('The Indian Constitution came into effect on:', ['15 August 1947', '26 January 1950', '26 November 1949', '2 October 1950'], 'B'),
        ('Which river is known as the "Sorrow of Bihar"?', ['Ganga', 'Kosi', 'Yamuna', 'Son'], 'B'),
        ('The Non-Cooperation Movement was launched by Mahatma Gandhi in:', ['1920', '1930', '1942', '1919'], 'A'),
        ('Which of these is a primary economic activity?', ['Agriculture', 'Manufacturing', 'Banking', 'Teaching'], 'A'),
    ],
    'class10_english': [
        ('Choose the correctly spelled word:', ['Recieve', 'Receive', 'Receeve', 'Receve'], 'B'),
        ("Which word in the sentence 'She sings beautifully' is an adverb?", ['She', 'Sings', 'Beautifully', 'None'], 'C'),
        ('Fill in the blank: "He ___ to school every day."', ['go', 'goes', 'going', 'gone'], 'B'),
        ('The antonym of "Ancient" is:', ['Old', 'Modern', 'Historic', 'Ruined'], 'B'),
        ('Choose the correct plural of "Child":', ['Childs', 'Childes', 'Children', 'Childrens'], 'C'),
    ],
    'class12_maths_board': [
        ('The derivative of sin(x) with respect to x is:', ['cos(x)', '-cos(x)', '-sin(x)', 'tan(x)'], 'A'),
        ('If A is a square matrix and |A| = 0, then A is called:', ['Invertible', 'Singular', 'Identity', 'Symmetric'], 'B'),
        ('The value of ∫ x dx is:', ['x²', 'x²/2 + C', '2x + C', 'x + C'], 'B'),
        ('The derivative of eˣ with respect to x is:', ['eˣ', 'x·eˣ⁻¹', 'ln(x)', '1/eˣ'], 'A'),
        ('Two lines are perpendicular if the product of their slopes is:', ['0', '1', '-1', 'Undefined'], 'C'),
    ],
    'class12_physics_board': [
        ('The SI unit of electric resistance is:', ['Ohm', 'Farad', 'Henry', 'Tesla'], 'A'),
        ("According to Ohm's Law, V equals:", ['I/R', 'IR', 'I+R', 'I−R'], 'B'),
        ('The speed of light in vacuum is approximately:', ['3×10⁵ m/s', '3×10⁸ m/s', '3×10⁶ m/s', '3×10¹⁰ m/s'], 'B'),
        ('Which of the following is a vector quantity?', ['Mass', 'Speed', 'Velocity', 'Temperature'], 'C'),
        ('The phenomenon of splitting white light into its constituent colours is called:', ['Reflection', 'Refraction', 'Dispersion', 'Diffraction'], 'C'),
    ],
    'class12_chemistry_board': [
        ('The pH of a neutral solution at 25°C is:', ['0', '7', '14', '1'], 'B'),
        ('Which of the following is an example of an alkane?', ['Ethene', 'Ethyne', 'Ethane', 'Benzene'], 'C'),
        ('The number of electrons in a neutral chlorine atom (atomic number 17) is:', ['17', '18', '7', '35'], 'A'),
        ('Which gas is produced when zinc reacts with dilute hydrochloric acid?', ['Oxygen', 'Hydrogen', 'Chlorine', 'Carbon dioxide'], 'B'),
        ('The functional group −COOH is called:', ['Aldehyde', 'Ketone', 'Carboxylic acid', 'Alcohol'], 'C'),
    ],
    'class12_biology_board': [
        ('The powerhouse of the cell is:', ['Nucleus', 'Mitochondria', 'Ribosome', 'Golgi body'], 'B'),
        ('DNA stands for:', ['Deoxyribonucleic Acid', 'Dinucleic Acid', 'Diribonucleic Acid', 'Deoxyribose Nuclear Acid'], 'A'),
        ('The process of cell division that produces gametes is called:', ['Mitosis', 'Meiosis', 'Binary fission', 'Budding'], 'B'),
        ('Which blood group is known as the universal donor?', ['A', 'B', 'AB', 'O negative'], 'D'),
        ('Photosynthesis mainly occurs in which part of the plant cell?', ['Mitochondria', 'Chloroplast', 'Nucleus', 'Vacuole'], 'B'),
    ],
    'neet_physics': [
        ('A body moving in a circle at constant speed has:', ['Zero acceleration', 'Constant velocity', 'Acceleration directed towards the centre', 'Acceleration directed away from the centre'], 'C'),
        ('The dimensional formula of force is:', ['[MLT⁻¹]', '[MLT⁻²]', '[ML²T⁻²]', '[ML⁻¹T⁻²]'], 'B'),
        ("According to Newton's third law, for every action there is:", ['An equal and opposite reaction', 'A smaller reaction', 'No reaction', 'A delayed reaction'], 'A'),
        ('The SI unit of power is:', ['Joule', 'Newton', 'Watt', 'Pascal'], 'C'),
        ('The work done by a force is maximum when the angle between force and displacement is:', ['0°', '90°', '180°', '45°'], 'A'),
    ],
    'neet_chemistry': [
        ('The number of moles in 44 g of CO2 (molar mass 44 g/mol) is:', ['0.5', '1', '2', '4'], 'B'),
        ('Deuterium and tritium are isotopes of:', ['Oxygen', 'Hydrogen', 'Carbon', 'Nitrogen'], 'B'),
        ('The hybridization of carbon in methane (CH4) is:', ['sp', 'sp²', 'sp³', 'sp³d'], 'C'),
        ('Which of the following is a noble gas?', ['Nitrogen', 'Neon', 'Oxygen', 'Chlorine'], 'B'),
        ('Glucose belongs to which class of compounds?', ['Aldehyde', 'Ketone', 'Carbohydrate', 'Protein'], 'C'),
    ],
    'neet_biology': [
        ('The functional unit of the kidney is called the:', ['Neuron', 'Nephron', 'Alveolus', 'Nephridium'], 'B'),
        ('Which hormone is known as the "fight or flight" hormone?', ['Insulin', 'Adrenaline', 'Thyroxine', 'Estrogen'], 'B'),
        ('The genetic material in most viruses is:', ['Protein only', 'DNA or RNA', 'Lipid', 'Carbohydrate'], 'B'),
        ('Photosynthesis converts light energy into:', ['Kinetic energy', 'Chemical energy', 'Heat energy', 'Sound energy'], 'B'),
        ('The number of chromosomes in a normal human somatic cell is:', ['23', '44', '46', '48'], 'C'),
    ],
    'jee_physics': [
        ('The dimensional formula for angular momentum is:', ['[ML²T⁻¹]', '[MLT⁻¹]', '[ML²T⁻²]', '[MLT⁻²]'], 'A'),
        ('A projectile has maximum range when it is launched at an angle of:', ['30°', '45°', '60°', '90°'], 'B'),
        ("The escape velocity from Earth's surface is approximately:", ['7.9 km/s', '11.2 km/s', '3 km/s', '25 km/s'], 'B'),
        ('In simple harmonic motion, the acceleration is:', ['Constant', 'Proportional to displacement and directed towards the mean position', 'Independent of displacement', 'Directed away from the mean position'], 'B'),
        ('The equivalent resistance of two equal resistors R connected in parallel is:', ['2R', 'R/2', 'R²', '0'], 'B'),
    ],
    'jee_chemistry': [
        ('The IUPAC name of CH3-CH2-OH is:', ['Methanol', 'Ethanol', 'Propanol', 'Ethanal'], 'B'),
        ('Which of the following has the highest first ionization energy?', ['Sodium', 'Magnesium', 'Neon', 'Chlorine'], 'C'),
        ('The oxidation state of manganese in KMnO4 is:', ['+5', '+6', '+7', '+4'], 'C'),
        ('Which type of bond is formed by the sharing of electron pairs?', ['Ionic bond', 'Covalent bond', 'Metallic bond', 'Hydrogen bond'], 'B'),
        ("Le Chatelier's principle is used to study:", ['Reaction rate', 'Chemical equilibrium', 'Atomic structure', 'Radioactivity'], 'B'),
    ],
    'jee_maths': [
        ('The value of sin²θ + cos²θ is:', ['0', '1', '2', 'Depends on θ'], 'B'),
        ('The number of ways to arrange 5 distinct objects in a row is:', ['5', '25', '120', '60'], 'C'),
        ("If f(x) = x², the derivative f'(x) is:", ['x', '2x', 'x²', '2'], 'B'),
        ('The determinant of a 2×2 identity matrix is:', ['0', '1', '2', '-1'], 'B'),
        ('The sum to infinity of a geometric series with first term a and common ratio r (|r|<1) is:', ['a/(1-r)', 'a(1-r)', 'a·r', 'a/(1+r)'], 'A'),
    ],
    'ssc_gk': [
        ('Who is known as the chief architect of the Indian Constitution?', ['Mahatma Gandhi', 'Dr. B. R. Ambedkar', 'Jawaharlal Nehru', 'Sardar Patel'], 'B'),
        ('The headquarters of the United Nations is located in:', ['Geneva', 'Paris', 'New York', 'London'], 'C'),
        ('Which is the largest state in India by area?', ['Madhya Pradesh', 'Maharashtra', 'Rajasthan', 'Uttar Pradesh'], 'C'),
        ('The currency of Japan is:', ['Yuan', 'Yen', 'Won', 'Ringgit'], 'B'),
        ('The Reserve Bank of India was established in:', ['1935', '1947', '1950', '1969'], 'A'),
    ],
    'ssc_quant': [
        ('What is 15% of 200?', ['20', '30', '25', '35'], 'B'),
        ('The average of 10, 20, and 30 is:', ['15', '20', '25', '30'], 'B'),
        ('If the cost price of an item is ₹500 and it is sold for ₹600, the profit percentage is:', ['10%', '15%', '20%', '25%'], 'C'),
        ('The simple interest on ₹1000 at 10% per annum for 2 years is:', ['₹100', '₹150', '₹200', '₹250'], 'C'),
        ('The LCM of 4 and 6 is:', ['12', '24', '6', '18'], 'A'),
    ],
    'ssc_english': [
        ('Choose the correct synonym of "Happy":', ['Sad', 'Joyful', 'Angry', 'Tired'], 'B'),
        ('Choose the correctly punctuated sentence:', ['"Where are you going."', '"Where are you going?"', '"where are you going?"', '"Where are you going,"'], 'B'),
        ('The past tense of "Go" is:', ['Gone', 'Goed', 'Went', 'Going'], 'C'),
        ('Choose the correct article: "___ apple a day keeps the doctor away."', ['A', 'An', 'The', 'No article'], 'B'),
        ('Identify the correctly spelled word:', ['Definately', 'Definitely', 'Definitly', 'Definetely'], 'B'),
    ],
    'ssc_reasoning': [
        ('Find the odd one out:', ['Dog', 'Cat', 'Cow', 'Chair'], 'D'),
        ('If A=1, B=2, C=3 and so on, what does J equal?', ['9', '10', '11', '8'], 'B'),
        ('Complete the series: 2, 4, 8, 16, ___', ['24', '32', '30', '20'], 'B'),
        ("Pointing to a photograph, a man says, \"She is the daughter of my grandfather's only son.\" How is the woman related to the man?", ['Sister', 'Mother', 'Aunt', 'Cousin'], 'A'),
        ('Find the next number in the series: 3, 6, 9, 12, ___', ['14', '15', '16', '18'], 'B'),
    ],
}

TEST_TYPE_SUFFIX = {
    'mock_test': 'Mock Test',
    'previous_year_paper': 'Previous Year Paper',
    'practice_test': 'Practice Test',
    'sectional_test': 'Sectional Test',
    'sample_papers': 'Sample Paper',
}
TEST_TYPE_CYCLE = ['mock_test', 'previous_year_paper', 'practice_test', 'sectional_test', 'sample_papers']

# name, logo_key, marks per question, duration in minutes
ROOT_CONFIG = {
    'CBSE': ('school', 1, 30),
    'ICSE': ('school', 1, 30),
    'UP Board': ('school', 1, 30),
    'NEET': ('medical', 4, 45),
    'JEE': ('engineering', 4, 45),
    'SSC': ('staff', 2, 30),
    'Banking & Insurance': ('banking', 2, 30),
}

# Exam -> Sub-exam -> [(Subject full name, question bank key), ...]
TREE = {
    'CBSE': {
        'CBSE Class 10': [
            ('CBSE Class 10 Mathematics', 'class10_maths'),
            ('CBSE Class 10 Science', 'class10_science'),
            ('CBSE Class 10 Social Science', 'class10_social_science'),
            ('CBSE Class 10 English', 'class10_english'),
        ],
        'CBSE Class 12': [
            ('CBSE Class 12 Physics', 'class12_physics_board'),
            ('CBSE Class 12 Chemistry', 'class12_chemistry_board'),
            ('CBSE Class 12 Mathematics', 'class12_maths_board'),
            ('CBSE Class 12 Biology', 'class12_biology_board'),
        ],
    },
    'ICSE': {
        'ICSE Class 10': [
            ('ICSE Class 10 Mathematics', 'class10_maths'),
            ('ICSE Class 10 Science', 'class10_science'),
            ('ICSE Class 10 English', 'class10_english'),
        ],
        'ISC Class 12': [
            ('ISC Class 12 Physics', 'class12_physics_board'),
            ('ISC Class 12 Chemistry', 'class12_chemistry_board'),
            ('ISC Class 12 Mathematics', 'class12_maths_board'),
        ],
    },
    'UP Board': {
        'UP Board Class 10': [
            ('UP Board Class 10 Mathematics', 'class10_maths'),
            ('UP Board Class 10 Science', 'class10_science'),
        ],
        'UP Board Class 12': [
            ('UP Board Class 12 Physics', 'class12_physics_board'),
            ('UP Board Class 12 Chemistry', 'class12_chemistry_board'),
            ('UP Board Class 12 Mathematics', 'class12_maths_board'),
        ],
    },
    'NEET': {
        'NEET UG': [
            ('NEET UG Physics', 'neet_physics'),
            ('NEET UG Chemistry', 'neet_chemistry'),
            ('NEET UG Biology', 'neet_biology'),
        ],
    },
    'JEE': {
        'JEE Main': [
            ('JEE Main Physics', 'jee_physics'),
            ('JEE Main Chemistry', 'jee_chemistry'),
            ('JEE Main Mathematics', 'jee_maths'),
        ],
        'JEE Advanced': [
            ('JEE Advanced Physics', 'jee_physics'),
            ('JEE Advanced Chemistry', 'jee_chemistry'),
            ('JEE Advanced Mathematics', 'jee_maths'),
        ],
    },
    'SSC': {
        'SSC CGL': [
            ('SSC CGL General Awareness', 'ssc_gk'),
            ('SSC CGL Quantitative Aptitude', 'ssc_quant'),
            ('SSC CGL English', 'ssc_english'),
            ('SSC CGL Reasoning', 'ssc_reasoning'),
        ],
        'SSC CHSL': [
            ('SSC CHSL General Awareness', 'ssc_gk'),
            ('SSC CHSL Quantitative Aptitude', 'ssc_quant'),
            ('SSC CHSL English', 'ssc_english'),
        ],
    },
    'Banking & Insurance': {
        'IBPS PO': [
            ('IBPS PO Quantitative Aptitude', 'ssc_quant'),
            ('IBPS PO Reasoning', 'ssc_reasoning'),
            ('IBPS PO English', 'ssc_english'),
        ],
        'SBI PO': [
            ('SBI PO Quantitative Aptitude', 'ssc_quant'),
            ('SBI PO Reasoning', 'ssc_reasoning'),
            ('SBI PO English', 'ssc_english'),
        ],
    },
}


class Command(BaseCommand):
    help = 'Seeds the Test Series exam hierarchy (CBSE, ICSE, UP Board, NEET, JEE, SSC, Banking) with categories, courses and real practice questions. Safe to re-run.'

    @transaction.atomic
    def handle(self, *args, **options):
        leaf_index = 0
        courses_created = 0
        questions_created = 0

        for root_name, sub_exams in TREE.items():
            logo_key, marks, duration = ROOT_CONFIG[root_name]
            root, _ = Category.objects.get_or_create(
                name=root_name, defaults={'logo_key': logo_key, 'order': len(Category.objects.filter(parent__isnull=True))},
            )
            if root.logo_key != logo_key or root.parent_id:
                root.logo_key = logo_key
                root.parent = None
                root.save()

            for sub_order, (sub_name, subjects) in enumerate(sub_exams.items()):
                sub_exam, _ = Category.objects.get_or_create(
                    name=sub_name, defaults={'logo_key': logo_key, 'order': sub_order, 'parent': root},
                )
                if sub_exam.parent_id != root.pk or sub_exam.logo_key != logo_key:
                    sub_exam.parent = root
                    sub_exam.logo_key = logo_key
                    sub_exam.save()

                for subj_order, (subject_name, bank_key) in enumerate(subjects):
                    subject, _ = Category.objects.get_or_create(
                        name=subject_name, defaults={'logo_key': logo_key, 'order': subj_order, 'parent': sub_exam},
                    )
                    if subject.parent_id != sub_exam.pk or subject.logo_key != logo_key:
                        subject.parent = sub_exam
                        subject.logo_key = logo_key
                        subject.save()

                    test_type = TEST_TYPE_CYCLE[leaf_index % len(TEST_TYPE_CYCLE)]
                    course_name = f'{subject_name} {TEST_TYPE_SUFFIX[test_type]}'
                    is_free = leaf_index % 2 == 0
                    course, created = Course.objects.get_or_create(
                        name=course_name,
                        course_type=Course.TEST_SERIES,
                        defaults={
                            'category': subject,
                            'test_type': test_type,
                            'duration_minutes': duration,
                            'original_price': 0 if is_free else 199,
                            'current_price': 0 if is_free else 99,
                            'force_free': is_free,
                            'order': leaf_index,
                            'is_active': True,
                            'about': f'A {TEST_TYPE_SUFFIX[test_type].lower()} covering {subject_name} for serious, focused practice.',
                        },
                    )
                    if created:
                        courses_created += 1
                    elif course.category_id != subject.pk:
                        course.category = subject
                        course.save()

                    if not course.questions.exists():
                        for q_order, (text, options, correct_letter) in enumerate(QUESTION_BANKS[bank_key]):
                            Question.objects.create(
                                course=course,
                                text=text,
                                option_a=options[0],
                                option_b=options[1],
                                option_c=options[2],
                                option_d=options[3],
                                correct_answer=correct_letter,
                                marks=marks,
                                order=q_order,
                            )
                            questions_created += 1

                    leaf_index += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeded exam hierarchy: {leaf_index} subjects, {courses_created} new test series, {questions_created} new questions.'
        ))
