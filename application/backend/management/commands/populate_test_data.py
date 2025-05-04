# wellness/management/commands/populate_test_data.py
import random
import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.conf import settings
from django.core.files.base import ContentFile
from backend.models import (
    ResourceCategory, WellnessResource, SavedResource, 
    ResourceRating, JournalEntry, JournalPrompt, JournalTemplate
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with test data for wellness resources and journals'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting database population...'))
        
        # Create test users
        self.create_users()
        
        # Create resource categories
        self.create_resource_categories()
        
        # Create wellness resources
        self.create_wellness_resources()
        
        # Create saved resources
        self.create_saved_resources()
        
        # Create resource ratings
        self.create_resource_ratings()
        
        # Create journal prompts
        self.create_journal_prompts()
        
        # Create journal templates
        self.create_journal_templates()
        
        # Create journal entries
        self.create_journal_entries()
        
        self.stdout.write(self.style.SUCCESS('Database successfully populated with test data!'))
    
    def create_users(self):
        self.stdout.write('Creating users...')
        
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('adminpass')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Admin user created'))
        
        # Create coach users
        coach_usernames = ['coach1', 'coach2']
        for username in coach_usernames:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'user_type': 'coach',
                }
            )
            if created:
                user.set_password('userpass')
                user.save()
                
        # Create psychologist users
        psych_usernames = ['psych1', 'psych2']
        for username in psych_usernames:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'user_type': 'psychologist',
                }
            )
            if created:
                user.set_password('userpass')
                user.save()
        
        # Create athlete users
        athlete_usernames = ['athlete1', 'athlete2', 'athlete3', 'athlete4', 'athlete5']
        self.athletes = []
        for username in athlete_usernames:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'user_type': 'athlete',
                }
            )
            if created:
                user.set_password('userpass')
                user.save()
            self.athletes.append(user)
        
        self.content_creators = list(User.objects.filter(is_staff=True) | User.objects.filter(user_type__in=['psychologist', 'coach']))
        self.stdout.write(self.style.SUCCESS(f'Created {User.objects.count()} users'))
    
    def create_resource_categories(self):
        self.stdout.write('Creating resource categories...')
        
        categories = [
            {
                'name': 'Stress Management',
                'description': 'Techniques and resources to help manage stress and anxiety',
                'icon': 'meditation',
                'order': 1,
            },
            {
                'name': 'Performance Psychology',
                'description': 'Mental skills for peak athletic performance',
                'icon': 'award',
                'order': 2,
            },
            {
                'name': 'Recovery & Rest',
                'description': 'Optimize your recovery for better performance and wellbeing',
                'icon': 'bed',
                'order': 3,
            },
            {
                'name': 'Team Dynamics',
                'description': 'Resources for better teamwork and communication',
                'icon': 'users',
                'order': 4,
            },
            {
                'name': 'Injury & Rehabilitation',
                'description': 'Mental aspects of coping with injuries and the rehabilitation process',
                'icon': 'heart',
                'order': 5,
            },
            {
                'name': 'Sports Nutrition',
                'description': 'Nutritional guidance for athletic performance',
                'icon': 'apple-alt',
                'order': 6,
            },
            {
                'name': 'Sleep Optimization',
                'description': 'Resources to improve sleep quality and duration',
                'icon': 'moon',
                'order': 7,
            },
        ]
        
        for category_data in categories:
            ResourceCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'slug': slugify(category_data['name']),
                    'icon': category_data['icon'],
                    'order': category_data['order'],
                }
            )
        
        self.categories = list(ResourceCategory.objects.all())
        self.stdout.write(self.style.SUCCESS(f'Created {ResourceCategory.objects.count()} resource categories'))
    
    def create_wellness_resources(self):
        self.stdout.write('Creating wellness resources...')
        
        resources = [
            # Stress Management resources
            {
                'title': 'The 5-Minute Mindfulness Technique for Athletes',
                'category': 'Stress Management',
                'content_type': 'article',
                'description': 'Learn a quick mindfulness technique you can use before competitions or training to center yourself and reduce anxiety.',
                'content': """
                <h2>The 5-Minute Mindfulness Technique for Athletes</h2>
                <p>As an athlete, managing pre-competition anxiety is crucial for peak performance. This simple 5-minute mindfulness exercise can help center your mind and reduce stress before important events.</p>
                
                <h3>The Technique:</h3>
                <ol>
                    <li><strong>Find a quiet space</strong> - Before your event, find somewhere you can have 5 minutes of uninterrupted time.</li>
                    <li><strong>Comfortable position</strong> - Sit or stand in a comfortable position with your back straight.</li>
                    <li><strong>Focus on your breath</strong> - Close your eyes and take 5 deep breaths, counting to 4 on the inhale and 6 on the exhale.</li>
                    <li><strong>Body scan</strong> - Starting from your toes, mentally scan up through your body, noticing any tension and consciously relaxing each area.</li>
                    <li><strong>Performance visualization</strong> - Spend the final 2 minutes visualizing yourself performing well, focusing on the process rather than the outcome.</li>
                </ol>
                
                <h3>Scientific Benefits:</h3>
                <p>Research shows that short mindfulness practices can significantly reduce cortisol (stress hormone) levels and improve focus. A 2018 study with Olympic athletes found that regular mindfulness practice improved performance under pressure by 14%.</p>
                
                <h3>When to Use:</h3>
                <ul>
                    <li>30-60 minutes before competition</li>
                    <li>Before important training sessions</li>
                    <li>When feeling overwhelmed during the season</li>
                    <li>As part of your regular mental training routine</li>
                </ul>
                
                <p>Remember, like any skill, mindfulness improves with practice. Try to incorporate this technique into your routine at least 3 times per week for optimal results.</p>
                """,
                'tags': 'mindfulness,competition,anxiety,mental skills,pre-game',
                'published': True,
                'featured': True,
            },
            {
                'title': 'Deep Breathing Exercises for Athletes',
                'category': 'Stress Management',
                'content_type': 'video',
                'description': 'A guided video on different breathing techniques that can help athletes manage stress and anxiety.',
                'external_url': 'https://example.com/videos/deep-breathing-exercises',
                'tags': 'breathing,anxiety,relaxation,stress',
                'published': True,
            },
            
            # Performance Psychology resources
            {
                'title': 'Developing a Pre-Competition Routine',
                'category': 'Performance Psychology',
                'content_type': 'article',
                'description': 'Learn how to create an effective pre-competition routine to optimize your performance.',
                'content': """
                <h2>Developing an Effective Pre-Competition Routine</h2>
                
                <p>A consistent pre-competition routine helps athletes prepare mentally and physically, reduce anxiety, and enter the optimal performance state. Here's how to develop yours:</p>
                
                <h3>Components of an Effective Routine:</h3>
                
                <h4>1. Physical Preparation (1-2 hours before)</h4>
                <ul>
                    <li>Nutrition: Light meal 2-3 hours before; perhaps a small snack 1 hour before</li>
                    <li>Hydration: Consistent fluid intake leading up to the event</li>
                    <li>Warm-up: Customized to your sport's demands</li>
                </ul>
                
                <h4>2. Mental Preparation (30-60 minutes before)</h4>
                <ul>
                    <li>Visualization: 5-10 minutes seeing yourself performing successfully</li>
                    <li>Self-talk: Repeat your performance cues and affirmations</li>
                    <li>Arousal regulation: Use breathing or music to reach your optimal arousal level</li>
                </ul>
                
                <h4>3. Technical Preparation (15-30 minutes before)</h4>
                <ul>
                    <li>Equipment check: Ensure everything is ready</li>
                    <li>Mental rehearsal: Run through key technical elements</li>
                    <li>Focus narrowing: Begin eliminating external distractions</li>
                </ul>
                
                <h3>Building Your Personal Routine:</h3>
                
                <ol>
                    <li><strong>Identify what works for you</strong> - Experiment with different activities</li>
                    <li><strong>Start small</strong> - Begin with 2-3 elements and expand</li>
                    <li><strong>Be flexible but consistent</strong> - Have alternatives if circumstances change</li>
                    <li><strong>Practice regularly</strong> - Use your routine in training, not just competition</li>
                    <li><strong>Refine over time</strong> - Keep a performance journal to track what works</li>
                </ol>
                
                <h3>Common Mistakes to Avoid:</h3>
                
                <ul>
                    <li>Making the routine too complex or time-consuming</li>
                    <li>Including superstitious elements that create dependency</li>
                    <li>Focusing on outcomes rather than process goals</li>
                    <li>Not practicing the routine regularly</li>
                </ul>
                
                <p>Remember that the goal of a pre-competition routine is to create a sense of familiarity and control in high-pressure situations. The more you practice your routine, the more automatic and effective it becomes.</p>
                """,
                'tags': 'competition,routine,preparation,performance',
                'published': True,
                'featured': True,
            },
            {
                'title': 'Goal Setting for Athletic Success',
                'category': 'Performance Psychology',
                'content_type': 'pdf',
                'description': 'A comprehensive guide to setting SMART goals for athletes at all levels.',
                'external_url': 'https://example.com/resources/goal-setting-guide.pdf',
                'tags': 'goals,motivation,success,planning',
                'published': True,
            },
            
            # Recovery & Rest resources
            {
                'title': 'Active Recovery Techniques',
                'category': 'Recovery & Rest',
                'content_type': 'article',
                'description': 'Learn about active recovery methods to help your body recover faster between training sessions.',
                'content': """
                <h2>Active Recovery Techniques for Athletes</h2>
                
                <p>Active recovery involves performing low-intensity exercise following a high-intensity workout or competition. These techniques help reduce muscle soreness, improve circulation, and speed up the recovery process.</p>
                
                <h3>Benefits of Active Recovery:</h3>
                
                <ul>
                    <li>Reduces lactic acid buildup in muscles</li>
                    <li>Increases blood flow to deliver nutrients and remove waste products</li>
                    <li>Maintains mobility and prevents stiffness</li>
                    <li>Can help reduce DOMS (Delayed Onset Muscle Soreness)</li>
                    <li>Provides mental benefits through continued movement</li>
                </ul>
                
                <h3>Top Active Recovery Methods:</h3>
                
                <h4>1. Light Cardio (20-30 minutes)</h4>
                <p>Aim for 30-40% of your maximum effort with activities like:</p>
                <ul>
                    <li>Swimming at a leisurely pace</li>
                    <li>Easy cycling on flat terrain</li>
                    <li>Light jogging or walking</li>
                    <li>Using an elliptical machine</li>
                </ul>
                
                <h4>2. Mobility Work (15-20 minutes)</h4>
                <ul>
                    <li>Dynamic stretching focusing on the muscles used in your sport</li>
                    <li>Yoga flows designed for recovery (try "gentle flow" or "restorative" classes)</li>
                    <li>Foam rolling major muscle groups (quads, hamstrings, calves, back)</li>
                </ul>
                
                <h4>3. Contrast Water Therapy</h4>
                <p>Alternating between hot and cold exposure:</p>
                <ul>
                    <li>30 seconds - 2 minutes in cold water (50-60°F / 10-15°C)</li>
                    <li>30 seconds - 2 minutes in warm water (100-104°F / 38-40°C)</li>
                    <li>Repeat 3-5 cycles, always finishing with cold</li>
                </ul>
                
                <h3>When to Implement Active Recovery:</h3>
                
                <ul>
                    <li><strong>Between training sessions:</strong> On rest days between intense workouts</li>
                    <li><strong>Within a session:</strong> Between high-intensity intervals or sets</li>
                    <li><strong>Post-competition:</strong> The day following a game or event</li>
                </ul>
                
                <h3>Sample Active Recovery Circuit (20 minutes total):</h3>
                
                <ol>
                    <li>5 minutes light jogging or cycling</li>
                    <li>5 minutes dynamic stretching</li>
                    <li>5 minutes foam rolling</li>
                    <li>5 minutes gentle yoga poses</li>
                </ol>
                
                <p>Remember that active recovery should feel restorative, not challenging. If you're working too hard during recovery, you're defeating the purpose!</p>
                """,
                'tags': 'recovery,training,soreness,rest,muscle',
                'published': True,
            },
            {
                'title': 'Sleep Strategies for Athletes',
                'category': 'Sleep Optimization',
                'content_type': 'article',
                'description': 'Evidence-based strategies to improve sleep quality and duration for better athletic performance.',
                'content': """
                <h2>Sleep Strategies for Peak Athletic Performance</h2>
                
                <p>Research consistently shows that sleep quality and duration directly impact athletic performance, recovery, and injury rates. Here are evidence-based strategies to optimize your sleep as an athlete.</p>
                
                <h3>The Performance Impact of Sleep:</h3>
                
                <p>Studies from Stanford University showed that when basketball players extended their sleep to 10 hours per night:</p>
                <ul>
                    <li>Sprint times improved by 5%</li>
                    <li>Free throw accuracy increased by 9%</li>
                    <li>Three-point shooting accuracy improved by 9.2%</li>
                    <li>Reaction time decreased significantly</li>
                </ul>
                
                <h3>Sleep Duration Guidelines:</h3>
                
                <ul>
                    <li><strong>General recommendation:</strong> 7-9 hours for adults</li>
                    <li><strong>Athletes in training:</strong> 8-10 hours</li>
                    <li><strong>During intense training periods:</strong> Additional 1-2 hours recommended</li>
                    <li><strong>Adolescent athletes:</strong> 9-10 hours minimum</li>
                </ul>
                
                <h3>Pre-Sleep Routine:</h3>
                
                <ol>
                    <li><strong>Set a consistent schedule</strong> - Go to bed and wake up at the same times daily</li>
                    <li><strong>Create a wind-down period</strong> - Start 30-60 minutes before bedtime:
                        <ul>
                            <li>Dim lights to signal your body to produce melatonin</li>
                            <li>Avoid screens or use blue light blockers</li>
                            <li>Try gentle stretching, reading, or deep breathing</li>
                        </ul>
                    </li>
                    <li><strong>Optimize your environment</strong>:
                        <ul>
                            <li>Keep room temperature between 60-67°F (15-19°C)</li>
                            <li>Ensure total darkness or use a sleep mask</li>
                            <li>Reduce noise or use white noise/earplugs</li>
                        </ul>
                    </li>
                </ol>
                
                <h3>Nutrition and Sleep:</h3>
                
                <ul>
                    <li>Avoid caffeine within 8-10 hours of bedtime</li>
                    <li>Limit alcohol, which disrupts REM sleep</li>
                    <li>Consider a small bedtime snack with tryptophan (milk, banana, nuts)</li>
                    <li>Stay hydrated but reduce fluids 90 minutes before bed</li>
                </ul>
                
                <h3>Travel and Competition Strategies:</h3>
                
                <ul>
                    <li><strong>For jet lag:</strong> Adjust to the new time zone 2-3 days before travel if possible</li>
                    <li><strong>Pre-competition:</strong> Prioritize sleep the week before, not just the night before</li>
                    <li><strong>Unfamiliar environments:</strong> Bring familiar items from home (pillow, blanket)</li>
                </ul>
                
                <h3>Sleep Tracking:</h3>
                
                <p>Consider tracking your sleep using:
                <ul>
                    <li>Sleep diary (subjective rating, duration, disturbances)</li>
                    <li>Wearable technology (various options with different accuracy levels)</li>
                    <li>Sleep cycle apps</li>
                </ul>
                
                <p>Remember that sleep is as important to your training regimen as physical workouts and nutrition. It's not a luxury—it's a necessity for peak performance!</p>
                """,
                'tags': 'sleep,recovery,performance,rest',
                'published': True,
                'featured': True,
            },
            
            # Injury & Rehabilitation resources
            {
                'title': 'Psychological Aspects of Injury Recovery',
                'category': 'Injury & Rehabilitation',
                'content_type': 'article',
                'description': 'Understanding the mental challenges of injury and strategies to maintain a positive mindset during recovery.',
                'content': """
                <h2>The Psychological Journey Through Sports Injury</h2>
                
                <p>Physical injury is only part of the challenge athletes face when injured. The psychological aspects of injury can be just as demanding and significantly impact recovery times and return-to-play success.</p>
                
                <h3>The Emotional Phases of Injury:</h3>
                
                <h4>1. Shock/Denial (First 24-72 hours)</h4>
                <ul>
                    <li>Common thoughts: "This can't be happening," "It's not that bad"</li>
                    <li>Common feelings: Disbelief, numbness, confusion</li>
                    <li><strong>Strategy:</strong> Allow yourself space to process without making major decisions</li>
                </ul>
                
                <h4>2. Anger/Bargaining (Days 3-14)</h4>
                <ul>
                    <li>Common thoughts: "Why me?", "If only I hadn't..."</li>
                    <li>Common feelings: Frustration, irritability, regret</li>
                    <li><strong>Strategy:</strong> Acknowledge emotions without judgment; channel energy into learning about your injury</li>
                </ul>
                
                <h4>3. Depression/Isolation (Weeks 2-6)</h4>
                <ul>
                    <li>Common thoughts: "I'll never get back," "I'm letting everyone down"</li>
                    <li>Common feelings: Sadness, loss of identity, disconnection</li>
                    <li><strong>Strategy:</strong> Maintain team connections; set non-physical goals; consider speaking with a sport psychologist</li>
                </ul>
                
                <h4>4. Acceptance/Reorganization (Varies)</h4>
                <ul>
                    <li>Common thoughts: "I can work through this," "This is my current reality"</li>
                    <li>Common feelings: Determination, focus, hopefulness</li>
                    <li><strong>Strategy:</strong> Embrace rehabilitation as training; set process-focused recovery goals</li>
                </ul>
                
                <h3>Research-Based Recovery Strategies:</h3>
                
                <h4>1. Goal Setting</h4>
                <p>Studies show that structured goal setting during rehabilitation can:
                <ul>
                    <li>Increase adherence to rehabilitation protocols by up to 40%</li>
                    <li>Reduce perceived pain during exercises</li>
                    <li>Create measurable progress markers that boost motivation</li>
                </ul>
                <p><strong>Action step:</strong> Set daily, weekly, and monthly goals that focus on the process, not just end results.</p>
                
                <h4>2. Visualization</h4>
                <p>Research from the Journal of Sport Rehabilitation shows that guided imagery can:
                <ul>
                    <li>Activate similar neural pathways as physical movement</li>
                    <li>Maintain neural connections to injured body parts</li>
                    <li>Reduce anxiety about return to play</li>
                </ul>
                <p><strong>Action step:</strong> Spend 5-10 minutes daily visualizing both successful rehabilitation exercises and eventual return to sport.</p>
                
                <h4>3. Maintaining Team Connection</h4>
                <p>Athletes who maintain involvement with their team during injury recovery:
                <ul>
                    <li>Report lower levels of depression and isolation</li>
                    <li>Have higher compliance with rehabilitation protocols</li>
                    <li>Experience smoother transitions back to competition</li>
                </ul>
                <p><strong>Action step:</strong> Attend practices/games when possible; find alternative roles during recovery (analysis, mentoring).</p>
                
                <h3>When to Seek Additional Support:</h3>
                
                <p>Consider consulting a sport psychologist if you experience:</p>
                <ul>
                    <li>Persistent negative thoughts or feelings lasting more than two weeks</li>
                    <li>Sleep disturbances or appetite changes</li>
                    <li>Loss of motivation for rehabilitation</li>
                    <li>Significant anxiety about re-injury</li>
                    <li>Identity crisis or feeling lost without your sport</li>
                </ul>
                
                <p>Remember that psychological recovery often doesn't follow the same timeline as physical recovery. Being proactive about your mental health during injury is as important as your physical rehabilitation protocol.</p>
                """,
                'tags': 'injury,rehabilitation,psychology,recovery,mental health',
                'published': True,
            },
            
            # Team Dynamics resources
            {
                'title': 'Building Team Cohesion',
                'category': 'Team Dynamics',
                'content_type': 'exercise',
                'description': 'Interactive exercises for coaches and team leaders to build stronger team cohesion.',
                'content': """
                <h2>Team Cohesion Building Exercises</h2>
                
                <p>Team cohesion—the tendency of a group to stick together in pursuit of objectives—has been consistently linked to improved performance across sports. These evidence-based exercises can help develop stronger bonds between teammates.</p>
                
                <h3>Exercise 1: Personal Histories Exchange</h3>
                
                <p><strong>Purpose:</strong> Increase interpersonal knowledge and develop appreciation for teammates' backgrounds</p>
                
                <p><strong>Time Required:</strong> 45-60 minutes</p>
                
                <p><strong>Materials:</strong> None required</p>
                
                <p><strong>Instructions:</strong></p>
                <ol>
                    <li>Arrange team members in pairs or groups of three (ideally pairing those who don't regularly interact)</li>
                    <li>Each athlete shares their "athletic biography" including:
                        <ul>
                            <li>How they first got involved in the sport</li>
                            <li>A significant challenge they've overcome</li>
                            <li>A mentor who influenced their athletic journey</li>
                            <li>Why they continue to compete in this sport</li>
                            <li>Something about their journey teammates might not know</li>
                        </ul>
                    </li>
                    <li>After sharing, each group introduces their partners to the larger team, highlighting one thing that impressed or surprised them</li>
                </ol>
                
                <h3>Exercise 2: Team Identity Workshop</h3>
                
                <p><strong>Purpose:</strong> Develop shared team values and create a collective identity</p>
                
                <p><strong>Time Required:</strong> 90 minutes</p>
                
                <p><strong>Materials:</strong> Whiteboard/flipchart, markers, note cards</p>
                
                <p><strong>Instructions:</strong></p>
                <ol>
                    <li>Individual reflection (10 min): Each athlete writes down:
                        <ul>
                            <li>Three values they believe are essential for team success</li>
                            <li>What makes this team unique from other teams</li>
                            <li>What they want the team to be known for</li>
                        </ul>
                    </li>
                    <li>Small group discussion (20 min): In groups of 4-5, share responses and identify common themes</li>
                    <li>Whole team synthesis (30 min): Groups present their themes, coach facilitates discussion to identify 4-6 core team values</li>
                    <li>Value definition (30 min): For each value, define:
                        <ul>
                            <li>What this value looks like in practice</li>
                            <li>How it will be demonstrated in training</li>
                            <li>How it will be demonstrated in competition</li>
                            <li>How the team will hold each other accountable</li>
                        </ul>
                    </li>
                </ol>
                
                <h3>Exercise 3: Role Clarity Cards</h3>
                
                <p><strong>Purpose:</strong> Enhance understanding of each person's role and contribution to team success</p>
                
                <p><strong>Time Required:</strong> 30-45 minutes</p>
                
                <p><strong>Materials:</strong> Index cards, pens</p>
                
                <p><strong>Instructions:</strong></p>
                <ol>
                    <li>Each athlete receives three index cards</li>
                    <li>On card 1: Write your name and what you believe your primary roles are on this team (both technical and social/emotional)</li>
                    <li>On card 2: Write the name of the teammate to your right and what you believe their unique contribution to the team is</li>
                    <li>On card 3: Write one thing you commit to doing to help the team achieve its goals this season</li>
                    <li>Share in a circle formation:
                        <ul>
                            <li>Each athlete reads their card about their teammate</li>
                            <li>That teammate then reads their self-assessment card</li>
                            <li>Discuss any differences in perception</li>
                            <li>Finally, each athlete shares their commitment card</li>
                        </ul>
                    </li>
                </ol>
                
                <h3>Exercise 4: Shared Adversity Challenge</h3>
                
                <p><strong>Purpose:</strong> Create a shared challenging experience outside of normal training to build resilience and cooperation</p>
                
                <p><strong>Time Required:</strong> 2-3 hours</p>
                
                <p><strong>Materials:</strong> Varies by selected activity</p>
                
                <p><strong>Instructions:</strong></p>
                <p>Select a novel physical challenge that:
                <ul>
                    <li>Requires teamwork to complete</li>
                    <li>Is challenging but achievable</li>
                    <li>Doesn't overly favor any particular skill set</li>
                    <li>Requires problem-solving under pressure</li>
                </ul>
                
                <p>Options include:
                <ul>
                    <li>Obstacle course completion with team challenges</li>
                    <li>Orienteering/navigation exercise</li>
                    <li>Beach or wilderness clean-up challenge</li>
                    <li>Community service project with physical components</li>
                </ul>
                
                <p><strong>Follow-up discussion questions:</strong></p>
                <ul>
                    <li>What did you learn about your teammates during this challenge?</li>
                    <li>How did the team respond when things got difficult?</li>
                    <li>What strengths emerged that we could utilize in our sport?</li>
                    <li>How can we transfer what we learned today to our performance?</li>
                </ul>
                
                <p>Remember to implement these exercises at strategic points in your season—team formation, mid-season reset, or before crucial competitions. Consistency and reinforcement of the lessons learned are key to lasting cohesion.</p>
                """,
                'tags': 'teamwork,cohesion,team building,leadership',
                'published': True,
            },
            
            # Sports Nutrition resources
            {
                'title': 'Nutrition for Recovery',
                'category': 'Sports Nutrition',
                'content_type': 'article',
                'description': 'Nutritional strategies to optimize recovery between training sessions and competitions.',
                'content': """
                <h2>Nutrition for Optimal Athletic Recovery</h2>
                
                <p>Proper nutrition plays a crucial role in how quickly and effectively your body recovers after training and competition. This guide outlines evidence-based nutritional strategies to optimize your recovery process.</p>
                
                <h3>The Recovery Nutrition Window</h3>
                
                <p>Research indicates that consuming the right nutrients within 30-60 minutes after exercise (often called the "recovery window") can significantly enhance:
                <ul>
                # Continuation of create_wellness_resources method in populate_test_data.py
                    <li>Glycogen replenishment (replaces muscle energy stores)</li>
                    <li>Protein synthesis (repairs and builds muscle tissue)</li>
                    <li>Immune system function (prevents post-exercise immunosuppression)</li>
                    <li>Hydration status (replacing fluids lost through sweat)</li>
                </ul>
                </p>
                
                <h3>Key Recovery Nutrients</h3>
                
                <h4>1. Carbohydrates</h4>
                <p><strong>Recommendation:</strong> 0.5-0.7g per pound of body weight within 30 minutes post-exercise</p>
                <p><strong>Purpose:</strong> Replenish glycogen stores</p>
                <p><strong>Good sources:</strong>
                <ul>
                    <li>Fresh or dried fruits (bananas, berries, raisins)</li>
                    <li>Starchy vegetables (sweet potatoes, squash)</li>
                    <li>Whole grains (oats, quinoa, rice)</li>
                    <li>Recovery-specific sports drinks or smoothies</li>
                </ul>
                </p>
                
                <h4>2. Protein</h4>
                <p><strong>Recommendation:</strong> 0.14-0.23g per pound of body weight within 30-60 minutes post-exercise</p>
                <p><strong>Purpose:</strong> Repair muscle damage and stimulate new protein synthesis</p>
                <p><strong>Good sources:</strong>
                <ul>
                    <li>Whey protein (fastest absorption rate)</li>
                    <li>Greek yogurt or cottage cheese</li>
                    <li>Lean meat, poultry, or fish</li>
                    <li>Plant-based options: tofu, lentils, chickpeas</li>
                </ul>
                </p>
                
                <h4>3. Fluids & Electrolytes</h4>
                <p><strong>Recommendation:</strong> 16-24 oz (500-750ml) for every pound lost during exercise</p>
                <p><strong>Purpose:</strong> Restore hydration and electrolyte balance</p>
                <p><strong>Good sources:</strong>
                <ul>
                    <li>Water plus electrolyte-rich foods</li>
                    <li>Sports drinks (especially for sessions >60 minutes)</li>
                    <li>Coconut water</li>
                    <li>Foods with naturally occurring electrolytes (bananas, sweet potatoes)</li>
                </ul>
                </p>
                
                <h3>Recovery Meal & Snack Ideas</h3>
                
                <h4>Quick Post-Workout Options (Within 30 minutes):</h4>
                <ul>
                    <li>Chocolate milk (natural carb:protein ratio of ~3:1)</li>
                    <li>Protein smoothie with banana and berries</li>
                    <li>Greek yogurt with honey and fruit</li>
                    <li>Apple or banana with nut butter</li>
                </ul>
                
                <h4>Complete Recovery Meals (Within 2 hours):</h4>
                <ul>
                    <li>Chicken or tofu stir-fry with vegetables and rice</li>
                    <li>Salmon with sweet potato and leafy greens</li>
                    <li>Egg omelet with vegetables and toast</li>
                    <li>Quinoa bowl with legumes, vegetables, and avocado</li>
                </ul>
                
                <h3>Special Considerations</h3>
                
                <h4>For Multiple Training Sessions:</h4>
                <p>If you train multiple times per day, recovery nutrition becomes even more critical. Prioritize liquid options immediately after the first session for faster absorption.</p>
                
                <h4>For Weight Management:</h4>
                <p>Even if trying to lose weight, don't skip recovery nutrition—it's essential for adaptation. Instead, adjust your overall daily intake while maintaining proper post-workout nutrition.</p>
                
                <h3>Anti-Inflammatory Foods</h3>
                <p>Including these foods can help reduce exercise-induced inflammation:
                <ul>
                    <li>Fatty fish (salmon, mackerel)</li>
                    <li>Berries (especially cherries, blueberries)</li>
                    <li>Turmeric (with black pepper for absorption)</li>
                    <li>Leafy greens</li>
                    <li>Nuts and seeds</li>
                </ul>
                </p>
                
                <p>Remember that proper recovery nutrition is not just about the next training session—it's about long-term health, adaptation, and performance improvement. Consistency in your recovery nutrition strategy is key to seeing progress over time.</p>
                """,
                'tags': 'nutrition,recovery,protein,carbohydrates,hydration',
                'published': True,
            },
        ]
        
        # Create the wellness resources
        for resource_data in resources:
            category = ResourceCategory.objects.get(name=resource_data['category'])
            creator = random.choice(self.content_creators)
            
            resource, created = WellnessResource.objects.get_or_create(
                title=resource_data['title'],
                defaults={
                    'category': category,
                    'content_type': resource_data['content_type'],
                    'description': resource_data['description'],
                    'content': resource_data.get('content'),
                    'external_url': resource_data.get('external_url'),
                    'tags': resource_data['tags'],
                    'published': resource_data['published'],
                    'featured': resource_data.get('featured', False),
                    'created_by': creator
                }
            )
            
        self.resources = list(WellnessResource.objects.all())
        self.stdout.write(self.style.SUCCESS(f'Created {WellnessResource.objects.count()} wellness resources'))
    
    def create_saved_resources(self):
        self.stdout.write('Creating saved resources...')
        
        # Each athlete saves 2-4 random resources
        for athlete in self.athletes:
            num_to_save = random.randint(2, 4)
            resources_to_save = random.sample(self.resources, min(num_to_save, len(self.resources)))
            
            for resource in resources_to_save:
                saved, created = SavedResource.objects.get_or_create(
                    user=athlete,
                    resource=resource,
                    defaults={
                        'notes': f"I found this {resource.content_type} really helpful for my {resource.category.name.lower()} needs."
                    }
                )
        
        self.stdout.write(self.style.SUCCESS(f'Created {SavedResource.objects.count()} saved resources'))
    
    def create_resource_ratings(self):
        self.stdout.write('Creating resource ratings...')
        
        # Athletes rate some of the resources they saved
        saved_resources = SavedResource.objects.select_related('user', 'resource').all()
        for saved in saved_resources:
            # 80% chance of rating a saved resource
            if random.random() < 0.8:
                rating, created = ResourceRating.objects.get_or_create(
                    user=saved.user,
                    resource=saved.resource,
                    defaults={
                        'rating': random.randint(3, 5),  # Most saved resources get positive ratings
                        'feedback': random.choice([
                            "This was very helpful!",
                            "Great resource, really helped me improve.",
                            "Exactly what I needed.",
                            "Will definitely use this information.",
                            ""  # Sometimes no feedback
                        ])
                    }
                )
        
        # Add a few ratings for resources that aren't saved (discovery)
        for athlete in self.athletes:
            # Rate 1-2 resources that weren't saved
            rated_resources = ResourceRating.objects.filter(user=athlete).values_list('resource_id', flat=True)
            unrated_resources = [r for r in self.resources if r.id not in rated_resources]
            
            if unrated_resources:
                num_to_rate = min(random.randint(1, 2), len(unrated_resources))
                resources_to_rate = random.sample(unrated_resources, num_to_rate)
                
                for resource in resources_to_rate:
                    rating = ResourceRating.objects.create(
                        user=athlete,
                        resource=resource,
                        rating=random.randint(2, 5),  # Slightly more variation
                        feedback=random.choice([
                            "Interesting content.",
                            "Could use more examples, but helpful.",
                            "Good information overall.",
                            ""  # Sometimes no feedback
                        ])
                    )
        
        self.stdout.write(self.style.SUCCESS(f'Created {ResourceRating.objects.count()} resource ratings'))
    
    def create_journal_prompts(self):
        self.stdout.write('Creating journal prompts...')
        
        prompts = [
            {
                'text': "Reflect on your performance in your most recent competition. What went well and what would you like to improve?",
                'category': "performance",
            },
            {
                'text': "Describe how you're feeling physically today. Are there any areas of tension, pain, or fatigue?",
                'category': "physical",
            },
            {
                'text': "What are your current mental barriers or challenges? How might you overcome them?",
                'category': "mental",
            },
            {
                'text': "What are you grateful for in your athletic journey right now?",
                'category': "gratitude",
            },
            {
                'text': "Describe your ideal performance state. When have you experienced this feeling before?",
                'category': "performance",
            },
            {
                'text': "How has your sleep been affecting your training and recovery? What patterns have you noticed?",
                'category': "recovery",
            },
            {
                'text': "What are your short-term goals for this week? What specific actions will you take to work toward them?",
                'category': "goals",
            },
            {
                'text': "How do you typically respond to setbacks or failures? What would be a more constructive approach?",
                'category': "resilience",
            },
            {
                'text': "Describe your pre-competition routine. What elements help you perform your best?",
                'category': "preparation",
            },
            {
                'text': "How is your current balance between athletic demands and other life responsibilities? What adjustments might help?",
                'category': "balance",
            },
        ]
        
        creator = User.objects.filter(is_staff=True).first()
        
        for prompt_data in prompts:
            prompt, created = JournalPrompt.objects.get_or_create(
                text=prompt_data['text'],
                defaults={
                    'category': prompt_data['category'],
                    'created_by': creator,
                    'is_active': True
                }
            )
        
        self.prompts = list(JournalPrompt.objects.all())
        self.stdout.write(self.style.SUCCESS(f'Created {JournalPrompt.objects.count()} journal prompts'))
    
    def create_journal_templates(self):
        self.stdout.write('Creating journal templates...')
        
        templates = [
            {
                'title': "Daily Performance Log",
                'description': "Track your daily training performance and physical/mental state",
                'structure': {
                    "sections": [
                        {
                            "title": "Training Summary",
                            "fields": [
                                {"name": "session_type", "type": "text", "label": "Type of Training Session"},
                                {"name": "session_duration", "type": "number", "label": "Duration (minutes)"},
                                {"name": "session_intensity", "type": "select", "label": "Session Intensity", 
                                 "options": ["Light", "Moderate", "Hard", "Very Hard"]}
                            ]
                        },
                        {
                            "title": "Physical State",
                            "fields": [
                                {"name": "energy_level", "type": "select", "label": "Energy Level", 
                                 "options": ["Very Low", "Low", "Moderate", "High", "Very High"]},
                                {"name": "muscle_soreness", "type": "select", "label": "Muscle Soreness", 
                                 "options": ["None", "Mild", "Moderate", "Severe"]},
                                {"name": "sleep_quality", "type": "select", "label": "Last Night's Sleep Quality", 
                                 "options": ["Poor", "Fair", "Good", "Excellent"]}
                            ]
                        },
                        {
                            "title": "Mental State",
                            "fields": [
                                {"name": "focus_level", "type": "select", "label": "Focus Level During Training", 
                                 "options": ["Poor", "Fair", "Good", "Excellent"]},
                                {"name": "motivation", "type": "select", "label": "Motivation Today", 
                                 "options": ["Very Low", "Low", "Moderate", "High", "Very High"]},
                                {"name": "stress_level", "type": "select", "label": "Overall Stress Level", 
                                 "options": ["Low", "Moderate", "High", "Very High"]}
                            ]
                        },
                        {
                            "title": "Reflection",
                            "fields": [
                                {"name": "went_well", "type": "textarea", "label": "What went well today?"},
                                {"name": "improve", "type": "textarea", "label": "What could be improved?"},
                                {"name": "tomorrow", "type": "textarea", "label": "Focus for tomorrow:"}
                            ]
                        }
                    ]
                },
                'is_public': True
            },
            {
                'title': "Pre-Competition Reflection",
                'description': "Mental preparation template to use before competitions",
                'structure': {
                    "sections": [
                        {
                            "title": "Competition Details",
                            "fields": [
                                {"name": "competition_name", "type": "text", "label": "Competition Name"},
                                {"name": "competition_date", "type": "date", "label": "Date"},
                                {"name": "importance", "type": "select", "label": "Importance Level", 
                                 "options": ["Practice/Minor", "Regular Season", "Important", "Championship/Critical"]}
                            ]
                        },
                        {
                            "title": "Current State",
                            "fields": [
                                {"name": "physical_readiness", "type": "select", "label": "Physical Readiness", 
                                 "options": ["Not Ready", "Somewhat Ready", "Ready", "Optimal"]},
                                {"name": "mental_readiness", "type": "select", "label": "Mental Readiness", 
                                 "options": ["Not Ready", "Somewhat Ready", "Ready", "Optimal"]},
                                {"name": "nervousness", "type": "select", "label": "Nervousness Level", 
                                 "options": ["None", "Low", "Moderate", "High", "Very High"]}
                            ]
                        },
                        {
                            "title": "Goal Setting",
                            "fields": [
                                {"name": "outcome_goals", "type": "textarea", "label": "Outcome Goals (results)"},
                                {"name": "performance_goals", "type": "textarea", "label": "Performance Goals (metrics)"},
                                {"name": "process_goals", "type": "textarea", "label": "Process Goals (focus points)"}
                            ]
                        },
                        {
                            "title": "Mental Preparation",
                            "fields": [
                                {"name": "strengths", "type": "textarea", "label": "My strengths I'll rely on:"},
                                {"name": "challenges", "type": "textarea", "label": "Potential challenges and solutions:"},
                                {"name": "key_cues", "type": "textarea", "label": "Key technical/mental cues:"},
                                {"name": "affirmations", "type": "textarea", "label": "Performance affirmations:"}
                            ]
                        }
                    ]
                },
                'is_public': True
            }
        ]
        
        creator = User.objects.filter(user_type='psychologist').first() or User.objects.filter(is_staff=True).first()
        
        for template_data in templates:
            template, created = JournalTemplate.objects.get_or_create(
                title=template_data['title'],
                defaults={
                    'description': template_data['description'],
                    'structure': template_data['structure'],
                    'created_by': creator,
                    'is_public': template_data['is_public']
                }
            )
        
        self.templates = list(JournalTemplate.objects.all())
        self.stdout.write(self.style.SUCCESS(f'Created {JournalTemplate.objects.count()} journal templates'))
    
    def create_journal_entries(self):
        self.stdout.write('Creating journal entries...')
        
        # Generate entries for the past 30 days for each athlete
        today = datetime.date.today()
        for athlete in self.athletes:
            # Only some athletes are regular journalers
            if random.random() < 0.6:  # 60% chance of being a regular journaler
                # Create between 10-20 entries in the past 30 days
                num_entries = random.randint(10, 20)
                entry_dates = sorted(random.sample(range(1, 31), num_entries))
                
                for days_ago in entry_dates:
                    entry_date = today - datetime.timedelta(days=days_ago)
                    
                    # Select a random prompt to respond to
                    prompt = random.choice(self.prompts) if self.prompts else None
                    prompt_text = prompt.text if prompt else ""
                    
                    mood = random.choice(['excellent', 'good', 'neutral', 'bad', 'terrible'])
                    energy = random.choice(['very_high', 'high', 'moderate', 'low', 'very_low'])
                    stress = random.choice(['none', 'mild', 'moderate', 'high', 'severe'])
                    sleep = round(random.uniform(5.0, 9.0), 1)  # Random sleep hours between 5-9
                    
                    # Generate title and content based on mood
                    if mood in ['excellent', 'good']:
                        title = random.choice([
                            "Feeling strong today",
                            "Great progress in training",
                            "Positive mindset",
                            "Breakthrough in technique",
                            "High energy day"
                        ])
                        content = f"""
                        Prompt: {prompt_text}
                        
                        Today was a {mood} day. I felt energized and focused during my training session.
                        {random.choice([
                            "I'm seeing improvements in my technique, especially with the adjustments my coach suggested last week.",
                            "The mental exercises are really helping me stay present during intense moments.",
                            "Recovery strategies seem to be working well - I feel less sore than usual.",
                            "My nutrition changes are making a noticeable difference in my energy levels."
                        ])}
                        
                        {random.choice([
                            "Goals for tomorrow: Continue working on breathing techniques during high-intensity intervals.",
                            "Need to remember to focus on form rather than speed for tomorrow's session.",
                            "Planning to incorporate more visualization before tomorrow's technical practice.",
                            "Tomorrow I'll pay special attention to my recovery protocol to maintain this momentum."
                        ])}
                        """
                    elif mood == 'neutral':
                        title = random.choice([
                            "Steady day",
                            "Average session",
                            "Maintaining consistency",
                            "Routine training day",
                            "Mixed results today"
                        ])
                        content = f"""
                        Prompt: {prompt_text}
                        
                        Today was a fairly standard training day. Nothing particularly outstanding but no major issues either.
                        {random.choice([
                            "My energy fluctuated throughout the session - started strong but faded in the final third.",
                            "Technique was inconsistent today. Some moments of good execution mixed with frustrating mistakes.",
                            "Mentally I felt a bit disconnected, possibly due to outside stressors affecting my focus.",
                            "Physical recovery seems on track, though I'm noticing some lingering tightness in my shoulders."
                        ])}
                        
                        {random.choice([
                            "Tomorrow I need to work on maintaining focus for the entire duration of training.",
                            "Should pay more attention to my pre-training nutrition to maintain energy levels.",
                            "Planning to implement some of the mindfulness techniques to improve my focus.",
                            "Will try to improve sleep quality tonight to see if that helps with tomorrow's performance."
                        ])}
                        """
                    else:  # bad or terrible
                        title = random.choice([
                            "Struggling today",
                            "Difficult session",
                            "Low energy day",
                            "Dealing with frustration",
                            "Recovery needed"
                        ])
                        content = f"""
                        Prompt: {prompt_text}
                        
                        Today was challenging. I felt {mood} both mentally and physically.
                        {random.choice([
                            "My body felt heavy and unresponsive during training. Possible signs of overtraining?",
                            "Frustration with lack of progress is affecting my motivation and focus.",
                            "Outside stressors are definitely impacting my performance and recovery.",
                            "Sleep has been poor which is catching up with me in terms of energy and recovery."
                        ])}
                        
                        {random.choice([
                            "Need to remember that progress isn't linear and these days are part of the journey.",
                            "Planning a lighter session tomorrow to prioritize recovery.",
                            "Going to revisit some of the stress management techniques in the resources section.",
                            "Should talk to my coach about adjusting the training plan if this continues."
                        ])}
                        """
                    
                    # Create the journal entry
                    entry = JournalEntry.objects.create(
                        user=athlete,
                        date=entry_date,
                        title=title,
                        content=content,
                        mood=mood,
                        energy_level=energy,
                        stress_level=stress,
                        sleep_hours=sleep,
                        is_private=random.choice([True, True, False]),  # 2/3 chance of being private
                        tags=random.choice(['training,reflection', 'mental,focus', 'recovery,progress', 'goals,performance', ''])
                    )
                    
                    # For some entries, share with a coach or psychologist
                    if not entry.is_private and random.random() < 0.5:
                        potential_viewers = list(User.objects.filter(user_type__in=['coach', 'psychologist']))
                        if potential_viewers:
                            viewer = random.choice(potential_viewers)
                            entry.shared_with.add(viewer)
        
        self.stdout.write(self.style.SUCCESS(f'Created {JournalEntry.objects.count()} journal entries'))