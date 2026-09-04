/* ============================================================
   Manjunath Academy — behaviour
   1. Sliding advertisement banner (autoplay, dots, arrows, swipe)
   2. Mobile menu
   3. Header shadow on scroll + active nav link
   4. Site language switcher
   ============================================================ */

/* ---------- Language switcher: dictionary + apply/switch logic ---------- */
var SITE_I18N = {
  hi: {
    nav_home: 'होम', nav_courses: 'कोर्स', nav_test_series: 'टेस्ट सीरीज़', nav_quiz_game: 'क्विज़ गेम',
    nav_estore: 'ई-स्टोर', nav_results: 'परिणाम', nav_about: 'हमारे बारे में', nav_contact: 'संपर्क करें',
    nav_more: 'और', nav_video_courses: 'वीडियो कोर्स', nav_elibrary: 'ई-लाइब्रेरी',
    nav_eligibility: 'पात्रता जाँच', nav_careers: 'करियर', nav_contact_us: 'संपर्क करें',
    nav_gallery: 'गैलरी', nav_login: 'लॉग इन', nav_join_free: 'मुफ़्त में जुड़ें', nav_join_now: 'अभी जुड़ें',
    drop_admin_panel: 'एडमिन पैनल', drop_update_account: 'खाता विवरण अपडेट करें',
    drop_purchases: 'मेरी खरीदारी', drop_results: 'परिणाम', drop_coupons: 'मेरे कूपन', drop_certificates: 'मेरे प्रमाणपत्र',
    drop_fees_attendance: 'फीस और उपस्थिति',
    drop_refer_earn: 'रेफ़र करें और कमाएँ', drop_classrooms: 'मेरी क्लासरूम', drop_logout: 'लॉग आउट',
    footer_courses: 'कोर्स', footer_ssc_railways: 'एसएससी और रेलवे', footer_banking: 'बैंकिंग', footer_neet_jee: 'नीट और जेईई',
    footer_test_series: 'टेस्ट सीरीज़', footer_resources: 'संसाधन', footer_pyq: 'पिछले वर्षों के प्रश्नपत्र',
    footer_current_affairs: 'करेंट अफेयर्स', footer_exam_calendar: 'परीक्षा कैलेंडर', footer_eligibility: 'पात्रता जाँच',
    footer_reach_us: 'हमसे संपर्क करें', footer_hours: 'सोम–शनि, सुबह 8 – रात 8', footer_privacy: 'गोपनीयता नीति',
    footer_terms: 'नियम व शर्तें', footer_refund: 'रिफंड और रद्दीकरण', footer_shipping: 'शिपिंग और डिलीवरी',
    footer_disclaimer: 'अस्वीकरण', footer_faq: 'सामान्य प्रश्न', footer_contact_us: 'संपर्क करें', footer_demo: 'डेमो साइट',
    idx_eyebrow_courses: '&lt;/&gt; परीक्षा श्रेणियाँ', idx_title_courses: 'हमारे लोकप्रिय <span class="text-orange">कोर्स</span>',
    idx_title_test_series: 'सभी <span class="text-orange">टेस्ट सीरीज़</span> देखें',
    idx_eyebrow_video: '🎬 वीडियो कोर्स एक्सप्लोर करें', idx_title_video: 'विशेषज्ञ शिक्षकों से सीखें, <span class="text-orange">वीडियो पर</span>',
    idx_eyebrow_elibrary: '📚 डिजिटल ई-लाइब्रेरी', idx_title_elibrary: 'आपकी संपूर्ण <span class="text-orange">डिजिटल लाइब्रेरी</span>',
    idx_eyebrow_quiz: '🎮 खेलें और सीखें', idx_title_quiz: 'क्विज़ ज़ोन',
    idx_eyebrow_gallery: '📸 गैलरी', idx_eyebrow_about: 'हमारे बारे में',
    idx_eyebrow_eligibility: '🎯 पात्रता जाँच', idx_title_eligibility: 'आप किन परीक्षाओं के लिए <span class="text-orange">पात्र हैं?</span>',
    idx_eyebrow_estore: '🛒 ई-स्टोर', idx_title_estore: 'नोट्स, किताबें और <span class="text-orange">मर्चेंडाइज़</span>',
    idx_eyebrow_careers: '💼 करियर', idx_title_careers: 'हमारे साथ <span class="text-orange">काम करें</span>',
    idx_eyebrow_admission: '🏫 ऑफ़लाइन प्रवेश', idx_title_admission: 'ऑफ़लाइन बैच के लिए <span class="text-orange">रजिस्टर करें</span>',
    idx_eyebrow_contact: '📞 संपर्क करें', idx_title_contact: 'एक काउंसलर से <span class="text-orange">बात करें</span>',
    btn_enroll_now: 'नामांकन करें →', btn_view_course: 'कोर्स देखें →', btn_view_book: 'किताब देखें →',
    btn_buy_now: 'अभी खरीदें', btn_out_of_stock: 'स्टॉक ख़त्म',
    idx_eyebrow_trusted: 'हमारे भरोसेमंद पार्टनर्स', idx_eyebrow_daily: 'दैनिक अपडेट',
    idx_daily_quiz_title: 'पढ़ो और जीतो<br>क्विज़ गेम',
    idx_daily_quiz_caption: 'एक बार में एक सवाल हल करके मनी लैडर चढ़ें — हर हफ़्ते नए सवाल जोड़े जाते हैं।',
    idx_sub_courses: 'विशेषज्ञ मार्गदर्शन और संपूर्ण अध्ययन सामग्री के साथ सभी प्रमुख सरकारी परीक्षाओं के लिए व्यापक कोर्स।',
    btn_view_all_bundles: 'सभी बंडल देखें →',
    idx_sub_video: 'व्यवस्थित कोर्स जिनमें कई रिकॉर्ड किए गए पाठ हैं — रोकें, दोबारा देखें और अपनी गति से पूरा करें।',
    btn_view_all_video: 'सभी वीडियो कोर्स देखें →',
    idx_sub_elibrary: 'व्यवस्थित PDF संग्रह, नोट्स, किताबें और पिछले वर्षों की सामग्री एक ही जगह पाएं।',
    btn_browse_elibrary: 'पूरी ई-लाइब्रेरी देखें →',
    idx_test_series_label: 'टेस्ट सीरीज़', ts_tab_all: 'सभी', btn_view_details: 'विवरण देखें →',
    idx_sub_quiz: 'खुद को परखने के दो तरीके — त्वरित विषय क्विज़, या पूरा KBC-स्टाइल चैलेंज।',
    kbc_tag: 'चैंपियन की कुर्सी', kbc_title: 'पढ़ो और जीतो',
    kbc_desc: 'हमारा अपना कौन बनेगा करोड़पति–स्टाइल क्विज़ — लाइफलाइन और हमारे मूल संगीत के साथ एक बार में एक सवाल हल करके मनी लैडर चढ़ें।',
    kbc_champion: 'चैंपियन', kbc_halfway: 'आधा रास्ता', kbc_start: 'शुरू',
    kbc_5050: '50-50', kbc_audience: 'ऑडियंस पोल', kbc_skip: 'सवाल छोड़ें', btn_play_now: '▶ अभी खेलें',
    quiz_card1_title: 'दैनिक जीके क्विज़', quiz_card1_desc: '10 सवाल, 5 मिनट, हर सुबह नया सेट।',
    quiz_card2_title: 'गणित स्पीड राउंड', quiz_card2_desc: '15 तेज़ गणना सवालों में समय को मात दें।',
    quiz_card3_title: 'करेंट अफेयर्स क्विज़', quiz_card3_desc: 'इस हफ़्ते की खबरें, 20 सवालों के क्विज़ में।',
    quiz_card4_title: 'रीज़निंग चैलेंज', quiz_card4_desc: 'पहेलियाँ और सीटिंग अरेंजमेंट सवाल, समय सीमा के साथ।',
    btn_know_faculty: '🎓 अपने फैकल्टी को जानें',
    idx_admission_desc: 'इसे एक बार भरें और हमारी एडमिशन टीम 24 घंटों के भीतर लखनऊ सेंटर में आपकी सीट पक्की करने के लिए कॉल करेगी।',
    admission_point1: 'छोटे बैच, अधिकतम 60 छात्र', admission_point2: 'लाइब्रेरी और स्टडी हॉल, सुबह 7 – रात 9',
    admission_point3: 'साप्ताहिक टेस्ट, साथ में एक रिपोर्ट जिस पर आप काम कर सकें',
    admission_label_name: 'पूरा नाम', admission_placeholder_name: 'आपका नाम',
    admission_label_phone: 'फ़ोन नंबर', admission_placeholder_phone: '10 अंकों का मोबाइल नंबर',
    admission_label_course: 'कोर्स', admission_placeholder_course: 'जैसे SSC GD, बैंकिंग और इंश्योरेंस',
    admission_label_batch: 'पसंदीदा बैच', admission_batch_morning: 'सुबह', admission_batch_afternoon: 'दोपहर', admission_batch_evening: 'शाम',
    btn_submit_registration: 'रजिस्ट्रेशन सबमिट करें',
    admission_error: 'कुछ गलत हो गया — कृपया अपनी जानकारी जांचें और फिर से प्रयास करें।',
    admission_success: 'धन्यवाद — हमारी एडमिशन टीम 24 घंटों के भीतर आपको कॉल करेगी।',
  },
  kn: {
    nav_home: 'ಮುಖಪುಟ', nav_courses: 'ಕೋರ್ಸ್‌ಗಳು', nav_test_series: 'ಟೆಸ್ಟ್ ಸೀರೀಸ್', nav_quiz_game: 'ಕ್ವಿಜ್ ಗೇಮ್',
    nav_estore: 'ಇ-ಸ್ಟೋರ್', nav_results: 'ಫಲಿತಾಂಶಗಳು', nav_about: 'ನಮ್ಮ ಬಗ್ಗೆ', nav_contact: 'ಸಂಪರ್ಕಿಸಿ',
    nav_more: 'ಇನ್ನಷ್ಟು', nav_video_courses: 'ವೀಡಿಯೊ ಕೋರ್ಸ್‌ಗಳು', nav_elibrary: 'ಇ-ಲೈಬ್ರರಿ',
    nav_eligibility: 'ಅರ್ಹತಾ ಪರಿಶೀಲನೆ', nav_careers: 'ವೃತ್ತಿಜೀವನ', nav_contact_us: 'ಸಂಪರ್ಕಿಸಿ',
    nav_gallery: 'ಗ್ಯಾಲರಿ', nav_login: 'ಲಾಗಿನ್', nav_join_free: 'ಉಚಿತವಾಗಿ ಸೇರಿ', nav_join_now: 'ಈಗ ಸೇರಿ',
    drop_admin_panel: 'ಅಡ್ಮಿನ್ ಪ್ಯಾನಲ್', drop_update_account: 'ಖಾತೆ ವಿವರಗಳನ್ನು ನವೀಕರಿಸಿ',
    drop_purchases: 'ನನ್ನ ಖರೀದಿಗಳು', drop_results: 'ಫಲಿತಾಂಶಗಳು', drop_coupons: 'ನನ್ನ ಕೂಪನ್‌ಗಳು', drop_certificates: 'ನನ್ನ ಪ್ರಮಾಣಪತ್ರಗಳು',
    drop_fees_attendance: 'ಶುಲ್ಕ ಮತ್ತು ಹಾಜರಾತಿ',
    drop_refer_earn: 'ರೆಫರ್ ಮಾಡಿ ಗಳಿಸಿ', drop_classrooms: 'ನನ್ನ ತರಗತಿಗಳು', drop_logout: 'ಲಾಗ್ ಔಟ್',
    footer_courses: 'ಕೋರ್ಸ್‌ಗಳು', footer_ssc_railways: 'ಎಸ್‌ಎಸ್‌ಸಿ ಮತ್ತು ರೈಲ್ವೆ', footer_banking: 'ಬ್ಯಾಂಕಿಂಗ್', footer_neet_jee: 'ನೀಟ್ ಮತ್ತು ಜೆಇಇ',
    footer_test_series: 'ಟೆಸ್ಟ್ ಸೀರೀಸ್', footer_resources: 'ಸಂಪನ್ಮೂಲಗಳು', footer_pyq: 'ಹಿಂದಿನ ವರ್ಷದ ಪ್ರಶ್ನೆ ಪತ್ರಿಕೆಗಳು',
    footer_current_affairs: 'ಪ್ರಚಲಿತ ವಿದ್ಯಮಾನಗಳು', footer_exam_calendar: 'ಪರೀಕ್ಷಾ ಕ್ಯಾಲೆಂಡರ್', footer_eligibility: 'ಅರ್ಹತಾ ಪರಿಶೀಲನೆ',
    footer_reach_us: 'ನಮ್ಮನ್ನು ಸಂಪರ್ಕಿಸಿ', footer_hours: 'ಸೋಮ–ಶನಿ, ಬೆಳಿಗ್ಗೆ 8 – ರಾತ್ರಿ 8', footer_privacy: 'ಗೌಪ್ಯತಾ ನೀತಿ',
    footer_terms: 'ನಿಯಮಗಳು ಮತ್ತು ಷರತ್ತುಗಳು', footer_refund: 'ಮರುಪಾವತಿ ಮತ್ತು ರದ್ದತಿ', footer_shipping: 'ಶಿಪ್ಪಿಂಗ್ ಮತ್ತು ಡೆಲಿವರಿ',
    footer_disclaimer: 'ಹಕ್ಕು ನಿರಾಕರಣೆ', footer_faq: 'ಪದೇ ಪದೇ ಕೇಳುವ ಪ್ರಶ್ನೆಗಳು', footer_contact_us: 'ಸಂಪರ್ಕಿಸಿ', footer_demo: 'ಡೆಮೊ ಸೈಟ್',
    idx_eyebrow_courses: '&lt;/&gt; ಪರೀಕ್ಷಾ ವಿಭಾಗಗಳು', idx_title_courses: 'ನಮ್ಮ ಜನಪ್ರಿಯ <span class="text-orange">ಕೋರ್ಸ್‌ಗಳು</span>',
    idx_title_test_series: 'ಎಲ್ಲಾ <span class="text-orange">ಟೆಸ್ಟ್ ಸೀರೀಸ್</span> ನೋಡಿ',
    idx_eyebrow_video: '🎬 ವೀಡಿಯೊ ಕೋರ್ಸ್‌ಗಳನ್ನು ಅನ್ವೇಷಿಸಿ', idx_title_video: 'ತಜ್ಞ ಶಿಕ್ಷಕರಿಂದ ಕಲಿಯಿರಿ, <span class="text-orange">ವೀಡಿಯೊದಲ್ಲಿ</span>',
    idx_eyebrow_elibrary: '📚 ಡಿಜಿಟಲ್ ಇ-ಲೈಬ್ರರಿ', idx_title_elibrary: 'ನಿಮ್ಮ ಸಂಪೂರ್ಣ <span class="text-orange">ಡಿಜಿಟಲ್ ಲೈಬ್ರರಿ</span>',
    idx_eyebrow_quiz: '🎮 ಆಡಿ ಮತ್ತು ಕಲಿಯಿರಿ', idx_title_quiz: 'ಕ್ವಿಜ್ ಝೋನ್',
    idx_eyebrow_gallery: '📸 ಗ್ಯಾಲರಿ', idx_eyebrow_about: 'ನಮ್ಮ ಬಗ್ಗೆ',
    idx_eyebrow_eligibility: '🎯 ಅರ್ಹತಾ ಪರಿಶೀಲನೆ', idx_title_eligibility: 'ನೀವು ಯಾವ ಪರೀಕ್ಷೆಗಳಿಗೆ <span class="text-orange">ಅರ್ಹರು?</span>',
    idx_eyebrow_estore: '🛒 ಇ-ಸ್ಟೋರ್', idx_title_estore: 'ನೋಟ್ಸ್, ಪುಸ್ತಕಗಳು ಮತ್ತು <span class="text-orange">ಮರ್ಚೆಂಡೈಸ್</span>',
    idx_eyebrow_careers: '💼 ವೃತ್ತಿಜೀವನ', idx_title_careers: 'ನಮ್ಮೊಂದಿಗೆ <span class="text-orange">ಕೆಲಸ ಮಾಡಿ</span>',
    idx_eyebrow_admission: '🏫 ಆಫ್‌ಲೈನ್ ಪ್ರವೇಶ', idx_title_admission: 'ಆಫ್‌ಲೈನ್ ಬ್ಯಾಚ್‌ಗೆ <span class="text-orange">ನೋಂದಣಿ ಮಾಡಿ</span>',
    idx_eyebrow_contact: '📞 ಸಂಪರ್ಕಿಸಿ', idx_title_contact: 'ಕೌನ್ಸೆಲರ್ ಜೊತೆ <span class="text-orange">ಮಾತನಾಡಿ</span>',
    btn_enroll_now: 'ನೋಂದಣಿ ಮಾಡಿ →', btn_view_course: 'ಕೋರ್ಸ್ ನೋಡಿ →', btn_view_book: 'ಪುಸ್ತಕ ನೋಡಿ →',
    btn_buy_now: 'ಈಗ ಖರೀದಿಸಿ', btn_out_of_stock: 'ಸ್ಟಾಕ್ ಮುಗಿದಿದೆ',
    idx_eyebrow_trusted: 'ನಮ್ಮ ವಿಶ್ವಾಸಾರ್ಹ ಪಾಲುದಾರರು', idx_eyebrow_daily: 'ದೈನಂದಿನ ಅಪ್‌ಡೇಟ್‌ಗಳು',
    idx_daily_quiz_title: 'ಪಢೋ ಔರ್ ಜೀತೋ<br>ಕ್ವಿಜ್ ಗೇಮ್',
    idx_daily_quiz_caption: 'ಒಂದೊಂದೇ ಪ್ರಶ್ನೆಗೆ ಉತ್ತರಿಸುತ್ತಾ ಹಣದ ಏಣಿಯನ್ನು ಏರಿರಿ — ಪ್ರತಿ ವಾರ ಹೊಸ ಪ್ರಶ್ನೆಗಳು ಸೇರಿಸಲಾಗುತ್ತವೆ.',
    idx_sub_courses: 'ಪರಿಣತ ಮಾರ್ಗದರ್ಶನ ಮತ್ತು ಸಂಪೂರ್ಣ ಅಧ್ಯಯನ ಸಾಮಗ್ರಿಯೊಂದಿಗೆ ಎಲ್ಲಾ ಪ್ರಮುಖ ಸರ್ಕಾರಿ ಪರೀಕ್ಷೆಗಳಿಗೆ ಸಮಗ್ರ ಕೋರ್ಸ್‌ಗಳು.',
    btn_view_all_bundles: 'ಎಲ್ಲಾ ಬಂಡಲ್‌ಗಳನ್ನು ನೋಡಿ →',
    idx_sub_video: 'ನೀವು ವಿರಾಮಗೊಳಿಸಿ, ಮತ್ತೆ ವೀಕ್ಷಿಸಿ ಮತ್ತು ನಿಮ್ಮ ವೇಗದಲ್ಲಿ ಪೂರ್ಣಗೊಳಿಸಬಹುದಾದ ಅನೇಕ ರೆಕಾರ್ಡ್ ಮಾಡಿದ ಪಾಠಗಳ ರಚನಾತ್ಮಕ ಕೋರ್ಸ್‌ಗಳು.',
    btn_view_all_video: 'ಎಲ್ಲಾ ವೀಡಿಯೊ ಕೋರ್ಸ್‌ಗಳನ್ನು ನೋಡಿ →',
    idx_sub_elibrary: 'ಸಂಘಟಿತ PDF ಸಂಗ್ರಹಗಳು, ಟಿಪ್ಪಣಿಗಳು, ಪುಸ್ತಕಗಳು ಮತ್ತು ಹಿಂದಿನ ವರ್ಷದ ಸಂಪನ್ಮೂಲಗಳನ್ನು ಒಂದೇ ಸ್ಥಳದಲ್ಲಿ ಪಡೆಯಿರಿ.',
    btn_browse_elibrary: 'ಸಂಪೂರ್ಣ ಇ-ಲೈಬ್ರರಿ ಬ್ರೌಸ್ ಮಾಡಿ →',
    idx_test_series_label: 'ಟೆಸ್ಟ್ ಸೀರೀಸ್', ts_tab_all: 'ಎಲ್ಲಾ', btn_view_details: 'ವಿವರಗಳನ್ನು ನೋಡಿ →',
    idx_sub_quiz: 'ನಿಮ್ಮನ್ನು ಪರೀಕ್ಷಿಸಿಕೊಳ್ಳಲು ಎರಡು ಮಾರ್ಗಗಳು — ತ್ವರಿತ ವಿಷಯ ಕ್ವಿಜ್‌ಗಳು, ಅಥವಾ ಸಂಪೂರ್ಣ KBC-ಶೈಲಿಯ ಸವಾಲು.',
    kbc_tag: 'ಚಾಂಪಿಯನ್ ಕುರ್ಚಿ', kbc_title: 'ಪಢೋ ಔರ್ ಜೀತೋ',
    kbc_desc: 'ನಮ್ಮದೇ ಆದ ಕೌನ್ ಬನೇಗಾ ಕರೋಡ್‌ಪತಿ–ಶೈಲಿಯ ಕ್ವಿಜ್ — ಲೈಫ್‌ಲೈನ್‌ಗಳು ಮತ್ತು ನಮ್ಮ ಸ್ವಂತ ಸಂಗೀತದೊಂದಿಗೆ ಒಂದೊಂದೇ ಪ್ರಶ್ನೆಗೆ ಉತ್ತರಿಸುತ್ತಾ ಹಣದ ಏಣಿಯನ್ನು ಏರಿರಿ.',
    kbc_champion: 'ಚಾಂಪಿಯನ್', kbc_halfway: 'ಅರ್ಧದಾರಿ', kbc_start: 'ಪ್ರಾರಂಭ',
    kbc_5050: '50-50', kbc_audience: 'ಪ್ರೇಕ್ಷಕರ ಮತ', kbc_skip: 'ಪ್ರಶ್ನೆ ಬಿಟ್ಟುಬಿಡಿ', btn_play_now: '▶ ಈಗ ಆಡಿ',
    quiz_card1_title: 'ದೈನಂದಿನ ಜಿಕೆ ಕ್ವಿಜ್', quiz_card1_desc: '10 ಪ್ರಶ್ನೆಗಳು, 5 ನಿಮಿಷಗಳು, ಪ್ರತಿ ಬೆಳಿಗ್ಗೆ ಹೊಸ ಸೆಟ್.',
    quiz_card2_title: 'ಗಣಿತ ವೇಗದ ಸುತ್ತು', quiz_card2_desc: '15 ವೇಗದ ಲೆಕ್ಕಾಚಾರ ಪ್ರಶ್ನೆಗಳಲ್ಲಿ ಸಮಯವನ್ನು ಸೋಲಿಸಿ.',
    quiz_card3_title: 'ಪ್ರಚಲಿತ ವಿದ್ಯಮಾನಗಳ ಕ್ವಿಜ್', quiz_card3_desc: 'ಈ ವಾರದ ಸುದ್ದಿಗಳು, 20-ಪ್ರಶ್ನೆಗಳ ಕ್ವಿಜ್ ಆಗಿ ಪರಿವರ್ತನೆ.',
    quiz_card4_title: 'ರೀಸನಿಂಗ್ ಸವಾಲು', quiz_card4_desc: 'ಒಗಟುಗಳು ಮತ್ತು ಆಸನ ವ್ಯವಸ್ಥೆ ಪ್ರಶ್ನೆಗಳು, ಸಮಯ ನಿಗದಿತ.',
    btn_know_faculty: '🎓 ನಿಮ್ಮ ಬೋಧಕ ವರ್ಗವನ್ನು ತಿಳಿಯಿರಿ',
    idx_admission_desc: 'ಇದನ್ನು ಒಮ್ಮೆ ಭರ್ತಿ ಮಾಡಿ ಮತ್ತು ಲಕ್ನೋ ಕೇಂದ್ರದಲ್ಲಿ ನಿಮ್ಮ ಸೀಟನ್ನು ಖಚಿತಪಡಿಸಲು ನಮ್ಮ ಪ್ರವೇಶ ತಂಡ 24 ಗಂಟೆಗಳ ಒಳಗೆ ಕರೆ ಮಾಡುತ್ತದೆ.',
    admission_point1: 'ಸಣ್ಣ ಬ್ಯಾಚ್‌ಗಳು, ಗರಿಷ್ಠ 60 ವಿದ್ಯಾರ್ಥಿಗಳು', admission_point2: 'ಗ್ರಂಥಾಲಯ ಮತ್ತು ಅಧ್ಯಯನ ಕೊಠಡಿ, ಬೆಳಿಗ್ಗೆ 7 – ರಾತ್ರಿ 9',
    admission_point3: 'ನೀವು ಕ್ರಮ ಕೈಗೊಳ್ಳಬಹುದಾದ ವರದಿಯೊಂದಿಗೆ ಸಾಪ್ತಾಹಿಕ ಪರೀಕ್ಷೆಗಳು',
    admission_label_name: 'ಪೂರ್ಣ ಹೆಸರು', admission_placeholder_name: 'ನಿಮ್ಮ ಹೆಸರು',
    admission_label_phone: 'ಫೋನ್ ಸಂಖ್ಯೆ', admission_placeholder_phone: '10 ಅಂಕಿಗಳ ಮೊಬೈಲ್ ಸಂಖ್ಯೆ',
    admission_label_course: 'ಕೋರ್ಸ್', admission_placeholder_course: 'ಉದಾ. SSC GD, ಬ್ಯಾಂಕಿಂಗ್ ಮತ್ತು ವಿಮೆ',
    admission_label_batch: 'ಆದ್ಯತೆಯ ಬ್ಯಾಚ್', admission_batch_morning: 'ಬೆಳಿಗ್ಗೆ', admission_batch_afternoon: 'ಮಧ್ಯಾಹ್ನ', admission_batch_evening: 'ಸಂಜೆ',
    btn_submit_registration: 'ನೋಂದಣಿ ಸಲ್ಲಿಸಿ',
    admission_error: 'ಏನೋ ತಪ್ಪಾಗಿದೆ — ದಯವಿಟ್ಟು ನಿಮ್ಮ ವಿವರಗಳನ್ನು ಪರಿಶೀಲಿಸಿ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.',
    admission_success: 'ಧನ್ಯವಾದಗಳು — ನಮ್ಮ ಪ್ರವೇಶ ತಂಡ 24 ಗಂಟೆಗಳ ಒಳಗೆ ನಿಮಗೆ ಕರೆ ಮಾಡುತ್ತದೆ.',
  },
};

