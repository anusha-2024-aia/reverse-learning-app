from app.database import SessionLocal, engine, Base
from app.models import Curriculum, Topic

# Create tables
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    if db.query(Curriculum).first():
        print("Data already seeded.")
        db.close()
        return

    curricula_data = [
        {
            "name": "Python Fundamentals",
            "description": "Learn the basics of Python programming.",
            "difficulty": "beginner",
            "topics": [
                "Variables & Data Types",
                "Lists & Tuples",
                "Dictionaries & Sets",
                "Functions & Lambda",
                "Loops & Conditionals",
                "String Operations",
                "File I/O",
                "Exception Handling",
                "List Comprehensions",
                "Decorators & Closures"
            ]
        },
        {
            "name": "System Design Basics",
            "description": "Core concepts for designing scalable systems.",
            "difficulty": "intermediate",
            "topics": [
                "Client-Server Architecture",
                "Load Balancing",
                "Database Design (SQL vs NoSQL)",
                "Caching Strategies",
                "Message Queues",
                "API Design Principles",
                "Scalability Concepts",
                "Microservices vs Monoliths",
                "Containerization & Docker",
                "Kubernetes Basics"
            ]
        },
        {
            "name": "Communication Skills",
            "description": "Essential soft skills for engineers.",
            "difficulty": "beginner",
            "topics": [
                "Clear Technical Explanations",
                "Writing for Non-Technical Audiences",
                "Presenting Code to Others",
                "Documentation Best Practices",
                "Asking Effective Questions",
                "Code Review Etiquette",
                "Email Communication",
                "Storytelling in Tech"
            ]
        }
    ]

    for c_data in curricula_data:
        curriculum = Curriculum(
            name=c_data["name"],
            description=c_data["description"],
            difficulty=c_data["difficulty"]
        )
        db.add(curriculum)
        db.flush()

        for index, topic_name in enumerate(c_data["topics"]):
            topic = Topic(
                name=topic_name,
                curriculum_id=curriculum.id,
                description=f"Learn about {topic_name}",
                difficulty=c_data["difficulty"],
                order_in_curriculum=index + 1
            )
            db.add(topic)
            
    # Seed Achievements
    from app.models import AchievementTemplate
    achievements = [
        {"slug": "first_evaluation", "name": "First Step", "description": "Completed your first evaluation", "icon_name": "star", "criteria_type": "evaluation_count", "criteria_threshold": 1, "points": 10},
        {"slug": "five_evaluations", "name": "Five Stars", "description": "Completed 5 evaluations", "icon_name": "star", "criteria_type": "evaluation_count", "criteria_threshold": 5, "points": 25},
        {"slug": "twenty_evaluations", "name": "Scholar", "description": "Completed 20 evaluations", "icon_name": "book", "criteria_type": "evaluation_count", "criteria_threshold": 20, "points": 50},
        {"slug": "perfect_score_single", "name": "Perfectionist", "description": "Got a 10/10 on an evaluation", "icon_name": "target", "criteria_type": "perfect_score", "criteria_threshold": 1, "points": 50},
        {"slug": "perfect_score_five", "name": "Flawless", "description": "Got five 10/10 evaluations", "icon_name": "award", "criteria_type": "perfect_score", "criteria_threshold": 5, "points": 100},
        {"slug": "streak_three_days", "name": "On Fire", "description": "3-day streak", "icon_name": "flame", "criteria_type": "streak_days", "criteria_threshold": 3, "points": 30},
        {"slug": "streak_seven_days", "name": "Unstoppable", "description": "7-day streak", "icon_name": "zap", "criteria_type": "streak_days", "criteria_threshold": 7, "points": 75},
        {"slug": "grammar_master", "name": "Grammar Master", "description": "10 error-free evaluations", "icon_name": "pen-tool", "criteria_type": "grammar_perfect", "criteria_threshold": 10, "points": 40},
        {"slug": "first_curriculum", "name": "Curriculum Explorer", "description": "Completed 5 topics in one curriculum", "icon_name": "map", "criteria_type": "curriculum_topics", "criteria_threshold": 5, "points": 50},
        {"slug": "all_weak_topics_fixed", "name": "Weakness Eradicated", "description": "Fixed all weak topics", "icon_name": "shield-check", "criteria_type": "no_weak_topics", "criteria_threshold": 1, "points": 100},
        {"slug": "topic_perfect", "name": "Topic Master", "description": "Perfect score on a topic", "icon_name": "check-circle", "criteria_type": "topic_perfect", "criteria_threshold": 1, "points": 25},
        {"slug": "midnight_studier", "name": "Night Owl", "description": "Studied after 11 PM", "icon_name": "moon", "criteria_type": "midnight_eval", "criteria_threshold": 1, "points": 15},
        {"slug": "weekend_warrior", "name": "Weekend Warrior", "description": "Studied on a weekend", "icon_name": "sun", "criteria_type": "weekend_eval", "criteria_threshold": 1, "points": 20},
        {"slug": "consistency_warrior", "name": "Consistency Warrior", "description": "14-day streak", "icon_name": "crown", "criteria_type": "streak_days", "criteria_threshold": 14, "points": 150},
    ]
    
    for ach in achievements:
        template = AchievementTemplate(**ach)
        db.add(template)
        
    db.commit()
    db.close()
    print("Database seeded successfully.")

if __name__ == "__main__":
    seed_data()
