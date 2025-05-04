# scoring.py - Scoring Engine
class ScoreCalculator:
    """Calculates assessment scores based on responses"""
    
    def __init__(self, assessment_response):
        self.assessment_response = assessment_response
        self.assessment = assessment_response.assessment
        self.questions = self.assessment.questions.all()
        self.scales = self.assessment.scales.all()
        self.question_responses = assessment_response.question_responses.all()
    
    def calculate(self):
        """Calculate scores for all scales"""
        results = {}
        
        # Get response data in a more accessible format
        response_dict = {qr.question_id: qr.answer_value for qr in self.question_responses}
        
        # Calculate raw scores
        raw_scores = self._calculate_raw_scores(response_dict)
        
        # Calculate scale scores
        for scale in self.scales:
            scale_score = self._calculate_scale_score(scale, raw_scores)
            interpretation = scale.interpret_score(scale_score)
            
            results[scale.name] = {
                'score': scale_score,
                'min': scale.min_score,
                'max': scale.max_score,
                'interpretation': interpretation
            }
        
        # Add overall score if applicable
        if len(self.scales) > 1:
            # Simple average of scale scores, normalized to 0-100
            scale_scores = [results[scale.name]['score'] for scale in self.scales]
            normalized_scores = [
                (score - scale.min_score) / (scale.max_score - scale.min_score) * 100
                for score, scale in zip(scale_scores, self.scales)
            ]
            overall_score = sum(normalized_scores) / len(normalized_scores)
            
            results['overall'] = {
                'score': overall_score,
                'min': 0,
                'max': 100
            }
        
        return results
    
    def _calculate_raw_scores(self, response_dict):
        """Calculate raw scores for each question"""
        raw_scores = {}
        
        for question in self.questions:
            if question.id not in response_dict:
                continue
                
            answer = response_dict[question.id]
            score = self._score_question(question, answer)
            raw_scores[question.id] = score
            
        return raw_scores
    
    def _score_question(self, question, answer):
        """Score an individual question based on its type and the answer"""
        if question.question_type == 'text':
            # Text responses don't contribute to numerical scores
            return None
            
        elif question.question_type in ['likert_5', 'likert_7']:
            # Likert scales are straightforward numerical values
            value = int(answer)
            max_value = 5 if question.question_type == 'likert_5' else 7
            
            # Apply reverse scoring if needed
            if question.reverse_scoring:
                value = (max_value + 1) - value
                
            return value * question.weight
            
        elif question.question_type == 'yes_no':
            # Convert yes/no to 1/0
            value = 1 if answer.lower() == 'yes' else 0
            
            # Apply reverse scoring if needed
            if question.reverse_scoring:
                value = 1 - value
                
            return value * question.weight
            
        elif question.question_type == 'multiple_choice':
            # For multiple choice, the value should be pre-determined
            # in the question configuration
            choices = question.choices
            selected_choice = next((c for c in choices if c.get('value') == answer), None)
            
            if selected_choice and 'score' in selected_choice:
                value = selected_choice['score']
                
                # Apply reverse scoring if needed
                if question.reverse_scoring:
                    # Reverse relative to the min/max scores available
                    min_score = min(c.get('score', 0) for c in choices)
                    max_score = max(c.get('score', 0) for c in choices)
                    value = max_score + min_score - value
                    
                return value * question.weight
                
            return 0
            
        elif question.question_type == 'slider':
            # Slider is a direct numerical value
            value = float(answer)
            
            # Apply reverse scoring if needed
            if question.reverse_scoring and question.min_value is not None and question.max_value is not None:
                value = question.max_value + question.min_value - value
                
            return value * question.weight
            
        return 0
    
    def _calculate_scale_score(self, scale, raw_scores):
        """Calculate score for a specific scale"""
        # Simple implementation - can be extended for more complex scoring models
        valid_scores = [score for score in raw_scores.values() if score is not None]
        
        if not valid_scores:
            return 0
            
        return sum(valid_scores) / len(valid_scores)

