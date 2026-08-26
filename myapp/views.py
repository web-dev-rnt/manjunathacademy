import csv
import io
import json
import random
import secrets
import uuid

from django.core import signing
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.db.models import Count, F, Q, Sum
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import (
    AccountUpdateForm,
    AdmissionRegistrationForm,
    BannerSlideForm,
    BrandForm,
    BundleForm,
    CareerApplicationForm,
    CategoryForm,
    CertificateForm,
    ChatbotQuestionForm,
    ChatbotSettingsForm,
    ClassroomAddStudentsForm,
    ClassroomForm,
    ContactMessageForm,
    CouponForm,
    CourseContentFolderForm,
    CourseDocumentForm,
    CourseForm,
    CourseDocumentFormSet,
    CourseVideoForm,
    CourseVideoFormSet,
    TestSectionFormSet,
    DailyUpdateCardForm,
    DailyUpdatePostForm,
    DailyUpdatePostTableRowForm,
    EligibilityCheckForm,
    EligibilityCriteriaForm,
    EmailAuthenticationForm,
    ExamCalendarEventForm,
    ExamTickerItemFormSet,
    ExamTickerSettingsForm,
    ExtraPageForm,
    FAQItemForm,
    FeeInvoiceForm,
    FooterSettingsForm,
    GalleryImageForm,
    HeroSectionForm,
    HomepageContentForm,
    JobPostingForm,
    NavbarCustomizationForm,
    NotificationForm,
    NotificationImageForm,
    NotificationProviderSettingsForm,
    NotificationTableRowForm,
    ProductForm,
    SSOCompleteSignupForm,
    SSOSettingsForm,
    PWASettingsForm,
    PanelSignupEditForm,
    QuestionForm,
    QuizGameSettingsForm,
    QuizQuestionForm,
    RazorpaySettingsForm,
    ResultHighlightForm,
    SignupForm,
    StaffMemberForm,
    StaffSalaryPaymentForm,
    StoreCheckoutForm,
    StoreOrderStatusForm,
    TransactionForm,
)
from .models import (
    AdmissionRegistration,
    BannerSlide,
    Brand,
    Bundle,
    BundlePurchase,
    Category,
    Certificate,
    ChatbotQuestion,
    ChatbotSettings,
    Classroom,
    ClassroomMember,
    ContactMessage,
    Coupon,
    CouponRedemption,
    Course,
    CourseContentFolder,
    CourseDocument,
    CourseEnrollment,
    CourseVideo,
    CustomUser,
    DailyQuizAttempt,
    DailyUpdateCard,
    DropboxSettings,
    DailyUpdatePost,
    DailyUpdatePostTableRow,
    EligibilityCriteria,
    EligibilitySubmission,
    ExamCalendarEvent,
    ExamTickerItem,
    ExamTickerSettings,
    ExtraPage,
    FAQItem,
    FeeInvoice,
    GalleryImage,
    HeroSection,
    HomepageContent,
    JobApplication,
    JobPosting,
    Notification,
    NotificationImage,
    NotificationProviderSettings,
    NotificationTableRow,
    OTPRequest,
    Product,
    PWASettings,
    Question,
    QuizGameSettings,
    QuizQuestion,
    QuizZoneAttempt,
    RazorpaySettings,
    ReferralCode,
    ReferralSignup,
    ResultHighlight,
    SiteSettings,
    SSOSettings,
    StaffAttendance,
    StaffMember,
    StaffSalaryPayment,
    StoreOrder,
    StudentAttendance,
    TestAnswer,
    TestAttempt,
    TestSection,
    Transaction,
)
from .certificate_utils import generate_certificate_image
from .razorpay_utils import RazorpayError, create_order, verify_payment_signature
from .otp_utils import send_otp
from . import sso_utils
from .sso_utils import SSOError
from . import backup_utils
from .dropbox_utils import DropboxError
from .signals import detect_device


def index(request):
    banner_slides = BannerSlide.objects.filter(is_active=True)

    test_series_courses = Course.objects.filter(course_type=Course.TEST_SERIES, is_active=True)
    test_series_categories = Category.objects.filter(courses__in=test_series_courses).distinct()
    video_courses = Course.objects.filter(
        course_type=Course.VIDEO_COURSE, is_active=True,
    ).prefetch_related('videos')[:4]
    elibrary_items = Course.objects.filter(
        course_type=Course.ELIBRARY, is_active=True,
    ).prefetch_related('documents')[:4]
    bundles = Bundle.objects.filter(is_active=True).prefetch_related('courses')[:4]
    exam_ticker_settings = ExamTickerSettings.load()
    exam_ticker_items = ExamTickerItem.objects.filter(is_active=True)
    homepage_content = HomepageContent.load()
    result_highlights = ResultHighlight.objects.filter(is_active=True)
    gallery_preview = GalleryImage.objects.filter(is_active=True)[:5]
    brands = Brand.objects.filter(is_active=True)
    latest_current_affair = DailyUpdatePost.objects.filter(
        category=DailyUpdateCard.CURRENT_AFFAIRS, is_active=True,
    ).first()

    return render(request, 'myapp/index.html', {
        'banner_slides': banner_slides,
        'test_series_courses': test_series_courses,
        'test_series_categories': test_series_categories,
        'video_courses': video_courses,
        'elibrary_items': elibrary_items,
        'bundles': bundles,
        'exam_ticker_settings': exam_ticker_settings,
        'exam_ticker_items': exam_ticker_items,
        'homepage_content': homepage_content,
        'result_highlights': result_highlights,
        'gallery_preview': gallery_preview,
        'brands': brands,
        'latest_current_affair': latest_current_affair,
    })


def video_courses_page(request):
    video_courses = Course.objects.filter(course_type=Course.VIDEO_COURSE, is_active=True).prefetch_related('videos')
    return render(request, 'myapp/video_courses_page.html', {'video_courses': video_courses})


def elibrary_page(request):
    elibrary_items = Course.objects.filter(course_type=Course.ELIBRARY, is_active=True).prefetch_related('documents')
    return render(request, 'myapp/elibrary_page.html', {'elibrary_items': elibrary_items})


def bundles_page(request):
    bundles = Bundle.objects.filter(is_active=True).prefetch_related('courses')
    return render(request, 'myapp/bundles_page.html', {'bundles': bundles})


def careers_page(request):
    jobs = JobPosting.objects.filter(is_active=True)
    return render(request, 'myapp/careers_page.html', {'jobs': jobs})


def notification_detail(request, pk):
    notification = get_object_or_404(Notification, pk=pk, is_active=True)
    other_notifications = Notification.objects.filter(is_active=True).exclude(pk=pk)[:5]
    return render(request, 'myapp/notification_detail.html', {
        'notification': notification,
        'other_notifications': other_notifications,
    })


