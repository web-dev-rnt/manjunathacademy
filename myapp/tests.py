import shutil
import tempfile
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .forms import CategoryForm, CourseContentFolderForm, CourseForm, QuestionForm
from .models import Bundle, Category, Course, CourseContentFolder, CourseDocument, CourseEnrollment, CourseVideo, CustomUser, DailyQuizAttempt, DailyUpdatePost, ExamTickerItem, ExamTickerSettings, Product, Question, StoreOrder, TestAnswer, TestAttempt, TestSection


class ExamTickerCustomizationTests(TestCase):
    def setUp(self):
        self.staff = CustomUser.objects.create_user(
            email='ticker-admin@example.com', name='Ticker Admin', number='7777777777',
            password='pass', is_staff=True,
        )
        self.client.force_login(self.staff)
        ExamTickerItem.objects.all().delete()

    def test_customization_page_is_available_under_admin_customization(self):
        response = self.client.get(reverse('panel_exam_ticker'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Customize the moving exam categories')
        self.assertContains(response, 'Exam ticker')
        self.assertContains(response, 'Add exam item')
        self.assertContains(response, 'Vector logo')
        self.assertContains(response, 'ticker-admin-logo')
        self.assertContains(response, 'Engineering')
        self.assertContains(response, 'class="panel-nav-ico panel-svg-icon-', count=27)
        self.assertContains(response, 'panel-svg-icon-dashboard')
        self.assertContains(response, 'panel-svg-icon-customization')
        self.assertContains(response, '.panel-svg-icon-dashboard{--nav-icon:#60A5FA')
        self.assertContains(response, '.panel-svg-icon-library{--nav-icon:#34D399')
        self.assertContains(response, '.panel-svg-icon-bundles{--nav-icon:#F472B6')
        self.assertNotContains(response, '📊')
        self.assertNotContains(response, '🎨')

    def test_admin_can_customize_ticker_and_homepage_uses_saved_items(self):
        response = self.client.post(reverse('panel_exam_ticker'), {
            'heading': 'Explore Every Competitive Exam',
            'animation_duration': '24',
            'is_active': 'on',
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            'items-0-label': 'UPSC Civil Services',
            'items-0-logo_key': 'civil',
            'items-0-link': '#test-series',
            'items-0-order': '2',
            'items-0-is_active': 'on',
        })

        self.assertRedirects(response, reverse('panel_exam_ticker'))
        settings = ExamTickerSettings.load()
        self.assertEqual(settings.heading, 'Explore Every Competitive Exam')
        self.assertEqual(settings.animation_duration, 24)
        self.assertTrue(ExamTickerItem.objects.filter(label='UPSC Civil Services', logo_key='civil', is_active=True).exists())

        homepage = self.client.get(reverse('index'))
        self.assertContains(homepage, 'Explore Every Competitive Exam')
        self.assertContains(homepage, 'UPSC Civil Services')
        self.assertContains(homepage, 'animation-duration:24s')
        self.assertContains(homepage, 'category-logo category-logo-civil')
        self.assertNotContains(homepage, '📜')
        self.assertContains(homepage, 'nav-menu-icon-admin')
        self.assertContains(homepage, 'nav-menu-icon-certificates')
        self.assertNotContains(homepage, '🛠️')

    def test_hidden_items_and_disabled_ticker_do_not_render(self):
        ExamTickerItem.objects.create(label='Hidden Exam', is_active=False)
        settings = ExamTickerSettings.load()
        settings.is_active = False
        settings.save()

        response = self.client.get(reverse('index'))

        self.assertNotContains(response, 'Hidden Exam')
        self.assertNotContains(response, '<section class="exam-ticker"', html=False)


class CurrentAffairsEnhancementTests(TestCase):
    def setUp(self):
        self.staff = CustomUser.objects.create_user(
            email='affairs-admin@example.com', name='Affairs Admin', number='7000000099',
            password='pass', is_staff=True,
        )
        self.today = timezone.localdate()
        self.latest = DailyUpdatePost.objects.create(
            category=DailyUpdatePost.CURRENT_AFFAIRS,
            news_category=DailyUpdatePost.NEWS_NATIONAL,
            event_date=self.today,
            title='Latest verified current affairs update',
            body='A complete current affairs summary for students.',
            thumbnail='daily_updates/posts/thumbnails/latest.jpg',
            image='daily_updates/posts/latest-main.jpg',
            video_url='https://cdn.example.com/latest.mp4?token=abc',
            youtube_url='https://www.youtube.com/watch?v=abc123XYZ89',
        )
        self.older = DailyUpdatePost.objects.create(
            category=DailyUpdatePost.CURRENT_AFFAIRS,
            news_category=DailyUpdatePost.NEWS_INTERNATIONAL,
            event_date=self.today - timezone.timedelta(days=1),
            title='Older international update',
            body='An older article that should be excluded by the selected date.',
        )
        self.legacy_news = DailyUpdatePost.objects.create(
            category=DailyUpdatePost.DAILY_NEWS,
            event_date=self.today,
            title='Legacy daily news row',
            body='Preserved in storage but hidden from the Current Affairs workflow.',
        )
        self.same_day = DailyUpdatePost.objects.create(
            category=DailyUpdatePost.CURRENT_AFFAIRS,
            news_category=DailyUpdatePost.NEWS_INTERNATIONAL,
            event_date=self.today,
            title='Second same-day current affairs update',
            body='This item should occupy the second side of the shared date grid.',
        )
        DailyUpdatePost.objects.filter(pk=self.latest.pk).update(
            created_at=timezone.now() + timezone.timedelta(seconds=1),
        )
        self.latest.refresh_from_db()

    def test_archive_is_wider_and_filters_posts_by_date(self):
        response = self.client.get(reverse('current_affairs_page'), {'date': self.today.isoformat()})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_date'], self.today)
        self.assertContains(response, 'Latest verified current affairs update')
        self.assertContains(response, 'Second same-day current affairs update')
        self.assertNotContains(response, 'Older international update')
        self.assertNotContains(response, 'Legacy daily news row')
        self.assertContains(response, 'Filter by date')
        self.assertContains(response, '.ca-wrap{max-width:1120px}')
        self.assertContains(response, 'ca-share-btn')
        self.assertContains(response, '/media/daily_updates/posts/thumbnails/latest.jpg')
        self.assertContains(response, 'myapp/images/current-affairs/international.svg')
        self.assertContains(response, 'class="ca-post-row"', count=2)
        self.assertEqual(len(response.context['days'][0]['posts']), 2)

    def test_homepage_features_latest_thumbnail_media_and_share_button(self):
        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['latest_current_affair'], self.latest)
        self.assertContains(response, 'Latest verified current affairs update')
        self.assertContains(response, '/media/daily_updates/posts/thumbnails/latest.jpg')
        self.assertContains(response, 'daily-share')
        self.assertContains(
            response,
            f'id="homepageCurrentAffairsLink" class="btn-daily btn-daily-red" href="{reverse("current_affairs_page")}"',
            html=False,
        )
        self.assertContains(response, 'YouTube')
        self.assertContains(response, 'Video')
        self.assertNotContains(response, 'Legacy daily news row')

    def test_detail_renders_youtube_direct_video_and_share(self):
        response = self.client.get(reverse('current_affairs_detail', args=[self.latest.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'https://www.youtube.com/embed/abc123XYZ89')
        self.assertContains(response, 'https://cdn.example.com/latest.mp4?token=abc')
        self.assertContains(response, 'caDetailShare')
        self.assertTrue(self.latest.video_url_is_direct_file)

    def test_admin_is_current_affairs_only_and_can_add_media_links(self):
        self.client.force_login(self.staff)
        dashboard = self.client.get(reverse('panel_daily_updates'))

        self.assertEqual(dashboard.status_code, 200)
        self.assertContains(dashboard, 'Current Affairs card')
        self.assertContains(dashboard, 'ca-admin-table')
        self.assertContains(dashboard, 'admin-post-thumb')
        self.assertContains(dashboard, '/media/daily_updates/posts/thumbnails/latest.jpg')
        self.assertNotContains(dashboard, 'Daily News card')
        self.assertNotContains(dashboard, 'Legacy daily news row')

        add_page = self.client.get(reverse('panel_daily_post_add'))
        self.assertContains(add_page, 'Thumbnail')
        self.assertContains(add_page, 'Video link')
        self.assertContains(add_page, 'YouTube link')
        self.assertNotContains(add_page, 'name="category"', html=False)

        response = self.client.post(reverse('panel_daily_post_add'), {
            'news_category': DailyUpdatePost.NEWS_SPORTS,
            'event_date': self.today.isoformat(),
            'title': 'New sports current affair',
            'body': 'A logically categorized sports update.',
            'video_url': 'https://example.com/watch-video',
            'youtube_url': 'https://youtu.be/ZXCVBNm1234',
            'is_active': 'on',
        })
        self.assertRedirects(response, reverse('panel_daily_updates'))
        post = DailyUpdatePost.objects.get(title='New sports current affair')
        self.assertEqual(post.category, DailyUpdatePost.CURRENT_AFFAIRS)
        self.assertEqual(post.news_category, DailyUpdatePost.NEWS_SPORTS)
        self.assertEqual(post.youtube_embed_url, 'https://www.youtube.com/embed/ZXCVBNm1234')

    def test_legacy_daily_news_url_redirects_without_deleting_data(self):
        response = self.client.get(reverse('daily_news_page'))

        self.assertRedirects(response, reverse('current_affairs_page'))
        self.assertTrue(DailyUpdatePost.objects.filter(pk=self.legacy_news.pk).exists())


class AdminAnalyticsAccuracyTests(TestCase):
    def setUp(self):
        self.staff = CustomUser.objects.create_user(
            email='analytics-admin@example.com', name='Analytics Admin', number='7000000001',
            password='pass', is_staff=True,
        )
        self.other_staff = CustomUser.objects.create_user(
            email='internal-staff@example.com', name='Internal Staff', number='7000000002',
            password='pass', is_staff=True,
        )
        self.student = CustomUser.objects.create_user(
            email='real-student@example.com', name='Real Student', number='7000000003',
            password='pass', device_type=CustomUser.DEVICE_ANDROID,
        )
        self.client.force_login(self.staff)

    def test_dashboard_uses_students_and_confirmed_payment_amounts_only(self):
        course = Course.objects.create(
            course_type=Course.VIDEO_COURSE, name='Real Paid Course', current_price=125,
        )
        enrollment = CourseEnrollment.objects.create(user=self.student, course=course)
        enrollment.grant_paid_access(amount_paid=Decimal('125.00'), razorpay_payment_id='pay_real')

        internal_enrollment = CourseEnrollment.objects.create(user=self.other_staff, course=course)
        internal_enrollment.grant_paid_access(amount_paid=Decimal('999.00'), razorpay_payment_id='pay_internal')

        product = Product.objects.create(name='Real Study Book', current_price=50, stock=1)
        order = StoreOrder.objects.create(
            user=self.student, product=product, quantity=1, amount=Decimal('50.00'),
            shipping_name='Real Student', shipping_phone='7000000003', shipping_address='Lucknow',
            status=StoreOrder.STATUS_PAID, razorpay_payment_id='pay_store',
        )

        response = self.client.get(reverse('panel_dashboard'))
        chart_data = response.context['chart_data']

        self.assertEqual(response.context['total_users'], 1)
        self.assertEqual(response.context['week_signups'], 1)
        self.assertEqual(response.context['total_revenue'], Decimal('175.00'))
        self.assertEqual(sum(chart_data['signups']), 1)
        self.assertEqual(sum(chart_data['devices']['values']), 1)
        self.assertEqual(sum(chart_data['payments']), 175.0)
        self.assertIsNotNone(enrollment.paid_at)
        self.assertIsNotNone(order.paid_at)

    def test_signup_page_excludes_staff_and_all_charts_follow_filters(self):
        response = self.client.get(reverse('panel_signups'), {'device': CustomUser.DEVICE_ANDROID})

        self.assertEqual(response.context['stats']['total'], 1)
        self.assertEqual(response.context['stats']['active'], 1)
        self.assertEqual(response.context['stats']['admins'], 2)
        self.assertEqual(response.context['filtered_count'], 1)
        self.assertEqual(list(response.context['users']), [self.student])
        self.assertEqual(sum(row['count'] for row in response.context['monthly_counts']), 1)
        self.assertEqual(sum(row['count'] for row in response.context['device_breakdown']), 1)

    def test_invalid_signup_date_filter_is_reported_without_crashing(self):
        response = self.client.get(reverse('panel_signups'), {'from': 'not-a-date'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['date_filter_error'], 'The From date is not valid.')
        self.assertEqual(response.context['filtered_count'], 1)

    def test_staff_can_edit_student_and_optionally_reset_password(self):
        response = self.client.post(reverse('panel_signup_edit', args=[self.student.pk]), {
            'name': 'Updated Student',
            'email': 'updated-student@example.com',
            'number': '7000000099',
            'age': '22',
            'gender': 'female',
            'state': 'Uttar Pradesh',
            'city': 'Lucknow',
            'device_type': CustomUser.DEVICE_DESKTOP,
            'is_active': 'on',
            'new_password': 'UpdatedPass123',
        })

        self.assertRedirects(response, reverse('panel_signups'))
        self.student.refresh_from_db()
        self.assertEqual(self.student.name, 'Updated Student')
        self.assertEqual(self.student.email, 'updated-student@example.com')
        self.assertEqual(self.student.device_type, CustomUser.DEVICE_DESKTOP)
        self.assertTrue(self.student.check_password('UpdatedPass123'))

    def test_delete_requires_confirmation_then_removes_exact_student(self):
        confirmation = self.client.get(reverse('panel_signup_delete', args=[self.student.pk]))

        self.assertEqual(confirmation.status_code, 200)
        self.assertContains(confirmation, self.student.email)
        self.assertTrue(CustomUser.objects.filter(pk=self.student.pk).exists())

        response = self.client.post(reverse('panel_signup_delete', args=[self.student.pk]))

        self.assertRedirects(response, reverse('panel_signups'))
        self.assertFalse(CustomUser.objects.filter(pk=self.student.pk).exists())
        self.assertTrue(CustomUser.objects.filter(pk=self.staff.pk).exists())

    def test_signup_actions_cannot_modify_internal_staff_accounts(self):
        edit_response = self.client.get(reverse('panel_signup_edit', args=[self.other_staff.pk]))
        delete_response = self.client.post(reverse('panel_signup_delete', args=[self.other_staff.pk]))

        self.assertEqual(edit_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 404)
        self.assertTrue(CustomUser.objects.filter(pk=self.other_staff.pk).exists())


class BundleImageTests(TestCase):
    def setUp(self):
        self.media_dir = tempfile.mkdtemp()
        self.media_override = override_settings(MEDIA_ROOT=self.media_dir)
        self.media_override.enable()
        self.staff = CustomUser.objects.create_user(
            email='bundle-admin@example.com', name='Bundle Admin', number='7111111111',
            password='pass', is_staff=True,
        )
        self.client.force_login(self.staff)

    def tearDown(self):
        self.media_override.disable()
        shutil.rmtree(self.media_dir, ignore_errors=True)

    def test_admin_uploads_bundle_image_and_cards_use_it_instead_of_emoji(self):
        gif = (
            b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff'
            b'!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00'
            b'\x00\x02\x02D\x01\x00;'
        )
        response = self.client.post(reverse('panel_bundle_add'), {
            'name': 'Image Bundle',
            'description': 'Bundle with a visual cover',
            'image': SimpleUploadedFile('bundle-cover.gif', gif, content_type='image/gif'),
            'icon': '🎓',
            'badge_label': 'Complete pack',
            'students_label': '100+',
            'access_label': 'Full Course',
            'original_price': '999',
            'current_price': '499',
            'rating': '4.9',
            'order': '0',
            'is_active': 'on',
        })

        self.assertRedirects(response, reverse('panel_bundle_list'))
        bundle = Bundle.objects.get(name='Image Bundle')
        self.assertTrue(bundle.image.name.startswith('bundles/'))

        homepage = self.client.get(reverse('index'))
        self.assertContains(homepage, bundle.image.url)
        self.assertContains(homepage, 'class="bundle-card-image"')
        edit_page = self.client.get(reverse('panel_bundle_edit', args=[bundle.pk]))
        self.assertContains(edit_page, 'Current bundle image')

    def test_emoji_remains_fallback_when_bundle_has_no_image(self):
        Bundle.objects.create(name='Emoji Bundle', icon='🧭', current_price=0, is_active=True)

        response = self.client.get(reverse('bundles_page'))

        self.assertContains(response, '🧭')
        self.assertNotContains(response, 'class="bundle-card-image"')


class CourseContentFolderTests(TestCase):
    def setUp(self):
        self.media_dir = tempfile.mkdtemp()
        self.media_override = override_settings(MEDIA_ROOT=self.media_dir)
        self.media_override.enable()
        self.staff = CustomUser.objects.create_user(
            email='admin@example.com', name='Admin', number='9999999999', password='pass', is_staff=True,
        )
        self.client.force_login(self.staff)
        self.video_course = Course.objects.create(
            course_type=Course.VIDEO_COURSE, name='Folder Video Course', enable_folders=True, current_price=0,
        )
        self.library_course = Course.objects.create(
            course_type=Course.ELIBRARY, name='Folder Library', enable_folders=True, current_price=0,
        )

    def tearDown(self):
        self.media_override.disable()
        shutil.rmtree(self.media_dir, ignore_errors=True)

    def test_enable_folders_field_only_appears_for_supported_content(self):
        self.assertIn('enable_folders', CourseForm(course_type=Course.VIDEO_COURSE).fields)
        self.assertIn('enable_folders', CourseForm(course_type=Course.ELIBRARY).fields)
        self.assertNotIn('enable_folders', CourseForm(course_type=Course.TEST_SERIES).fields)

    def test_highlights_are_available_only_for_video_courses(self):
        self.assertIn('highlights', CourseForm(course_type=Course.VIDEO_COURSE).fields)
        self.assertNotIn('highlights', CourseForm(course_type=Course.ELIBRARY).fields)
        self.assertNotIn('highlights', CourseForm(course_type=Course.TEST_SERIES).fields)

    def test_video_course_highlights_render_in_admin_and_public_cards(self):
        self.video_course.highlights = '- Expert faculty\nChapter-wise lessons\nWatch on any device'
        self.video_course.save(update_fields=['highlights'])

        self.assertEqual(
            self.video_course.highlight_list,
            ['Expert faculty', 'Chapter-wise lessons', 'Watch on any device'],
        )
        admin_response = self.client.get(reverse('panel_course_edit', args=[Course.VIDEO_COURSE, self.video_course.pk]))
        self.assertContains(admin_response, 'Course highlights')
        homepage_response = self.client.get(reverse('index'))
        self.assertContains(homepage_response, 'Expert faculty')
        listing_response = self.client.get(reverse('video_courses_page'))
        self.assertContains(listing_response, 'Chapter-wise lessons')

    def test_paid_video_course_checkout_shows_locked_searchable_syllabus(self):
        paid_course = Course.objects.create(
            course_type=Course.VIDEO_COURSE,
            name='Paid Mathematics',
            current_price=499,
            original_price=999,
            enable_folders=True,
            highlights='Experienced educators',
        )
        folder = CourseContentFolder.objects.create(course=paid_course, name='Basic Mathematics')
        video = CourseVideo.objects.create(
            course=paid_course,
            folder=folder,
            title='Basic Mathematics Part 1',
            video_file=SimpleUploadedFile('paid-lesson.mp4', b'video-data', content_type='video/mp4'),
            duration_minutes=40,
        )

        response = self.client.get(reverse('course_detail', args=[paid_course.pk]))

        self.assertTemplateUsed(response, 'myapp/course_checkout.html')
        self.assertNotContains(response, 'Search by folder or video name')
        self.assertContains(response, 'Basic Mathematics Part 1')
        self.assertContains(response, 'Experienced educators')
        self.assertContains(response, 'Buy Now')
        self.assertNotContains(response, video.video_file.url)

    def test_folder_path_supports_unlimited_nested_levels(self):
        root = CourseContentFolder.objects.create(course=self.video_course, name='Module 1')
        child = CourseContentFolder.objects.create(course=self.video_course, parent=root, name='Chapter 1')
        grandchild = CourseContentFolder.objects.create(course=self.video_course, parent=child, name='Lessons')
        self.assertEqual(grandchild.full_path, 'Module 1 / Chapter 1 / Lessons')

    def test_folder_rejects_parent_from_another_course(self):
        library_folder = CourseContentFolder.objects.create(course=self.library_course, name='Notes')
        invalid = CourseContentFolder(course=self.video_course, parent=library_folder, name='Wrong')
        with self.assertRaises(ValidationError):
            invalid.full_clean()

    def test_folder_form_prevents_duplicate_name_in_current_folder(self):
        CourseContentFolder.objects.create(course=self.video_course, name='Module 1')
        form = CourseContentFolderForm(
            data={'name': 'module 1', 'order': 0, 'is_active': True},
            course=self.video_course,
            parent=None,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_admin_can_create_folder_then_subfolder_from_current_location(self):
        root_url = reverse('panel_course_content', args=[Course.VIDEO_COURSE, self.video_course.pk])
        response = self.client.post(root_url, {
            'action': 'create_folder', 'folder-name': 'Module 1', 'folder-order': 0, 'folder-is_active': 'on',
        })
        self.assertRedirects(response, root_url)
        root = CourseContentFolder.objects.get(course=self.video_course, name='Module 1')

        child_url = reverse('panel_course_content_folder', args=[Course.VIDEO_COURSE, self.video_course.pk, root.pk])
        response = self.client.post(child_url, {
            'action': 'create_folder', 'folder-name': 'Chapter 1', 'folder-order': 0, 'folder-is_active': 'on',
        })
        self.assertRedirects(response, child_url)
        self.assertTrue(CourseContentFolder.objects.filter(course=self.video_course, parent=root, name='Chapter 1').exists())

    def test_admin_uploads_video_into_open_folder(self):
        folder = CourseContentFolder.objects.create(course=self.video_course, name='Module 1')
        url = reverse('panel_course_content_folder', args=[Course.VIDEO_COURSE, self.video_course.pk, folder.pk])
        long_filename = f'YTDown_YouTube_{"very-long-video-title-" * 6}720p.mp4'
        response = self.client.post(url, {
            'action': 'upload',
            'upload-title': 'Introduction',
            'upload-video_file': SimpleUploadedFile(long_filename, b'video-data', content_type='video/mp4'),
            'upload-duration_minutes': 10,
            'upload-order': 0,
            'upload-is_active': 'on',
        })
        self.assertRedirects(response, url)
        video = CourseVideo.objects.get(course=self.video_course, title='Introduction')
        self.assertEqual(video.folder, folder)
        self.assertLessEqual(len(video.video_file.name), 500)

    def test_admin_uploads_pdf_into_open_library_folder(self):
        folder = CourseContentFolder.objects.create(course=self.library_course, name='Polity')
        url = reverse('panel_course_content_folder', args=[Course.ELIBRARY, self.library_course.pk, folder.pk])
        response = self.client.post(url, {
            'action': 'upload',
            'upload-title': 'Constitution Notes',
            'upload-pdf_file': SimpleUploadedFile('notes.pdf', b'%PDF-test', content_type='application/pdf'),
            'upload-pages': 20,
            'upload-order': 0,
            'upload-is_active': 'on',
        })
        self.assertRedirects(response, url)
        document = CourseDocument.objects.get(course=self.library_course, title='Constitution Notes')
        self.assertEqual(document.folder, folder)

    def test_public_course_detail_renders_internal_folder_tree(self):
        folder = CourseContentFolder.objects.create(course=self.video_course, name='Module 1')
        CourseVideo.objects.create(
            course=self.video_course,
            folder=folder,
            title='Nested Lesson',
            video_file=SimpleUploadedFile('nested.mp4', b'video-data', content_type='video/mp4'),
        )
        response = self.client.get(reverse('course_detail', args=[self.video_course.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Module 1')
        self.assertContains(response, 'Nested Lesson')
        self.assertContains(response, 'vcInlinePlayer')
        self.assertNotContains(response, 'Search by folder or video name')
        self.assertNotContains(response, 'vcPlayerOverlay')
        self.assertTemplateUsed(response, 'myapp/video_course_detail.html')
        self.assertEqual(response.context['content_tree'][0]['item_count'], 1)

    def test_disabling_folders_flattens_content_and_removes_folder_tree(self):
        folder = CourseContentFolder.objects.create(course=self.video_course, name='Module 1')
        video = CourseVideo.objects.create(
            course=self.video_course,
            folder=folder,
            title='Lesson',
            video_file=SimpleUploadedFile('lesson.mp4', b'video-data', content_type='video/mp4'),
        )
        url = reverse('panel_course_edit', args=[Course.VIDEO_COURSE, self.video_course.pk])
        response = self.client.post(url, {
            'name': self.video_course.name,
            'original_price': 0,
            'current_price': 0,
            'validity_unit': Course.VALIDITY_MONTHS,
            'order': 0,
            'is_active': 'on',
        })
        self.assertRedirects(response, reverse('panel_course_list', args=[Course.VIDEO_COURSE]))
        video.refresh_from_db()
        self.video_course.refresh_from_db()
        self.assertFalse(self.video_course.enable_folders)
        self.assertIsNone(video.folder)
        self.assertFalse(self.video_course.content_folders.exists())


class TestSeriesHomepageCatalogTests(TestCase):
    SEEDED_TESTS = {
        'UPSC Prelims General Studies Mock Test': ('UPSC & Civil Services', 'civil'),
        'NDA & CDS General Ability Test': ('Defence Exams', 'defence'),
        'CTET Paper I Practice Test': ('Teaching Exams', 'teaching'),
        'UPPSC PCS Prelims Mock Test': ('State PSC', 'state'),
        'Police Constable Recruitment Practice Test': ('Police & Constable', 'police'),
        'JEE Main Physics Chapter Test': ('Engineering Entrance', 'engineering'),
    }

    def test_seeded_catalog_has_categories_sections_and_usable_questions(self):
        for course_name, (category_name, logo_key) in self.SEEDED_TESTS.items():
            course = Course.objects.get(course_type=Course.TEST_SERIES, name=course_name)
            self.assertEqual(course.category.name, category_name)
            self.assertEqual(course.category.logo_key, logo_key)
            self.assertEqual(course.test_sections.count(), 2)
            self.assertEqual(course.questions.count(), 8)
            for question in course.questions.all():
                self.assertIn(question.correct_answer, {'A', 'B', 'C', 'D'})
                self.assertTrue(question.section_id)
                self.assertTrue(question.option_a)
                self.assertTrue(question.option_b)
                self.assertTrue(question.option_c)
                self.assertTrue(question.option_d)

        self.assertEqual(
            Question.objects.get(text='What is three-fourths of 200?').correct_answer,
            'C',
        )
        self.assertEqual(
            Question.objects.get(text='What does FIR stand for?').option_b,
            'First Information Report',
        )

    def test_homepage_uses_four_column_grid_and_vector_category_logos(self):
        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'grid-template-columns:repeat(4,minmax(0,1fr))')
        self.assertContains(response, 'category-logo category-logo-engineering')
        self.assertContains(response, 'Engineering Entrance')
        self.assertContains(response, 'JEE Main Physics Chapter Test')
        self.assertNotContains(response, '<span class="ts-tab-ico">📚', html=False)

    def test_category_admin_form_exposes_logo_style_choices(self):
        form = CategoryForm()

        self.assertIn('logo_key', form.fields)
        self.assertIn(('engineering', 'Engineering'), list(form.fields['logo_key'].choices))
        self.assertIn(('medical', 'Medical'), list(form.fields['logo_key'].choices))


class TestSeriesAutoQuizTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='quiz@example.com', name='Quiz Student', number='8888888888', password='pass',
        )
        self.client.force_login(self.user)
        self.course = Course.objects.create(
            course_type=Course.TEST_SERIES,
            name='Automatic Practice Test',
            test_type='mock_test',
            current_price=0,
        )
        for number in range(1, 8):
            Question.objects.create(
                course=self.course,
                question_type=Question.SINGLE,
                text=f'Automatic question {number}',
                option_a='Correct answer',
                option_b='Wrong answer',
                correct_answer='A',
                marks=1,
                order=number,
            )

    def test_quizzes_section_automatically_selects_five_random_questions(self):
        response = self.client.get(reverse('test_series_detail', args=[self.course.pk]))

        selected_questions = response.context['daily_quiz_questions']
        self.assertEqual(len(selected_questions), 5)
        self.assertEqual(len({question.pk for question in selected_questions}), 5)
        self.assertTrue(all(question.course_id == self.course.pk for question in selected_questions))
        self.assertEqual(response.context['daily_quiz_total_marks'], 5)
        self.assertContains(response, '5-Question Practice Quiz')
        self.assertContains(response, 'Start Quiz')
        self.assertNotContains(response, 'No daily quizzes added yet')

    def test_automatic_five_question_quiz_is_scored_and_recorded(self):
        page = self.client.get(reverse('test_series_detail', args=[self.course.pk]))
        selected_questions = page.context['daily_quiz_questions']
        payload = {
            'action': 'daily_quiz',
            'quiz_token': page.context['daily_quiz_token'],
            'quiz_question_ids': [str(question.pk) for question in selected_questions],
        }
        payload.update({f'q_{question.pk}': 'A' for question in selected_questions})

        response = self.client.post(reverse('test_series_detail', args=[self.course.pk]), payload)

        self.assertEqual(response.context['quiz_result'], {'score': 5, 'total': 5})
        attempt = DailyQuizAttempt.objects.get(user=self.user, course=self.course)
        self.assertEqual(attempt.score, 5)
        self.assertEqual(attempt.total, 5)
        self.assertEqual(len(attempt.answer_details), 5)
        self.assertTrue(all(row['is_correct'] for row in attempt.answer_details))
        self.assertContains(response, 'You scored 5 / 5')

    def test_daily_quiz_rejects_tampered_question_ids(self):
        page = self.client.get(reverse('test_series_detail', args=[self.course.pk]))
        selected_questions = page.context['daily_quiz_questions']

        response = self.client.post(reverse('test_series_detail', args=[self.course.pk]), {
            'action': 'daily_quiz',
            'quiz_token': page.context['daily_quiz_token'],
            'quiz_question_ids': [str(question.pk) for question in selected_questions[:4]],
        })

        self.assertFalse(DailyQuizAttempt.objects.filter(user=self.user, course=self.course).exists())
        self.assertContains(response, 'invalid or expired')

    def test_question_form_rejects_invalid_answer_keys(self):
        form = QuestionForm(data={
            'question_type': Question.SINGLE,
            'text': 'Invalid answer key question',
            'option_a': 'Only option',
            'correct_answer': 'D',
            'marks': 1,
            'order': 0,
        }, course=self.course)

        self.assertFalse(form.is_valid())
        self.assertIn('Option D is empty', form.errors['correct_answer'][0])

    def test_start_test_first_shows_instructions_without_starting_timer(self):
        self.course.duration_minutes = 60
        self.course.save(update_fields=['duration_minutes'])

        response = self.client.get(reverse('test_attempt_start', args=[self.course.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myapp/test_attempt_instructions.html')
        self.assertContains(response, 'General Instructions')
        self.assertContains(response, 'Total duration of the examination is')
        self.assertContains(response, 'I am ready to begin')
        self.assertFalse(TestAttempt.objects.filter(user=self.user, course=self.course).exists())

    def test_confirming_instructions_creates_attempt_and_starts_test(self):
        response = self.client.post(reverse('test_attempt_start', args=[self.course.pk]))

        attempt = TestAttempt.objects.get(user=self.user, course=self.course, submitted_at__isnull=True)
        self.assertRedirects(response, reverse('test_attempt_take', args=[attempt.pk]))

    def test_saved_results_use_snapshots_real_metrics_and_one_leaderboard_row_per_user(self):
        questions = list(self.course.questions.all())
        other_user = CustomUser.objects.create_user(
            email='other@example.com', name='Other Student', number='7777777777', password='pass',
        )
        for correct_answers in (2, 7):
            other_attempt = TestAttempt.objects.create(
                user=other_user,
                course=self.course,
                submitted_at=timezone.now(),
                score=correct_answers,
                total_marks=7,
            )
            for index, question in enumerate(questions):
                is_correct = index < correct_answers
                TestAnswer.objects.create(
                    attempt=other_attempt,
                    question=question,
                    submitted_answer='A' if is_correct else 'B',
                    is_correct=is_correct,
                    marks_awarded=1 if is_correct else 0,
                    question_text_snapshot=question.text,
                    correct_answer_snapshot=question.correct_answer,
                    section_name_snapshot='General',
                    question_marks_snapshot=question.marks,
                )

        self.client.post(reverse('test_attempt_start', args=[self.course.pk]))
        attempt = TestAttempt.objects.get(user=self.user, course=self.course, submitted_at__isnull=True)
        submitted_answers = {f'q_{question.pk}': 'A' for question in questions}
        submitted_answers[f'q_{questions[-1].pk}'] = 'B'
        self.client.post(reverse('test_attempt_take', args=[attempt.pk]), submitted_answers)
        attempt.refresh_from_db()

        self.assertEqual(attempt.score, 6)
        self.assertEqual(attempt.total_marks, 7)
        self.assertEqual(attempt.answers.count(), 7)
        saved_answer = attempt.answers.get(question=questions[0])
        original_question_text = saved_answer.question_text_snapshot
        self.assertEqual(saved_answer.correct_answer_snapshot, 'A')

        result = self.client.get(reverse('test_attempt_result', args=[attempt.pk]))
        self.assertEqual(result.context['participant_count'], 2)
        self.assertEqual(len(result.context['leaderboard']), 2)
        self.assertEqual(result.context['topper'].user_id, other_user.pk)
        self.assertEqual(result.context['topper_metrics']['correct_count'], 7)
        self.assertEqual(result.context['rank'], 2)
        self.assertContains(result, '100%')

        questions[0].delete()
        saved_answer.refresh_from_db()
        self.assertIsNone(saved_answer.question)
        result = self.client.get(reverse('test_attempt_result', args=[attempt.pk]))
        self.assertContains(result, original_question_text)
        self.assertEqual(result.context['total_questions'], 7)

        profile_results = self.client.get(reverse('account_results'))
        self.assertContains(profile_results, self.course.name)
        self.assertContains(profile_results, '85.71% accuracy')

    def test_admin_question_list_filters_by_section_and_unassigned(self):
        self.user.is_staff = True
        self.user.save(update_fields=['is_staff'])
        first_section = TestSection.objects.create(course=self.course, name='Reasoning', order=0)
        second_section = TestSection.objects.create(course=self.course, name='Mathematics', order=1)
        questions = list(self.course.questions.all())
        Question.objects.filter(pk__in=[question.pk for question in questions[:3]]).update(section=first_section)
        Question.objects.filter(pk__in=[question.pk for question in questions[3:5]]).update(section=second_section)

        url = reverse('panel_question_list', args=[self.course.pk])
        response = self.client.get(url, {'section': str(first_section.pk)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['questions'].values_list('pk', flat=True)), [question.pk for question in questions[:3]])
        self.assertEqual(response.context['filtered_question_count'], 3)
        self.assertEqual(response.context['total_question_count'], 7)
        self.assertContains(response, 'Filter by section')
        self.assertContains(response, 'question-table')
        self.assertContains(response, 'section-cell')

        response = self.client.get(url, {'section': 'unassigned'})
        self.assertEqual(list(response.context['questions'].values_list('pk', flat=True)), [question.pk for question in questions[5:]])

    def test_admin_can_create_sections_and_assign_questions(self):
        self.user.is_staff = True
        self.user.save(update_fields=['is_staff'])
        edit_url = reverse('panel_course_edit', args=[Course.TEST_SERIES, self.course.pk])
        response = self.client.post(edit_url, {
            'name': self.course.name,
            'test_type': self.course.test_type,
            'original_price': 0,
            'current_price': 0,
            'validity_unit': Course.VALIDITY_MONTHS,
            'duration_minutes': 60,
            'max_optional_sections': 1,
            'order': 0,
            'is_active': 'on',
            'sections-TOTAL_FORMS': 1,
            'sections-INITIAL_FORMS': 0,
            'sections-MIN_NUM_FORMS': 0,
            'sections-MAX_NUM_FORMS': 1000,
            'sections-0-name': 'Section A — Mathematics',
            'sections-0-negative_marks': '0.25',
            'sections-0-order': 0,
        })
        self.assertRedirects(response, reverse('panel_course_list', args=[Course.TEST_SERIES]))
        section = TestSection.objects.get(course=self.course, name='Section A — Mathematics')

        question_url = reverse('panel_question_add', args=[self.course.pk])
        response = self.client.post(question_url, {
            'section': section.pk,
            'question_type': Question.SINGLE,
            'text': 'Section assigned question',
            'option_a': 'Correct',
            'option_b': 'Wrong',
            'correct_answer': 'A',
            'marks': 2,
            'order': 20,
        })
        self.assertRedirects(response, reverse('panel_question_list', args=[self.course.pk]))
        self.assertTrue(Question.objects.filter(course=self.course, section=section, text='Section assigned question').exists())

    def test_optional_section_limit_is_shown_and_enforced(self):
        required = TestSection.objects.create(course=self.course, name='Compulsory', order=0)
        first_optional = TestSection.objects.create(course=self.course, name='Optional One', is_optional=True, order=1)
        second_optional = TestSection.objects.create(course=self.course, name='Optional Two', is_optional=True, order=2)
        self.course.max_optional_sections = 1
        self.course.save(update_fields=['max_optional_sections'])

        instruction_page = self.client.get(reverse('test_attempt_start', args=[self.course.pk]))
        self.assertContains(instruction_page, 'Choose maximum 1 optional section')
        self.assertContains(instruction_page, 'Next')
        self.assertContains(instruction_page, 'Go back')

        self.client.post(reverse('test_attempt_start', args=[self.course.pk]), {
            'selected_sections': [str(first_optional.pk), str(second_optional.pk)],
        })
        attempt = TestAttempt.objects.get(user=self.user, course=self.course)
        self.assertEqual(attempt.selected_section_ids, [required.pk, first_optional.pk])

    def test_section_selection_exam_palette_negative_marking_and_dashboard(self):
        required = TestSection.objects.create(course=self.course, name='Section A', negative_marks='0.25', order=0)
        optional = TestSection.objects.create(course=self.course, name='Section B', is_optional=True, order=1)
        questions = list(self.course.questions.all())
        Question.objects.filter(pk__in=[question.pk for question in questions[:4]]).update(section=required)
        Question.objects.filter(pk__in=[question.pk for question in questions[4:]]).update(section=optional)

        instruction_page = self.client.get(reverse('test_attempt_start', args=[self.course.pk]))
        self.assertContains(instruction_page, 'Section A')
        self.assertContains(instruction_page, 'Section B')
        self.assertContains(instruction_page, 'Compulsory')
        self.assertContains(instruction_page, 'Optional')

        start_response = self.client.post(reverse('test_attempt_start', args=[self.course.pk]), {
            'selected_sections': [str(optional.pk)],
        })
        attempt = TestAttempt.objects.get(user=self.user, course=self.course)
        self.assertEqual(set(attempt.selected_section_ids), {required.pk, optional.pk})
        self.assertRedirects(start_response, reverse('test_attempt_take', args=[attempt.pk]))

        take_page = self.client.get(reverse('test_attempt_take', args=[attempt.pk]))
        self.assertContains(take_page, 'Question Palette')
        self.assertContains(take_page, 'Mark for Review')
        self.assertContains(take_page, 'SUBMIT TEST')
        self.assertContains(take_page, 'Section A')
        self.assertContains(take_page, 'Section B')

        first_question = questions[0]
        result_response = self.client.post(
            reverse('test_attempt_take', args=[attempt.pk]),
            {f'q_{first_question.pk}': 'B'},
            follow=True,
        )
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, -0.25)
        self.assertContains(result_response, 'Your performance report')
        self.assertContains(result_response, 'Leaderboard')
        self.assertContains(result_response, 'Section Performance')
        self.assertContains(result_response, 'View Solutions')
