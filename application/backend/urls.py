from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views



urlpatterns = [
    path('', views.home, name='homepage'),
    path('contact/submit/', views.contact_submit, name='contact_submit'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('password/reset/', views.forgot_password, name='forgot_password'),
    path('password/reset/verify/', views.password_reset_verify, name='password_reset_verify'),
    path('password/reset/resend/', views.resend_verification_code, name='resend_verification_code'),
    path('term/', views.term, name='term'),
    path('accounts/', include('allauth.urls')),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('social/signup/', views.social_signup_complete, name='social_signup_complete'),
    path('social/redirect/', views.redirect_after_social_login, name='redirect_after_social_login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Dashboard URLs
    path('dashboard/athlete/', views.athlete_dashboard, name='athlete_dashboard'),
    path('dashboard/psychologist/', views.psychologist_dashboard, name='psychologist_dashboard'),
    path('dashboard/coach/', views.coach_dashboard, name='coach_dashboard'),
    path('dashboard/nutritionist/', views.nutritionist_dashboard, name='nutritionist_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),

    # admin urls
    path('admin_user/', views.admin_crud, name='admin_user'),
    # Admin API endpoints for user management
    path('admin_user/', views.admin_crud, name='admin_get_users'),
    # Detailed user view, creation, updating
    path('crud/users/<int:user_id>/', views.admin_get_user, name='admin_get_user'),
    path('crud/users/create/', views.admin_create_user, name='admin_create_user'),
    path('crud/users/<int:user_id>/update/', views.admin_update_user, name='admin_update_user'),
    path('crud/users/<int:user_id>/delete/', views.admin_delete_user, name='admin_delete_user'),  # Added delete URL
    # Professional verification
    path('crud/users/<int:user_id>/verify/', views.admin_verify_professional, name='admin_verify_professional'),
    # Account status management
    path('crud/users/<int:user_id>/status/', views.admin_update_account_status, name='admin_update_account_status'),
    # Statistics and reporting
    path('crud/statistics/', views.admin_get_statistics, name='admin_get_statistics'),
    # Data export
    path('crud/users/export/', views.admin_export_users, name='admin_export_users'),
    path('contact_management/', views.contact_management, name='contact_management'),


## error
    path('complete-profile/athlete/', views.complete_athlete_profile, name='complete_athlete_profile'),
    path('payment/status/<str:reference>/', views.payment_status, name='payment_status'),
    path('payment/receipt/download/', views.download_receipt, name='download_receipt'),
    path('check-profile-completion/athlete/', views.check_profile_completion, name='check_profile_completion'),

## athlete panel
    path('appointments/', views.appointments, name='appointments'),
    path('appointments/specialists/', views.specialist_list, name='specialist_list'),
    path('appointments/specialists/<int:specialist_id>/', views.specialist_detail, name='specialist_detail'),
    path('appointments/create/', views.create_appointment, name='create_appointment'),
    path('appointments/cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('appointments/review/<int:appointment_id>/', views.review_appointment, name='review_appointment'),

    # Specialist appointment views
    path('specialist/appointments/', views.manage_appointment_requests, name='manage_appointment_requests'),
    path('specialist/appointments/respond/<int:appointment_id>/', views.respond_to_appointment, name='respond_to_appointment'),
    path('specialist/appointments/complete/<int:appointment_id>/', views.complete_appointment, name='complete_appointment'),
    
    # Common appointment views
    path('appointments/notes/<int:appointment_id>/', views.appointment_notes, name='appointment_notes'),
    # videos  urls
    path('appointments/video-session/<int:appointment_id>/', views.join_video_session, name='join_video_session'),
    path('Assessments/', views.Assessments, name='Assessments'),
    path('<int:assessment_id>/', views.assessment_detail, name='assessment_detail'),
    path('<int:assessment_id>/start/', views.start_assessment, name='start_assessment'),
    path('response/<int:response_id>/', views.continue_assessment, name='continue_assessment'),
    path('response/<int:response_id>/save/', views.save_question_response, name='save_question_response'),
    path('response/<int:response_id>/complete/', views.complete_assessment, name='complete_assessment'),
    path('results/<int:response_id>/', views.view_results, name='view_results'),
    path('progress/', views.athlete_progress, name='athlete_progress'),
    path('progress/<int:athlete_id>/', views.athlete_progress, name='athlete_progress_detail'),


    path('WellnessResources/', views.WellnessResources, name='WellnessResources'),
    path('wellness-resources/category/<slug:slug>/', views.resource_category, name='resource_category'),
    path('wellness-resources/resource/<slug:slug>/', views.resource_detail, name='resource_detail'),
    path('wellness-resources/saved/', views.saved_resources, name='saved_resources'),
    path('wellness-resources/search/', views.search_resources, name='search_resources'),
    path('wellness-resources/save/', views.save_resource, name='save_resource'),
    path('wellness-resources/rate/', views.rate_resource, name='rate_resource'),

# Journal URLs

    path('journal/', views.journal_home, name='journal_home'),
    path('journal/new/', views.new_journal_entry, name='new_journal_entry'),
    path('journal/entry/<int:entry_id>/', views.view_journal_entry, name='view_journal_entry'),
    path('journal/entry/<int:entry_id>/edit/', views.edit_journal_entry, name='edit_journal_entry'),
    path('journal/entry/<int:entry_id>/delete/', views.delete_journal_entry, name='delete_journal_entry'),
    path('journal/calendar/', views.journal_calendar, name='journal_calendar'),
    path('journal/analysis/', views.journal_analysis, name='journal_analysis'),
    path('journal/search/', views.journal_search, name='journal_search'),
    path('journal/export/', views.export_journal_entries, name='export_journal_entries'),
    path('journal/prompt/', views.random_prompt, name='random_prompt'),
    path('journal/template/<int:template_id>/', views.journal_template_detail, name='journal_template_detail'),
    path('journal/template/<int:template_id>/create/', views.create_entry_from_template, name='create_from_template'),

# Admin views for managing content (Optional for admin users)
    # These would be additional views for content management
    # path('admin/resources/categories/', views.admin_resource_categories, name='admin_resource_categories'),
    # path('admin/resources/manage/', views.admin_manage_resources, name='admin_manage_resources'),
    # path('admin/journal/prompts/', views.admin_journal_prompts, name='admin_journal_prompts'),
    # path('admin/journal/templates/', views.admin_journal_templates, name='admin_journal_templates'),


   # Community home
    path('community/', views.community_home, name='community_home'),
        
        # Categories
    path('community/categories/', views.CategoryListView.as_view(), name='category_list'),
    path('community/category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
        
        # Threads
    path('community/thread/create/', views.ThreadCreateView.as_view(), name='thread_create'),
    path('community/category/<slug:category_slug>/new-thread/', views.ThreadCreateView.as_view(), name='category_thread_create'),
    path('community/category/<slug:category_slug>/thread/<slug:thread_slug>/', views.ThreadDetailView.as_view(), name='thread_detail'),
    path('community/category/<slug:category_slug>/thread/<slug:thread_slug>/comment/', views.thread_comment, name='thread_comment'),
    path('community/category/<slug:category_slug>/thread/<slug:thread_slug>/lock/', views.thread_lock_toggle, name='thread_lock_toggle'),
    path('community/category/<slug:category_slug>/thread/<slug:thread_slug>/pin/', views.thread_pin_toggle, name='thread_pin_toggle'),
        
        # Anonymous Questions
    path('community/anonymous-questions/', views.anonymous_questions_list, name='anonymous_questions_list'),
    path('community/anonymous-questions/ask/', views.anonymous_question_create, name='anonymous_question_create'),
    path('community/anonymous-questions/my-questions/', views.my_anonymous_questions, name='my_anonymous_questions'),
        
        # Success Stories
    path('community/success-stories/', views.SuccessStoryListView.as_view(), name='success_story_list'),
    path('community/success-stories/<slug:slug>/', views.SuccessStoryDetailView.as_view(), name='success_story_detail'),    
    path('success-stories/<slug:slug>/delete/', views.SuccessStoryDeleteView.as_view(), name='success_story_delete'),
    path('success-stories/<slug:slug>/update/', views.SuccessStoryUpdateView.as_view(), name='success_story_update'),
    path('success-stories/create/', views.SuccessStoryCreateView.as_view(), name='success_story_create'),
    
        # Mentorship
    path('community/mentorship/', views.mentorship_programs_list, name='mentorship_programs_list'),
    path('community/mentorship/<int:pk>/', views.mentorship_program_detail, name='mentorship_program_detail'),
        
        # Support Groups
    path('community/support-groups/', views.support_groups_list, name='support_groups_list'),
    path('community/support-groups/<int:pk>/', views.support_group_detail, name='support_group_detail'),
    path('community/support-groups/<int:pk>/register/', views.support_group_register, name='support_group_register'),
    path('community/support-groups/<int:pk>/leave/', views.support_group_leave, name='support_group_leave'),
    path('community/support-groups/<int:group_pk>/session/<int:session_pk>/', views.support_group_session_detail, name='support_group_session_detail'),
    path('community/facilitated-groups/', views.facilitated_groups, name='facilitated_groups'),
    path('community/participant-request/<int:participant_id>/action/', views.participant_request_action, name='participant_request_action'),


## admin view of management forum

    path('community/admin/dashboard/', views.CommunityAdminDashboard.as_view(), name='CommunityAdminDashboard'),
    path('community/admin/forum/', views.ForumModerationView.as_view(), name='forum_moderation'),
    path('community/admin/forum/thread/<int:thread_id>/', views.moderate_thread, name='moderate_thread'),
    path('community/admin/mentorship/', views.MentorshipAdminView.as_view(), name='mentorship_admin'),
    path('community/admin/mentorship/<int:program_id>/', views.mentorship_program_detail, name='mentorship_program_detail'),
    path('community/admin/support-groups/', views.SupportGroupAdminView.as_view(), name='support_group_admin'),
    path('community/admin/support-groups/<int:group_id>/', views.support_group_detail, name='support_group_detail'),  

## professional user url for Forum

    path('professional/dashboard/', views.ProfessionalDashboard.as_view(), name='professional_dashboard'),
    path('professional/support-groups/create/', views.create_support_group, name='create_support_group'),
    path('psychologist/mentorship/', views.PsychologistMentorshipView.as_view(), name='psychologist_mentorship'),
    path('psychologist/questions/<int:question_id>/', views.respond_to_question, name='respond_to_question'),


## chat All user

 # Chat URLs
    path('chat/', views.chat_home, name='chat_home'),
    path('chat/token/<uuid:conversation_id>/', views.get_conversation_token, name='chat_token'),
    path('chat/send/', views.create_message, name='send_message'),








    path('AthleteCommunity/', views.AthleteCommunity, name='AthleteCommunity'),
    path('ProgressTracker/', views.ProgressTracker, name='ProgressTracker'),


    
    # Psychologist views
    path('PsychologistAssessments/', views.PsychologistAssessments, name='PsychologistAssessments'),
    path('review/<int:response_id>/', views.psychologist_review, name='psychologist_review'),
    path('assign/', views.psychologist_assign_assessment, name='assign_assessment'),
    path('assign/<int:athlete_id>/',views. psychologist_assign_assessment, name='assign_to_athlete'),
    path('create/', views.create_assessment, name='create_assessment'),
    path('<int:assessment_id>/edit/', views.edit_assessment, name='edit_assessment'),
    path('question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('scale/<int:scale_id>/delete/', views.delete_scale, name='delete_scale'),
    path('<int:assessment_id>/duplicate/', views.duplicate_assessment, name='duplicate_assessment'),

   

## not yet done
    path('PsychologistAppointments/', views.PsychologistAppointments, name='PsychologistAppointments'),
    path('PsychologistAthletes/', views.PsychologistAthletes, name='PsychologistAthletes'),
    path('PsychologistWellnessResources/', views.PsychologistWellnessResources, name='PsychologistWellnessResources'),
    path('PsychologistCommunity/', views.PsychologistCommunity, name='PsychologistCommunity'),
    path('PsychologistSetting/', views.PsychologistSetting, name='PsychologistSetting'),



## coach panel
    #path('CoachAppointments/', views.CoachAppointments, name='CoachAppointments'),
    path('CoachForums/', views.CoachForums, name='CoachForums'),
    path('CoachMessages/', views.CoachMessages, name='CoachMessages'),
    path('CoachAthletes/', views.CoachAthletes, name='CoachAthletes'),
    path('CoachResources/', views.CoachResources, name='CoachResources'),
    path('CoachSetting/', views.CoachSetting, name='CoachSetting'),

## nutritionist panel
    path('NutritionistAppointments/', views.NutritionistAppointments, name='NutritionistAppointments'),
    path('NutritionistAthletes/', views.NutritionistAthletes, name='NutritionistAthletes'),
    path('NutritionistResources/', views.NutritionistResources, name='NutritionistResources'),
    path('NutritionistForum/', views.NutritionistForum, name='NutritionistForum'),
    path('NutritionistSetting/', views.NutritionistSetting, name='NutritionistSetting'),



]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)