def pwa_manifest(request):
    pwa = PWASettings.load()
    icons = []
    if pwa.android_icon:
        icons.append({'src': pwa.android_icon.url, 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any maskable'})
        icons.append({'src': pwa.android_icon.url, 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any maskable'})

    return JsonResponse({
        'name': pwa.app_name,
        'short_name': pwa.short_name,
        'description': pwa.description,
        'start_url': '/',
        'scope': '/',
        'display': 'standalone',
        'background_color': pwa.background_color,
        'theme_color': pwa.theme_color,
        'icons': icons,
    })


def service_worker(request):
    js = (
        "self.addEventListener('install', function (e) { self.skipWaiting(); });\n"
        "self.addEventListener('activate', function (e) { self.clients.claim(); });\n"
        "self.addEventListener('fetch', function (e) {\n"
        "  e.respondWith(fetch(e.request).catch(function () { return caches.match(e.request); }));\n"
        "});\n"
    )
    return HttpResponse(js, content_type='application/javascript')


def _current_affairs_translations(posts):
    data = {}
    for post in posts:
        entry = {}
        if post.title_hi or post.body_hi:
            entry['hi'] = {'title': post.title_hi or post.title, 'body': post.body_hi or post.body}
        if post.title_kn or post.body_kn:
            entry['kn'] = {'title': post.title_kn or post.title, 'body': post.body_kn or post.body}
        if entry:
            data[post.pk] = entry
    return json.dumps(data)


def daily_updates_page(request, category):
    if category == DailyUpdateCard.DAILY_NEWS:
        return redirect('current_affairs_page')
    if category != DailyUpdateCard.CURRENT_AFFAIRS:
        raise Http404

    card = DailyUpdateCard.load(category)
    posts = DailyUpdatePost.objects.filter(category=category, is_active=True)

    if category == DailyUpdateCard.CURRENT_AFFAIRS:
        available_dates = list(
            posts.order_by('-event_date').values_list('event_date', flat=True).distinct()
        )
        selected_date = parse_date(request.GET.get('date', ''))
        if selected_date:
            posts = posts.filter(event_date=selected_date)
        news_category_order = [key for key, _ in DailyUpdatePost.NEWS_CATEGORY_CHOICES]
        news_category_rank = {key: position for position, key in enumerate(news_category_order)}
        days = []
        days_by_date = {}
        for post in posts:
            if post.event_date not in days_by_date:
                day_group = {'date': post.event_date, 'posts': []}
                days_by_date[post.event_date] = day_group
                days.append(day_group)
            days_by_date[post.event_date]['posts'].append(post)

        for day_group in days:
            day_group['posts'].sort(
                key=lambda post: (news_category_rank.get(post.news_category, len(news_category_rank)), -post.pk)
            )

        ca_i18n_json = _current_affairs_translations(posts)
        return render(request, 'myapp/current_affairs_page.html', {
            'card': card,
            'days': days,
            'available_dates': available_dates,
            'selected_date': selected_date,
            'ca_i18n_json': ca_i18n_json,
        })

    return render(request, 'myapp/daily_updates_page.html', {'card': card, 'posts': posts})


def current_affairs_detail(request, pk):
    post = get_object_or_404(DailyUpdatePost, pk=pk, category=DailyUpdateCard.CURRENT_AFFAIRS, is_active=True)
    ca_i18n_json = _current_affairs_translations([post])
    return render(request, 'myapp/current_affairs_detail.html', {'post': post, 'ca_i18n_json': ca_i18n_json})


def gallery_page(request):
    images = GalleryImage.objects.filter(is_active=True)
    return render(request, 'myapp/gallery_page.html', {'images': images})


def extra_page_view(request, page_key):
    valid_keys = dict(ExtraPage.PAGE_CHOICES)
    if page_key not in valid_keys or page_key == ExtraPage.CONTACT_US:
        raise Http404
    page_obj, _ = ExtraPage.objects.get_or_create(page=page_key)
    return render(request, 'myapp/extra_page.html', {'page_obj': page_obj})


def contact_us_page(request):
    page_obj, _ = ExtraPage.objects.get_or_create(page=ExtraPage.CONTACT_US)
    sent = False
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            sent = True
            form = ContactMessageForm()
    else:
        form = ContactMessageForm()
    return render(request, 'myapp/contact_us.html', {'page_obj': page_obj, 'form': form, 'sent': sent})


def faq_page(request):
    faqs = FAQItem.objects.filter(is_active=True)
    return render(request, 'myapp/faq_page.html', {'faqs': faqs})


def exam_calendar_page(request):
    today = timezone.localdate()
    upcoming = ExamCalendarEvent.objects.filter(is_active=True, event_date__gte=today)
    past = ExamCalendarEvent.objects.filter(is_active=True, event_date__lt=today).order_by('-event_date')[:20]
    return render(request, 'myapp/exam_calendar.html', {'upcoming': upcoming, 'past': past})


def page_not_found_view(request, exception=None):
    return render(request, '404.html', status=404)


def admission_register(request):
    if request.method != 'POST':
        raise Http404

    form = AdmissionRegistrationForm(request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)


def signup(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            referral_code_str = form.cleaned_data.get('referral_code')
            if referral_code_str:
                referral_code = ReferralCode.objects.filter(code=referral_code_str).first()
                if referral_code:
                    ReferralSignup.objects.create(referral_code=referral_code, referred_user=user)
                    Coupon.objects.create(
                        code=f'WELCOME10-{user.pk}',
                        description=f'10% referral welcome discount (referred by {referral_code.user.name})',
                        discount_type=Coupon.PERCENTAGE,
                        discount_value=10,
                        applies_to=Coupon.APPLIES_ALL,
                        per_user_limit=1,
                        usage_limit=1,
                        restricted_to_user=user,
                        is_active=True,
                    )
            auth_login(request, user)
            messages.success(request, f'Welcome, {user.name}! Your account has been created and you are now logged in')
            return redirect('index')
    else:
        initial = {}
        ref_param = request.GET.get('ref', '').strip().upper()
        if ref_param:
            initial['referral_code'] = ref_param
        form = SignupForm(initial=initial)

    return render(request, 'myapp/signup.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'myapp/login.html'
    form_class = EmailAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Welcome back, {self.request.user.name}! You are now logged in')
        return response

    def get_success_url(self):
        return reverse('index')


def _sso_post_login_redirect(request, user):
    messages.success(request, f'Welcome, {user.name}! You are now logged in')
    return redirect('index')


def sso_start(request, provider):
    if request.user.is_authenticated:
        return redirect('index')

    settings_obj = SSOSettings.load()
    redirect_uri = request.build_absolute_uri(reverse('sso_callback', args=[provider]))
    state = uuid.uuid4().hex
    request.session['sso_state'] = state

    if provider == 'google' and settings_obj.google_active:
        return redirect(sso_utils.google_auth_url(settings_obj, redirect_uri, state))
    if provider == 'facebook' and settings_obj.facebook_active:
        return redirect(sso_utils.facebook_auth_url(settings_obj, redirect_uri, state))

    messages.error(request, 'This sign-in option is not available right now')
    return redirect('login')


def sso_callback(request, provider):
    if provider not in ('google', 'facebook'):
        raise Http404()

    settings_obj = SSOSettings.load()
    error = request.GET.get('error')
    code = request.GET.get('code')
    state = request.GET.get('state')
    expected_state = request.session.pop('sso_state', None)

    if error or not code or not state or state != expected_state:
        messages.error(request, 'Sign-in was cancelled or could not be verified. Please try again')
        return redirect('login')

    redirect_uri = request.build_absolute_uri(reverse('sso_callback', args=[provider]))
    try:
        if provider == 'google':
            profile = sso_utils.google_fetch_profile(settings_obj, redirect_uri, code)
        else:
            profile = sso_utils.facebook_fetch_profile(settings_obj, redirect_uri, code)
    except SSOError as exc:
        messages.error(request, str(exc))
        return redirect('login')

    existing_user = CustomUser.objects.filter(email__iexact=profile['email']).first()
    if existing_user:
        auth_login(request, existing_user)
        return _sso_post_login_redirect(request, existing_user)

    request.session['pending_sso_profile'] = {'email': profile['email'], 'name': profile['name'], 'provider': provider}
    return redirect('sso_complete_signup')


def sso_complete_signup(request):
    pending = request.session.get('pending_sso_profile')
    if not pending:
        return redirect('signup')

    if request.method == 'POST':
        form = SSOCompleteSignupForm(request.POST)
        if form.is_valid():
            user = CustomUser.objects.create_user(
                email=pending['email'],
                name=pending['name'],
                number=form.cleaned_data['number'],
                password=None,
            )
            del request.session['pending_sso_profile']
            auth_login(request, user)
            return _sso_post_login_redirect(request, user)
    else:
        form = SSOCompleteSignupForm()

    return render(request, 'myapp/sso_complete_signup.html', {'form': form, 'pending': pending})


def logout_view(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('index')


@login_required(login_url='login')
def account_edit(request):
    from django.contrib.auth import update_session_auth_hash
    from django.contrib.auth.forms import PasswordChangeForm

    if request.method == 'POST' and 'change_password' in request.POST:
        form = AccountUpdateForm(instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            if user.active_session_key:
                user.active_session_key = request.session.session_key or ''
                user.save(update_fields=['active_session_key'])
            messages.success(request, 'Your password has been changed')
            return redirect('account_edit')
    elif request.method == 'POST':
        form = AccountUpdateForm(request.POST, request.FILES, instance=request.user)
        password_form = PasswordChangeForm(request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account details have been updated')
            return redirect('account_edit')
    else:
        form = AccountUpdateForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)

    return render(request, 'myapp/account/edit.html', {'form': form, 'password_form': password_form})


@login_required(login_url='login')
def account_purchases(request):
    enrollments = request.user.enrollments.select_related('course', 'course__category')
    return render(request, 'myapp/account/purchases.html', {'enrollments': enrollments})


def _attempt_metrics(attempt, answers=None):
    answers = list(answers if answers is not None else attempt.answers.all())
    total_questions = len(answers)
    answered_count = sum(1 for answer in answers if (answer.submitted_answer or '').strip())
    correct_count = sum(1 for answer in answers if answer.is_correct)
    incorrect_count = answered_count - correct_count
    unattempted_count = total_questions - answered_count
    accuracy = round((correct_count / answered_count) * 100, 2) if answered_count else 0
    percentage = round((float(attempt.score) / float(attempt.total_marks)) * 100, 2) if attempt.total_marks else 0
    elapsed_seconds = max(0, int(((attempt.submitted_at or timezone.now()) - attempt.started_at).total_seconds()))
    average_seconds = round(elapsed_seconds / total_questions) if total_questions else 0
    return {
        'total_questions': total_questions,
        'answered_count': answered_count,
        'correct_count': correct_count,
        'incorrect_count': incorrect_count,
        'unattempted_count': unattempted_count,
        'accuracy': accuracy,
        'percentage': percentage,
        'elapsed_seconds': elapsed_seconds,
        'average_seconds': average_seconds,
        'elapsed_label': f'{elapsed_seconds // 60} Min {elapsed_seconds % 60} Sec',
        'average_label': f'{average_seconds // 60} Min {average_seconds % 60} Sec',
    }


@login_required(login_url='login')
def account_results(request):
    test_attempts = list(
        TestAttempt.objects.filter(user=request.user, submitted_at__isnull=False)
        .select_related('course').prefetch_related('answers')
    )
    for attempt in test_attempts:
        attempt.result_metrics = _attempt_metrics(attempt, attempt.answers.all())

    daily_quiz_attempts = list(DailyQuizAttempt.objects.filter(user=request.user).select_related('course'))
    for quiz_attempt in daily_quiz_attempts:
        quiz_attempt.correct_count = sum(1 for row in quiz_attempt.answer_details if row.get('is_correct'))
        quiz_attempt.question_count = len(quiz_attempt.answer_details)
    quiz_zone_attempts = QuizZoneAttempt.objects.filter(user=request.user)

    stats = {
        'tests_attempted': len(test_attempts),
        'daily_quizzes_taken': len(daily_quiz_attempts),
        'quiz_zone_played': quiz_zone_attempts.count(),
    }

    return render(request, 'myapp/account/results.html', {
        'test_attempts': test_attempts, 'daily_quiz_attempts': daily_quiz_attempts,
        'quiz_zone_attempts': quiz_zone_attempts, 'stats': stats,
    })


@login_required(login_url='login')
def account_coupons(request):
    redemptions = list(CouponRedemption.objects.filter(user=request.user).select_related('coupon').order_by('-created_at'))
    times_used_by_coupon = {}
    for redemption in redemptions:
        times_used_by_coupon[redemption.coupon_id] = times_used_by_coupon.get(redemption.coupon_id, 0) + 1

    coupons = Coupon.objects.filter(
        Q(is_active=True) | Q(pk__in=times_used_by_coupon.keys())
    ).filter(
        Q(restricted_to_user__isnull=True) | Q(restricted_to_user=request.user)
    ).distinct()

    coupon_rows = []
    status_order = {'available': 0, 'used': 1, 'expired': 2}
    for coupon in coupons:
        times_used = times_used_by_coupon.get(coupon.pk, 0)
        if times_used >= coupon.per_user_limit:
            status = 'used'
        elif not coupon.is_valid_now():
            status = 'expired'
        else:
            status = 'available'
        coupon_rows.append({'coupon': coupon, 'status': status})
    coupon_rows.sort(key=lambda row: status_order[row['status']])

    return render(request, 'myapp/account/coupons.html', {'coupon_rows': coupon_rows, 'redemptions': redemptions})


@login_required(login_url='login')
def account_certificates(request):
    certificates = request.user.certificates.all()
    return render(request, 'myapp/account/certificates.html', {'certificates': certificates})


@login_required(login_url='login')
def account_fees_attendance(request):
    invoices = request.user.fee_invoices.all()
    fee_stats = {
        'pending_count': invoices.filter(status=FeeInvoice.STATUS_PENDING).count(),
        'pending_total': invoices.filter(status=FeeInvoice.STATUS_PENDING).aggregate(total=Sum('amount'))['total'] or 0,
        'paid_total': invoices.filter(status=FeeInvoice.STATUS_PAID).aggregate(total=Sum('amount'))['total'] or 0,
    }

    records = request.user.attendance_records.all()
    total = records.count()
    present_count = records.filter(status=StudentAttendance.PRESENT).count()
    half_day_count = records.filter(status=StudentAttendance.HALF_DAY).count()
    attendance_percent = round(((present_count + half_day_count * 0.5) / total) * 100, 1) if total else None
    attendance_stats = {
        'total': total,
        'present_count': present_count,
        'absent_count': records.filter(status=StudentAttendance.ABSENT).count(),
        'attendance_percent': attendance_percent,
    }

    return render(request, 'myapp/account/fees_attendance.html', {
        'invoices': invoices, 'fee_stats': fee_stats,
        'records': records[:120], 'attendance_stats': attendance_stats,
    })


@login_required(login_url='login')
def account_refer_earn(request):
    referral = ReferralCode.get_or_create_for(request.user)
    signups = referral.signups.select_related('referred_user').order_by('-created_at')
    signup_url = request.build_absolute_uri(f"{reverse('signup')}?ref={referral.code}")
    return render(request, 'myapp/account/refer_earn.html', {'referral': referral, 'signups': signups, 'signup_url': signup_url})


@login_required(login_url='login')
def account_classrooms(request):
    memberships = ClassroomMember.objects.filter(student=request.user).select_related('classroom', 'classroom__test_course')
    rows = []
    for member in memberships:
        attempt = TestAttempt.objects.filter(user=request.user, course=member.classroom.test_course).first()
        rows.append({'member': member, 'classroom': member.classroom, 'status': member.classroom.status_label(), 'attempt': attempt})
    return render(request, 'myapp/account/classrooms.html', {'rows': rows})


@login_required(login_url='login')
def classroom_pay(request, pk):
    member = get_object_or_404(ClassroomMember, classroom_id=pk, student=request.user)
    if member.classroom.is_free or member.is_paid:
        return redirect('account_classrooms')
    return render(request, 'myapp/classroom_pay.html', {'member': member, 'classroom': member.classroom})


def _test_section_rows(course, selected_ids=None):
    selected_ids = {int(value) for value in (selected_ids or [])}
    rows = []
    for section in course.test_sections.prefetch_related('questions'):
        questions = list(section.questions.all())
        rows.append({
            'section': section,
            'question_count': len(questions),
            'maximum_marks': sum(question.marks for question in questions),
            'positive_marks': questions[0].marks if questions else 0,
            'selected': section.pk in selected_ids or not section.is_optional,
        })
    return rows


def _save_attempt_section_choices(attempt, course, request):
    sections = list(course.test_sections.all())
    valid_optional_ids = {section.pk for section in sections if section.is_optional}
    required_ids = [section.pk for section in sections if not section.is_optional]
    requested_ids = {
        int(value) for value in request.POST.getlist('selected_sections') if value.isdigit()
    }
    optional_limit = max(0, course.max_optional_sections)
    selected_optional_ids = [
        section.pk for section in sections
        if section.pk in requested_ids and section.pk in valid_optional_ids
    ][:optional_limit]
    attempt.selected_section_ids = required_ids + selected_optional_ids
    attempt.save(update_fields=['selected_section_ids'])


def _attempt_questions(attempt):
    questions = attempt.course.questions.select_related('section')
    if not attempt.course.test_sections.exists():
        return questions
    selected_ids = attempt.selected_section_ids or list(
        attempt.course.test_sections.filter(is_optional=False).values_list('pk', flat=True)
    )
    return questions.filter(Q(section__isnull=True) | Q(section_id__in=selected_ids))


@login_required(login_url='login')
def classroom_test_start(request, pk):
    member = get_object_or_404(ClassroomMember, classroom_id=pk, student=request.user)
    classroom = member.classroom

    if not member.is_paid:
        return redirect('classroom_pay', pk=classroom.pk)

    status = classroom.status_label()
    if status != 'open':
        return render(request, 'myapp/classroom_gate.html', {'classroom': classroom, 'status': status})

    course = classroom.test_course
    if not course.questions.exists():
        return render(request, 'myapp/classroom_gate.html', {'classroom': classroom, 'status': 'no_questions'})

    existing_attempt = TestAttempt.objects.filter(
        user=request.user,
        course=course,
        submitted_at__isnull=True,
    ).first()
    if request.method == 'POST':
        attempt = existing_attempt or TestAttempt.objects.create(user=request.user, course=course)
        _save_attempt_section_choices(attempt, course, request)
        return redirect('test_attempt_take', pk=attempt.pk)

    section_rows = _test_section_rows(course, existing_attempt.selected_section_ids if existing_attempt else [])
    return render(request, 'myapp/test_attempt_instructions.html', {
        'course': course,
        'question_count': course.questions.count(),
        'total_marks': course.questions.aggregate(total=Sum('marks'))['total'] or 0,
        'existing_attempt': existing_attempt,
        'section_rows': section_rows,
        'optional_section_rows': [row for row in section_rows if row['section'].is_optional],
        'hide_site_chrome': True,
    })


def _get_or_create_free_enrollment(user, course):
    """Returns the enrollment for a course, auto-granting access if it's free."""
    enrollment = CourseEnrollment.objects.filter(user=user, course=course).first()
    if course.is_free and (not enrollment or not enrollment.is_paid):
        enrollment, _ = CourseEnrollment.objects.get_or_create(user=user, course=course)
        if not enrollment.is_paid:
            enrollment.grant_paid_access(amount_paid=0)
    return enrollment


def _build_course_content_tree(course, public_only=True):
    folders = course.content_folders.all().select_related('parent')
    if public_only:
        folders = folders.filter(is_active=True)
    folders = list(folders)

    if course.course_type == Course.VIDEO_COURSE:
        items = course.videos.all()
    else:
        items = course.documents.all()
    if public_only:
        items = items.filter(is_active=True)
    items = list(items)

    folders_by_parent = {}
    for folder in folders:
        folders_by_parent.setdefault(folder.parent_id, []).append(folder)
    items_by_folder = {}
    for item in items:
        items_by_folder.setdefault(item.folder_id, []).append(item)

    visible_folder_ids = set()
    visible_items = list(items_by_folder.get(None, []))

    def build(parent_id, ancestors=None):
        ancestors = ancestors or set()
        nodes = []
        for folder in folders_by_parent.get(parent_id, []):
            if folder.pk in ancestors:
                continue
            visible_folder_ids.add(folder.pk)
            folder_items = items_by_folder.get(folder.pk, [])
            visible_items.extend(folder_items)
            children = build(folder.pk, ancestors | {folder.pk})
            nodes.append({
                'folder': folder,
                'items': folder_items,
                'children': children,
                'item_count': len(folder_items) + sum(child['item_count'] for child in children),
            })
        return nodes

    tree = build(None)
    return tree, items_by_folder.get(None, []), visible_items


@login_required(login_url='login')
def course_detail(request, pk):
    course = get_object_or_404(
        Course.objects.prefetch_related('videos', 'documents', 'content_folders'),
        pk=pk,
        is_active=True,
    )
    enrollment = _get_or_create_free_enrollment(request.user, course)

    if not enrollment or not enrollment.is_paid:
        preview_tree = []
        preview_root_content = []
        if course.course_type == Course.VIDEO_COURSE:
            preview_content = list(course.published_videos)
        elif course.course_type == Course.ELIBRARY:
            preview_content = list(course.published_documents)
        else:
            preview_content = []
        if course.enable_folders and course.course_type in (Course.VIDEO_COURSE, Course.ELIBRARY):
            preview_tree, preview_root_content, preview_content = _build_course_content_tree(course)
        return render(request, 'myapp/course_checkout.html', {
            'course': course,
            'content_tree': preview_tree,
            'root_content': preview_root_content,
            'visible_content': preview_content,
        })

    if request.method == 'POST' and enrollment.has_access:
        enrollment.is_completed = 'mark_incomplete' not in request.POST
        enrollment.save()
        return redirect('course_detail', pk=pk)

    content_tree = []
    root_content = []
    if course.course_type == Course.VIDEO_COURSE:
        visible_content = list(course.published_videos)
    elif course.course_type == Course.ELIBRARY:
        visible_content = list(course.published_documents)
    else:
        visible_content = []
    if course.enable_folders and course.course_type in (Course.VIDEO_COURSE, Course.ELIBRARY):
        content_tree, root_content, visible_content = _build_course_content_tree(course)

    template_name = (
        'myapp/video_course_detail.html'
        if course.course_type == Course.VIDEO_COURSE and enrollment.has_access
        else 'myapp/course_detail.html'
    )
    return render(request, template_name, {
        'course': course,
        'enrollment': enrollment,
        'content_tree': content_tree,
        'root_content': root_content,
        'visible_content': visible_content,
    })


def _grade_answer(question, submitted):
    submitted = (submitted or '').strip()
    correct = (question.correct_answer or '').strip()
    if not submitted or not correct:
        return False
    if question.question_type == Question.MULTIPLE:
        submitted_set = {part.strip().upper() for part in submitted.split(',') if part.strip()}
        correct_set = {part.strip().upper() for part in correct.split(',') if part.strip()}
        return submitted_set == correct_set
    if question.question_type == Question.NUMERIC:
        try:
            return Decimal(submitted.replace(',', '')) == Decimal(correct.replace(',', ''))
        except InvalidOperation:
            return False
    normalized_submitted = ' '.join(submitted.split()).casefold()
    normalized_correct = ' '.join(correct.split()).casefold()
    return normalized_submitted == normalized_correct


@login_required(login_url='login')
def test_series_detail(request, pk):
    course = get_object_or_404(Course, pk=pk, course_type=Course.TEST_SERIES, is_active=True)
    enrollment = _get_or_create_free_enrollment(request.user, course)
    all_questions = list(course.questions.all())
    quiz_result = None
    quiz_error = None

    if request.method == 'POST' and request.POST.get('action') == 'daily_quiz':
        try:
            quiz_payload = signing.loads(
                request.POST.get('quiz_token', ''),
                salt='test-series-daily-quiz',
                max_age=7200,
            )
        except (signing.BadSignature, signing.SignatureExpired):
            quiz_payload = {}

        expected_ids = quiz_payload.get('questions', []) if quiz_payload.get('course') == course.pk else []
        posted_ids = [int(value) for value in request.POST.getlist('quiz_question_ids') if value.isdigit()]
        valid_quiz = len(expected_ids) == 5 and len(set(expected_ids)) == 5 and posted_ids == expected_ids
        question_map = {
            question.pk: question
            for question in Question.objects.filter(course=course, pk__in=expected_ids)
        } if valid_quiz else {}
        valid_quiz = valid_quiz and len(question_map) == 5

        if not valid_quiz:
            quiz_error = 'This quiz set is invalid or expired. A fresh five-question quiz is ready below.'
        else:
            quiz_questions = [question_map[question_id] for question_id in expected_ids]
            score = 0
            total = sum(question.marks for question in quiz_questions)
            answer_details = []
            for question in quiz_questions:
                if question.question_type == Question.MULTIPLE:
                    submitted = ','.join(request.POST.getlist(f'q_{question.id}'))
                else:
                    submitted = request.POST.get(f'q_{question.id}', '')
                is_correct = _grade_answer(question, submitted)
                marks_awarded = question.marks if is_correct else 0
                score += marks_awarded
                answer_details.append({
                    'question_id': question.pk,
                    'question_text': question.text,
                    'submitted_answer': submitted,
                    'correct_answer': question.correct_answer,
                    'is_correct': is_correct,
                    'marks': question.marks,
                    'marks_awarded': marks_awarded,
                })
            DailyQuizAttempt.objects.create(
                user=request.user,
                course=course,
                score=score,
                total=total,
                answer_details=answer_details,
            )
            quiz_result = {'score': score, 'total': total}

    daily_quiz_questions = random.sample(all_questions, 5) if len(all_questions) >= 5 else []
    daily_quiz_total_marks = sum(question.marks for question in daily_quiz_questions)
    daily_quiz_minutes = max(5, len(daily_quiz_questions) * 2) if daily_quiz_questions else 0
    daily_quiz_token = signing.dumps({
        'course': course.pk,
        'questions': [question.pk for question in daily_quiz_questions],
    }, salt='test-series-daily-quiz') if daily_quiz_questions else ''

    # Sibling tests grouped into a Mock Tests / Topic wise / Previous Year Papers sidebar.
    sibling_tests = (
        Course.objects.filter(course_type=Course.TEST_SERIES, is_active=True)
        .exclude(test_type='daily_quiz')
        .select_related('category')
        .annotate(q_count=Count('questions', distinct=True), total_marks=Sum('questions__marks'))
    )
    paid_course_ids = set(
        CourseEnrollment.objects.filter(user=request.user, is_paid=True).values_list('course_id', flat=True)
    )

    test_type_order = ['mock_test', 'sectional_test', 'previous_year_paper', 'practice_test', 'sample_papers']
    test_type_labels = {
        'mock_test': 'Mock Tests',
        'sectional_test': 'Topic Wise',
        'previous_year_paper': 'Previous Year Papers',
        'practice_test': 'Practice Tests',
        'sample_papers': 'Sample Papers',
    }
    sections = []
    for tt in test_type_order:
        tests = [c for c in sibling_tests if c.test_type == tt]
        if not tests:
            continue
        groups = {}
        for c in tests:
            key = c.category.name if c.category else 'General'
            groups.setdefault(key, []).append(c)
        sections.append({
            'key': tt,
            'label': test_type_labels[tt],
            'groups': [{'name': name, 'tests': group_tests} for name, group_tests in groups.items()],
            'count': len(tests),
            'free_count': sum(1 for c in tests if c.is_free),
        })
    untyped = [c for c in sibling_tests if not c.test_type]
    if untyped:
        sections.append({
            'key': 'other', 'label': 'Other Tests',
            'groups': [{'name': 'General', 'tests': untyped}],
            'count': len(untyped),
            'free_count': sum(1 for c in untyped if c.is_free),
        })

    return render(request, 'myapp/test_series_detail.html', {
        'course': course, 'enrollment': enrollment,
        'daily_quiz_questions': daily_quiz_questions, 'quiz_result': quiz_result,
        'daily_quiz_token': daily_quiz_token, 'quiz_error': quiz_error,
        'daily_quiz_total_marks': daily_quiz_total_marks,
        'daily_quiz_minutes': daily_quiz_minutes,
        'sections': sections,
        'paid_course_ids': paid_course_ids,
    })


@login_required(login_url='login')
def test_attempt_start(request, pk):
    course = get_object_or_404(Course, pk=pk, course_type=Course.TEST_SERIES, is_active=True)
    enrollment = _get_or_create_free_enrollment(request.user, course)

    if not enrollment or not enrollment.is_paid:
        return render(request, 'myapp/course_checkout.html', {'course': course})

    if not enrollment.has_access:
        return render(request, 'myapp/test_expired.html', {'course': course, 'enrollment': enrollment})

    if not course.questions.exists():
        messages.info(request, 'No questions have been added to this test yet')
        return redirect('index')

    existing_attempt = TestAttempt.objects.filter(
        user=request.user,
        course=course,
        submitted_at__isnull=True,
    ).first()
    if request.method == 'POST':
        attempt = existing_attempt or TestAttempt.objects.create(user=request.user, course=course)
        _save_attempt_section_choices(attempt, course, request)
        return redirect('test_attempt_take', pk=attempt.pk)

    section_rows = _test_section_rows(course, existing_attempt.selected_section_ids if existing_attempt else [])
    return render(request, 'myapp/test_attempt_instructions.html', {
        'course': course,
        'question_count': course.questions.count(),
        'total_marks': course.questions.aggregate(total=Sum('marks'))['total'] or 0,
        'existing_attempt': existing_attempt,
        'section_rows': section_rows,
        'optional_section_rows': [row for row in section_rows if row['section'].is_optional],
        'hide_site_chrome': True,
    })


@login_required(login_url='login')
def test_attempt_take(request, pk):
    attempt = get_object_or_404(TestAttempt, pk=pk, user=request.user)
    if attempt.is_submitted:
        return redirect('test_attempt_result', pk=attempt.pk)

    questions = _attempt_questions(attempt)

    if request.method == 'POST':
        total_marks = 0
        score = 0
        for question in questions:
            if question.question_type == Question.MULTIPLE:
                submitted = ','.join(request.POST.getlist(f'q_{question.id}'))
            else:
                submitted = request.POST.get(f'q_{question.id}', '')
            is_correct = _grade_answer(question, submitted)
            negative_marks = question.section.negative_marks if question.section_id else Decimal('0')
            marks_awarded = question.marks if is_correct else (-negative_marks if submitted else Decimal('0'))
            TestAnswer.objects.update_or_create(
                attempt=attempt, question=question,
                defaults={
                    'submitted_answer': submitted,
                    'is_correct': is_correct,
                    'marks_awarded': marks_awarded,
                    'question_text_snapshot': question.text,
                    'correct_answer_snapshot': question.correct_answer,
                    'section_name_snapshot': question.section.name if question.section_id else 'General',
                    'question_marks_snapshot': question.marks,
                },
            )
            total_marks += question.marks
            score += marks_awarded

        attempt.total_marks = total_marks
        attempt.score = score
        attempt.submitted_at = timezone.now()
        attempt.save()
        return redirect('test_attempt_result', pk=attempt.pk)

    question_list = list(questions)
    for index, question in enumerate(question_list, start=1):
        question.exam_number = index
    exam_sections = []
    for section in attempt.course.test_sections.filter(pk__in=attempt.selected_section_ids):
        section_questions = [question for question in question_list if question.section_id == section.pk]
        if section_questions:
            exam_sections.append({'section': section, 'questions': section_questions})
    general_questions = [question for question in question_list if question.section_id is None]
    if general_questions:
        exam_sections.insert(0, {'section': None, 'name': 'General', 'questions': general_questions})
    if not exam_sections and question_list:
        exam_sections = [{'section': None, 'name': 'Section A', 'questions': question_list}]
    return render(request, 'myapp/test_attempt_take.html', {
        'attempt': attempt,
        'questions': question_list,
        'exam_sections': exam_sections,
        'hide_site_chrome': True,
    })


@login_required(login_url='login')
def test_attempt_result(request, pk):
    attempt = get_object_or_404(TestAttempt, pk=pk, user=request.user)
    if not attempt.is_submitted:
        return redirect('test_attempt_take', pk=attempt.pk)

    answers = list(attempt.answers.select_related('question', 'question__section'))
    metrics = _attempt_metrics(attempt, answers)
    chart_correct = round((metrics['correct_count'] / metrics['total_questions']) * 100, 2) if metrics['total_questions'] else 0
    chart_incorrect = round((metrics['incorrect_count'] / metrics['total_questions']) * 100, 2) if metrics['total_questions'] else 0

    completed_attempts = list(
        TestAttempt.objects.filter(course=attempt.course, submitted_at__isnull=False)
        .select_related('user').prefetch_related('answers')
    )
    for item in completed_attempts:
        item.result_metrics = _attempt_metrics(item, item.answers.all())
    completed_attempts.sort(key=lambda item: (
        -item.result_metrics['percentage'],
        -float(item.score),
        item.result_metrics['elapsed_seconds'],
        item.submitted_at,
        item.pk,
    ))
    best_by_user = {}
    for item in completed_attempts:
        best_by_user.setdefault(item.user_id, item)
    ranked_attempts = list(best_by_user.values())
    rank = next(
        (position for position, item in enumerate(ranked_attempts, start=1) if item.user_id == attempt.user_id),
        len(ranked_attempts),
    )
    leaderboard = ranked_attempts[:6]
    topper = ranked_attempts[0] if ranked_attempts else attempt
    topper_metrics = topper.result_metrics if hasattr(topper, 'result_metrics') else metrics

    section_buckets = {}
    for answer in answers:
        section_name = answer.section_name_snapshot or (
            answer.question.section.name if answer.question and answer.question.section_id else 'General'
        )
        bucket = section_buckets.setdefault(section_name, {
            'name': section_name,
            'score': Decimal('0'),
            'total': Decimal('0'),
            'correct': 0,
            'questions': 0,
        })
        bucket['score'] += answer.marks_awarded
        bucket['total'] += answer.question_marks_snapshot or (
            Decimal(answer.question.marks) if answer.question else Decimal('0')
        )
        bucket['correct'] += 1 if answer.is_correct else 0
        bucket['questions'] += 1
    section_results = []
    for bucket in section_buckets.values():
        bucket['percentage'] = max(
            0,
            min(100, round((float(bucket['score']) / float(bucket['total'])) * 100, 2)),
        ) if bucket['total'] else 0
        section_results.append(bucket)

    return render(request, 'myapp/test_attempt_result.html', {
        'attempt': attempt,
        'answers': answers,
        'chart_correct': chart_correct,
        'chart_incorrect': chart_incorrect,
        'rank': rank,
        'participant_count': len(ranked_attempts),
        'leaderboard': leaderboard,
        'topper': topper,
        'topper_metrics': topper_metrics,
        'section_results': section_results,
        **metrics,
    })


def _get_purchase_base(content_type, object_id, user):
    """Returns (object, base_amount, display_name) for a checkout target, or (None, None, None)."""
    if content_type == 'course':
        obj = get_object_or_404(Course, pk=object_id, is_active=True)
        return obj, obj.current_price, obj.name
    if content_type == 'store':
        obj = get_object_or_404(StoreOrder, pk=object_id, user=user, status=StoreOrder.STATUS_PENDING)
        return obj, obj.amount, obj.product.name
    if content_type == 'bundle':
        obj = get_object_or_404(Bundle, pk=object_id, is_active=True)
        return obj, obj.current_price, obj.name
    if content_type == 'classroom':
        obj = get_object_or_404(ClassroomMember, classroom_id=object_id, student=user)
        return obj, obj.classroom.price, obj.classroom.name
    return None, None, None


def _validate_coupon(code, content_type, base_amount, user):
    """Returns (coupon, discount_amount, error_message)."""
    try:
        coupon = Coupon.objects.get(code__iexact=code.strip())
    except Coupon.DoesNotExist:
        return None, Decimal('0'), 'Invalid coupon code.'

    if not coupon.is_valid_now():
        return None, Decimal('0'), 'This coupon is inactive or has expired.'

    if coupon.restricted_to_user_id and coupon.restricted_to_user_id != user.id:
        return None, Decimal('0'), 'This coupon is not valid for your account.'

    if coupon.applies_to != Coupon.APPLIES_ALL and coupon.applies_to != content_type:
        return None, Decimal('0'), 'This coupon is not valid for this purchase.'

    if base_amount < coupon.min_order_amount:
        return None, Decimal('0'), f'This coupon needs a minimum order of ₹{coupon.min_order_amount}.'

    if CouponRedemption.objects.filter(coupon=coupon, user=user).count() >= coupon.per_user_limit:
        return None, Decimal('0'), 'You have already used this coupon.'

    discount = coupon.calculate_discount(base_amount)
    if discount <= 0:
        return None, Decimal('0'), 'This coupon does not apply to this order.'

    return coupon, discount, None


@login_required(login_url='login')
def apply_coupon(request):
    if request.method != 'POST':
        raise Http404

    content_type = request.POST.get('content_type')
    object_id = request.POST.get('object_id')
    code = request.POST.get('code', '').strip()
    if not code:
        return JsonResponse({'ok': False, 'error': 'Enter a coupon code.'}, status=400)

    obj, base_amount, _name = _get_purchase_base(content_type, object_id, request.user)
    if obj is None:
        raise Http404

    coupon, discount, error = _validate_coupon(code, content_type, base_amount, request.user)
    if error:
        return JsonResponse({'ok': False, 'error': error}, status=400)

    final_amount = (base_amount - discount).quantize(Decimal('0.01'))
    return JsonResponse({
        'ok': True,
        'code': coupon.code,
        'discount': str(discount),
        'base_amount': str(base_amount),
        'final_amount': str(final_amount),
    })


@login_required(login_url='login')
def razorpay_create_order(request):
    if request.method != 'POST':
        raise Http404

    settings_obj = RazorpaySettings.load()
    if not settings_obj.is_configured:
        return JsonResponse({'ok': False, 'error': 'Online payments are not set up yet. Please contact support.'}, status=400)

    content_type = request.POST.get('content_type')
    object_id = request.POST.get('object_id')
    coupon_code = request.POST.get('coupon_code', '').strip()
    timestamp = int(timezone.now().timestamp())

    if content_type == 'course':
        course = get_object_or_404(Course, pk=object_id, is_active=True)
        amount = course.current_price
        name = course.name
        receipt = f'course_{course.pk}_{request.user.pk}_{timestamp}'
    elif content_type == 'store':
        order = get_object_or_404(StoreOrder, pk=object_id, user=request.user, status=StoreOrder.STATUS_PENDING)
        amount = order.amount
        name = order.product.name
        receipt = f'store_{order.pk}_{timestamp}'
    elif content_type == 'bundle':
        bundle = get_object_or_404(Bundle, pk=object_id, is_active=True)
        amount = bundle.current_price
        name = bundle.name
        receipt = f'bundle_{bundle.pk}_{request.user.pk}_{timestamp}'
    elif content_type == 'classroom':
        member = get_object_or_404(ClassroomMember, classroom_id=object_id, student=request.user)
        if member.classroom.is_free or member.is_paid:
            raise Http404
        amount = member.classroom.price
        name = member.classroom.name
        receipt = f'classroom_{member.classroom.pk}_{request.user.pk}_{timestamp}'
    else:
        raise Http404

    if coupon_code:
        _coupon, discount, error = _validate_coupon(coupon_code, content_type, amount, request.user)
        if error:
            return JsonResponse({'ok': False, 'error': error}, status=400)
        amount = (amount - discount).quantize(Decimal('0.01'))

    try:
        razorpay_order = create_order(settings_obj.key_id, settings_obj.key_secret, amount, receipt)
    except RazorpayError as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=502)

    return JsonResponse({
        'ok': True,
        'order_id': razorpay_order['id'],
        'amount': razorpay_order['amount'],
        'currency': razorpay_order['currency'],
        'key_id': settings_obj.key_id,
        'name': name,
        'prefill_name': request.user.name,
        'prefill_email': request.user.email,
        'prefill_contact': request.user.number,
    })


@login_required(login_url='login')
def razorpay_verify_payment(request):
    if request.method != 'POST':
        raise Http404

    settings_obj = RazorpaySettings.load()
    razorpay_order_id = request.POST.get('razorpay_order_id', '')
    razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
    razorpay_signature = request.POST.get('razorpay_signature', '')
    content_type = request.POST.get('content_type')
    object_id = request.POST.get('object_id')
    coupon_code = request.POST.get('coupon_code', '').strip()

    if not verify_payment_signature(settings_obj.key_secret, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        return JsonResponse({'ok': False, 'error': 'Payment verification failed.'}, status=400)

    def resolve_amount(base_amount):
        """Recomputes the coupon discount for bookkeeping. The actual amount charged
        was already fixed when the Razorpay order was created, so a coupon problem
        here must never block a payment that has already gone through."""
        if not coupon_code:
            return base_amount, None, Decimal('0')
        coupon, discount, error = _validate_coupon(coupon_code, content_type, base_amount, request.user)
        if error:
            return base_amount, None, Decimal('0')
        return (base_amount - discount).quantize(Decimal('0.01')), coupon, discount

    def record_redemption(coupon, discount, amount_before, amount_after, object_pk):
        if not coupon:
            return
        CouponRedemption.objects.create(
            coupon=coupon, user=request.user, content_type=content_type, object_id=object_pk,
            amount_before=amount_before, discount_amount=discount, amount_after=amount_after,
            razorpay_order_id=razorpay_order_id,
        )
        Coupon.objects.filter(pk=coupon.pk).update(used_count=F('used_count') + 1)

    if content_type == 'course':
        course = get_object_or_404(Course, pk=object_id)
        base_amount = course.current_price
        amount_paid, coupon, discount = resolve_amount(base_amount)
        enrollment, _ = CourseEnrollment.objects.get_or_create(user=request.user, course=course)
        enrollment.grant_paid_access(
            amount_paid=amount_paid,
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id,
        )
        record_redemption(coupon, discount, base_amount, amount_paid, course.pk)
        if course.course_type == Course.TEST_SERIES:
            redirect_url = reverse('test_attempt_start', args=[course.pk])
        else:
            redirect_url = reverse('course_detail', args=[course.pk])
    elif content_type == 'store':
        order = get_object_or_404(StoreOrder, pk=object_id, user=request.user)
        base_amount = order.amount
        amount_paid, coupon, discount = resolve_amount(base_amount)
        order.status = StoreOrder.STATUS_PAID
        order.amount = amount_paid
        order.razorpay_order_id = razorpay_order_id
        order.razorpay_payment_id = razorpay_payment_id
        order.save()
        record_redemption(coupon, discount, base_amount, amount_paid, order.pk)
        redirect_url = reverse('store_order_success', args=[order.pk])
    elif content_type == 'bundle':
        bundle = get_object_or_404(Bundle, pk=object_id)
        base_amount = bundle.current_price
        amount_paid, coupon, discount = resolve_amount(base_amount)
        BundlePurchase.objects.create(
            user=request.user, bundle=bundle, amount_paid=amount_paid,
            razorpay_order_id=razorpay_order_id, razorpay_payment_id=razorpay_payment_id,
        )
        for course in bundle.courses.all():
            enrollment, _ = CourseEnrollment.objects.get_or_create(user=request.user, course=course)
            if not enrollment.is_paid:
                enrollment.grant_paid_access(amount_paid=0, razorpay_order_id=razorpay_order_id, razorpay_payment_id=razorpay_payment_id)
        record_redemption(coupon, discount, base_amount, amount_paid, bundle.pk)
        redirect_url = reverse('bundle_success', args=[bundle.pk])
    elif content_type == 'classroom':
        member = get_object_or_404(ClassroomMember, classroom_id=object_id, student=request.user)
        base_amount = member.classroom.price
        amount_paid, coupon, discount = resolve_amount(base_amount)
        member.is_paid = True
        member.amount_paid = amount_paid
        member.razorpay_order_id = razorpay_order_id
        member.razorpay_payment_id = razorpay_payment_id
        member.save()
        record_redemption(coupon, discount, base_amount, amount_paid, member.classroom.pk)
        redirect_url = reverse('account_classrooms')
    else:
        raise Http404

    return JsonResponse({'ok': True, 'redirect_url': redirect_url})


def store_page(request):
    products = Product.objects.filter(is_active=True).select_related('category')
    categories = Category.objects.filter(products__in=products).distinct()
    return render(request, 'myapp/store.html', {'products': products, 'categories': categories})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    return render(request, 'myapp/product_detail.html', {'product': product})


@login_required(login_url='login')
def store_checkout(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)

    if request.method == 'POST':
        form = StoreCheckoutForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            order = StoreOrder.objects.create(
                user=request.user,
                product=product,
                quantity=quantity,
                amount=product.current_price * quantity,
                shipping_name=form.cleaned_data['shipping_name'],
                shipping_phone=form.cleaned_data['shipping_phone'],
                shipping_address=form.cleaned_data['shipping_address'],
            )
            return redirect('store_pay', pk=order.pk)
    else:
        form = StoreCheckoutForm(initial={'shipping_name': request.user.name, 'shipping_phone': request.user.number})

    return render(request, 'myapp/store_checkout.html', {'product': product, 'form': form})


@login_required(login_url='login')
def store_pay(request, pk):
    order = get_object_or_404(StoreOrder, pk=pk, user=request.user)
    if order.status != StoreOrder.STATUS_PENDING:
        return redirect('store_order_success', pk=order.pk)
    return render(request, 'myapp/store_pay.html', {'order': order})


@login_required(login_url='login')
def store_order_success(request, pk):
    order = get_object_or_404(StoreOrder, pk=pk, user=request.user)
    return render(request, 'myapp/store_order_success.html', {'order': order})


def career_apply(request, job_pk):
    if request.method != 'POST':
        raise Http404

    job = get_object_or_404(JobPosting, pk=job_pk, is_active=True)
    form = CareerApplicationForm(request.POST, request.FILES)
    if form.is_valid():
        application = form.save(commit=False)
        application.job = job
        application.save()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)


@login_required(login_url='login')
def bundle_checkout(request, pk):
    bundle = get_object_or_404(Bundle, pk=pk, is_active=True)
    already_owned = not bundle.courses.exclude(enrollments__user=request.user, enrollments__is_paid=True).exists() and bundle.courses.exists()
    return render(request, 'myapp/bundle_checkout.html', {'bundle': bundle, 'already_owned': already_owned})


@login_required(login_url='login')
def bundle_success(request, pk):
    bundle = get_object_or_404(Bundle, pk=pk)
    return render(request, 'myapp/bundle_success.html', {'bundle': bundle})


def _education_rank(value):
    order = [EligibilityCriteria.EDU_10TH, EligibilityCriteria.EDU_12TH, EligibilityCriteria.EDU_GRADUATE, EligibilityCriteria.EDU_POST_GRADUATE]
    return order.index(value) if value in order else 0


def _matches_criteria(criteria, data):
    if _education_rank(data['education']) < _education_rank(criteria.min_education):
        return False
    if criteria.min_age and data['age'] < criteria.min_age:
        return False
    if criteria.max_age and data['age'] > criteria.max_age:
        return False
    if criteria.min_height_cm and data['height_cm'] < criteria.min_height_cm:
        return False
    if criteria.allowed_gender != 'any' and data['gender'] != criteria.allowed_gender:
        return False
    if criteria.marital_status == 'unmarried_only' and data['marital_status'] != 'unmarried':
        return False
    if criteria.allowed_states:
        allowed = [s.strip().lower() for s in criteria.allowed_states.split(',') if s.strip()]
        if allowed and data['state'].strip().lower() not in allowed:
            return False
    return True


@login_required(login_url='login')
def eligibility_check(request):
    result = None
    if request.method == 'POST':
        form = EligibilityCheckForm(request.POST)
        if form.is_valid():
            from datetime import date

            dob = form.cleaned_data['dob']
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            data = {
                'education': form.cleaned_data['education'],
                'gender': form.cleaned_data['gender'],
                'age': age,
                'height_cm': form.cleaned_data['height_cm'],
                'state': form.cleaned_data['state'],
                'marital_status': form.cleaned_data['marital_status'],
            }
            matched = []
            if form.cleaned_data['nationality'] == 'indian':
                matched = [c for c in EligibilityCriteria.objects.filter(is_active=True) if _matches_criteria(c, data)]

            submission = EligibilitySubmission.objects.create(
                user=request.user,
                education=data['education'],
                gender=data['gender'],
                dob=dob,
                height_cm=data['height_cm'],
                state=data['state'],
                district=form.cleaned_data['district'],
                marital_status=data['marital_status'],
                matched_jobs=', '.join(c.job_name for c in matched),
            )
            result = {
                'matched': matched,
                'age': age,
                'submission': submission,
                'nationality': form.cleaned_data['nationality'],
                'category': form.cleaned_data['category'],
            }
    else:
        form = EligibilityCheckForm()

    return render(request, 'myapp/eligibility_check.html', {'form': form, 'result': result})


@login_required(login_url='login')
def quiz_game_page(request):
    quiz_settings = QuizGameSettings.load()
    return render(request, 'myapp/quiz_game_page.html', {'quiz_settings': quiz_settings})


@login_required(login_url='login')
def quiz_reset(request):
    if request.method != 'POST':
        raise Http404
    request.session['quiz_level'] = 1
    request.session['quiz_used_fifty'] = False
    request.session['quiz_used_audience'] = False
    request.session['quiz_used_skip'] = False
    request.session['quiz_questions_answered'] = 0
    request.session['quiz_correct_count'] = 0
    request.session['quiz_last_prize_label'] = ''
    request.session['quiz_recorded'] = False
    return JsonResponse({'ok': True})


def _record_quiz_zone_attempt(request):
    if request.session.get('quiz_recorded'):
        return
    answered = request.session.get('quiz_questions_answered', 0)
    if answered <= 0:
        return
    QuizZoneAttempt.objects.create(
        user=request.user,
        questions_answered=answered,
        correct_count=request.session.get('quiz_correct_count', 0),
        final_prize_label=request.session.get('quiz_last_prize_label', ''),
    )
    request.session['quiz_recorded'] = True


@login_required(login_url='login')
def quiz_get_question(request):
    level = request.session.get('quiz_level', 1)
    question = QuizQuestion.objects.filter(is_active=True, level__gte=level).order_by('level', 'id').first()
    if not question:
        _record_quiz_zone_attempt(request)
        return JsonResponse({'ok': True, 'finished': True})
    return JsonResponse({
        'ok': True,
        'finished': False,
        'question': {
            'id': question.pk,
            'level': question.level,
            'text': question.text,
            'option_a': question.option_a,
            'option_b': question.option_b,
            'option_c': question.option_c,
            'option_d': question.option_d,
            'prize_label': question.prize_label,
        },
        'lifelines_used': {
            'fifty': request.session.get('quiz_used_fifty', False),
            'audience': request.session.get('quiz_used_audience', False),
            'skip': request.session.get('quiz_used_skip', False),
        },
    })


@login_required(login_url='login')
def quiz_submit_answer(request):
    if request.method != 'POST':
        raise Http404
    question = get_object_or_404(QuizQuestion, pk=request.POST.get('question_id'))
    selected = (request.POST.get('selected_option') or '').strip().upper()
    is_correct = selected == question.correct_option

    request.session['quiz_questions_answered'] = request.session.get('quiz_questions_answered', 0) + 1
    if is_correct:
        request.session['quiz_level'] = question.level + 1
        request.session['quiz_correct_count'] = request.session.get('quiz_correct_count', 0) + 1
        request.session['quiz_last_prize_label'] = question.prize_label
    else:
        _record_quiz_zone_attempt(request)
    return JsonResponse({
        'ok': True,
        'is_correct': is_correct,
        'correct_option': question.correct_option,
        'prize_label': question.prize_label,
    })


@login_required(login_url='login')
def quiz_lifeline_fifty(request):
    question = get_object_or_404(QuizQuestion, pk=request.GET.get('question_id'))
    if request.session.get('quiz_used_fifty'):
        return JsonResponse({'ok': False, 'error': 'Lifeline already used.'}, status=400)
    import random

    wrong_options = [o for o in ['A', 'B', 'C', 'D'] if o != question.correct_option]
    keep_wrong = random.choice(wrong_options)
    eliminate = [o for o in ['A', 'B', 'C', 'D'] if o not in (question.correct_option, keep_wrong)]
    request.session['quiz_used_fifty'] = True
    return JsonResponse({'ok': True, 'eliminate': eliminate})


@login_required(login_url='login')
def quiz_lifeline_audience(request):
    question = get_object_or_404(QuizQuestion, pk=request.GET.get('question_id'))
    if request.session.get('quiz_used_audience'):
        return JsonResponse({'ok': False, 'error': 'Lifeline already used.'}, status=400)
    import random

    correct_share = random.randint(55, 80)
    remaining = 100 - correct_share
    others = ['A', 'B', 'C', 'D']
    others.remove(question.correct_option)
    random.shuffle(others)
    splits = [0, 0, 0]
    for i in range(remaining):
        splits[i % 3] += 1
    percentages = {question.correct_option: correct_share}
    for option, share in zip(others, splits):
        percentages[option] = share
    request.session['quiz_used_audience'] = True
    return JsonResponse({'ok': True, 'percentages': percentages})


@login_required(login_url='login')
def quiz_lifeline_skip(request):
    if request.method != 'POST':
        raise Http404
    if request.session.get('quiz_used_skip'):
        return JsonResponse({'ok': False, 'error': 'Lifeline already used.'}, status=400)
    question = get_object_or_404(QuizQuestion, pk=request.POST.get('question_id'))
    request.session['quiz_used_skip'] = True
    request.session['quiz_level'] = question.level + 1
    return JsonResponse({'ok': True})


def _is_staff(user):
    return user.is_authenticated and user.is_staff


def _safe_next(request, fallback):
    candidate = request.POST.get('next') or request.GET.get('next') or ''
    if candidate and url_has_allowed_host_and_scheme(candidate, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return candidate
    return fallback


def _registered_students():
    """Public student accounts only; internal staff never count as signups."""
    return CustomUser.objects.filter(is_staff=False, is_superuser=False).exclude(
        email__contains='.demo', email__endswith='@example.com',
    )


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_dashboard(request):
    today = timezone.localdate()
    dates = [today - timezone.timedelta(days=offset) for offset in range(6, -1, -1)]
    students = _registered_students()
    student_ids = students.values('pk')

    signup_counts = [students.filter(date_joined__date=day).count() for day in dates]
    course_revenue = [
        float(CourseEnrollment.objects.filter(
            user_id__in=student_ids,
            is_paid=True, amount_paid__gt=0, paid_at__date=day,
        ).aggregate(total=Sum('amount_paid'))['total'] or 0)
        for day in dates
    ]
    bundle_revenue = [
        float(BundlePurchase.objects.filter(
            user_id__in=student_ids, amount_paid__gt=0,
            purchased_at__date=day,
        ).aggregate(total=Sum('amount_paid'))['total'] or 0)
        for day in dates
    ]
    paid_store_statuses = [StoreOrder.STATUS_PAID, StoreOrder.STATUS_SHIPPED, StoreOrder.STATUS_DELIVERED]
    store_revenue = [
        float(StoreOrder.objects.filter(
            user_id__in=student_ids,
            status__in=paid_store_statuses, amount__gt=0, paid_at__date=day,
        ).aggregate(total=Sum('amount'))['total'] or 0)
        for day in dates
    ]
    payment_totals = [course_revenue[i] + bundle_revenue[i] + store_revenue[i] for i in range(len(dates))]

    device_rows = students.values('device_type').annotate(total=Count('id')).order_by('-total', 'device_type')
    device_labels = dict(CustomUser.DEVICE_CHOICES)
    device_data = {
        'labels': [device_labels.get(row['device_type'], 'Not recorded') if row['device_type'] else 'Not recorded' for row in device_rows],
        'values': [row['total'] for row in device_rows],
    }
    payment_device_totals = {}
    payment_device_sources = [
        CourseEnrollment.objects.filter(
            user_id__in=student_ids, is_paid=True, amount_paid__gt=0,
        ).values('user__device_type').annotate(total=Sum('amount_paid')).order_by('user__device_type'),
        BundlePurchase.objects.filter(
            user_id__in=student_ids, amount_paid__gt=0,
        ).values('user__device_type').annotate(total=Sum('amount_paid')).order_by('user__device_type'),
        StoreOrder.objects.filter(
            user_id__in=student_ids,
            status__in=paid_store_statuses, amount__gt=0,
        ).values('user__device_type').annotate(total=Sum('amount')).order_by('user__device_type'),
    ]
    for source in payment_device_sources:
        for row in source:
            key = row['user__device_type'] or ''
            payment_device_totals[key] = payment_device_totals.get(key, 0) + float(row['total'] or 0)
    payment_device_data = {
        'labels': [device_labels.get(key, 'Not recorded') if key else 'Not recorded' for key in payment_device_totals],
        'values': list(payment_device_totals.values()),
    }
    exam_rows = Course.objects.filter(is_active=True).values('category__name').annotate(total=Count('id')).order_by('-total')
    exam_data = {
        'labels': [row['category__name'] or 'Uncategorised' for row in exam_rows],
        'values': [row['total'] for row in exam_rows],
    }
    chart_data = {
        'labels': [day.strftime('%d %b') for day in dates],
        'signups': signup_counts,
        'payments': payment_totals,
        'devices': device_data,
        'payment_devices': payment_device_data,
        'exams': exam_data,
    }
    total_revenue = (
        (CourseEnrollment.objects.filter(
            user_id__in=student_ids, is_paid=True, amount_paid__gt=0,
        ).aggregate(total=Sum('amount_paid'))['total'] or 0)
        + (BundlePurchase.objects.filter(
            user_id__in=student_ids, amount_paid__gt=0,
        ).aggregate(total=Sum('amount_paid'))['total'] or 0)
        + (StoreOrder.objects.filter(
            user_id__in=student_ids,
            status__in=paid_store_statuses, amount__gt=0,
        ).aggregate(total=Sum('amount'))['total'] or 0)
    )
    context = {
        'chart_data': chart_data,
        'total_users': students.count(),
        'week_signups': sum(signup_counts),
        'total_revenue': total_revenue,
        'active_courses': Course.objects.filter(is_active=True).count(),
        'eligibility_checks': EligibilitySubmission.objects.count(),
    }
    return render(request, 'myapp/panel/dashboard.html', context)


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_signups(request):
    students = _registered_students()
    week_start = timezone.localdate() - timezone.timedelta(days=6)
    stats = {
        'total': students.count(),
        'admins': CustomUser.objects.filter(is_staff=True).count(),
        'active': students.filter(is_active=True).count(),
        'this_week': students.filter(date_joined__date__gte=week_start).count(),
    }

    date_from = request.GET.get('from', '').strip()
    date_to = request.GET.get('to', '').strip()
    device_filter = request.GET.get('device', '').strip()
    parsed_from = parse_date(date_from) if date_from else None
    parsed_to = parse_date(date_to) if date_to else None
    date_filter_error = ''
    if date_from and parsed_from is None:
        date_filter_error = 'The From date is not valid.'
    elif date_to and parsed_to is None:
        date_filter_error = 'The To date is not valid.'
    elif parsed_from and parsed_to and parsed_from > parsed_to:
        date_filter_error = 'The From date must be before the To date.'

    filtered = students
    if not date_filter_error and parsed_from:
        filtered = filtered.filter(date_joined__date__gte=parsed_from)
    if not date_filter_error and parsed_to:
        filtered = filtered.filter(date_joined__date__lte=parsed_to)
    if device_filter in dict(CustomUser.DEVICE_CHOICES):
        filtered = filtered.filter(device_type=device_filter)

    users = filtered.order_by('-date_joined')

    device_labels = dict(CustomUser.DEVICE_CHOICES)
    device_labels[''] = 'Not recorded'
    device_counts = {key: 0 for key in device_labels}
    for row in filtered.values('device_type').annotate(count=Count('id')):
        key = row['device_type'] or ''
        device_counts[key] = device_counts.get(key, 0) + row['count']
    device_breakdown = [
        {'key': key or 'unknown', 'label': device_labels[key], 'count': count}
        for key, count in device_counts.items()
    ]
    device_max = max((d['count'] for d in device_breakdown), default=0) or 1

    # The trend and device chart use exactly the same filtered student dataset as the table.
    trend_source = filtered

    months = []
    month_cursor = timezone.localdate().replace(day=1)
    for _ in range(6):
        months.append(month_cursor)
        month_cursor = (month_cursor - timezone.timedelta(days=1)).replace(day=1)
    months.reverse()

    monthly_counts = []
    for month_start in months:
        if month_start.month == 12:
            next_month = month_start.replace(year=month_start.year + 1, month=1)
        else:
            next_month = month_start.replace(month=month_start.month + 1)
        count = trend_source.filter(date_joined__date__gte=month_start, date_joined__date__lt=next_month).count()
        monthly_counts.append({'label': month_start.strftime('%b %Y'), 'count': count})
    monthly_max = max((m['count'] for m in monthly_counts), default=0) or 1

    return render(request, 'myapp/panel/signups_list.html', {
        'users': users,
        'stats': stats,
        'filters': {'from': date_from, 'to': date_to, 'device': device_filter},
        'date_filter_error': date_filter_error,
        'filtered_count': filtered.count(),
        'device_choices': CustomUser.DEVICE_CHOICES,
        'device_breakdown': device_breakdown,
        'device_max': device_max,
        'monthly_counts': monthly_counts,
        'monthly_max': monthly_max,
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_signup_add(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully')
            return redirect('panel_signups')
    else:
        form = SignupForm()

    return render(request, 'myapp/panel/signup_add.html', {'form': form})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_signup_edit(request, pk):
    student = get_object_or_404(_registered_students(), pk=pk)
    if request.method == 'POST':
        form = PanelSignupEditForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f'{student.name} updated successfully')
            return redirect('panel_signups')
    else:
        form = PanelSignupEditForm(instance=student)

    return render(request, 'myapp/panel/signup_edit.html', {'form': form, 'student': student})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_signup_delete(request, pk):
    student = get_object_or_404(_registered_students(), pk=pk)
    related_counts = {
        'enrollments': student.enrollments.count(),
        'test_attempts': student.test_attempts.count(),
        'store_orders': student.store_orders.count(),
        'classrooms': student.classroom_memberships.count(),
    }
    if request.method == 'POST':
        student_name = student.name or student.email
        student.delete()
        messages.success(request, f'{student_name} and their linked account records were deleted')
        return redirect('panel_signups')

    return render(request, 'myapp/panel/signup_delete_confirm.html', {
        'student': student,
        'related_counts': related_counts,
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_bulk_signup(request):
    results = None
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        results = []
        if not csv_file:
            messages.error(request, 'Please choose a CSV file to upload')
        elif not csv_file.name.lower().endswith('.csv'):
            messages.error(request, 'Please upload a .csv file')
        else:
            try:
                decoded = csv_file.read().decode('utf-8-sig')
            except UnicodeDecodeError:
                messages.error(request, 'Could not read that file. Please save it as a UTF-8 CSV and try again')
                decoded = None

            if decoded is not None:
                reader = csv.DictReader(io.StringIO(decoded))
                reader.fieldnames = [(f or '').strip().lower() for f in (reader.fieldnames or [])]
                created_count = 0
                for i, raw_row in enumerate(reader, start=2):
                    row = {(k or '').strip().lower(): (v or '').strip() for k, v in raw_row.items()}
                    name = row.get('name', '')
                    email = row.get('email', '')
                    number = row.get('number', '') or row.get('phone', '')

                    if not (name and email and number):
                        results.append({'row': i, 'email': email, 'status': 'skipped', 'reason': 'Missing name, email or number.'})
                        continue
                    if CustomUser.objects.filter(email__iexact=email).exists():
                        results.append({'row': i, 'email': email, 'status': 'skipped', 'reason': 'Email already registered.'})
                        continue

                    password = row.get('password') or secrets.token_urlsafe(6)
                    try:
                        age_value = int(row['age']) if row.get('age', '').isdigit() else None
                        CustomUser.objects.create_user(
                            email=email, name=name, number=number, password=password,
                            age=age_value, gender=row.get('gender', ''),
                            state=row.get('state', ''), city=row.get('city', ''),
                        )
                        created_count += 1
                        results.append({'row': i, 'email': email, 'status': 'created', 'reason': '', 'password': password})
                    except Exception as exc:
                        results.append({'row': i, 'email': email, 'status': 'skipped', 'reason': str(exc)})

                if created_count:
                    messages.success(request, f'{created_count} student{"s" if created_count != 1 else ""} imported successfully')
                elif results:
                    messages.error(request, 'No students were imported. See the details below')

    return render(request, 'myapp/panel/bulk_signup.html', {'results': results})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_navbar_customization(request):
    site_settings = SiteSettings.load()
    if request.method == 'POST':
        form = NavbarCustomizationForm(request.POST, request.FILES, instance=site_settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Navbar customization saved')
            return redirect('panel_navbar_customization')
    else:
        form = NavbarCustomizationForm(instance=site_settings)

    return render(request, 'myapp/panel/navbar_customization.html', {'form': form, 'site_settings': site_settings})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_banner_list(request):
    slides = BannerSlide.objects.all()
    return render(request, 'myapp/panel/banner_list.html', {'slides': slides})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_banner_add(request):
    if request.method == 'POST':
        form = BannerSlideForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Banner slide added')
            return redirect('panel_banner_list')
    else:
        form = BannerSlideForm(initial={'order': BannerSlide.objects.count()})

    return render(request, 'myapp/panel/banner_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_banner_edit(request, pk):
    slide = get_object_or_404(BannerSlide, pk=pk)

    if request.method == 'POST':
        form = BannerSlideForm(request.POST, request.FILES, instance=slide)
        if form.is_valid():
            form.save()
            messages.success(request, 'Banner slide updated')
            return redirect('panel_banner_list')
    else:
        form = BannerSlideForm(instance=slide)

    return render(request, 'myapp/panel/banner_form.html', {'form': form, 'is_new': False, 'slide': slide})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_banner_delete(request, pk):
    slide = get_object_or_404(BannerSlide, pk=pk)
    if request.method == 'POST':
        slide.delete()
        messages.success(request, 'Banner slide deleted')
    return redirect('panel_banner_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_notification_list(request):
    notifications = Notification.objects.all()
    return render(request, 'myapp/panel/notification_list.html', {'notifications': notifications})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_notification_add(request):
    if request.method == 'POST':
        form = NotificationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification added')
            return redirect('panel_notification_list')
    else:
        form = NotificationForm(initial={'order': Notification.objects.count()})

    return render(request, 'myapp/panel/notification_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_notification_edit(request, pk):
    notification = get_object_or_404(Notification, pk=pk)

    if request.method == 'POST':
        form = NotificationForm(request.POST, request.FILES, instance=notification)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification updated')
            return redirect('panel_notification_edit', pk=notification.pk)
    else:
        form = NotificationForm(instance=notification)

    image_form = NotificationImageForm()
    table_row_form = NotificationTableRowForm(initial={'order': notification.table_rows.count()})
    return render(request, 'myapp/panel/notification_form.html', {
        'form': form,
        'is_new': False,
        'notification': notification,
        'image_form': image_form,
        'table_row_form': table_row_form,
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_notification_delete(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    if request.method == 'POST':
        notification.delete()
        messages.success(request, 'Notification deleted')
    return redirect('panel_notification_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_notification_image_add(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    if request.method == 'POST':
        image_form = NotificationImageForm(request.POST, request.FILES)
        if image_form.is_valid():
            image = image_form.save(commit=False)
            image.notification = notification
            image.save()
            messages.success(request, 'Photo added to the gallery')
        else:
            messages.error(request, 'Could not add that photo — please choose an image file')
    return redirect('panel_notification_edit', pk=notification.pk)


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_notification_image_delete(request, pk, image_pk):
    notification = get_object_or_404(Notification, pk=pk)
    image = get_object_or_404(NotificationImage, pk=image_pk, notification=notification)
    if request.method == 'POST':
        image.delete()
        messages.success(request, 'Photo removed')
    return redirect('panel_notification_edit', pk=notification.pk)


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_notification_table_row_add(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    if request.method == 'POST':
        row_form = NotificationTableRowForm(request.POST)
        if row_form.is_valid():
            row = row_form.save(commit=False)
            row.notification = notification
            row.save()
            messages.success(request, 'Table row added')
        else:
            messages.error(request, 'Could not add that row — please fill in both fields')
    return redirect('panel_notification_edit', pk=notification.pk)


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_notification_table_row_delete(request, pk, row_pk):
    notification = get_object_or_404(Notification, pk=pk)
    row = get_object_or_404(NotificationTableRow, pk=row_pk, notification=notification)
    if request.method == 'POST':
        row.delete()
        messages.success(request, 'Table row removed')
    return redirect('panel_notification_edit', pk=notification.pk)


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_chatbot_list(request):
    settings_obj = ChatbotSettings.load()
    if request.method == 'POST':
        settings_form = ChatbotSettingsForm(request.POST, instance=settings_obj)
        if settings_form.is_valid():
            settings_form.save()
            messages.success(request, 'Chatbot visibility updated')
            return redirect('panel_chatbot_list')
    else:
        settings_form = ChatbotSettingsForm(instance=settings_obj)

    questions = ChatbotQuestion.objects.all()
    return render(request, 'myapp/panel/chatbot_list.html', {'settings_form': settings_form, 'questions': questions})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_chatbot_question_add(request):
    if request.method == 'POST':
        form = ChatbotQuestionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question added')
            return redirect('panel_chatbot_list')
    else:
        form = ChatbotQuestionForm(initial={'order': ChatbotQuestion.objects.count()})

    return render(request, 'myapp/panel/chatbot_question_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_chatbot_question_edit(request, pk):
    question = get_object_or_404(ChatbotQuestion, pk=pk)

    if request.method == 'POST':
        form = ChatbotQuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated')
            return redirect('panel_chatbot_list')
    else:
        form = ChatbotQuestionForm(instance=question)

    return render(request, 'myapp/panel/chatbot_question_form.html', {'form': form, 'is_new': False, 'question': question})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_chatbot_question_delete(request, pk):
    question = get_object_or_404(ChatbotQuestion, pk=pk)
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted')
    return redirect('panel_chatbot_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_hero_section(request):
    hero = HeroSection.load()
    if request.method == 'POST':
        form = HeroSectionForm(request.POST, request.FILES, instance=hero)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hero section updated')
            return redirect('panel_hero_section')
    else:
        form = HeroSectionForm(instance=hero)

    return render(request, 'myapp/panel/hero_section.html', {'form': form, 'hero': hero})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_daily_updates(request):
    current_card = DailyUpdateCard.load(DailyUpdateCard.CURRENT_AFFAIRS)

    if request.method == 'POST':
        current_form = DailyUpdateCardForm(request.POST, request.FILES, instance=current_card)
        if current_form.is_valid():
            current_form.save()
            messages.success(request, 'Current Affairs card updated')
            return redirect('panel_daily_updates')
    else:
        current_form = DailyUpdateCardForm(instance=current_card)

    posts = DailyUpdatePost.objects.filter(category=DailyUpdateCard.CURRENT_AFFAIRS)
    return render(request, 'myapp/panel/daily_updates.html', {
        'current_form': current_form,
        'posts': posts,
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_daily_post_add(request):
    if request.method == 'POST':
        form = DailyUpdatePostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.category = DailyUpdateCard.CURRENT_AFFAIRS
            post.save()
            messages.success(request, 'Current Affairs post added')
            return redirect('panel_daily_updates')
    else:
        form = DailyUpdatePostForm(initial={'news_category': DailyUpdatePost.NEWS_NATIONAL})

    return render(request, 'myapp/panel/daily_post_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_daily_post_edit(request, pk):
    post = get_object_or_404(DailyUpdatePost, pk=pk, category=DailyUpdateCard.CURRENT_AFFAIRS)

    if request.method == 'POST':
        form = DailyUpdatePostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated')
            return redirect('panel_daily_updates')
    else:
        form = DailyUpdatePostForm(instance=post)

    return render(request, 'myapp/panel/daily_post_form.html', {
        'form': form, 'is_new': False, 'post': post, 'table_row_form': DailyUpdatePostTableRowForm(),
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_daily_post_delete(request, pk):
    post = get_object_or_404(DailyUpdatePost, pk=pk, category=DailyUpdateCard.CURRENT_AFFAIRS)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted')
    return redirect('panel_daily_updates')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_daily_post_table_row_add(request, pk):
    post = get_object_or_404(DailyUpdatePost, pk=pk, category=DailyUpdateCard.CURRENT_AFFAIRS)
    if request.method == 'POST':
        row_form = DailyUpdatePostTableRowForm(request.POST)
        if row_form.is_valid():
            row = row_form.save(commit=False)
            row.post = post
            row.save()
            messages.success(request, 'Table row added')
        else:
            messages.error(request, 'Could not add that row — please fill in both fields')
    return redirect('panel_daily_post_edit', pk=post.pk)


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_daily_post_table_row_delete(request, pk, row_pk):
    post = get_object_or_404(DailyUpdatePost, pk=pk, category=DailyUpdateCard.CURRENT_AFFAIRS)
    row = get_object_or_404(DailyUpdatePostTableRow, pk=row_pk, post=post)
    if request.method == 'POST':
        row.delete()
        messages.success(request, 'Table row removed')
    return redirect('panel_daily_post_edit', pk=post.pk)


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_admissions(request):
    registrations = AdmissionRegistration.objects.all()
    week_ago = timezone.now() - timezone.timedelta(days=7)
    stats = {
        'total': registrations.count(),
        'this_week': registrations.filter(created_at__gte=week_ago).count(),
    }
    return render(request, 'myapp/panel/admissions_list.html', {'registrations': registrations, 'stats': stats})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_admission_delete(request, pk):
    registration = get_object_or_404(AdmissionRegistration, pk=pk)
    if request.method == 'POST':
        registration.delete()
        messages.success(request, 'Registration deleted')
    return redirect('panel_admissions')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_contact_messages(request):
    messages_qs = ContactMessage.objects.all()
    if request.method == 'POST' and request.POST.get('action') == 'mark_read':
        ContactMessage.objects.filter(pk=request.POST.get('pk')).update(is_read=True)
        return redirect('panel_contact_messages')
    week_ago = timezone.now() - timezone.timedelta(days=7)
    stats = {
        'total': messages_qs.count(),
        'unread': messages_qs.filter(is_read=False).count(),
        'this_week': messages_qs.filter(created_at__gte=week_ago).count(),
    }
    return render(request, 'myapp/panel/contact_messages_list.html', {'contact_messages': messages_qs, 'stats': stats})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_contact_message_delete(request, pk):
    message_obj = get_object_or_404(ContactMessage, pk=pk)
    if request.method == 'POST':
        message_obj.delete()
        messages.success(request, 'Message deleted')
    return redirect('panel_contact_messages')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_pwa_settings(request):
    pwa = PWASettings.load()
    if request.method == 'POST':
        form = PWASettingsForm(request.POST, request.FILES, instance=pwa)
        if form.is_valid():
            form.save()
            messages.success(request, 'App settings saved')
            return redirect('panel_pwa_settings')
    else:
        form = PWASettingsForm(instance=pwa)

    return render(request, 'myapp/panel/pwa_settings.html', {'form': form, 'pwa': pwa})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_gallery_list(request):
    images = GalleryImage.objects.all()
    return render(request, 'myapp/panel/gallery_list.html', {'images': images})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_gallery_add(request):
    if request.method == 'POST':
        form = GalleryImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Image added')
            return redirect('panel_gallery_list')
    else:
        form = GalleryImageForm(initial={'order': GalleryImage.objects.count()})

    return render(request, 'myapp/panel/gallery_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_gallery_edit(request, pk):
    image = get_object_or_404(GalleryImage, pk=pk)

    if request.method == 'POST':
        form = GalleryImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            messages.success(request, 'Image updated')
            return redirect('panel_gallery_list')
    else:
        form = GalleryImageForm(instance=image)

    return render(request, 'myapp/panel/gallery_form.html', {'form': form, 'is_new': False, 'image': image})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_gallery_delete(request, pk):
    image = get_object_or_404(GalleryImage, pk=pk)
    if request.method == 'POST':
        image.delete()
        messages.success(request, 'Image deleted')
    return redirect('panel_gallery_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_brand_list(request):
    brands = Brand.objects.all()
    return render(request, 'myapp/panel/brand_list.html', {'brands': brands})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_brand_add(request):
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand added')
            return redirect('panel_brand_list')
    else:
        form = BrandForm(initial={'order': Brand.objects.count()})

    return render(request, 'myapp/panel/brand_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_brand_edit(request, pk):
    brand = get_object_or_404(Brand, pk=pk)

    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand updated')
            return redirect('panel_brand_list')
    else:
        form = BrandForm(instance=brand)

    return render(request, 'myapp/panel/brand_form.html', {'form': form, 'is_new': False, 'brand': brand})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_brand_delete(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        brand.delete()
        messages.success(request, 'Brand deleted')
    return redirect('panel_brand_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_category_list(request):
    categories = Category.objects.all()
    return render(request, 'myapp/panel/category_list.html', {'categories': categories})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added')
            return redirect('panel_category_list')
    else:
        form = CategoryForm(initial={'order': Category.objects.count()})

    return render(request, 'myapp/panel/category_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated')
            return redirect('panel_category_list')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'myapp/panel/category_form.html', {'form': form, 'is_new': False, 'category': category})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted')
    return redirect('panel_category_list')


COURSE_TYPE_LABELS = dict(Course.TYPE_CHOICES)


def _course_type_or_404(course_type):
    if course_type not in COURSE_TYPE_LABELS:
        raise Http404


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_course_list(request, course_type):
    _course_type_or_404(course_type)
    courses = Course.objects.filter(course_type=course_type).select_related('category')

    stats = {'total': courses.count()}
    if course_type == Course.TEST_SERIES:
        stats['total_questions'] = Question.objects.filter(course__course_type=course_type).count()
    elif course_type == Course.VIDEO_COURSE:
        courses = courses.prefetch_related('videos')
        stats['total_videos'] = sum(c.published_video_count for c in courses)
    elif course_type == Course.ELIBRARY:
        courses = courses.prefetch_related('documents')

    return render(request, 'myapp/panel/course_list.html', {
        'courses': courses,
        'course_type': course_type,
        'type_label': COURSE_TYPE_LABELS[course_type],
        'stats': stats,
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_course_add(request, course_type):
    _course_type_or_404(course_type)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, course_type=course_type)
        course = form.instance
        course.course_type = course_type
        video_formset = CourseVideoFormSet(request.POST, request.FILES, instance=course, prefix='videos') if course_type == Course.VIDEO_COURSE else None
        document_formset = CourseDocumentFormSet(request.POST, request.FILES, instance=course, prefix='documents') if course_type == Course.ELIBRARY else None
        section_formset = TestSectionFormSet(request.POST, instance=course, prefix='sections') if course_type == Course.TEST_SERIES else None
        form_is_valid = form.is_valid()
        folders_enabled = form_is_valid and form.cleaned_data.get('enable_folders', False)
        uploads_are_valid = folders_enabled or (
            (video_formset is None or video_formset.is_valid())
            and (document_formset is None or document_formset.is_valid())
        )
        sections_are_valid = section_formset is None or section_formset.is_valid()
        if form_is_valid and uploads_are_valid and sections_are_valid:
            course = form.save(commit=False)
            course.course_type = course_type
            course.save()
            if video_formset is not None and not folders_enabled:
                video_formset.instance = course
                video_formset.save()
            if document_formset is not None and not folders_enabled:
                document_formset.instance = course
                document_formset.save()
            if section_formset is not None:
                section_formset.instance = course
                section_formset.save()
            messages.success(request, 'Course added')
            if folders_enabled:
                return redirect('panel_course_content', course_type=course_type, pk=course.pk)
            return redirect('panel_course_list', course_type=course_type)
    else:
        form = CourseForm(initial={'order': Course.objects.filter(course_type=course_type).count()}, course_type=course_type)
        course = Course(course_type=course_type)
        video_formset = CourseVideoFormSet(instance=course, prefix='videos') if course_type == Course.VIDEO_COURSE else None
        document_formset = CourseDocumentFormSet(instance=course, prefix='documents') if course_type == Course.ELIBRARY else None
        section_formset = TestSectionFormSet(instance=course, prefix='sections') if course_type == Course.TEST_SERIES else None

    return render(request, 'myapp/panel/course_form.html', {
        'form': form, 'video_formset': video_formset, 'document_formset': document_formset, 'section_formset': section_formset, 'is_new': True, 'course_type': course_type, 'type_label': COURSE_TYPE_LABELS[course_type],
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_course_edit(request, course_type, pk):
    _course_type_or_404(course_type)
    course = get_object_or_404(Course, pk=pk, course_type=course_type)

    folders_were_enabled = course.enable_folders
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course, course_type=course_type)
        video_formset = CourseVideoFormSet(request.POST, request.FILES, instance=course, prefix='videos') if course_type == Course.VIDEO_COURSE else None
        document_formset = CourseDocumentFormSet(request.POST, request.FILES, instance=course, prefix='documents') if course_type == Course.ELIBRARY else None
        section_formset = TestSectionFormSet(request.POST, instance=course, prefix='sections') if course_type == Course.TEST_SERIES else None
        form_is_valid = form.is_valid()
        folders_enabled = form_is_valid and form.cleaned_data.get('enable_folders', False)
        management_prefix = 'videos' if course_type == Course.VIDEO_COURSE else 'documents'
        has_flat_management_form = f'{management_prefix}-TOTAL_FORMS' in request.POST
        validate_flat_uploads = not folders_enabled and (not folders_were_enabled or has_flat_management_form)
        uploads_are_valid = not validate_flat_uploads or (
            (video_formset is None or video_formset.is_valid())
            and (document_formset is None or document_formset.is_valid())
        )
        sections_are_valid = section_formset is None or section_formset.is_valid()
        if form_is_valid and uploads_are_valid and sections_are_valid:
            course = form.save()
            if video_formset is not None and validate_flat_uploads:
                video_formset.save()
            if document_formset is not None and validate_flat_uploads:
                document_formset.save()
            if section_formset is not None:
                section_formset.save()
            if folders_were_enabled and not course.enable_folders:
                course.videos.update(folder=None)
                course.documents.update(folder=None)
                course.content_folders.all().delete()
            messages.success(request, 'Course updated')
            if course.enable_folders:
                return redirect('panel_course_content', course_type=course_type, pk=course.pk)
            return redirect('panel_course_list', course_type=course_type)
    else:
        form = CourseForm(instance=course, course_type=course_type)
        video_formset = CourseVideoFormSet(instance=course, prefix='videos') if course_type == Course.VIDEO_COURSE else None
        document_formset = CourseDocumentFormSet(instance=course, prefix='documents') if course_type == Course.ELIBRARY else None
        section_formset = TestSectionFormSet(instance=course, prefix='sections') if course_type == Course.TEST_SERIES else None

    return render(request, 'myapp/panel/course_form.html', {
        'form': form, 'video_formset': video_formset, 'document_formset': document_formset, 'section_formset': section_formset, 'is_new': False, 'course': course, 'course_type': course_type, 'type_label': COURSE_TYPE_LABELS[course_type],
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_course_delete(request, course_type, pk):
    _course_type_or_404(course_type)
    course = get_object_or_404(Course, pk=pk, course_type=course_type)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted')
    return redirect('panel_course_list', course_type=course_type)


def _content_course_or_404(course_type, pk):
    if course_type not in (Course.VIDEO_COURSE, Course.ELIBRARY):
        raise Http404
    return get_object_or_404(Course, pk=pk, course_type=course_type)


def _course_content_redirect(course, folder=None):
    if folder:
        return redirect('panel_course_content_folder', course_type=course.course_type, pk=course.pk, folder_pk=folder.pk)
    return redirect('panel_course_content', course_type=course.course_type, pk=course.pk)


def _content_breadcrumbs(folder):
    breadcrumbs = []
    visited = set()
    while folder and folder.pk not in visited:
        visited.add(folder.pk)
        breadcrumbs.append(folder)
        folder = folder.parent
    return list(reversed(breadcrumbs))


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_course_content(request, course_type, pk, folder_pk=None):
    course = _content_course_or_404(course_type, pk)
    if not course.enable_folders:
        messages.error(request, 'Enable folders in the course settings first')
        return redirect('panel_course_edit', course_type=course_type, pk=course.pk)

    current_folder = None
    if folder_pk is not None:
        current_folder = get_object_or_404(
            CourseContentFolder.objects.select_related('parent'),
            pk=folder_pk,
            course=course,
        )

    folder_form = CourseContentFolderForm(
        course=course,
        parent=current_folder,
        initial={'order': CourseContentFolder.objects.filter(course=course, parent=current_folder).count()},
        prefix='folder',
    )
    upload_form_class = CourseVideoForm if course_type == Course.VIDEO_COURSE else CourseDocumentForm
    upload_form = upload_form_class(
        initial={'order': (course.videos if course_type == Course.VIDEO_COURSE else course.documents).filter(folder=current_folder).count()},
        prefix='upload',
    )

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create_folder':
            folder_form = CourseContentFolderForm(
                request.POST,
                course=course,
                parent=current_folder,
                prefix='folder',
            )
            if folder_form.is_valid():
                folder_form.save()
                messages.success(request, 'Folder created. Open it to upload content or create another folder')
                return _course_content_redirect(course, current_folder)
        elif action == 'upload':
            upload_form = upload_form_class(request.POST, request.FILES, prefix='upload')
            if upload_form.is_valid():
                item = upload_form.save(commit=False)
                item.course = course
                item.folder = current_folder
                item.save()
                messages.success(request, 'Video uploaded.' if course_type == Course.VIDEO_COURSE else 'PDF uploaded')
                return _course_content_redirect(course, current_folder)

    child_folders = CourseContentFolder.objects.filter(course=course, parent=current_folder).annotate(
        child_count=Count('subfolders', distinct=True),
        video_count=Count('videos', distinct=True),
        document_count=Count('documents', distinct=True),
    )
    items = course.videos.filter(folder=current_folder) if course_type == Course.VIDEO_COURSE else course.documents.filter(folder=current_folder)
    return render(request, 'myapp/panel/course_content.html', {
        'course': course,
        'course_type': course_type,
        'type_label': COURSE_TYPE_LABELS[course_type],
        'current_folder': current_folder,
        'breadcrumbs': _content_breadcrumbs(current_folder),
        'child_folders': child_folders,
        'items': items,
        'folder_form': folder_form,
        'upload_form': upload_form,
        'content_label': 'video' if course_type == Course.VIDEO_COURSE else 'PDF',
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_course_content_folder_edit(request, course_type, pk, folder_pk):
    course = _content_course_or_404(course_type, pk)
    folder = get_object_or_404(CourseContentFolder, pk=folder_pk, course=course)
    if request.method == 'POST':
        form = CourseContentFolderForm(request.POST, instance=folder, course=course, parent=folder.parent)
        if form.is_valid():
            form.save()
            messages.success(request, 'Folder updated')
            return _course_content_redirect(course, folder)
    else:
        form = CourseContentFolderForm(instance=folder, course=course, parent=folder.parent)
    return render(request, 'myapp/panel/content_folder_form.html', {
        'form': form, 'course': course, 'folder': folder, 'course_type': course_type,
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_course_content_folder_delete(request, course_type, pk, folder_pk):
    course = _content_course_or_404(course_type, pk)
    folder = get_object_or_404(CourseContentFolder, pk=folder_pk, course=course)
    parent = folder.parent
    if request.method == 'POST':
        folder.delete()
        messages.success(request, 'Folder deleted. Its uploaded files were moved to the course root')
    return _course_content_redirect(course, parent)


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_course_content_item_edit(request, course_type, pk, item_pk):
    course = _content_course_or_404(course_type, pk)
    model = CourseVideo if course_type == Course.VIDEO_COURSE else CourseDocument
    form_class = CourseVideoForm if course_type == Course.VIDEO_COURSE else CourseDocumentForm
    item = get_object_or_404(model, pk=item_pk, course=course)
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Content updated')
            return _course_content_redirect(course, item.folder)
    else:
        form = form_class(instance=item)
    return render(request, 'myapp/panel/content_item_form.html', {
        'form': form, 'course': course, 'item': item, 'course_type': course_type,
        'content_label': 'video' if course_type == Course.VIDEO_COURSE else 'PDF',
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_course_content_item_delete(request, course_type, pk, item_pk):
    course = _content_course_or_404(course_type, pk)
    model = CourseVideo if course_type == Course.VIDEO_COURSE else CourseDocument
    item = get_object_or_404(model, pk=item_pk, course=course)
    folder = item.folder
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Content deleted')
    return _course_content_redirect(course, folder)


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_question_list(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, course_type=Course.TEST_SERIES)
    sections = list(course.test_sections.all())
    section_filter = request.GET.get('section', '').strip()
    selected_section_id = None
    show_unassigned = section_filter == 'unassigned'
    questions = course.questions.select_related('section')

    if show_unassigned:
        questions = questions.filter(section__isnull=True)
    elif section_filter.isdigit():
        requested_section_id = int(section_filter)
        if any(section.pk == requested_section_id for section in sections):
            selected_section_id = requested_section_id
            questions = questions.filter(section_id=selected_section_id)
        else:
            section_filter = ''
    else:
        section_filter = ''

    return render(request, 'myapp/panel/question_list.html', {
        'course': course,
        'course_type': course.course_type,
        'questions': questions,
        'sections': sections,
        'section_filter': section_filter,
        'selected_section_id': selected_section_id,
        'show_unassigned': show_unassigned,
        'filter_active': bool(section_filter),
        'filtered_question_count': questions.count(),
        'total_question_count': course.questions.count(),
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_question_add(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, course_type=Course.TEST_SERIES)
    if request.method == 'POST':
        form = QuestionForm(request.POST, course=course)
        if form.is_valid():
            question = form.save(commit=False)
            question.course = course
            question.save()
            messages.success(request, 'Question added')
            return redirect('panel_question_list', course_pk=course.pk)
    else:
        form = QuestionForm(initial={'order': course.questions.count()}, course=course)

    return render(request, 'myapp/panel/question_form.html', {'form': form, 'is_new': True, 'course': course, 'course_type': course.course_type})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_question_edit(request, course_pk, pk):
    course = get_object_or_404(Course, pk=course_pk, course_type=Course.TEST_SERIES)
    question = get_object_or_404(Question, pk=pk, course=course)

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question, course=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated')
            return redirect('panel_question_list', course_pk=course.pk)
    else:
        form = QuestionForm(instance=question, course=course)

    return render(request, 'myapp/panel/question_form.html', {'form': form, 'is_new': False, 'course': course, 'question': question, 'course_type': course.course_type})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_question_delete(request, course_pk, pk):
    course = get_object_or_404(Course, pk=course_pk, course_type=Course.TEST_SERIES)
    question = get_object_or_404(Question, pk=pk, course=course)
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted')
    return redirect('panel_question_list', course_pk=course.pk)


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_razorpay_settings(request):
    settings_obj = RazorpaySettings.load()
    if request.method == 'POST':
        form = RazorpaySettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Razorpay settings saved')
            return redirect('panel_razorpay_settings')
    else:
        form = RazorpaySettingsForm(instance=settings_obj)

    return render(request, 'myapp/panel/razorpay_settings.html', {'form': form, 'settings_obj': settings_obj})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_notification_provider_settings(request):
    settings_obj = NotificationProviderSettings.load()
    test_result = None
    if request.method == 'POST':
        if request.POST.get('action') == 'send_test_otp':
            target = request.POST.get('test_target', '').strip()
            channel = request.POST.get('test_channel', 'email')
            if target:
                ok, detail, otp = send_otp(settings_obj, target, channel)
                test_result = {'ok': ok, 'detail': detail, 'target': target, 'channel': channel}
                if ok:
                    messages.success(request, f'Test OTP sent to {target}. {detail}')
                else:
                    messages.error(request, f'Could not send test OTP. {detail}')
            form = NotificationProviderSettingsForm(instance=settings_obj)
        else:
            form = NotificationProviderSettingsForm(request.POST, instance=settings_obj)
            if form.is_valid():
                form.save()
                messages.success(request, 'SMS & Email settings saved')
                return redirect('panel_notification_provider_settings')
    else:
        form = NotificationProviderSettingsForm(instance=settings_obj)

    return render(request, 'myapp/panel/notification_provider_settings.html', {
        'form': form, 'settings_obj': settings_obj, 'test_result': test_result,
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_sso_settings(request):
    settings_obj = SSOSettings.load()
    if request.method == 'POST':
        form = SSOSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'SSO settings saved')
            return redirect('panel_sso_settings')
    else:
        form = SSOSettingsForm(instance=settings_obj)

    google_redirect_uri = request.build_absolute_uri(reverse('sso_callback', args=['google']))
    facebook_redirect_uri = request.build_absolute_uri(reverse('sso_callback', args=['facebook']))

    return render(request, 'myapp/panel/sso_settings.html', {
        'form': form, 'settings_obj': settings_obj,
        'google_redirect_uri': google_redirect_uri, 'facebook_redirect_uri': facebook_redirect_uri,
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_dropbox_settings(request):
    settings_obj = DropboxSettings.load()

    if request.method == 'POST':
        if request.POST.get('action') == 'backup_now':
            ok, detail = backup_utils.run_full_backup(settings_obj)
            messages.success(request, f'Backup complete. {detail}') if ok else messages.error(request, f'Backup finished with errors. {detail}')
            return redirect('panel_dropbox_settings')

        if request.POST.get('action') == 'restore':
            filename = request.POST.get('filename') or None
            ok, detail = backup_utils.restore_database(settings_obj, filename=filename)
            messages.success(request, detail) if ok else messages.error(request, f'Restore failed: {detail}')
            return redirect('panel_dropbox_settings')

        if request.POST.get('action') == 'delete_all_backups':
            ok, detail = backup_utils.delete_all_backups()
            messages.success(request, detail) if ok else messages.error(request, f'Delete failed: {detail}')
            return redirect('panel_dropbox_settings')

    backups = []
    dropbox_error = None
    if settings_obj.is_configured:
        try:
            backups = backup_utils.list_db_backups()
        except DropboxError as exc:
            dropbox_error = str(exc)

    return render(request, 'myapp/panel/dropbox_settings.html', {
        'settings_obj': settings_obj,
        'backups': backups,
        'dropbox_error': dropbox_error,
        'latest_backup': backups[0] if backups else None,
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_store_product_list(request):
    products = Product.objects.all()
    return render(request, 'myapp/panel/store_product_list.html', {'products': products})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_store_product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added')
            return redirect('panel_store_product_list')
    else:
        form = ProductForm(initial={'order': Product.objects.count()})

    return render(request, 'myapp/panel/store_product_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_store_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated')
            return redirect('panel_store_product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'myapp/panel/store_product_form.html', {'form': form, 'is_new': False, 'product': product})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_store_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted')
    return redirect('panel_store_product_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_store_orders(request):
    orders = StoreOrder.objects.select_related('product', 'user').exclude(status=StoreOrder.STATUS_PENDING)
    return render(request, 'myapp/panel/store_orders.html', {'orders': orders})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_store_order_update(request, pk):
    order = get_object_or_404(StoreOrder, pk=pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method == 'POST':
        form = StoreOrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            if is_ajax:
                return JsonResponse({'ok': True, 'status': order.status, 'status_display': order.get_status_display()})
            messages.success(request, 'Order status updated')
        elif is_ajax:
            return JsonResponse({'ok': False, 'errors': form.errors}, status=400)

    return redirect('panel_store_orders')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_career_job_list(request):
    jobs = JobPosting.objects.all()
    return render(request, 'myapp/panel/career_job_list.html', {'jobs': jobs})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_career_job_add(request):
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job posting added')
            return redirect('panel_career_job_list')
    else:
        form = JobPostingForm(initial={'order': JobPosting.objects.count()})

    return render(request, 'myapp/panel/career_job_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_career_job_edit(request, pk):
    job = get_object_or_404(JobPosting, pk=pk)

    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job posting updated')
            return redirect('panel_career_job_list')
    else:
        form = JobPostingForm(instance=job)

    return render(request, 'myapp/panel/career_job_form.html', {'form': form, 'is_new': False, 'job': job})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_career_job_delete(request, pk):
    job = get_object_or_404(JobPosting, pk=pk)
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job posting deleted')
    return redirect('panel_career_job_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_career_applications(request):
    applications = JobApplication.objects.select_related('job')
    return render(request, 'myapp/panel/career_applications.html', {'applications': applications})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_career_application_delete(request, pk):
    application = get_object_or_404(JobApplication, pk=pk)
    if request.method == 'POST':
        application.delete()
        messages.success(request, 'Application deleted')
    return redirect('panel_career_applications')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_footer_settings(request):
    site_settings_obj = SiteSettings.load()
    if request.method == 'POST':
        form = FooterSettingsForm(request.POST, instance=site_settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Footer settings saved')
            return redirect('panel_footer_settings')
    else:
        form = FooterSettingsForm(instance=site_settings_obj)

    return render(request, 'myapp/panel/footer_settings.html', {'form': form})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_extra_page_list(request):
    pages_by_key = {page.page: page for page in ExtraPage.objects.all()}
    rows = [
        {'key': key, 'label': label, 'page': pages_by_key.get(key)}
        for key, label in ExtraPage.PAGE_CHOICES
    ]
    return render(request, 'myapp/panel/extra_page_list.html', {'rows': rows, 'faq_count': FAQItem.objects.count()})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_extra_page_edit(request, page_key):
    valid_keys = dict(ExtraPage.PAGE_CHOICES)
    if page_key not in valid_keys:
        raise Http404
    page_obj, _ = ExtraPage.objects.get_or_create(page=page_key)

    if request.method == 'POST':
        form = ExtraPageForm(request.POST, instance=page_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'{valid_keys[page_key]} updated')
            return redirect('panel_extra_page_list')
    else:
        form = ExtraPageForm(instance=page_obj)

    return render(request, 'myapp/panel/extra_page_form.html', {'form': form, 'page_obj': page_obj, 'label': valid_keys[page_key]})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_exam_calendar_list(request):
    events = ExamCalendarEvent.objects.all()
    return render(request, 'myapp/panel/exam_calendar_list.html', {'events': events})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_exam_calendar_add(request):
    if request.method == 'POST':
        form = ExamCalendarEventForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam calendar event added')
            return redirect('panel_exam_calendar_list')
    else:
        form = ExamCalendarEventForm(initial={'order': ExamCalendarEvent.objects.count()})

    return render(request, 'myapp/panel/exam_calendar_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_exam_calendar_edit(request, pk):
    event = get_object_or_404(ExamCalendarEvent, pk=pk)

    if request.method == 'POST':
        form = ExamCalendarEventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam calendar event updated')
            return redirect('panel_exam_calendar_list')
    else:
        form = ExamCalendarEventForm(instance=event)

    return render(request, 'myapp/panel/exam_calendar_form.html', {'form': form, 'is_new': False, 'event': event})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_exam_calendar_delete(request, pk):
    event = get_object_or_404(ExamCalendarEvent, pk=pk)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Exam calendar event deleted')
    return redirect('panel_exam_calendar_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_faq_list(request):
    faqs = FAQItem.objects.all()
    return render(request, 'myapp/panel/faq_list.html', {'faqs': faqs})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_faq_add(request):
    if request.method == 'POST':
        form = FAQItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'FAQ added')
            return redirect('panel_faq_list')
    else:
        form = FAQItemForm(initial={'order': FAQItem.objects.count()})

    return render(request, 'myapp/panel/faq_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_faq_edit(request, pk):
    faq = get_object_or_404(FAQItem, pk=pk)

    if request.method == 'POST':
        form = FAQItemForm(request.POST, instance=faq)
        if form.is_valid():
            form.save()
            messages.success(request, 'FAQ updated')
            return redirect('panel_faq_list')
    else:
        form = FAQItemForm(instance=faq)

    return render(request, 'myapp/panel/faq_form.html', {'form': form, 'is_new': False, 'faq': faq})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_faq_delete(request, pk):
    faq = get_object_or_404(FAQItem, pk=pk)
    if request.method == 'POST':
        faq.delete()
        messages.success(request, 'FAQ deleted')
    return redirect('panel_faq_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_homepage_content(request):
    content = HomepageContent.load()
    if request.method == 'POST':
        form = HomepageContentForm(request.POST, request.FILES, instance=content)
        if form.is_valid():
            form.save()
            messages.success(request, 'Homepage content saved')
            return redirect('panel_homepage_content')
    else:
        form = HomepageContentForm(instance=content)

    return render(request, 'myapp/panel/homepage_content.html', {'form': form, 'content': content})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_exam_ticker(request):
    ticker_settings = ExamTickerSettings.load()
    items = ExamTickerItem.objects.all()

    if request.method == 'POST':
        settings_form = ExamTickerSettingsForm(request.POST, instance=ticker_settings)
        item_formset = ExamTickerItemFormSet(request.POST, queryset=items, prefix='items')
        if settings_form.is_valid() and item_formset.is_valid():
            settings_form.save()
            item_formset.save()
            messages.success(request, 'Exam ticker settings saved')
            return redirect('panel_exam_ticker')
    else:
        settings_form = ExamTickerSettingsForm(instance=ticker_settings)
        item_formset = ExamTickerItemFormSet(queryset=items, prefix='items')

    return render(request, 'myapp/panel/exam_ticker.html', {
        'settings_form': settings_form,
        'item_formset': item_formset,
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_result_list(request):
    results = ResultHighlight.objects.all()
    return render(request, 'myapp/panel/result_list.html', {'results': results})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_result_add(request):
    if request.method == 'POST':
        form = ResultHighlightForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Result photo added')
            return redirect('panel_result_list')
    else:
        form = ResultHighlightForm(initial={'order': ResultHighlight.objects.count()})

    return render(request, 'myapp/panel/result_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_result_edit(request, pk):
    result = get_object_or_404(ResultHighlight, pk=pk)

    if request.method == 'POST':
        form = ResultHighlightForm(request.POST, request.FILES, instance=result)
        if form.is_valid():
            form.save()
            messages.success(request, 'Result photo updated')
            return redirect('panel_result_list')
    else:
        form = ResultHighlightForm(instance=result)

    return render(request, 'myapp/panel/result_form.html', {'form': form, 'is_new': False, 'result': result})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_result_delete(request, pk):
    result = get_object_or_404(ResultHighlight, pk=pk)
    if request.method == 'POST':
        result.delete()
        messages.success(request, 'Result photo deleted')
    return redirect('panel_result_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_bundle_list(request):
    bundles = Bundle.objects.all().prefetch_related('courses')
    return render(request, 'myapp/panel/bundle_list.html', {'bundles': bundles})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_bundle_add(request):
    if request.method == 'POST':
        form = BundleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bundle added')
            return redirect('panel_bundle_list')
    else:
        form = BundleForm(initial={'order': Bundle.objects.count()})

    return render(request, 'myapp/panel/bundle_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_bundle_edit(request, pk):
    bundle = get_object_or_404(Bundle, pk=pk)

    if request.method == 'POST':
        form = BundleForm(request.POST, request.FILES, instance=bundle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bundle updated')
            return redirect('panel_bundle_list')
    else:
        form = BundleForm(instance=bundle)

    return render(request, 'myapp/panel/bundle_form.html', {'form': form, 'is_new': False, 'bundle': bundle})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_bundle_delete(request, pk):
    bundle = get_object_or_404(Bundle, pk=pk)
    if request.method == 'POST':
        bundle.delete()
        messages.success(request, 'Bundle deleted')
    return redirect('panel_bundle_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_classroom_list(request):
    classrooms = Classroom.objects.select_related('test_course').annotate(member_count=Count('members'))
    return render(request, 'myapp/panel/classroom_list.html', {'classrooms': classrooms})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_classroom_add(request):
    if request.method == 'POST':
        form = ClassroomForm(request.POST)
        if form.is_valid():
            classroom = form.save()
            messages.success(request, 'Classroom created. Now add students to it')
            return redirect('panel_classroom_students', pk=classroom.pk)
    else:
        form = ClassroomForm()

    return render(request, 'myapp/panel/classroom_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_classroom_edit(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)

    if request.method == 'POST':
        form = ClassroomForm(request.POST, instance=classroom)
        if form.is_valid():
            form.save()
            messages.success(request, 'Classroom updated')
            return redirect('panel_classroom_list')
    else:
        form = ClassroomForm(instance=classroom)

    return render(request, 'myapp/panel/classroom_form.html', {'form': form, 'is_new': False, 'classroom': classroom})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_classroom_delete(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    if request.method == 'POST':
        classroom.delete()
        messages.success(request, 'Classroom deleted')
    return redirect('panel_classroom_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_classroom_students(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    members = classroom.members.select_related('student').order_by('-added_at')

    if request.method == 'POST':
        form = ClassroomAddStudentsForm(request.POST, exclude_ids=members.values_list('student_id', flat=True))
        if form.is_valid():
            for student in form.cleaned_data['students']:
                ClassroomMember.objects.get_or_create(classroom=classroom, student=student)
            messages.success(request, 'Students added')
            return redirect('panel_classroom_students', pk=classroom.pk)
    else:
        form = ClassroomAddStudentsForm(exclude_ids=members.values_list('student_id', flat=True))

    return render(request, 'myapp/panel/classroom_students.html', {'classroom': classroom, 'members': members, 'form': form})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_classroom_member_remove(request, pk, member_pk):
    member = get_object_or_404(ClassroomMember, pk=member_pk, classroom_id=pk)
    if request.method == 'POST':
        member.delete()
        messages.success(request, 'Student removed from classroom')
    return redirect('panel_classroom_students', pk=pk)


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_coupon_list(request):
    coupons = Coupon.objects.all()
    return render(request, 'myapp/panel/coupon_list.html', {'coupons': coupons})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_coupon_add(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon created')
            return redirect('panel_coupon_list')
    else:
        form = CouponForm()

    return render(request, 'myapp/panel/coupon_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_coupon_edit(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)

    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon updated')
            return redirect('panel_coupon_list')
    else:
        form = CouponForm(instance=coupon)

    return render(request, 'myapp/panel/coupon_form.html', {'form': form, 'is_new': False, 'coupon': coupon})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_coupon_delete(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    if request.method == 'POST':
        coupon.delete()
        messages.success(request, 'Coupon deleted')
    return redirect('panel_coupon_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_refer_earn(request):
    codes = ReferralCode.objects.select_related('user').annotate(signup_count=Count('signups'))
    signups = ReferralSignup.objects.select_related('referral_code__user', 'referred_user')
    return render(request, 'myapp/panel/refer_earn.html', {'codes': codes, 'signups': signups})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_certificate_list(request):
    certificates = Certificate.objects.select_related('user')
    return render(request, 'myapp/panel/certificate_list.html', {'certificates': certificates})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_certificate_add(request):
    if request.method == 'POST':
        form = CertificateForm(request.POST)
        if form.is_valid():
            certificate = form.save()
            certificate.image.save(
                f'{certificate.certificate_number}.png',
                generate_certificate_image(certificate),
                save=True,
            )
            messages.success(request, f'Certificate generated and issued to {certificate.recipient_name}')
            return redirect('panel_certificate_list')
    else:
        form = CertificateForm(initial={'issue_date': timezone.localdate()})

    return render(request, 'myapp/panel/certificate_form.html', {'form': form})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_certificate_delete(request, pk):
    certificate = get_object_or_404(Certificate, pk=pk)
    if request.method == 'POST':
        certificate.image.delete(save=False)
        certificate.delete()
        messages.success(request, 'Certificate deleted')
    return redirect('panel_certificate_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_quiz_question_list(request):
    questions = QuizQuestion.objects.all()
    music_form = QuizGameSettingsForm(instance=QuizGameSettings.load())
    return render(request, 'myapp/panel/quiz_question_list.html', {'questions': questions, 'music_form': music_form})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_quiz_music_update(request):
    quiz_settings = QuizGameSettings.load()
    if request.method == 'POST':
        form = QuizGameSettingsForm(request.POST, request.FILES, instance=quiz_settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Background music updated')
    return redirect('panel_quiz_question_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_quiz_question_add(request):
    if request.method == 'POST':
        form = QuizQuestionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question added')
            return redirect('panel_quiz_question_list')
    else:
        form = QuizQuestionForm(initial={'level': QuizQuestion.objects.count() + 1})

    return render(request, 'myapp/panel/quiz_question_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_quiz_question_edit(request, pk):
    question = get_object_or_404(QuizQuestion, pk=pk)

    if request.method == 'POST':
        form = QuizQuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated')
            return redirect('panel_quiz_question_list')
    else:
        form = QuizQuestionForm(instance=question)

    return render(request, 'myapp/panel/quiz_question_form.html', {'form': form, 'is_new': False, 'question': question})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_quiz_question_delete(request, pk):
    question = get_object_or_404(QuizQuestion, pk=pk)
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted')
    return redirect('panel_quiz_question_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_eligibility_criteria_list(request):
    criteria = EligibilityCriteria.objects.all()
    return render(request, 'myapp/panel/eligibility_criteria_list.html', {'criteria': criteria})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_eligibility_criteria_add(request):
    if request.method == 'POST':
        form = EligibilityCriteriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Eligibility criteria added')
            return redirect('panel_eligibility_criteria_list')
    else:
        form = EligibilityCriteriaForm(initial={'order': EligibilityCriteria.objects.count()})

    return render(request, 'myapp/panel/eligibility_criteria_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_eligibility_criteria_edit(request, pk):
    criteria = get_object_or_404(EligibilityCriteria, pk=pk)

    if request.method == 'POST':
        form = EligibilityCriteriaForm(request.POST, instance=criteria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Eligibility criteria updated')
            return redirect('panel_eligibility_criteria_list')
    else:
        form = EligibilityCriteriaForm(instance=criteria)

    return render(request, 'myapp/panel/eligibility_criteria_form.html', {'form': form, 'is_new': False, 'criteria': criteria})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_eligibility_criteria_delete(request, pk):
    criteria = get_object_or_404(EligibilityCriteria, pk=pk)
    if request.method == 'POST':
        criteria.delete()
        messages.success(request, 'Eligibility criteria deleted')
    return redirect('panel_eligibility_criteria_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_eligibility_submissions(request):
    submissions = EligibilitySubmission.objects.select_related('user')
    stats = {
        'total': submissions.count(),
        'this_week': submissions.filter(created_at__gte=timezone.now() - timezone.timedelta(days=7)).count(),
    }
    return render(request, 'myapp/panel/eligibility_submissions.html', {'submissions': submissions, 'stats': stats})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_erp_dashboard(request):
    from datetime import date

    from django.db.models import Sum

    today = date.today()
    month_start = today.replace(day=1)

    total_staff = StaffMember.objects.filter(is_active=True).count()
    present_today = StaffAttendance.objects.filter(date=today, status=StaffAttendance.PRESENT).count()

    pending_fees = FeeInvoice.objects.filter(status=FeeInvoice.STATUS_PENDING)
    pending_fees_total = pending_fees.aggregate(total=Sum('amount'))['total'] or 0

    month_income = Transaction.objects.filter(type=Transaction.INCOME, date__gte=month_start).aggregate(total=Sum('amount'))['total'] or 0
    month_expense = Transaction.objects.filter(type=Transaction.EXPENSE, date__gte=month_start).aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'myapp/panel/erp_dashboard.html', {
        'total_staff': total_staff,
        'present_today': present_today,
        'pending_fees_count': pending_fees.count(),
        'pending_fees_total': pending_fees_total,
        'month_income': month_income,
        'month_expense': month_expense,
        'month_net': month_income - month_expense,
        'recent_transactions': Transaction.objects.all()[:8],
        'overdue_invoices': [inv for inv in pending_fees.select_related('student') if inv.is_overdue][:8],
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_staff_list(request):
    staff = StaffMember.objects.all()
    return render(request, 'myapp/panel/staff_list.html', {'staff': staff})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_staff_add(request):
    if request.method == 'POST':
        form = StaffMemberForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff member added')
            return redirect('panel_staff_list')
    else:
        form = StaffMemberForm()

    return render(request, 'myapp/panel/staff_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_staff_edit(request, pk):
    staff_member = get_object_or_404(StaffMember, pk=pk)

    if request.method == 'POST':
        form = StaffMemberForm(request.POST, request.FILES, instance=staff_member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff member updated')
            return redirect('panel_staff_list')
    else:
        form = StaffMemberForm(instance=staff_member)

    return render(request, 'myapp/panel/staff_form.html', {'form': form, 'is_new': False, 'staff_member': staff_member})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_staff_delete(request, pk):
    staff_member = get_object_or_404(StaffMember, pk=pk)
    if request.method == 'POST':
        staff_member.delete()
        messages.success(request, 'Staff member deleted')
    return redirect('panel_staff_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_attendance(request):
    from datetime import date

    date_str = request.POST.get('date') or request.GET.get('date')
    try:
        selected_date = date.fromisoformat(date_str) if date_str else date.today()
    except ValueError:
        selected_date = date.today()

    staff_list = StaffMember.objects.filter(is_active=True)

    if request.method == 'POST':
        for staff_member in staff_list:
            status = request.POST.get(f'status_{staff_member.pk}')
            if status:
                StaffAttendance.objects.update_or_create(
                    staff=staff_member, date=selected_date, defaults={'status': status},
                )
        messages.success(request, f'Attendance saved for {selected_date:%d %b %Y}')
        return redirect(f"{reverse('panel_attendance')}?date={selected_date.isoformat()}")

    existing = {a.staff_id: a.status for a in StaffAttendance.objects.filter(date=selected_date)}
    rows = [{'staff': s, 'status': existing.get(s.pk, StaffAttendance.PRESENT)} for s in staff_list]

    return render(request, 'myapp/panel/attendance.html', {
        'rows': rows,
        'selected_date': selected_date,
        'status_choices': StaffAttendance.STATUS_CHOICES,
    })


def _parse_month(value):
    from datetime import date

    try:
        year_str, month_str = value.split('-')
        return date(int(year_str), int(month_str), 1)
    except (ValueError, AttributeError, TypeError):
        return None


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_payroll_list(request):
    from calendar import monthrange

    selected_month = _parse_month(request.GET.get('month')) or timezone.localdate().replace(day=1)
    month_end = selected_month.replace(day=monthrange(selected_month.year, selected_month.month)[1])

    staff_list = StaffMember.objects.filter(is_active=True)
    payslips = {p.staff_id: p for p in StaffSalaryPayment.objects.filter(month=selected_month)}
    absent_counts = dict(
        StaffAttendance.objects.filter(
            date__gte=selected_month, date__lte=month_end, status=StaffAttendance.ABSENT,
        ).values_list('staff_id').annotate(count=Count('id'))
    )

    rows = [
        {
            'staff': staff_member,
            'absent_days': absent_counts.get(staff_member.pk, 0),
            'payslip': payslips.get(staff_member.pk),
        }
        for staff_member in staff_list
    ]

    stats = {
        'generated_count': len(payslips),
        'pending_count': sum(1 for p in payslips.values() if p.status == StaffSalaryPayment.STATUS_PENDING),
        'total_net': sum((p.net_amount for p in payslips.values()), Decimal('0')),
    }

    return render(request, 'myapp/panel/payroll_list.html', {
        'rows': rows, 'selected_month': selected_month, 'stats': stats,
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_payroll_generate(request):
    if request.method != 'POST':
        return redirect('panel_payroll_list')

    from calendar import monthrange

    selected_month = _parse_month(request.POST.get('month'))
    if not selected_month:
        messages.error(request, 'Choose a valid month first')
        return redirect('panel_payroll_list')

    month_end = selected_month.replace(day=monthrange(selected_month.year, selected_month.month)[1])
    staff_qs = StaffMember.objects.filter(is_active=True)
    staff_id = request.POST.get('staff_id')
    if staff_id:
        staff_qs = staff_qs.filter(pk=staff_id)

    generated = 0
    for staff_member in staff_qs:
        absent_days = StaffAttendance.objects.filter(
            staff=staff_member, date__gte=selected_month, date__lte=month_end, status=StaffAttendance.ABSENT,
        ).count()
        daily_rate = (staff_member.salary / 30) if staff_member.salary else Decimal('0')
        deduction = (daily_rate * absent_days).quantize(Decimal('0.01'))
        existing = StaffSalaryPayment.objects.filter(staff=staff_member, month=selected_month).first()
        bonus = existing.bonus if existing else Decimal('0')
        StaffSalaryPayment.objects.update_or_create(
            staff=staff_member, month=selected_month,
            defaults={
                'basic_salary': staff_member.salary,
                'absent_days': absent_days,
                'deductions': deduction,
                'bonus': bonus,
                'net_amount': staff_member.salary - deduction + bonus,
            },
        )
        generated += 1

    messages.success(request, f'Payslip{"s" if generated != 1 else ""} generated for {generated} staff member{"s" if generated != 1 else ""} — {selected_month:%B %Y}')
    return redirect(f"{reverse('panel_payroll_list')}?month={selected_month:%Y-%m}")


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_payroll_edit(request, pk):
    payslip = get_object_or_404(StaffSalaryPayment, pk=pk)
    next_url = _safe_next(request, '')

    if request.method == 'POST':
        form = StaffSalaryPaymentForm(request.POST, instance=payslip)
        if form.is_valid():
            payslip = form.save(commit=False)
            payslip.net_amount = payslip.basic_salary - payslip.deductions + payslip.bonus
            payslip.save()
            messages.success(request, 'Payslip updated')
            return redirect(next_url or f"{reverse('panel_payroll_list')}?month={payslip.month:%Y-%m}")
    else:
        form = StaffSalaryPaymentForm(instance=payslip)

    return render(request, 'myapp/panel/payroll_form.html', {'form': form, 'payslip': payslip, 'next': next_url})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_payroll_mark_paid(request, pk):
    payslip = get_object_or_404(StaffSalaryPayment, pk=pk)
    if request.method == 'POST':
        payslip.status = StaffSalaryPayment.STATUS_PAID
        payslip.paid_on = timezone.now().date()
        payslip.payment_mode = request.POST.get('payment_mode') or payslip.payment_mode or 'cash'
        payslip.save()
        messages.success(request, 'Payslip marked as paid')
    return redirect(f"{reverse('panel_payroll_list')}?month={payslip.month:%Y-%m}")


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_payroll_delete(request, pk):
    payslip = get_object_or_404(StaffSalaryPayment, pk=pk)
    month = payslip.month
    if request.method == 'POST':
        payslip.delete()
        messages.success(request, 'Payslip deleted')
    return redirect(f"{reverse('panel_payroll_list')}?month={month:%Y-%m}")


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_student_attendance(request):
    from datetime import date

    date_str = request.POST.get('date') or request.GET.get('date')
    try:
        selected_date = date.fromisoformat(date_str) if date_str else date.today()
    except ValueError:
        selected_date = date.today()

    search = (request.GET.get('q') or request.POST.get('q') or '').strip()
    students = _registered_students().filter(is_active=True)
    if search:
        students = students.filter(Q(name__icontains=search) | Q(email__icontains=search) | Q(number__icontains=search))
    students = students.order_by('name')

    if request.method == 'POST':
        for student in students:
            status = request.POST.get(f'status_{student.pk}')
            if status:
                StudentAttendance.objects.update_or_create(
                    student=student, date=selected_date, defaults={'status': status},
                )
        messages.success(request, f'Attendance saved for {selected_date:%d %b %Y}')
        redirect_url = f"{reverse('panel_student_attendance')}?date={selected_date.isoformat()}"
        if search:
            redirect_url += f'&q={search}'
        return redirect(redirect_url)

    existing = {a.student_id: a.status for a in StudentAttendance.objects.filter(date=selected_date)}
    rows = [{'student': s, 'status': existing.get(s.pk, StudentAttendance.PRESENT)} for s in students]

    return render(request, 'myapp/panel/student_attendance.html', {
        'rows': rows,
        'selected_date': selected_date,
        'status_choices': StudentAttendance.STATUS_CHOICES,
        'search': search,
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_fee_list(request):
    from django.db.models import Sum

    invoices = FeeInvoice.objects.select_related('student')
    stats = {
        'pending_count': invoices.filter(status=FeeInvoice.STATUS_PENDING).count(),
        'pending_total': invoices.filter(status=FeeInvoice.STATUS_PENDING).aggregate(total=Sum('amount'))['total'] or 0,
        'paid_total': invoices.filter(status=FeeInvoice.STATUS_PAID).aggregate(total=Sum('amount'))['total'] or 0,
    }
    return render(request, 'myapp/panel/fee_list.html', {'invoices': invoices, 'stats': stats})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_fee_add(request):
    next_url = _safe_next(request, '')
    if request.method == 'POST':
        form = FeeInvoiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fee invoice created')
            return redirect(next_url or 'panel_fee_list')
    else:
        initial = {}
        student_id = request.GET.get('student')
        if student_id:
            initial['student'] = student_id
        form = FeeInvoiceForm(initial=initial)

    return render(request, 'myapp/panel/fee_form.html', {'form': form, 'is_new': True, 'next': next_url})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_fee_edit(request, pk):
    invoice = get_object_or_404(FeeInvoice, pk=pk)
    next_url = _safe_next(request, '')

    if request.method == 'POST':
        form = FeeInvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fee invoice updated')
            return redirect(next_url or 'panel_fee_list')
    else:
        form = FeeInvoiceForm(instance=invoice)

    return render(request, 'myapp/panel/fee_form.html', {'form': form, 'is_new': False, 'invoice': invoice, 'next': next_url})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_fee_delete(request, pk):
    invoice = get_object_or_404(FeeInvoice, pk=pk)
    next_url = _safe_next(request, 'panel_fee_list')
    if request.method == 'POST':
        invoice.delete()
        messages.success(request, 'Fee invoice deleted')
    return redirect(next_url)


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_fee_mark_paid(request, pk):
    invoice = get_object_or_404(FeeInvoice, pk=pk)
    next_url = _safe_next(request, 'panel_fee_list')
    if request.method == 'POST':
        invoice.status = FeeInvoice.STATUS_PAID
        invoice.paid_on = timezone.now().date()
        invoice.payment_mode = request.POST.get('payment_mode') or invoice.payment_mode or 'cash'
        invoice.save()
        messages.success(request, 'Invoice marked as paid')
    return redirect(next_url)


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_student_fee_ledger(request, pk):
    student = get_object_or_404(_registered_students(), pk=pk)
    invoices = student.fee_invoices.all()
    stats = {
        'pending_count': invoices.filter(status=FeeInvoice.STATUS_PENDING).count(),
        'pending_total': invoices.filter(status=FeeInvoice.STATUS_PENDING).aggregate(total=Sum('amount'))['total'] or 0,
        'paid_total': invoices.filter(status=FeeInvoice.STATUS_PAID).aggregate(total=Sum('amount'))['total'] or 0,
    }
    return render(request, 'myapp/panel/student_fee_ledger.html', {
        'student': student, 'invoices': invoices, 'stats': stats,
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_account_list(request):
    from django.db.models import Sum

    transactions = Transaction.objects.all()
    stats = {
        'total_income': transactions.filter(type=Transaction.INCOME).aggregate(total=Sum('amount'))['total'] or 0,
        'total_expense': transactions.filter(type=Transaction.EXPENSE).aggregate(total=Sum('amount'))['total'] or 0,
    }
    stats['net'] = stats['total_income'] - stats['total_expense']
    return render(request, 'myapp/panel/account_list.html', {'transactions': transactions, 'stats': stats})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_account_add(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction recorded')
            return redirect('panel_account_list')
    else:
        form = TransactionForm()

    return render(request, 'myapp/panel/account_form.html', {'form': form})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_account_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted')
    return redirect('panel_account_list')
