from sqlalchemy.orm import Session
from sqlalchemy import func, asc, desc
from app.models import Evaluation, Topic, AdaptiveRecommendation, UserMastery
from app.services.knowledge_gap_engine import analyze_user_knowledge
import datetime

def calculate_adaptive_state(mastery_score, trend, attempt_count):
    if attempt_count == 0:
        return "NOT_STARTED"
    
    if mastery_score >= 90:
        return "MASTERED"
    elif mastery_score >= 80:
        if trend == "DECLINING":
            return "PRACTICE"
        return "STRONG"
    elif mastery_score >= 65:
        return "DEVELOPING"
    elif mastery_score >= 50:
        return "WEAK"
    else:
        return "CRITICAL"

def determine_action_type(state, attempt_count):
    if state == "NOT_STARTED":
        return "LEARN"
    elif state in ["CRITICAL", "WEAK"]:
        return "REVIEW"
    elif state == "DEVELOPING":
        return "EXPLAIN"
    elif state in ["STRONG", "PRACTICE"]:
        return "PRACTICE"
    elif state == "MASTERED":
        return "MOVE_FORWARD"
    return "REVIEW"

def calculate_priority_score(gap, attempt_count, last_attempt_days_ago):
    # Base priority from severity
    severity_weights = {
        "CRITICAL": 100,
        "HIGH": 80,
        "MEDIUM": 50,
        "LOW": 30,
        "RESOLVED": 10
    }
    
    base_priority = severity_weights.get(gap['severity'], 30)
    
    # Trend modifier
    if gap['trend'] == "DECLINING":
        base_priority += 20
    elif gap['trend'] == "IMPROVING":
        base_priority -= 10
        
    # Weakness modifier (lower mastery = higher priority)
    weakness_bonus = max(0, 100 - gap['mastery_score']) * 0.3
    
    # Recency modifier (if attempted recently and failed, high priority)
    # If not attempted in a long time and score is low, also high priority
    recency_bonus = 0
    if gap['mastery_score'] < 70 and last_attempt_days_ago < 3:
        recency_bonus = 15 # Repeated recent failure
    
    return min(100, base_priority + weakness_bonus + recency_bonus)

def determine_difficulty(mastery_score, trend):
    if mastery_score >= 85 and trend in ["IMPROVING", "STABLE"]:
        return "HARD"
    elif mastery_score >= 65:
        return "MEDIUM"
    return "EASY"

def get_target_concept_from_gap(db: Session, topic_id: int, user_id: int):
    # Fetch recent evaluations to find specific weaknesses
    evals = db.query(Evaluation).filter(
        Evaluation.user_id == user_id, 
        Evaluation.topic_id == topic_id,
        Evaluation.ai_score != None
    ).order_by(desc(Evaluation.created_at)).limit(3).all()
    
    # In a real scenario, we might parse ai_feedback_json for specific gap concepts.
    # For now, we will return a generic concept based on the topic.
    if evals and len(evals) > 0 and evals[0].ai_score is not None and evals[0].ai_score < 60:
         return "Core Fundamentals"
    return None

def generate_user_learning_path(db: Session, user_id: int):
    # Get all gaps and mastery data
    gaps = analyze_user_knowledge(db, user_id)
    
    path_nodes = []
    
    now = datetime.datetime.now(datetime.timezone.utc)
    
    for gap in gaps:
        # Get attempt stats
        evals = db.query(Evaluation).filter(
            Evaluation.user_id == user_id, 
            Evaluation.topic_id == gap['topic_id'],
            Evaluation.ai_score != None
        ).order_by(desc(Evaluation.created_at)).all()
        
        attempt_count = gap['attempts']
        
        last_attempt_days_ago = 0
        if evals:
            last_eval = evals[0]
            # Ensure last_eval.created_at is timezone-aware
            last_created = last_eval.created_at
            if last_created.tzinfo is None:
                last_created = last_created.replace(tzinfo=datetime.timezone.utc)
            delta = now - last_created
            last_attempt_days_ago = delta.days
            
        state = calculate_adaptive_state(gap['mastery_score'], gap['trend'], attempt_count)
        action_type = determine_action_type(state, attempt_count)
        priority = calculate_priority_score(gap, attempt_count, last_attempt_days_ago)
        difficulty = determine_difficulty(gap['mastery_score'], gap['trend'])
        target_concept = get_target_concept_from_gap(db, gap['topic_id'], user_id)
        
        node = {
            "topic_id": gap['topic_id'],
            "topic_name": gap['topic_name'],
            "mastery_score": gap['mastery_score'],
            "state": state,
            "action_type": action_type,
            "priority": priority,
            "difficulty": difficulty,
            "trend": gap['trend'],
            "target_concept": target_concept,
            "reason": gap['recommendation']
        }
        path_nodes.append(node)
        
    # Add topics not yet attempted (if we have a roadmap or curriculum)
    all_topics = db.query(Topic).all()
    attempted_topic_ids = [n['topic_id'] for n in path_nodes]
    
    for topic in all_topics:
        if topic.id not in attempted_topic_ids:
            path_nodes.append({
                "topic_id": topic.id,
                "topic_name": topic.name,
                "mastery_score": 0,
                "state": "NOT_STARTED",
                "action_type": "LEARN",
                "priority": 10, # Low priority compared to failing topics, but higher than mastered
                "difficulty": "EASY",
                "trend": "STABLE",
                "target_concept": None,
                "reason": f"Start learning {topic.name}."
            })
            
    # Sort by priority descending
    path_nodes.sort(key=lambda x: x['priority'], reverse=True)
    return path_nodes

def calculate_next_recommendation(db: Session, user_id: int):
    # Mark old pending recommendations as skipped or obsolete if they exist
    existing_pending = db.query(AdaptiveRecommendation).filter(
        AdaptiveRecommendation.user_id == user_id,
        AdaptiveRecommendation.status == "PENDING"
    ).all()
    
    for req in existing_pending:
        req.status = "OBSOLETE"
    db.commit()

    path = generate_user_learning_path(db, user_id)
    
    if not path:
        return None
        
    top_node = path[0]
    
    # If top node is MASTERED, maybe student is done with all topics
    if top_node['state'] == "MASTERED" and top_node['priority'] < 20:
        return None # Everything mastered
        
    # Create new recommendation
    new_rec = AdaptiveRecommendation(
        user_id=user_id,
        topic_id=top_node['topic_id'],
        action_type=top_node['action_type'],
        priority_score=top_node['priority'],
        reason=top_node['reason'],
        target_concept=top_node['target_concept'],
        difficulty=top_node['difficulty'],
        status="PENDING"
    )
    
    db.add(new_rec)
    db.commit()
    db.refresh(new_rec)
    
    return new_rec
