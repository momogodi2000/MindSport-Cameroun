
# recommendation.py - Recommendation Engine
class RecommendationEngine:
    """Recommends specialists based on assessment results"""
    
    def __init__(self, assessment_response):
        self.assessment_response = assessment_response
        self.athlete = assessment_response.athlete
        self.scores = assessment_response.scores
    
    def generate_recommendations(self):
        """Generate specialist recommendations based on assessment results"""
        from django.db.models import Q
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        recommendations = []
        
        # Get all available specialists
        specialists = User.objects.filter(
            user_type__in=['psychologist', 'coach', 'nutritionist'],
            is_active=True,
            is_verified_professional=True
        )
        
        # For each scale in the assessment
        for scale_name, scale_data in self.scores.items():
            if scale_name == 'overall':  # Skip overall score
                continue
                
            interpretation = scale_data.get('interpretation', {})
            if not interpretation:
                continue
                
            # Get specialists matching this scale's needs
            matching_specialists = self._find_matching_specialists(
                specialists, 
                scale_name,
                interpretation
            )
            
            # Add to recommendations
            for specialist, reason in matching_specialists:
                recommendations.append({
                    'specialist': specialist,
                    'reason': reason,
                    'priority': self._calculate_priority(scale_data, interpretation)
                })
        
        # Sort by priority and return
        recommendations.sort(key=lambda x: x['priority'])
        return recommendations
    
    def _find_matching_specialists(self, specialists, scale_name, interpretation):
        """Find specialists matching the needs identified in the interpretation"""
        from django.db.models import Q
        
        matches = []
        
        # Get expertise keywords from interpretation
        keywords = interpretation.get('recommendations', [])
        label = interpretation.get('label', '')
        
        for specialist in specialists:
            # Skip if no specialist_profile
            if not hasattr(specialist, 'specialist_profile'):
                continue
                
            expertise = specialist.specialist_profile.expertise_areas.lower()
            match_reason = None
            
            # Check if specialist expertise matches keywords
            for keyword in keywords:
                if keyword.lower() in expertise:
                    match_reason = f"Expertise in {keyword} for {scale_name} scale ({label})"
                    break
            
            # If scale name itself is part of expertise
            if not match_reason and scale_name.lower() in expertise:
                match_reason = f"Specializes in {scale_name} ({label})"
            
            if match_reason:
                matches.append((specialist, match_reason))
        
        # If no matches, include generalists
        if not matches:
            for specialist in specialists:
                if not hasattr(specialist, 'specialist_profile'):
                    continue
                    
                if 'general' in specialist.specialist_profile.expertise_areas.lower():
                    matches.append((
                        specialist, 
                        f"General expertise relevant to {scale_name} ({label})"
                    ))
        
        return matches
    
    def _calculate_priority(self, scale_data, interpretation):
        """Calculate priority based on score severity"""
        # Simplistic implementation - can be extended
        score = scale_data['score']
        min_score = scale_data['min']
        max_score = scale_data['max']
        
        # Normalize to 0-1 scale
        normalized_score = (score - min_score) / (max_score - min_score)
        
        # Check if this is a concerning score (either very low or very high)
        # Assuming scores closer to extremes require more urgent attention
        severity = min(normalized_score, 1 - normalized_score)
        
        # Convert to priority (1-5 where 1 is highest priority)
        if severity < 0.2:
            return 1  # High priority
        elif severity < 0.4:
            return 2
        elif severity < 0.6:
            return 3
        elif severity < 0.8:
            return 4
        else:
            return 5  # Low priority
    
    def save_recommendations(self):
        """Save generated recommendations to database"""
        from backend.models import RecommendedSpecialist
        
        # Generate recommendations
        recommendations = self.generate_recommendations()
        
        # Save to database
        for rec in recommendations:
            RecommendedSpecialist.objects.create(
                assessment_response=self.assessment_response,
                specialist=rec['specialist'],
                recommendation_reason=rec['reason'],
                priority=rec['priority']
            )
        
        return len(recommendations)