function applySiteLanguage(lang) {
  document.documentElement.lang = (lang === 'hi' || lang === 'kn') ? lang : 'en';

  var nodes = document.querySelectorAll('[data-i18n]');
  nodes.forEach(function (el) {
    if (!el.dataset.i18nDefault) {
      el.dataset.i18nDefault = el.innerHTML;
    }
    if (lang === 'en' || !SITE_I18N[lang] || !SITE_I18N[lang][el.dataset.i18n]) {
      el.innerHTML = el.dataset.i18nDefault;
    } else {
      el.innerHTML = SITE_I18N[lang][el.dataset.i18n];
    }
  });

  var placeholderNodes = document.querySelectorAll('[data-i18n-placeholder]');
  placeholderNodes.forEach(function (el) {
    if (!el.dataset.i18nPlaceholderDefault) {
      el.dataset.i18nPlaceholderDefault = el.placeholder || '';
    }
    var key = el.dataset.i18nPlaceholder;
    if (lang === 'en' || !SITE_I18N[lang] || !SITE_I18N[lang][key]) {
      el.placeholder = el.dataset.i18nPlaceholderDefault;
    } else {
      el.placeholder = SITE_I18N[lang][key];
    }
  });

  var labels = { en: 'EN', hi: 'हिन्दी', kn: 'ಕನ್ನಡ' };
  document.querySelectorAll('.nav-lang-current').forEach(function (el) {
    el.textContent = labels[lang] || 'EN';
  });
  document.querySelectorAll('.nav-lang-dropdown [data-lang]').forEach(function (btn) {
    btn.classList.toggle('is-current', btn.dataset.lang === lang);
  });
}

