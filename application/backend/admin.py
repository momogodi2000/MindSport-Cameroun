# backendy/admin.py
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    Category, Thread, Comment, MentorshipProgram, MentorshipRelationship,
    AnonymousQuestion, SuccessStory, SupportGroup, SupportGroupSession,
    SupportGroupParticipant, SupportGroupAttendance
)

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'thread_count', 'order')
    list_editable = ('is_active', 'order')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    actions = ['activate_categories', 'deactivate_categories']

    def thread_count(self, obj):
        return obj.thread_count()
    thread_count.short_description = 'Threads'

    def activate_categories(self, request, queryset):
        queryset.update(is_active=True)
    activate_categories.short_description = "Activate selected categories"

    def deactivate_categories(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_categories.short_description = "Deactivate selected categories"

@admin.register(Thread)
class ThreadAdmin(ModelAdmin):
    list_display = ('title', 'category', 'author', 'is_pinned', 'is_locked', 'is_active', 'view_count', 'comment_count')
    list_filter = ('category', 'is_pinned', 'is_locked', 'is_active')
    search_fields = ('title', 'content', 'author__username')
    actions = ['pin_threads', 'unpin_threads', 'lock_threads', 'unlock_threads', 'activate_threads', 'deactivate_threads']

    def pin_threads(self, request, queryset):
        queryset.update(is_pinned=True)
    pin_threads.short_description = "Pin selected threads"

    def unpin_threads(self, request, queryset):
        queryset.update(is_pinned=False)
    unpin_threads.short_description = "Unpin selected threads"

    def lock_threads(self, request, queryset):
        queryset.update(is_locked=True)
    lock_threads.short_description = "Lock selected threads"

    def unlock_threads(self, request, queryset):
        queryset.update(is_locked=False)
    unlock_threads.short_description = "Unlock selected threads"

    def activate_threads(self, request, queryset):
        queryset.update(is_active=True)
    activate_threads.short_description = "Activate selected threads"

    def deactivate_threads(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_threads.short_description = "Deactivate selected threads"

@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('truncated_content', 'thread', 'author', 'is_active', 'created_at')
    list_filter = ('is_active', 'thread__category')
    search_fields = ('content', 'author__username', 'thread__title')
    actions = ['activate_comments', 'deactivate_comments']

    def truncated_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    truncated_content.short_description = 'Content'

    def activate_comments(self, request, queryset):
        queryset.update(is_active=True)
    activate_comments.short_description = "Activate selected comments"

    def deactivate_comments(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_comments.short_description = "Deactivate selected comments"

@admin.register(MentorshipProgram)
class MentorshipProgramAdmin(ModelAdmin):
    list_display = ('name', 'is_active', 'start_date', 'end_date', 'relationship_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    date_hierarchy = 'start_date'

    def relationship_count(self, obj):
        return obj.relationships.count()
    relationship_count.short_description = 'Relationships'

@admin.register(MentorshipRelationship)
class MentorshipRelationshipAdmin(ModelAdmin):
    list_display = ('program', 'mentor', 'mentee', 'status', 'start_date', 'end_date')
    list_filter = ('program', 'status')
    search_fields = ('mentor__username', 'mentee__username', 'program__name')
    raw_id_fields = ('mentor', 'mentee')

@admin.register(AnonymousQuestion)
class AnonymousQuestionAdmin(ModelAdmin):
    list_display = ('title', 'status', 'is_public', 'created_at', 'respondent')
    list_filter = ('status', 'is_public')
    search_fields = ('title', 'content', 'response')
    actions = ['mark_answered', 'mark_pending', 'mark_rejected', 'make_public', 'make_private']

    def mark_answered(self, request, queryset):
        queryset.update(status='answered')
    mark_answered.short_description = "Mark selected as answered"

    def mark_pending(self, request, queryset):
        queryset.update(status='pending')
    mark_pending.short_description = "Mark selected as pending"

    def mark_rejected(self, request, queryset):
        queryset.update(status='rejected')
    mark_rejected.short_description = "Mark selected as rejected"

    def make_public(self, request, queryset):
        queryset.update(is_public=True)
    make_public.short_description = "Make selected public"

    def make_private(self, request, queryset):
        queryset.update(is_public=False)
    make_private.short_description = "Make selected private"

@admin.register(SuccessStory)
class SuccessStoryAdmin(ModelAdmin):
    list_display = ('title', 'author', 'is_approved', 'is_featured', 'view_count', 'created_at')
    list_filter = ('is_approved', 'is_featured')
    search_fields = ('title', 'content', 'author__username')
    actions = ['approve_stories', 'unapprove_stories', 'feature_stories', 'unfeature_stories']

    def approve_stories(self, request, queryset):
        queryset.update(is_approved=True)
    approve_stories.short_description = "Approve selected stories"

    def unapprove_stories(self, request, queryset):
        queryset.update(is_approved=False)
    unapprove_stories.short_description = "Unapprove selected stories"

    def feature_stories(self, request, queryset):
        queryset.update(is_featured=True)
    feature_stories.short_description = "Feature selected stories"

    def unfeature_stories(self, request, queryset):
        queryset.update(is_featured=False)
    unfeature_stories.short_description = "Unfeature selected stories"

@admin.register(SupportGroup)
class SupportGroupAdmin(ModelAdmin):
    list_display = ('name', 'facilitator', 'frequency', 'is_active', 'participant_count', 'max_participants')
    list_filter = ('frequency', 'is_active')
    search_fields = ('name', 'description', 'facilitator__username')
    raw_id_fields = ('facilitator',)

    def participant_count(self, obj):
        return obj.current_participant_count()
    participant_count.short_description = 'Participants'

@admin.register(SupportGroupSession)
class SupportGroupSessionAdmin(ModelAdmin):
    list_display = ('title', 'group', 'start_time', 'end_time', 'is_completed')
    list_filter = ('group', 'is_completed')
    search_fields = ('title', 'description', 'group__name')
    date_hierarchy = 'start_time'

@admin.register(SupportGroupParticipant)
class SupportGroupParticipantAdmin(ModelAdmin):
    list_display = ('group', 'user', 'status', 'joined_at', 'left_at')
    list_filter = ('group', 'status')
    search_fields = ('group__name', 'user__username')
    raw_id_fields = ('user',)

@admin.register(SupportGroupAttendance)
class SupportGroupAttendanceAdmin(ModelAdmin):
    list_display = ('session', 'participant', 'attended', 'feedback_short')
    list_filter = ('session', 'attended')
    search_fields = ('session__title', 'participant__user__username')

    def feedback_short(self, obj):
        return obj.feedback[:50] + '...' if obj.feedback and len(obj.feedback) > 50 else obj.feedback or ''
    feedback_short.short_description = 'Feedback'