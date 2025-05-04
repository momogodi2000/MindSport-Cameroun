# backend/management/commands/generate_test_data.py
import random
import datetime
import uuid
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from faker import Faker

from backend.models import (
    AssessmentCategory, Assessment, Question, ResponseScale, 
    AssignedAssessment, AssessmentResponse, QuestionResponse,
    PsychologistReview, RecommendedSpecialist, ProgressMetric,
    AthleteMetricProgress
)

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Generate test data for mental health assessment models'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=10, help='Number of users of each type to create')
        parser.add_argument('--categories', type=int, default=5, help='Number of assessment categories to create')
        parser.add_argument('--assessments', type=int, default=10, help='Number of assessments to create')
        parser.add_argument('--responses', type=int, default=50, help='Number of assessment responses to create')
        parser.add_argument('--clear', action='store_true', help='Clear existing data before generating new data')

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_data()
            self.stdout.write(self.style.SUCCESS('Cleared existing data'))

        with transaction.atomic():
            users = self.create_users(options['users'])
            self.stdout.write(self.style.SUCCESS(f'Created {len(users["athletes"])} athletes, {len(users["psychologists"])} psychologists, and {len(users["others"])} other professionals'))
            
            categories = self.create_categories(options['categories'])
            self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} assessment categories'))
            
            assessments = self.create_assessments(categories, users["psychologists"], options['assessments'])
            self.stdout.write(self.style.SUCCESS(f'Created {len(assessments)} assessments with questions and scales'))
            
            assignments = self.create_assignments(assessments, users["athletes"], users["psychologists"])
            self.stdout.write(self.style.SUCCESS(f'Created {len(assignments)} assigned assessments'))
            
            responses = self.create_responses(assessments, users["athletes"], assignments, options['responses'])
            self.stdout.write(self.style.SUCCESS(f'Created {len(responses)} assessment responses with question answers'))
            
            reviews = self.create_reviews(responses, users["psychologists"])
            self.stdout.write(self.style.SUCCESS(f'Created {len(reviews)} psychologist reviews'))
            
            recommendations = self.create_specialist_recommendations(responses, users["others"])
            self.stdout.write(self.style.SUCCESS(f'Created {len(recommendations)} specialist recommendations'))
            
            metrics = self.create_metrics(categories, users["psychologists"])
            self.stdout.write(self.style.SUCCESS(f'Created {len(metrics)} progress metrics'))
            
            progress = self.create_metric_progress(metrics, users["athletes"], responses)
            self.stdout.write(self.style.SUCCESS(f'Created {len(progress)} athlete metric progress records'))
            
        self.stdout.write(self.style.SUCCESS('Successfully generated test data'))

    def clear_data(self):
        # Clear all model data in reverse order of dependencies
        AthleteMetricProgress.objects.all().delete()
        ProgressMetric.objects.all().delete()
        RecommendedSpecialist.objects.all().delete()
        PsychologistReview.objects.all().delete()
        QuestionResponse.objects.all().delete()
        AssessmentResponse.objects.all().delete()
        AssignedAssessment.objects.all().delete()
        ResponseScale.objects.all().delete()
        Question.objects.all().delete()
        Assessment.objects.all().delete()
        AssessmentCategory.objects.all().delete()
        # Don't delete users as they might be referenced elsewhere

    def create_users(self, count):
        user_types = {
            'athlete': [],
            'psychologist': [],
            'coach': [],
            'nutritionist': [],
            'admin': []
        }
        
        # Create athletes with unique usernames
        for i in range(count):
            username = f'athlete_{uuid.uuid4().hex[:8]}'  # More unique username
            user = User.objects.create(
                username=username,
                email=f'{username}@example.com',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                user_type='athlete'
            )
            user_types['athlete'].append(user)
        
        # Create psychologists with unique usernames
        for i in range(count // 2):
            username = f'psych_{uuid.uuid4().hex[:8]}'
            user = User.objects.create(
                username=username,
                email=f'{username}@example.com',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                user_type='psychologist'
            )
            user_types['psychologist'].append(user)
        
        # Create other professional users with unique usernames
        for user_type in ['coach', 'nutritionist', 'admin']:
            for i in range(count // 4):
                username = f'{user_type}_{uuid.uuid4().hex[:8]}'
                user = User.objects.create(
                    username=username,
                    email=f'{username}@example.com',
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    user_type=user_type
                )
                user_types[user_type].append(user)
        
        return {
            "athletes": user_types['athlete'],
            "psychologists": user_types['psychologist'],
            "others": user_types['coach'] + user_types['nutritionist'] + user_types['admin']
        }

    def create_categories(self, count):
        categories = []
        category_data = [
            {'name': 'Anxiety Assessment', 'description': 'Tools to measure anxiety levels and symptoms', 'icon': 'nervous'},
            {'name': 'Depression Screening', 'description': 'Assessments for depressive symptoms and mood disorders', 'icon': 'sad'},
            {'name': 'Performance Confidence', 'description': 'Measures of athletic confidence and performance anxiety', 'icon': 'trophy'},
            {'name': 'Stress Management', 'description': 'Tools to assess stress levels and coping mechanisms', 'icon': 'brain'},
            {'name': 'Team Cohesion', 'description': 'Assessments of team dynamics and interpersonal relationships', 'icon': 'people'},
            {'name': 'Recovery Mindset', 'description': 'Psychological aspects of injury recovery', 'icon': 'heart'},
            {'name': 'Sleep Quality', 'description': 'Assessments of sleep patterns and quality', 'icon': 'moon'},
            {'name': 'Focus & Concentration', 'description': 'Tools to measure attention and focus', 'icon': 'target'},
            {'name': 'Burnout Risk', 'description': 'Assessments for burnout symptoms and risk factors', 'icon': 'fire'},
            {'name': 'Motivation & Goal Setting', 'description': 'Measures of athletic motivation and goal orientation', 'icon': 'flag'}
        ]
        
        # Use predefined data or generate random if needed more
        for i in range(count):
            if i < len(category_data):
                data = category_data[i]
            else:
                data = {
                    'name': f'Category {i+1}',
                    'description': fake.paragraph(),
                    'icon': random.choice(['star', 'circle', 'square', 'triangle'])
                }
            
            category = AssessmentCategory.objects.create(**data)
            categories.append(category)
        
        return categories

    def create_assessments(self, categories, psychologists, count):
        assessments = []
        
        assessment_templates = [
            {
                'title': 'Athlete Anxiety Scale (AAS)',
                'description': 'A comprehensive assessment of competition anxiety in athletes',
                'difficulty': 'intermediate',
                'time': 10
            },
            {
                'title': 'Sport Confidence Inventory',
                'description': 'Measures self-confidence in competitive athletic situations',
                'difficulty': 'basic',
                'time': 5
            },
            {
                'title': 'Athletic Burnout Questionnaire',
                'description': 'Identifies signs of burnout and overtraining in athletes',
                'difficulty': 'advanced',
                'time': 15
            },
            {
                'title': 'Performance Pressure Assessment',
                'description': 'Evaluates how athletes respond to high-pressure situations',
                'difficulty': 'intermediate',
                'time': 12
            },
            {
                'title': 'Sleep Quality for Athletes',
                'description': 'Assesses sleep patterns and their impact on recovery',
                'difficulty': 'basic',
                'time': 8
            }
        ]
        
        for i in range(count):
            # Use template if available, otherwise generate random
            if i < len(assessment_templates):
                template = assessment_templates[i]
                title = template['title']
                description = template['description']
                difficulty = template['difficulty']
                time = template['time']
            else:
                title = f'Assessment {i+1}: {fake.bs().capitalize()}'
                description = fake.paragraph()
                difficulty = random.choice(['basic', 'intermediate', 'advanced'])
                time = random.randint(5, 30)
            
            assessment = Assessment.objects.create(
                title=title,
                description=description,
                category=random.choice(categories),
                creator=random.choice(psychologists),
                difficulty_level=difficulty,
                status=random.choice(['draft', 'published', 'published', 'published', 'archived']),  # More likely to be published
                is_public=random.choice([True, True, False]),  # More likely to be public
                estimated_time_minutes=time,
                show_results_immediately=random.choice([True, False]),
                require_psychologist_review=random.choice([True, False]),
                allow_retake=random.choice([True, True, False]),  # More likely to allow retakes
                minimum_days_between_retakes=random.choice([1, 7, 14, 30])
            )
            
            # Create questions for this assessment
            self.create_questions(assessment)
            
            # Create scales for this assessment
            self.create_scales(assessment)
            
            assessments.append(assessment)
        
        return assessments

    def create_questions(self, assessment):
        # Common question templates based on category
        anxiety_questions = [
            "I feel nervous before competitions",
            "My heart races when thinking about upcoming events",
            "I have trouble sleeping before important competitions",
            "I worry about making mistakes during performances",
            "I experience physical tension before competing"
        ]
        
        confidence_questions = [
            "I believe in my abilities even when facing challenges",
            "I can perform well under pressure",
            "I maintain focus throughout competitions",
            "I recover quickly from setbacks during events",
            "I visualize myself succeeding before performances"
        ]
        
        recovery_questions = [
            "I follow proper recovery protocols after training",
            "I get adequate sleep most nights",
            "I practice relaxation techniques regularly",
            "I maintain a balanced diet for recovery",
            "I listen to my body's signals about rest needs"
        ]
        
        # Choose question set based on category name
        category_name = assessment.category.name.lower()
        if 'anxiety' in category_name or 'stress' in category_name:
            question_templates = anxiety_questions
        elif 'confidence' in category_name or 'performance' in category_name:
            question_templates = confidence_questions
        elif 'recovery' in category_name or 'sleep' in category_name:
            question_templates = recovery_questions
        else:
            question_templates = []
        
        # Number of questions based on estimated time
        num_questions = max(3, min(20, assessment.estimated_time_minutes // 2))
        
        for i in range(num_questions):
            # Use template if available
            if i < len(question_templates):
                question_text = question_templates[i]
            else:
                question_text = fake.sentence()
            
            question_type = random.choice(['likert_5', 'likert_7', 'multiple_choice', 'yes_no'])
            
            # Prepare question data
            question_data = {
                'assessment': assessment,
                'text': question_text,
                'help_text': fake.sentence() if random.choice([True, False]) else None,
                'question_type': question_type,
                'required': random.choice([True, True, True, False]),  # Most questions required
                'order': i + 1,
                'reverse_scoring': random.choice([True, False]),
                'weight': round(random.uniform(0.5, 1.5), 1)
            }
            
            # Add type-specific fields
            if question_type == 'multiple_choice':
                question_data['choices'] = [
                    {"value": "1", "label": "Not at all"},
                    {"value": "2", "label": "Slightly"},
                    {"value": "3", "label": "Moderately"},
                    {"value": "4", "label": "Very much"},
                    {"value": "5", "label": "Extremely"}
                ]
            elif question_type == 'slider':
                question_data['min_value'] = 0
                question_data['max_value'] = 10
                question_data['step'] = 1
            
            Question.objects.create(**question_data)

    def create_scales(self, assessment):
        # Create 1-3 scales for each assessment
        scale_count = random.randint(1, 3)
        
        scale_templates = [
            {
                'name': 'Overall Score',
                'description': 'Combined score across all dimensions',
                'min_score': 0,
                'max_score': 100,
                'ranges': [
                    {"min": 0, "max": 30, "label": "Low", "description": "Significant concerns present", "color": "#e74c3c"},
                    {"min": 31, "max": 70, "label": "Moderate", "description": "Some concerns that should be addressed", "color": "#f39c12"},
                    {"min": 71, "max": 100, "label": "High", "description": "Healthy functioning in this area", "color": "#2ecc71"}
                ]
            },
            {
                'name': 'Anxiety Level',
                'description': 'Measure of competition anxiety',
                'min_score': 0,
                'max_score': 100,
                'ranges': [
                    {"min": 0, "max": 40, "label": "Minimal", "description": "Healthy competitive focus", "color": "#2ecc71"},
                    {"min": 41, "max": 70, "label": "Moderate", "description": "Some performance anxiety", "color": "#f39c12"},
                    {"min": 71, "max": 100, "label": "High", "description": "Significant anxiety that may impact performance", "color": "#e74c3c"}
                ]
            },
            {
                'name': 'Confidence',
                'description': 'Level of self-belief and performance confidence',
                'min_score': 0,
                'max_score': 100,
                'ranges': [
                    {"min": 0, "max": 30, "label": "Low", "description": "Significant confidence issues", "color": "#e74c3c"},
                    {"min": 31, "max": 70, "label": "Developing", "description": "Building confidence but improvement needed", "color": "#f39c12"},
                    {"min": 71, "max": 100, "label": "Strong", "description": "Healthy confidence level", "color": "#2ecc71"}
                ]
            }
        ]
        
        for i in range(scale_count):
            if i < len(scale_templates):
                template = scale_templates[i]
                scale_data = template
            else:
                scale_data = {
                    'name': f'Scale {i+1}',
                    'description': fake.sentence(),
                    'min_score': 0,
                    'max_score': 100,
                    'ranges': [
                        {"min": 0, "max": 33, "label": "Low", "description": fake.sentence(), "color": "#e74c3c"},
                        {"min": 34, "max": 66, "label": "Medium", "description": fake.sentence(), "color": "#f39c12"},
                        {"min": 67, "max": 100, "label": "High", "description": fake.sentence(), "color": "#2ecc71"}
                    ]
                }
            
            ResponseScale.objects.create(
                assessment=assessment,
                **scale_data
            )

    def create_assignments(self, assessments, athletes, psychologists):
        assignments = []
        
        # Create 1-3 assignments per athlete
        for athlete in athletes:
            num_assignments = random.randint(1, 3)
            for _ in range(num_assignments):
                # Only assign published assessments
                published_assessments = [a for a in assessments if a.status == 'published']
                if not published_assessments:
                    continue
                    
                assessment = random.choice(published_assessments)
                psychologist = random.choice(psychologists)
                
                # Set due date between 1-30 days from now
                due_days = random.randint(1, 30)
                due_date = timezone.now() + datetime.timedelta(days=due_days)
                
                assignment = AssignedAssessment.objects.create(
                    assessment=assessment,
                    athlete=athlete,
                    assigned_by=psychologist,
                    due_date=due_date if random.choice([True, True, False]) else None,  # Some without due dates
                    instructions=fake.paragraph() if random.choice([True, False]) else None,
                    completed=False
                )
                
                assignments.append(assignment)
        
        return assignments

    def create_responses(self, assessments, athletes, assignments, count):
        responses = []
        completed_count = 0
        
        # First create responses for assigned assessments
        for assignment in assignments:
            # 70% chance of completing an assigned assessment
            if random.random() < 0.7:
                # Create response with completed status
                response = self.create_single_response(
                    assignment.assessment, 
                    assignment.athlete, 
                    assignment=assignment, 
                    completed=True
                )
                responses.append(response)
                completed_count += 1
        
        # Create additional random responses to reach desired count
        while len(responses) < count:
            # Select random athlete and published assessment
            athlete = random.choice(athletes)
            published_assessments = [a for a in assessments if a.status == 'published']
            
            if not published_assessments:
                break
                
            assessment = random.choice(published_assessments)
            
            # 70% completed, 30% in progress
            completed = random.random() < 0.7
            
            # Create response
            response = self.create_single_response(assessment, athlete, completed=completed)
            responses.append(response)
            
            if completed:
                completed_count += 1
        
        return responses

    def create_single_response(self, assessment, athlete, assignment=None, completed=True):
        # Calculate dates
        started_at = timezone.now() - datetime.timedelta(days=random.randint(1, 60))
        
        # For completed responses, set completion time and calculate scores
        completed_at = None
        completion_time = None
        status = 'in_progress'
        scores = None
        
        if completed:
            # Complete between 5 minutes and 2 hours after starting
            completion_time = random.randint(5*60, 120*60)  # seconds
            completed_at = started_at + datetime.timedelta(seconds=completion_time)
            status = 'completed'
            
            # Generate fake scores
            scales = ResponseScale.objects.filter(assessment=assessment)
            scores = {}
            for scale in scales:
                scores[scale.name] = round(random.uniform(scale.min_score, scale.max_score), 1)
        
        # Create the response
        response = AssessmentResponse.objects.create(
            assessment=assessment,
            athlete=athlete,
            started_at=started_at,
            completed_at=completed_at,
            status=status,
            assignment=assignment,
            scores=scores,
            completion_time_seconds=completion_time
        )
        
        # Create answers to questions if completed
        if completed:
            self.create_question_responses(response)
            
            # Update assignment if exists
            if assignment:
                assignment.completed = True
                assignment.save()
        
        return response

    def create_question_responses(self, assessment_response):
        questions = Question.objects.filter(assessment=assessment_response.assessment)
        
        for question in questions:
            # Generate answer based on question type
            if question.question_type == 'likert_5':
                answer = {"value": random.randint(1, 5)}
            elif question.question_type == 'likert_7':
                answer = {"value": random.randint(1, 7)}
            elif question.question_type == 'yes_no':
                answer = {"value": random.choice(["yes", "no"])}
            elif question.question_type == 'multiple_choice':
                if question.choices:
                    choices = question.choices
                    answer = {"value": choices[random.randint(0, len(choices)-1)]["value"]}
                else:
                    answer = {"value": str(random.randint(1, 5))}
            elif question.question_type == 'slider':
                min_val = question.min_value or 0
                max_val = question.max_value or 10
                answer = {"value": random.randint(min_val, max_val)}
            elif question.question_type == 'text':
                answer = {"value": fake.paragraph()}
            else:
                answer = {"value": "No response"}
            
            # Create response
            QuestionResponse.objects.create(
                assessment_response=assessment_response,
                question=question,
                answer_value=answer,
                answered_at=assessment_response.completed_at or timezone.now()
            )

    def create_reviews(self, responses, psychologists):
        reviews = []
        
        # Only review completed responses where review is required
        completed_responses = [r for r in responses if r.status == 'completed' and r.assessment.require_psychologist_review]
        
        for response in completed_responses:
            # 80% chance of being reviewed
            if random.random() < 0.8:
                review_date = response.completed_at + datetime.timedelta(days=random.randint(1, 14))
                
                # Create score adjustments for ~30% of reviews
                score_adjustments = None
                if random.random() < 0.3 and response.scores:
                    score_adjustments = {}
                    for scale_name, score in response.scores.items():
                        # Adjust by ±15%
                        adjustment = round(score * random.uniform(-0.15, 0.15), 1)
                        score_adjustments[scale_name] = {
                            "original": score,
                            "adjusted": round(score + adjustment, 1),
                            "reason": random.choice([
                                "Clinical observation suggests adjustment",
                                "Based on additional information",
                                "Response patterns indicate modification needed",
                                "Historical data comparison"
                            ])
                        }
                
                review = PsychologistReview.objects.create(
                    assessment_response=response,
                    psychologist=random.choice(psychologists),
                    review_date=review_date,
                    comments=fake.paragraph(),
                    recommendations="\n".join(fake.sentences(random.randint(2, 5))),
                    follow_up_needed=random.choice([True, False]),
                    score_adjustments=score_adjustments
                )
                
                # Update response status
                response.status = 'reviewed'
                response.save()
                
                reviews.append(review)
        
        return reviews

    def create_specialist_recommendations(self, responses, specialists):
        recommendations = []
        
        # Only make recommendations for reviewed responses
        reviewed_responses = [r for r in responses if r.status == 'reviewed']
        
        for response in reviewed_responses:
            # 50% chance of specialist recommendation
            if random.random() < 0.5:
                # Generate 1-3 recommendations
                num_recommendations = random.randint(1, 3)
                for i in range(num_recommendations):
                    recommendation = RecommendedSpecialist.objects.create(
                        assessment_response=response,
                        specialist=random.choice(specialists),
                        recommendation_reason=fake.paragraph(),
                        priority=random.randint(1, 3),
                        created_at=response.completed_at + datetime.timedelta(days=random.randint(1, 5))
                    )
                    recommendations.append(recommendation)
        
        return recommendations

    def create_metrics(self, categories, psychologists):
        metrics = []
        
        metric_templates = [
            {
                'name': 'Competitive Anxiety Index',
                'description': 'Measures level of anxiety experienced during competitions',
                'min_value': 0,
                'max_value': 100,
                'default_goal': 40,
                'higher_is_better': False
            },
            {
                'name': 'Athletic Confidence Score',
                'description': 'Assesses self-confidence in competitive situations',
                'min_value': 0,
                'max_value': 100,
                'default_goal': 80,
                'higher_is_better': True
            },
            {
                'name': 'Mental Resilience Rating',
                'description': 'Measures ability to recover from setbacks and maintain focus',
                'min_value': 0,
                'max_value': 10,
                'default_goal': 8,
                'higher_is_better': True
            },
            {
                'name': 'Sleep Quality Index',
                'description': 'Rating of sleep quality and its impact on recovery',
                'min_value': 0,
                'max_value': 10,
                'default_goal': 8,
                'higher_is_better': True
            },
            {
                'name': 'Burnout Risk Score',
                'description': 'Assessment of current burnout risk level',
                'min_value': 0,
                'max_value': 100,
                'default_goal': 20,
                'higher_is_better': False
            }
        ]
        
        # Create metrics for each category
        for category in categories:
            # Create 1-2 metrics per category
            num_metrics = random.randint(1, 2)
            
            for i in range(num_metrics):
                # Use template if available
                if len(metrics) < len(metric_templates):
                    template = metric_templates[len(metrics)]
                    metric_data = template
                else:
                    metric_data = {
                        'name': f'{category.name} Metric {i+1}',
                        'description': fake.sentence(),
                        'min_value': 0,
                        'max_value': random.choice([10, 100]),
                        'default_goal': None,
                        'higher_is_better': random.choice([True, False])
                    }
                    
                    # Set default goal if applicable
                    if metric_data['higher_is_better']:
                        metric_data['default_goal'] = round(metric_data['max_value'] * 0.8)
                    else:
                        metric_data['default_goal'] = round(metric_data['max_value'] * 0.2)
                
                metric = ProgressMetric.objects.create(
                    name=metric_data['name'],
                    description=metric_data['description'],
                    assessment_category=category,
                    created_by=random.choice(psychologists),
                    min_value=metric_data['min_value'],
                    max_value=metric_data['max_value'],
                    default_goal=metric_data['default_goal'],
                    higher_is_better=metric_data['higher_is_better']
                )
                
                metrics.append(metric)
        
        return metrics

    def create_metric_progress(self, metrics, athletes, responses):
        progress_records = []
        
        # Create progress entries for each athlete on each metric
        for athlete in athletes:
            # Select 1-3 metrics for this athlete
            if not metrics:
                continue
                
            selected_metrics = random.sample(metrics, min(random.randint(1, 3), len(metrics)))
            
            for metric in selected_metrics:
                # Create 3-10 entries over time
                num_entries = random.randint(3, 10)
                
                # Get responses from this athlete
                athlete_responses = [r for r in responses if r.athlete == athlete and r.status == 'completed']
                
                for i in range(num_entries):
                    # Gradually improve for most metrics over time
                    if metric.higher_is_better:
                        # Start low, gradually increase
                        progress = metric.min_value + (metric.max_value - metric.min_value) * (i / num_entries) * random.uniform(0.3, 1.0)
                    else:
                        # Start high, gradually decrease
                        progress = metric.max_value - (metric.max_value - metric.min_value) * (i / num_entries) * random.uniform(0.3, 1.0)
                    
                    # Add some randomness
                    progress += random.uniform(-5, 5)
                    progress = max(metric.min_value, min(metric.max_value, progress))
                    
                    # Set date, going back in time
                    date = timezone.now().date() - datetime.timedelta(days=180 - (180 * i / num_entries))
                    
                    # Link to response if available and timing matches
                    response = None
                    if athlete_responses:
                        matching_responses = [r for r in athlete_responses if abs((r.completed_at.date() - date).days) < 3]
                        if matching_responses:
                            response = random.choice(matching_responses)
                    
                    progress_record = AthleteMetricProgress.objects.create(
                        athlete=athlete,
                        metric=metric,
                        value=round(progress, 1),
                        date=date,
                        notes=fake.sentence() if random.choice([True, False]) else None,
                        assessment_response=response
                    )
                    
                    progress_records.append(progress_record)
        
        return progress_records