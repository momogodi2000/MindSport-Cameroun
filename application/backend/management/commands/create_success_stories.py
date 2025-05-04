from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta, datetime
import random
import pytz
from faker import Faker

from backend.models import (
    Category,
    Thread,
    Comment,
    MentorshipProgram,
    MentorshipRelationship,
    AnonymousQuestion,
    SuccessStory,
    SupportGroup,
    SupportGroupParticipant,
    SupportGroupSession,
    SupportGroupAttendance,
    User
)

UserModel = get_user_model()

class Command(BaseCommand):
    help = 'Generates sample data for the MentalApp application'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker()
        self.users = []
        self.categories = []
        self.threads = []
        self.comments = []
        self.mentorship_programs = []
        self.support_groups = []

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=50, help='Number of users to create')
        parser.add_argument('--categories', type=int, default=10, help='Number of forum categories to create')
        parser.add_argument('--threads', type=int, default=100, help='Number of forum threads to create')
        parser.add_argument('--comments', type=int, default=500, help='Number of forum comments to create')
        parser.add_argument('--programs', type=int, default=5, help='Number of mentorship programs to create')
        parser.add_argument('--questions', type=int, default=30, help='Number of anonymous questions to create')
        parser.add_argument('--stories', type=int, default=20, help='Number of success stories to create')
        parser.add_argument('--groups', type=int, default=15, help='Number of support groups to create')
        parser.add_argument('--force', action='store_true', help='Force creation even if data exists')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data generation for MentalApp...'))
        
        # Create data based on command arguments
        self.create_users(options['users'], force=options['force'])
        self.create_forum_categories(options['categories'], force=options['force'])
        self.create_forum_threads(options['threads'], force=options['force'])
        self.create_forum_comments(options['comments'], force=options['force'])
        self.create_mentorship_programs(options['programs'], force=options['force'])
        self.create_mentorship_relations(force=options['force'])
        self.create_anonymous_questions(options['questions'], force=options['force'])
        self.create_success_stories(options['stories'], force=options['force'])
        self.create_support_groups(options['groups'], force=options['force'])
        self.create_support_group_participants(force=options['force'])
        self.create_support_group_sessions(force=options['force'])
        self.create_support_group_attendance(force=options['force'])
        
        self.stdout.write(self.style.SUCCESS('Successfully generated sample data!'))

    def check_existing_data(self, model, force=False):
        """Check if data already exists for a model and return existing instances"""
        existing = model.objects.all()
        if existing.exists() and not force:
            self.stdout.write(self.style.WARNING(f'{model.__name__} data already exists ({existing.count()} records). Skipping...'))
            return list(existing)
        return []

    def create_users(self, count, force=False):
        """Create sample users with realistic profiles"""
        existing_users = self.check_existing_data(UserModel, force)
        if existing_users and not force:
            self.users = existing_users
            return
            
        self.stdout.write('Creating users...')
        
        # Create superuser
        admin_user = UserModel.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = UserModel.objects.create_superuser(
                username='admin',
                email='admin@mentalapp.com',
                password='adminpassword',
                user_type='admin'
            )
            self.stdout.write(self.style.SUCCESS('Created superuser: admin@mentalapp.com'))
        
        # User roles we want to ensure exist
        roles = [
            {'user_type': 'psychologist', 'is_staff': True},
            {'user_type': 'coach', 'is_staff': False},
            {'user_type': 'nutritionist', 'is_staff': True},
            {'user_type': 'athlete', 'is_staff': True}
        ]
        
        # Create base users with specific roles first
        for role in roles:
            username = f"{role['user_type']}_user_{random.randint(1000, 9999)}"
            email = f"{username}@example.com"
            
            if UserModel.objects.filter(username=username).exists():
                continue
                
            user = UserModel.objects.create_user(
                username=username,
                email=email,
                password='password123',
                first_name=self.fake.first_name(),
                last_name=self.fake.last_name(),
                is_staff=role['is_staff'],
                user_type=role['user_type'],
                sport=random.choice([choice[0] for choice in UserModel.SPORT_CHOICES]),
                level=random.choice([choice[0] for choice in UserModel.LEVEL_CHOICES]),
                years_experience=random.randint(0, 20) if role['user_type'] != 'athlete' else None,
                qualifications=self.fake.job() if role['user_type'] != 'athlete' else None,
                town=self.fake.city(),
                account_status='active',
                terms_accepted=True,
                date_joined=self.fake.date_time_between(start_date='-2y', end_date='now', tzinfo=pytz.UTC)
            )
            self.users.append(user)
            self.stdout.write(f'Created user with role: {username}')
        
        # Create random users
        for i in range(count):
            try:
                first_name = self.fake.first_name()
                last_name = self.fake.last_name()
                
                # Generate a unique username
                base_username = f"{first_name.lower()}{last_name.lower()}"
                username = base_username[:25]
                suffix = 1
                
                while UserModel.objects.filter(username=username).exists():
                    username = f"{base_username[:20]}{suffix}"
                    suffix += 1
                    
                # Random user type with different probabilities
                user_type = random.choices(
                    ['athlete', 'psychologist', 'coach', 'nutritionist'],
                    weights=[0.7, 0.1, 0.1, 0.1]
                )[0]
                
                user = UserModel.objects.create_user(
                    username=username,
                    email=self.fake.email(),
                    password='password123',
                    first_name=first_name,
                    last_name=last_name,
                    is_staff=random.random() < 0.1,
                    user_type=user_type,
                    sport=random.choice([choice[0] for choice in UserModel.SPORT_CHOICES]) if user_type == 'athlete' else None,
                    level=random.choice([choice[0] for choice in UserModel.LEVEL_CHOICES]) if user_type == 'athlete' else None,
                    years_experience=random.randint(1, 30) if user_type != 'athlete' else None,
                    qualifications=self.fake.job() if user_type != 'athlete' else None,
                    town=self.fake.city(),
                    account_status=random.choice(['active', 'pending', 'active', 'active']),
                    terms_accepted=True,
                    date_joined=self.fake.date_time_between(start_date='-2y', end_date='now', tzinfo=pytz.UTC)
                )
                self.users.append(user)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating user: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(self.users)} users'))

    def create_forum_categories(self, count, force=False):
        """Create forum categories with a hierarchy"""
        existing_categories = self.check_existing_data(Category, force)
        if existing_categories and not force:
            self.categories = existing_categories
            return
            
        self.stdout.write('Creating forum categories...')
        
        # First create all main categories
        main_categories = [
            {"name": "Mental Health Support", "description": "Discuss mental health challenges specific to combat sports"},
            {"name": "Injury Recovery", "description": "Share experiences and advice on recovering from injuries"},
            {"name": "Training Mindset", "description": "Techniques to improve mental toughness and focus"},
            {"name": "Competition Anxiety", "description": "Support for dealing with pre-competition anxiety"},
            {"name": "Sport-Specific Forums", "description": "Discussions organized by combat sport"}
        ]
        
        for cat_data in main_categories:
            if Category.objects.filter(name=cat_data["name"]).exists():
                continue
                
            category = Category.objects.create(
                name=cat_data["name"],
                description=cat_data["description"],
                slug=slugify(cat_data["name"]),
                order=main_categories.index(cat_data)
            )
            self.categories.append(category)
        
        # Then create sport subcategories under Sport-Specific Forums
        sport_category = Category.objects.filter(name="Sport-Specific Forums").first()
        if sport_category:
            sports = ['boxing', 'wrestling', 'judo', 'karate', 'taekwondo', 'mma', 'other']
            for sport in sports:
                sport_name = f"{sport.title()} Discussion"
                if Category.objects.filter(name=sport_name).exists():
                    continue
                    
                sport_category = Category.objects.create(
                    name=sport_name,
                    description=f"Topics specific to {sport.title()} mental health",
                    slug=slugify(f"{sport}-discussion"),
                    order=sports.index(sport)
                )
                self.categories.append(sport_category)
        
        # Finally create additional categories with parents
        for i in range(count - len(self.categories)):
            try:
                # Only set parent if we have categories to choose from
                parent = random.choice(self.categories[:5]) if self.categories else None
                
                name = self.fake.catch_phrase()
                if Category.objects.filter(name=name).exists():
                    continue
                    
                category = Category.objects.create(
                    name=name,
                    description=self.fake.paragraph(),
                    slug=slugify(f"{self.fake.word()}-{random.randint(1, 999)}"),
                    order=i + 10,
                    parent=parent  # Add parent field if your model has it
                )
                self.categories.append(category)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating category: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(self.categories)} forum categories'))

    def create_forum_threads(self, count, force=False):
        """Create forum threads across categories"""
        existing_threads = self.check_existing_data(Thread, force)
        if existing_threads and not force:
            self.threads = existing_threads
            return
            
        self.stdout.write('Creating forum threads...')
        
        # Predefined thread titles for realism
        thread_topics = [
            "How to deal with pre-fight anxiety?",
            "Depression after losing a major competition",
            "Managing weight cut stress",
            "Building confidence after a knockout",
            "Mental recovery techniques after injury",
            "Visualization exercises that work",
            "Balancing training with mental health",
            "How to stay motivated during plateaus",
            "Dealing with aggressive coaches",
            "Imposter syndrome in competition",
            "Post-tournament depression",
            "Fear of re-injury when returning",
            "Meditation techniques for fighters",
            "Handling pressure from family/friends",
            "Mental health resources for athletes"
        ]
        
        # Create threads with predefined topics first
        for topic in thread_topics:
            category = random.choice(self.categories)
            author = random.choice(self.users)
            is_anonymous = random.random() < 0.2  # 20% chance of anonymous
            
            if Thread.objects.filter(title=topic, category=category).exists():
                continue
                
            thread = Thread.objects.create(
                title=topic,
                slug=slugify(f"{topic}-{random.randint(1, 99)}"),
                category=category,
                author=author,
                content=self.fake.paragraph(nb_sentences=5),
                is_pinned=random.random() < 0.1,  # 10% chance of being pinned
                is_locked=random.random() < 0.05,  # 5% chance of being locked
                is_active=True,
                view_count=random.randint(5, 500),
                created_at=self.fake.date_time_between(start_date='-1y', end_date='now', tzinfo=pytz.UTC)
            )
            self.threads.append(thread)
        
        # Create random threads for the remaining count
        for i in range(count - len(thread_topics)):
            try:
                category = random.choice(self.categories)
                author = random.choice(self.users)
                is_anonymous = random.random() < 0.2  # 20% chance of anonymous
                
                title = self.fake.sentence(nb_words=6).rstrip('.')
                
                if Thread.objects.filter(title=title, category=category).exists():
                    continue
                    
                thread = Thread.objects.create(
                    title=title,
                    slug=slugify(f"{title[:30]}-{random.randint(1, 999)}"),
                    category=category,
                    author=author,
                    content=self.fake.paragraph(nb_sentences=5),
                    is_pinned=random.random() < 0.1,
                    is_locked=random.random() < 0.05,
                    is_active=True,
                    view_count=random.randint(5, 500),
                    created_at=self.fake.date_time_between(start_date='-1y', end_date='now', tzinfo=pytz.UTC)
                )
                self.threads.append(thread)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating thread: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(self.threads)} forum threads'))

    def create_forum_comments(self, count, force=False):
        """Create forum comments (replies) for threads"""
        existing_comments = self.check_existing_data(Comment, force)
        if existing_comments and not force:
            self.comments = existing_comments
            return
            
        self.stdout.write('Creating forum comments...')
        
        # Create at least one comment for each thread first
        for thread in self.threads:
            created_at = thread.created_at
            author = thread.author if random.random() < 0.3 else random.choice(self.users)
            
            if Comment.objects.filter(thread=thread, author=author).exists():
                continue
                
            comment = Comment.objects.create(
                thread=thread,
                author=author,
                content=self.fake.paragraph(nb_sentences=5),
                is_active=True,
                created_at=created_at
            )
            self.comments.append(comment)
        
        # Create additional random comments
        for i in range(count - len(self.threads)):
            try:
                thread = random.choice(self.threads)
                author = random.choice(self.users)
                
                # Comment should be after thread creation but before now
                thread_created = thread.created_at
                comment_date = self.fake.date_time_between(
                    start_date=thread_created, 
                    end_date='now', 
                    tzinfo=pytz.UTC
                )
                
                # 10% chance of being a reply to another comment
                parent = None
                if random.random() < 0.1 and self.comments:
                    parent = random.choice(self.comments)
                
                comment = Comment.objects.create(
                    thread=thread,
                    author=author,
                    content=self.fake.paragraph(nb_sentences=random.randint(1, 10)),
                    parent=parent,
                    is_active=True,
                    created_at=comment_date
                )
                self.comments.append(comment)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating comment: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(self.comments)} forum comments'))

    def create_mentorship_programs(self, count, force=False):
        """Create mentorship programs"""
        existing_programs = self.check_existing_data(MentorshipProgram, force)
        if existing_programs and not force:
            self.mentorship_programs = existing_programs
            return
            
        self.stdout.write('Creating mentorship programs...')
        
        # Predefined program names and descriptions for realism
        program_data = [
            {
                "name": "Combat Sports Mental Resilience Program",
                "description": "A structured 8-week program focused on building mental toughness for combat sports athletes. Includes weekly sessions on visualization, anxiety management, and performance psychology."
            },
            {
                "name": "Return from Injury Support",
                "description": "This program pairs athletes recovering from major injuries with mentors who have successfully returned to competition. Focus on overcoming fear, rebuilding confidence, and setting realistic goals."
            },
            {
                "name": "Pre-Competition Anxiety Management",
                "description": "A targeted 4-week program designed to help athletes manage competition anxiety. Includes breathing techniques, cognitive restructuring, and performance routines."
            },
            {
                "name": "Combat Sports Life Balance",
                "description": "For athletes struggling with balancing training, competition, and personal life. Mentors provide guidance on time management, priority setting, and preventing burnout."
            },
            {
                "name": "Youth Combat Sports Mental Health",
                "description": "Specially designed for young athletes (14-18) in combat sports, focusing on healthy relationship with the sport, managing parental expectations, and developing a growth mindset."
            }
        ]
        
        sports = ['boxing', 'wrestling', 'judo', 'karate', 'taekwondo', 'mma', 'other']
        status_choices = ['draft', 'active', 'paused', 'completed']
        status_weights = [0.1, 0.5, 0.2, 0.2]  # Weighted probabilities
        
        # Create programs using predefined data
        for program in program_data:
            if MentorshipProgram.objects.filter(name=program["name"]).exists():
                continue
                
            # Find coordinators (coaches with staff privileges ideally)
            potential_coordinators = [u for u in self.users if u.user_type in ['coach', 'psychologist']]
            if not potential_coordinators:
                potential_coordinators = self.users
                
            coordinator = random.choice(potential_coordinators)
            
            # Create program dates
            start_date = self.fake.date_between(start_date='-3m', end_date='+3m')
            end_date = start_date + timedelta(days=random.randint(30, 90))
            
            # Determine status based on dates and randomness
            if start_date > timezone.now().date():
                status = 'draft'
            elif end_date < timezone.now().date():
                status = 'completed'
            else:
                status = random.choices(status_choices, weights=status_weights)[0]
            
            mentorship_program = MentorshipProgram.objects.create(
                name=program["name"],
                description=program["description"],
                is_active=status == 'active',
                start_date=start_date,
                end_date=end_date,
                created_at=self.fake.date_time_between(start_date='-1y', end_date='now', tzinfo=pytz.UTC)
            )
            self.mentorship_programs.append(mentorship_program)
        
        # Create additional random programs if needed
        for i in range(count - len(program_data)):
            program_name = f"{random.choice(['Mental', 'Mindset', 'Resilience', 'Focus', 'Performance'])} {random.choice(['Development', 'Training', 'Enhancement', 'Coaching'])} Program"
            
            if MentorshipProgram.objects.filter(name=program_name).exists():
                continue
                
            start_date = self.fake.date_between(start_date='-6m', end_date='+3m')
            end_date = start_date + timedelta(days=random.randint(30, 120))
            
            if start_date > timezone.now().date():
                status = 'draft'
            elif end_date < timezone.now().date():
                status = 'completed'
            else:
                status = random.choices(status_choices, weights=status_weights)[0]
            
            mentorship_program = MentorshipProgram.objects.create(
                name=program_name,
                description=self.fake.paragraph(nb_sentences=3),
                is_active=status == 'active',
                start_date=start_date,
                end_date=end_date,
                created_at=self.fake.date_time_between(start_date='-1y', end_date='now', tzinfo=pytz.UTC)
            )
            self.mentorship_programs.append(mentorship_program)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(self.mentorship_programs)} mentorship programs'))

    def create_mentorship_relations(self, force=False):
        """Create mentorship relations for programs"""
        existing_relations = self.check_existing_data(MentorshipRelationship, force)
        if existing_relations and not force:
            return
            
        self.stdout.write('Creating mentorship relations...')
        
        relation_count = 0
        # For each program, create mentor-mentee pairs
        for program in self.mentorship_programs:
            # Determine number of relationships to create
            num_relations = random.randint(3, 10)
            
            # Get potential mentors (coaches and psychologists)
            potential_mentors = [u for u in self.users if u.user_type in ['coach', 'psychologist']]
            if not potential_mentors:
                potential_mentors = self.users
                
            # Get potential mentees (athletes)
            potential_mentees = [u for u in self.users if u.user_type == 'athlete']
            if not potential_mentees:
                potential_mentees = self.users
                
            for i in range(num_relations):
                try:
                    # Get random mentor and mentee
                    mentor = random.choice(potential_mentors)
                    mentee = random.choice(potential_mentees)
                    
                    # Skip if this relationship already exists
                    if MentorshipRelationship.objects.filter(program=program, mentor=mentor, mentee=mentee).exists():
                        continue
                        
                    # Determine status
                    status = random.choice(['pending', 'active', 'completed', 'cancelled'])
                    
                    MentorshipRelationship.objects.create(
                        program=program,
                        mentor=mentor,
                        mentee=mentee,
                        status=status,
                        goals=self.fake.paragraph(nb_sentences=1) if random.random() < 0.7 else None,
                        start_date=program.start_date,
                        created_at=self.fake.date_time_between(start_date=program.created_at, end_date='now', tzinfo=pytz.UTC)
                    )
                    relation_count += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Error creating relationship: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Created {relation_count} mentorship relations'))

    def create_anonymous_questions(self, count, force=False):
        """Create anonymous questions"""
        existing_questions = self.check_existing_data(AnonymousQuestion, force)
        if existing_questions and not force:
            return
            
        self.stdout.write('Creating anonymous questions...')
        
        # Realistic question titles for combat sports mental health
        question_titles = [
            "How to deal with anxiety before first competition?",
            "Coping with a loss in front of friends and family",
            "Mental recovery after a knockout",
            "Depression during injury rehabilitation",
            "Fear of getting back in the ring",
            "Handling criticism from coach",
            "Performance anxiety tips",
            "Balancing college and training",
            "Post-competition mood swings",
            "Mental preparation rituals",
            "Dealing with weight cut stress",
            "Losing motivation after years of training",
            "Managing anger during matches",
            "How to stop comparing myself to teammates",
            "Impostor syndrome in combat sports"
        ]
        
        status_choices = ['pending', 'answered', 'rejected']
        status_weights = [0.2, 0.5, 0.1]  # Weighted probabilities
        
        question_count = 0
        # Create questions with predefined titles first
        for title in question_titles:
            author = random.choice(self.users)
            
            status = random.choices(status_choices, weights=status_weights)[0]
            
            # If answered, add answer details
            answer = None
            answered_by = None
            answered_at = None
            if status == 'answered':
                # Find staff member to answer
                potential_answerers = [u for u in self.users if u.is_staff]
                if not potential_answerers:
                    potential_answerers = self.users
                
                answered_by = random.choice(potential_answerers)
                answer = self.fake.paragraph(nb_sentences=3)
                # Set answered date after question creation but before now
                created_date = self.fake.date_time_between(start_date='-1y', end_date='-1d', tzinfo=pytz.UTC)
                answered_at = self.fake.date_time_between(start_date=created_date, end_date='now', tzinfo=pytz.UTC)
            
            AnonymousQuestion.objects.create(
                title=title,
                content=self.fake.paragraph(nb_sentences=random.randint(2, 5)),
                asker=author,
                status=status,
                response=answer,
                respondent=answered_by,
                is_public=status == 'answered',
                created_at=created_date if status == 'answered' else self.fake.date_time_between(start_date='-1y', end_date='now', tzinfo=pytz.UTC)
            )
            question_count += 1
        
        # Create random questions for remaining count
        for i in range(count - len(question_titles)):
            author = random.choice(self.users)
            
            status = random.choices(status_choices, weights=status_weights)[0]
            
            title = self.fake.sentence(nb_words=random.randint(5, 10)).rstrip('.')
            
            # If answered, add answer details
            answer = None
            answered_by = None
            answered_at = None
            created_date = self.fake.date_time_between(start_date='-1y', end_date='-1d', tzinfo=pytz.UTC)
            
            if status == 'answered':
                # Find staff member to answer
                potential_answerers = [u for u in self.users if u.is_staff]
                if not potential_answerers:
                    potential_answerers = self.users
                
                answered_by = random.choice(potential_answerers)
                answer = self.fake.paragraph(nb_sentences=3)
                # Set answered date after question creation but before now
                answered_at = self.fake.date_time_between(start_date=created_date, end_date='now', tzinfo=pytz.UTC)
            
            AnonymousQuestion.objects.create(
                title=title,
                content=self.fake.paragraph(nb_sentences=random.randint(2, 5)),
                asker=author,
                status=status,
                response=answer,
                respondent=answered_by,
                is_public=status == 'answered',
                created_at=created_date
            )
            question_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {question_count} anonymous questions'))

    def create_success_stories(self, count, force=False):
        """Create success stories"""
        existing_stories = self.check_existing_data(SuccessStory, force)
        if existing_stories and not force:
            return
            
        self.stdout.write('Creating success stories...')
        
        # Realistic success story titles
        story_titles = [
            "How mental training helped me win my first championship",
            "Overcoming competition anxiety: My journey",
            "From panic attacks to podium: A fighter's story",
            "Finding balance: My path to mental wellness while competing",
            "The injury that changed my mindset forever",
            "How therapy made me a better fighter",
            "Breaking the stigma: My experience with depression as an athlete",
            "The power of visualization in my comeback story",
            "From burnout to gold medal: How I regained my love for the sport",
            "How mentorship changed my mental approach to fighting"
        ]
        
        story_count = 0
        # Create stories with predefined titles first
        for title in story_titles:
            author = random.choice(self.users)
            is_anonymous = random.random() < 0.3  # 30% chance of being anonymous
            is_featured = random.random() < 0.2  # 20% chance of being featured
            
            if SuccessStory.objects.filter(title=title, author=author).exists():
                continue
                
            content = "\n\n".join([
                self.fake.paragraph(nb_sentences=3),
                "## The Challenge",
                self.fake.paragraph(nb_sentences=4),
                "## Finding Help",
                self.fake.paragraph(nb_sentences=4),
                "## The Turning Point",
                self.fake.paragraph(nb_sentences=3),
                "## Advice for Others",
                self.fake.paragraph(nb_sentences=3)
            ])
            
            SuccessStory.objects.create(
                title=title,
                slug=slugify(f"{title}-{random.randint(1, 999)}"),
                content=content,
                author=author,
                is_anonymous=is_anonymous,
                is_featured=is_featured,
                is_approved=True,
                view_count=random.randint(10, 1000),
                created_at=self.fake.date_time_between(start_date='-1y', end_date='now', tzinfo=pytz.UTC)
            )
            story_count += 1
        
        # Create random stories for remaining count
        for i in range(count - len(story_titles)):
            author = random.choice(self.users)
            is_anonymous = random.random() < 0.3
            is_featured = random.random() < 0.2
            
            title = self.fake.sentence(nb_words=random.randint(5, 12)).rstrip('.')
            
            if SuccessStory.objects.filter(title=title, author=author).exists():
                continue
                
            # Create structured content with markdown headings
            content = "\n\n".join([
                self.fake.paragraph(nb_sentences=3),
                "## The Challenge",
                self.fake.paragraph(nb_sentences=4),
                "## Finding Help",
                self.fake.paragraph(nb_sentences=4),
                "## The Turning Point",
                self.fake.paragraph(nb_sentences=3),
                "## Advice for Others",
                self.fake.paragraph(nb_sentences=3)
            ])
            
            SuccessStory.objects.create(
                title=title,
                slug=slugify(f"{title}-{random.randint(1, 999)}"),
                content=content,
                author=author,
                is_anonymous=is_anonymous,
                is_featured=is_featured,
                is_approved=True,
                view_count=random.randint(10, 1000),
                created_at=self.fake.date_time_between(start_date='-1y', end_date='now', tzinfo=pytz.UTC)
            )
            story_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {story_count} success stories'))

    def create_support_groups(self, count, force=False):
        """Create support groups"""
        existing_groups = self.check_existing_data(SupportGroup, force)
        if existing_groups and not force:
            self.support_groups = existing_groups
            return
            
        self.stdout.write('Creating support groups...')
        
        # Realistic support group names and descriptions
        group_data = [
            {
                "name": "Injury Recovery Circle",
                "description": "A support group for athletes recovering from major injuries, focusing on mental health during the recovery process."
            },
            {
                "name": "Performance Anxiety Group",
                "description": "For athletes struggling with competition anxiety, we share coping strategies and support each other."
            },
            {
                "name": "Balancing Life and Training",
                "description": "Discussion group for combat sports athletes managing the demands of training with work, school, and family responsibilities."
            },
            {
                "name": "Weight Management Support",
                "description": "Support for athletes dealing with the psychological aspects of weight cutting and maintaining weight classes."
            },
            {
                "name": "Post-Competition Mental Health",
                "description": "A group focused on the emotional comedown after major competitions, both wins and losses."
            },
            {
                "name": "Women in Combat Sports",
                "description": "A safe space for women to discuss the unique mental health challenges they face in combat sports."
            },
            {
                "name": "Retirement Transition",
                "description": "For athletes considering retirement or recently retired, dealing with identity change and new life direction."
            }
        ]
        
        frequency_choices = ['one-time', 'weekly', 'biweekly', 'monthly']
        
        group_count = 0
        # Create groups with predefined data first
        for group in group_data:
            if SupportGroup.objects.filter(name=group["name"]).exists():
                continue
                
            # Find facilitator (preferably a coach or staff member)
            potential_facilitators = [u for u in self.users if u.user_type in ['coach', 'psychologist']]
            if not potential_facilitators:
                potential_facilitators = self.users
                
            facilitator = random.choice(potential_facilitators)
            
            support_group = SupportGroup.objects.create(
                name=group["name"],
                description=group["description"],
                facilitator=facilitator,
                max_participants=random.randint(5, 20),
                frequency=random.choice(frequency_choices),
                is_active=True,
                created_at=self.fake.date_time_between(start_date='-1y', end_date='now', tzinfo=pytz.UTC)
            )
            self.support_groups.append(support_group)
            group_count += 1
        
        # Create additional random groups
        for i in range(count - len(group_data)):
            name = f"{random.choice(['Mindful', 'Supportive', 'Focus', 'Resilience', 'Growth'])} {random.choice(['Athletes', 'Fighters', 'Competitors', 'Warriors', 'Team'])}"
            
            if SupportGroup.objects.filter(name=name).exists():
                continue
                
            # Find facilitator (preferably a coach or staff member)
            potential_facilitators = [u for u in self.users if u.user_type in ['coach', 'psychologist']]
            if not potential_facilitators:
                potential_facilitators = self.users
                
            facilitator = random.choice(potential_facilitators)
            
            support_group = SupportGroup.objects.create(
                name=name,
                description=self.fake.paragraph(nb_sentences=2),
                facilitator=facilitator,
                max_participants=random.randint(5, 20),
                frequency=random.choice(frequency_choices),
                is_active=True,
                created_at=self.fake.date_time_between(start_date='-1y', end_date='now', tzinfo=pytz.UTC)
            )
            self.support_groups.append(support_group)
            group_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {group_count} support groups'))

    def create_support_group_participants(self, force=False):
        """Create participants for support groups"""
        existing_participants = self.check_existing_data(SupportGroupParticipant, force)
        if existing_participants and not force:
            return
            
        self.stdout.write('Creating support group participants...')
        
        total_participants = 0
        # For each group, add participants
        for group in self.support_groups:
            # Skip inactive groups sometimes
            if not group.is_active and random.random() < 0.5:
                continue
                
            # Determine number of participants (between 3 and max_participants)
            num_participants = random.randint(3, group.max_participants)
            
            # Start with the facilitator
            if not SupportGroupParticipant.objects.filter(group=group, user=group.facilitator).exists():
                SupportGroupParticipant.objects.create(
                    group=group,
                    user=group.facilitator,
                    status='approved',
                    joined_at=group.created_at
                )
                total_participants += 1
            
            # Add regular participants
            added = 1  # Count facilitator
            for user in random.sample(self.users, min(len(self.users), num_participants * 2)):
                # Skip if user is facilitator
                if user == group.facilitator:
                    continue
                    
                # Skip if we've reached target number
                if added >= num_participants:
                    break
                    
                # Check if this participant already exists
                if SupportGroupParticipant.objects.filter(group=group, user=user).exists():
                    continue
                    
                # Determine status (mostly active, some pending or left)
                status_choices = ['pending', 'approved', 'declined', 'left']
                status_weights = [0.1, 0.7, 0.1, 0.1]  # Weighted probabilities
                status = random.choices(status_choices, weights=status_weights)[0]
                
                # For left, add left_at date
                left_at = None
                if status == 'left':
                    joined_at = self.fake.date_time_between(
                        start_date=group.created_at, 
                        end_date=timezone.now() - timedelta(days=7),
                        tzinfo=pytz.UTC
                    )
                    left_at = self.fake.date_time_between(
                        start_date=joined_at,
                        end_date=timezone.now(),
                        tzinfo=pytz.UTC
                    )
                else:
                    joined_at = self.fake.date_time_between(
                        start_date=group.created_at,
                        end_date=timezone.now(),
                        tzinfo=pytz.UTC
                    )
                
                SupportGroupParticipant.objects.create(
                    group=group,
                    user=user,
                    status=status,
                    joined_at=joined_at,
                    left_at=left_at,
                    notes=self.fake.sentence() if random.random() < 0.3 else None
                )
                added += 1
                total_participants += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {total_participants} support group participants'))

    def create_support_group_sessions(self, force=False):
        """Create sessions for support groups"""
        existing_sessions = self.check_existing_data(SupportGroupSession, force)
        if existing_sessions and not force:
            return
            
        self.stdout.write('Creating support group sessions...')
        
        session_count = 0
        for group in self.support_groups:
            # Determine number of sessions based on group frequency
            if group.frequency == 'one-time':
                num_sessions = 1
            elif group.frequency == 'weekly':
                num_sessions = random.randint(4, 12)
            elif group.frequency == 'biweekly':
                num_sessions = random.randint(2, 6)
            else:  # monthly
                num_sessions = random.randint(1, 3)
            
            # Create sessions
            for i in range(num_sessions):
                # Calculate session date based on group creation date
                days_offset = random.randint(0, 180)  # within 6 months
                start_time = self.fake.date_time_between(
                    start_date=group.created_at,
                    end_date=group.created_at + timedelta(days=days_offset),
                    tzinfo=pytz.UTC
                )
                end_time = start_time + timedelta(hours=random.randint(1, 3))
                
                session = SupportGroupSession.objects.create(
                    group=group,
                    title=f"Session {i+1}: {self.fake.sentence(nb_words=3).rstrip('.')}",
                    description=self.fake.paragraph(nb_sentences=2),
                    start_time=start_time,
                    end_time=end_time,
                    meeting_link=f"https://meet.example.com/{self.fake.uuid4()}",
                    is_completed=end_time < timezone.now(),
                    notes=self.fake.paragraph(nb_sentences=3) if random.random() < 0.7 else None,
                    created_at=group.created_at
                )
                session_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {session_count} support group sessions'))

    def create_support_group_attendance(self, force=False):
        """Create attendance records for support group sessions"""
        existing_attendance = self.check_existing_data(SupportGroupAttendance, force)
        if existing_attendance and not force:
            return
            
        self.stdout.write('Creating support group attendance records...')
        
        attendance_count = 0
        for session in SupportGroupSession.objects.all():
            # Get all participants for this group
            participants = SupportGroupParticipant.objects.filter(
                group=session.group,
                status='approved'
            )
            
            # Create attendance records
            for participant in participants:
                # Skip if attendance record already exists
                if SupportGroupAttendance.objects.filter(session=session, participant=participant).exists():
                    continue
                
                # 80% chance of attending
                attended = random.random() < 0.8
                
                SupportGroupAttendance.objects.create(
                    session=session,
                    participant=participant,
                    attended=attended,
                    feedback=self.fake.paragraph(nb_sentences=1) if attended and random.random() < 0.5 else None,
                    created_at=session.start_time
                )
                attendance_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {attendance_count} attendance records'))