/* Test-series questions/options carry admin-entered translations as data-tr-hi /
   data-tr-kn attributes (see panel question form). Swap to whichever is picked,
   falling back to the original English text when no translation was entered. */
function applyQuestionTranslations(lang) {
  var key = 'tr' + lang.charAt(0).toUpperCase() + lang.slice(1);
  document.querySelectorAll('[data-tr-hi],[data-tr-kn]').forEach(function (el) {
    if (!el.dataset.trDefault) el.dataset.trDefault = el.textContent;
    var translated = (lang !== 'en') ? el.dataset[key] : '';
    el.textContent = translated ? translated : el.dataset.trDefault;
  });
}

window.setSiteLanguage = function (lang) {
  localStorage.setItem('site_lang', lang);
  applySiteLanguage(lang);
  applyQuestionTranslations(lang);
};

function applySiteTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme === 'dark' ? 'dark' : 'light');
  const btn = document.getElementById('themeToggle');
  if (btn) btn.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
}

window.setSiteTheme = function (theme) {
  localStorage.setItem('site_theme', theme);
  applySiteTheme(theme);
};

document.addEventListener('DOMContentLoaded', function () {
  var savedLang = localStorage.getItem('site_lang') || 'en';
  applySiteLanguage(savedLang);
  applyQuestionTranslations(savedLang);
  applySiteTheme(localStorage.getItem('site_theme') || 'light');

  const themeToggleBtn = document.getElementById('themeToggle');
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', function () {
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
      window.setSiteTheme(isDark ? 'light' : 'dark');
    });
  }


  /* ---------- 0. Preloader (logo animation, hides once page is ready) ---------- */
  const preloader = document.getElementById('preloader');
  if (preloader) {
    window.addEventListener('load', () => {
      setTimeout(() => preloader.classList.add('is-hidden'), 500);
    });
    setTimeout(() => preloader.classList.add('is-hidden'), 2500);
  }

  /* ---------- 0a. Top loader for login/signup navigation ---------- */
  const topLoader = document.getElementById('topLoader');
  if (topLoader) {
    document.querySelectorAll('a[href$="/login/"], a[href$="/signup/"]').forEach((link) => {
      link.addEventListener('click', () => topLoader.classList.add('is-active'));
    });
  }

  /* ---------- 0a-2. Back button ---------- */
  const backBtn = document.getElementById('backBtn');
  if (backBtn) {
    backBtn.addEventListener('click', () => {
      const cameFromSameSite = document.referrer && document.referrer.indexOf(window.location.origin) === 0;
      if (cameFromSameSite && window.history.length > 1) {
        window.history.back();
      } else {
        window.location.href = window.MA_URLS.index;
      }
    });
  }

  /* ---------- 0a-3. Home link: scroll to top if already home ---------- */
  const homeLink = document.getElementById('navHomeLink');
  if (homeLink && window.location.pathname === '/') {
    homeLink.addEventListener('click', (e) => {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* ---------- 0b. Notification bar modal ---------- */
  const notifItems = document.querySelectorAll('.notif-item:not([aria-hidden="true"])');
  const notifModal = document.getElementById('notifModal');
  const notifTitle = document.getElementById('notifModalTitle');
  const notifBody = document.getElementById('notifModalBody');
  const notifClose = document.getElementById('notifClose');
  const notifViewAll = document.getElementById('notifViewAll');
  const notifOfficialLink = document.getElementById('notifOfficialLink');
  const notifDetailPageLink = document.getElementById('notifDetailPageLink');
  const notifModalList = document.getElementById('notifModalList');

  function openNotif(title, detail, link, page) {
    if (!notifModal) return;
    notifTitle.textContent = title;
    notifBody.textContent = detail;
    if (notifOfficialLink) {
      if (link) {
        notifOfficialLink.href = link;
        notifOfficialLink.style.display = '';
      } else {
        notifOfficialLink.href = '#';
        notifOfficialLink.style.display = 'none';
      }
    }
    if (notifDetailPageLink) {
      if (page) {
        notifDetailPageLink.href = page;
        notifDetailPageLink.style.display = '';
      } else {
        notifDetailPageLink.href = '#';
        notifDetailPageLink.style.display = 'none';
      }
    }
    notifModal.classList.remove('list-mode');
    notifModal.classList.add('is-open');
  }
  function openNotifList() {
    if (!notifModal || !notifModalList) return;
    notifModalList.innerHTML = '';
    if (notifItems.length === 0) {
      const empty = document.createElement('p');
      empty.className = 'notif-modal-empty';
      empty.textContent = 'No notifications right now — check back soon.';
      notifModalList.appendChild(empty);
    } else {
      notifItems.forEach(item => {
        const row = document.createElement('button');
        row.type = 'button';
        row.className = 'notif-modal-list-item';
        row.textContent = item.textContent.trim();
        row.addEventListener('click', () => openNotif(item.textContent.trim(), item.dataset.detail || '', item.dataset.link || '', item.dataset.page || ''));
        notifModalList.appendChild(row);
      });
    }
    notifModal.classList.add('list-mode');
    notifModal.classList.add('is-open');
  }
  notifItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      openNotif(item.textContent.trim(), item.dataset.detail || '', item.dataset.link || '', item.dataset.page || '');
    });
  });
  if (notifViewAll) {
    notifViewAll.addEventListener('click', openNotifList);
  }
  if (notifClose) notifClose.addEventListener('click', () => notifModal.classList.remove('is-open'));
  if (notifModal) notifModal.addEventListener('click', (e) => { if (e.target === notifModal) notifModal.classList.remove('is-open'); });

  /* ---------- 1. Sliding announcement banner ---------- */
  const card   = document.getElementById('promoCard');
  const slides = Array.from(document.querySelectorAll('.promo-slide'));
  const dotsEl = document.getElementById('promoDots');
  const prevBtn = document.getElementById('promoPrev');
  const nextBtn = document.getElementById('promoNext');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (card && slides.length) {
    let index = 0;
    let timer = null;
    const DELAY = 5000;

    // build dots
    slides.forEach((_, i) => {
      const dot = document.createElement('button');
      dot.type = 'button';
      dot.setAttribute('role', 'tab');
      dot.setAttribute('aria-label', 'Announcement ' + (i + 1));
      dot.setAttribute('aria-selected', i === 0 ? 'true' : 'false');
      dot.addEventListener('click', () => { goTo(i); restart(); });
      dotsEl.appendChild(dot);
    });
    const dots = Array.from(dotsEl.children);

    function goTo(next) {
      index = (next + slides.length) % slides.length;
      slides.forEach((s, i) => s.classList.toggle('is-active', i === index));
      dots.forEach((d, i) => d.setAttribute('aria-selected', i === index ? 'true' : 'false'));
    }

    function start() { if (!reduceMotion) timer = setInterval(() => goTo(index + 1), DELAY); }
    function stop()  { clearInterval(timer); }
    function restart(){ stop(); start(); }

    nextBtn.addEventListener('click', () => { goTo(index + 1); restart(); });
    prevBtn.addEventListener('click', () => { goTo(index - 1); restart(); });

    card.addEventListener('mouseenter', stop);
    card.addEventListener('mouseleave', start);
    card.addEventListener('focusin', stop);
    card.addEventListener('focusout', start);

    // keyboard
    card.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') { goTo(index + 1); restart(); }
      if (e.key === 'ArrowLeft')  { goTo(index - 1); restart(); }
    });

    // touch swipe
    let startX = 0;
    card.addEventListener('touchstart', (e) => { startX = e.touches[0].clientX; stop(); }, { passive: true });
    card.addEventListener('touchend', (e) => {
      const dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 45) goTo(index + (dx < 0 ? 1 : -1));
      start();
    }, { passive: true });

    // pause when tab is hidden
    document.addEventListener('visibilitychange', () => document.hidden ? stop() : start());

    start();
  }

  /* ---------- 2. Mobile menu ---------- */
  const toggle = document.getElementById('menuToggle');
  const nav = document.getElementById('primaryNav');

  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    });

    nav.addEventListener('click', (e) => {
      if (e.target.closest('a') && window.innerWidth <= 940) {
        nav.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* ---------- 2a. "More" nav dropdown ---------- */
  const navMore = document.getElementById('navMore');
  const navMoreToggle = document.getElementById('navMoreToggle');

  if (navMore && navMoreToggle) {
    navMoreToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      const open = navMore.classList.toggle('is-open');
      navMoreToggle.setAttribute('aria-expanded', String(open));
    });

    document.addEventListener('click', (e) => {
      if (!navMore.contains(e.target)) {
        navMore.classList.remove('is-open');
        navMoreToggle.setAttribute('aria-expanded', 'false');
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        navMore.classList.remove('is-open');
        navMoreToggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* ---------- 2a-2. Language dropdown(s) — every .nav-lang instance on the page ---------- */
  document.querySelectorAll('.nav-lang').forEach((langBox) => {
    const toggle = langBox.querySelector('.nav-lang-toggle');
    if (!toggle) return;

    toggle.addEventListener('click', (e) => {
      e.stopPropagation();
      const open = langBox.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', String(open));
    });

    document.addEventListener('click', (e) => {
      if (!langBox.contains(e.target)) {
        langBox.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        langBox.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });

    langBox.querySelectorAll('[data-lang]').forEach((btn) => {
      btn.addEventListener('click', () => {
        window.setSiteLanguage(btn.dataset.lang);
        langBox.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  });

  /* ---------- 2b. Logged-in user dropdown ---------- */
  const userMenu = document.getElementById('navUserMenu');
  const userTrigger = document.getElementById('navUserTrigger');

  if (userMenu && userTrigger) {
    userTrigger.addEventListener('click', (e) => {
      e.stopPropagation();
      const open = userMenu.classList.toggle('is-open');
      userTrigger.setAttribute('aria-expanded', String(open));
    });

    document.addEventListener('click', (e) => {
      if (!userMenu.contains(e.target)) {
        userMenu.classList.remove('is-open');
        userTrigger.setAttribute('aria-expanded', 'false');
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        userMenu.classList.remove('is-open');
        userTrigger.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* ---------- 3. Header shadow + active link ---------- */
  const header = document.querySelector('.site-header');
  const navLinks = Array.from(document.querySelectorAll('.primary-nav > ul a'));
  const sections = navLinks
    .map(a => {
      const href = a.getAttribute('href') || '';
      const hashIdx = href.indexOf('#');
      return hashIdx === -1 ? null : document.querySelector(href.slice(hashIdx));
    })
    .filter(Boolean);

  function onScroll() {
    header.classList.toggle('is-stuck', window.scrollY > 8);

    let current = sections[0];
    sections.forEach(sec => {
      if (sec.getBoundingClientRect().top <= 140) current = sec;
    });
    if (current) {
      navLinks.forEach(a => a.classList.toggle('is-active', a.getAttribute('href').endsWith('#' + current.id)));
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- 5. Scroll-reveal animations (site-wide) ---------- */
  const revealSelector = [
    '.section-title', '.eyebrow', '.section-sub',
    '.pc-card', '.ts-card', '.gallery-card', '.daily-post-card', '.quiz-card',
    '.career-card', '.store-card', '.cal-card', '.coupon-card', '.cert-card',
    '.classroom-card', '.result-card', '.elig-card',
    '.brand-band', '.notif-side-card',
  ].join(',');
  const revealEls = Array.from(document.querySelectorAll(revealSelector))
    .filter(el => !el.closest('.panel-main'));

  if (window.IntersectionObserver && revealEls.length) {
    const revealIo = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          revealIo.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });

    revealEls.forEach((el, i) => {
      el.classList.add('reveal-io');
      el.style.transitionDelay = (i % 6) * 60 + 'ms';
      revealIo.observe(el);
    });
  }

  /* ---------- footer year ---------- */
  const year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();

  /* ---------- test series exam hierarchy (breadcrumb + drill-down tabs) ---------- */
  (function () {
    const treeData = document.getElementById('tsCategoryTreeData');
    const breadcrumb = document.getElementById('tsBreadcrumb');
    const rows = [
      document.getElementById('tsTabsLevel0'),
      document.getElementById('tsTabsLevel1'),
      document.getElementById('tsTabsLevel2'),
      document.getElementById('tsTabsLevel3'),
    ];
    const tsCards = document.querySelectorAll('#tsGrid .ts-card');
    const tsEmptyState = document.getElementById('tsEmptyState');
    if (!treeData || !rows[0]) return;

    let tree = [];
    try { tree = JSON.parse(treeData.textContent || '[]'); } catch (e) { tree = []; }

    const ALL_ICON = '<span class="category-logo category-logo-general" aria-hidden="true"><svg viewBox="0 0 64 64" focusable="false"><rect class="logo-main" x="8" y="8" width="21" height="21" rx="6"/><rect class="logo-accent" x="35" y="8" width="21" height="21" rx="6"/><rect class="logo-dark" x="8" y="35" width="21" height="21" rx="6"/><rect class="logo-paper" x="35" y="35" width="21" height="21" rx="6"/></svg></span>';
    let selection = [];

    function renderRow(row, depth, nodes) {
      row.innerHTML = '';
      const allBtn = document.createElement('button');
      allBtn.type = 'button';
      allBtn.className = 'ts-tab' + (selection.length === depth ? ' is-active' : '');
      allBtn.innerHTML = '<span class="ts-tab-ico">' + ALL_ICON + '</span><span>All</span>';
      allBtn.addEventListener('click', () => selectAt(depth, null));
      row.appendChild(allBtn);
      nodes.forEach(node => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'ts-tab' + (selection[depth] && selection[depth].id === node.id ? ' is-active' : '');
        const icoSpan = document.createElement('span');
        icoSpan.className = 'ts-tab-ico';
        icoSpan.innerHTML = node.icon_html;
        const labelSpan = document.createElement('span');
        labelSpan.textContent = node.name;
        btn.appendChild(icoSpan);
        btn.appendChild(labelSpan);
        btn.addEventListener('click', () => selectAt(depth, node));
        row.appendChild(btn);
      });
    }

    function selectAt(depth, node) {
      selection = selection.slice(0, depth);
      if (node) selection.push(node);
      render();
    }

    function render() {
      renderRow(rows[0], 0, tree);
      for (let depth = 1; depth < rows.length; depth++) {
        const nodes = selection[depth - 1] ? selection[depth - 1].children : [];
        rows[depth].hidden = !nodes.length;
        if (nodes.length) renderRow(rows[depth], depth, nodes);
      }

      breadcrumb.innerHTML = '';
      const homeBtn = document.createElement('button');
      homeBtn.type = 'button';
      homeBtn.className = 'ts-breadcrumb-item' + (selection.length === 0 ? ' is-current' : '');
      homeBtn.textContent = 'Home';
      homeBtn.addEventListener('click', () => selectAt(0, null));
      breadcrumb.appendChild(homeBtn);
      selection.forEach((node, i) => {
        const sep = document.createElement('span');
        sep.className = 'ts-breadcrumb-sep';
        sep.textContent = '›';
        breadcrumb.appendChild(sep);
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'ts-breadcrumb-item' + (i === selection.length - 1 ? ' is-current' : '');
        btn.textContent = node.name;
        btn.addEventListener('click', () => selectAt(i + 1, node));
        breadcrumb.appendChild(btn);
      });

      const activeId = selection.length ? selection[selection.length - 1].id : null;
      let visibleCount = 0;
      tsCards.forEach(card => {
        let visible = true;
        if (activeId !== null) {
          const chain = (card.dataset.catChain || '').split(',').filter(Boolean).map(Number);
          visible = chain.includes(activeId);
        }
        card.hidden = !visible;
        if (visible) visibleCount++;
      });
      if (tsEmptyState) tsEmptyState.hidden = tsCards.length === 0 || visibleCount > 0;
    }

    render();
  })();

  /* ---------- Admission form (saved to the database) ---------- */
  const admissionForm = document.getElementById('admissionForm');
  const admissionCourseParam = new URLSearchParams(window.location.search).get('course');
  if (admissionCourseParam) {
    const courseInput = document.getElementById('admissionCourseInput');
    if (courseInput) courseInput.value = admissionCourseParam;
    const admissionSection = document.getElementById('admission');
    if (admissionSection) {
      window.addEventListener('load', () => admissionSection.scrollIntoView({ behavior: 'smooth', block: 'start' }));
    }
  }
  if (admissionForm) {
    admissionForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const successMsg = document.getElementById('admissionSuccess');
      const errorMsg = document.getElementById('admissionError');
      errorMsg.hidden = true;
      successMsg.hidden = true;

      fetch(admissionForm.action, { method: 'POST', body: new FormData(admissionForm) })
        .then((res) => res.json().then((data) => ({ ok: res.ok, data })))
        .then(({ ok, data }) => {
          if (ok && data.ok) {
            successMsg.hidden = false;
            admissionForm.reset();
          } else {
            errorMsg.hidden = false;
          }
        })
        .catch(() => { errorMsg.hidden = false; });
    });
  }

  /* ---------- Career apply modal (saved to the database) ---------- */
  const careerModal = document.getElementById('careerModal');
  const careerApplyForm = document.getElementById('careerApplyForm');
  if (careerModal && careerApplyForm) {
    const careerModalTitle = document.getElementById('careerModalTitle');
    const careerModalClose = document.getElementById('careerModalClose');
    const careerSuccess = document.getElementById('careerApplySuccess');
    const careerError = document.getElementById('careerApplyError');

    document.querySelectorAll('.career-apply-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        careerModalTitle.textContent = btn.dataset.jobTitle;
        careerApplyForm.dataset.jobId = btn.dataset.jobId;
        careerSuccess.hidden = true;
        careerError.hidden = true;
        careerApplyForm.reset();
        careerModal.classList.add('is-open');
      });
    });
    if (careerModalClose) careerModalClose.addEventListener('click', () => careerModal.classList.remove('is-open'));
    careerModal.addEventListener('click', (e) => { if (e.target === careerModal) careerModal.classList.remove('is-open'); });

    careerApplyForm.addEventListener('submit', (e) => {
      e.preventDefault();
      careerError.hidden = true;
      careerSuccess.hidden = true;
      const jobId = careerApplyForm.dataset.jobId;
      fetch(`/career/${jobId}/apply/`, { method: 'POST', body: new FormData(careerApplyForm) })
        .then((res) => res.json().then((data) => ({ ok: res.ok, data })))
        .then(({ ok, data }) => {
          if (ok && data.ok) {
            careerSuccess.hidden = false;
            careerApplyForm.reset();
          } else {
            careerError.hidden = false;
          }
        })
        .catch(() => { careerError.hidden = false; });
    });
  }

  /* ---------- Install App (PWA) ---------- */
  const installFab = document.getElementById('installFab');
  const installModal = document.getElementById('installModal');
  const installModalClose = document.getElementById('installModalClose');
  const isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
  const isIOS = /iphone|ipad|ipod/i.test(window.navigator.userAgent);
  let deferredInstallPrompt = null;

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js').catch(() => {});
    });
  }

  if (installFab && !isStandalone) {
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredInstallPrompt = e;
      installFab.hidden = false;
    });

    if (isIOS) {
      installFab.hidden = false;
    }

    installFab.addEventListener('click', () => {
      if (deferredInstallPrompt) {
        deferredInstallPrompt.prompt();
        deferredInstallPrompt.userChoice.finally(() => { deferredInstallPrompt = null; });
      } else if (isIOS && installModal) {
        installModal.classList.add('is-open');
      }
    });

    window.addEventListener('appinstalled', () => { installFab.hidden = true; });
  }
  if (installModalClose) installModalClose.addEventListener('click', () => installModal.classList.remove('is-open'));
  if (installModal) installModal.addEventListener('click', (e) => { if (e.target === installModal) installModal.classList.remove('is-open'); });

  /* ---------- Chatbot widget (preloaded questions) ---------- */
  const chatFab = document.getElementById('chatFab');
  const chatPanel = document.getElementById('chatPanel');
  const chatClose = document.getElementById('chatClose');
  const chatBody = document.getElementById('chatBody');
  const chatQuestions = document.getElementById('chatQuestions');

  function openChat() { chatPanel.classList.add('is-open'); chatFab.classList.add('is-open'); chatFab.textContent = '✕'; }
  function closeChat() { chatPanel.classList.remove('is-open'); chatFab.classList.remove('is-open'); chatFab.textContent = '💬'; }

  if (chatFab && chatPanel) {
    chatFab.addEventListener('click', () => {
      chatPanel.classList.contains('is-open') ? closeChat() : openChat();
    });
  }
  if (chatClose) chatClose.addEventListener('click', closeChat);

  if (chatQuestions && chatBody) {
    chatQuestions.addEventListener('click', (e) => {
      const btn = e.target.closest('.chat-q-btn');
      if (!btn) return;

      const userMsg = document.createElement('div');
      userMsg.className = 'chat-msg chat-msg-user';
      userMsg.textContent = btn.dataset.question || '';
      chatBody.appendChild(userMsg);

      const botMsg = document.createElement('div');
      botMsg.className = 'chat-msg chat-msg-bot';
      botMsg.textContent = btn.dataset.answer || '';
      chatBody.appendChild(botMsg);

      chatBody.scrollTop = chatBody.scrollHeight;
    });
  }
});

