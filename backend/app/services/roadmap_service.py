import json
from sqlalchemy.orm import Session
from app.models import Roadmap, RoadmapItem, User
from app.ai_service.gemini_agent import client, model_name
import asyncio

class RoadmapService:
    @staticmethod
    async def generate_roadmap_for_user(db: Session, user: User):
        """
        Calls Gemini to generate a personalized roadmap based on the user's profile.
        """
        if not client:
            raise Exception("GEMINI_API_KEY is not configured.")

        # Build prompt based on user profile
        target_role = user.target_role or "Software Developer"
        skill_level = user.skill_level or "Beginner"
        learning_goals = user.learning_goals or "General improvement"

        system_prompt = f"""
        You are an expert technical curriculum designer.
        The user wants to become a: {target_role}
        Their current skill level is: {skill_level}
        Their goals are: {learning_goals}
        
        Generate a comprehensive, sequential learning roadmap for them.
        
        FORMATTING RULES:
        Output your response strictly as a JSON object inside <json>...</json> tags.
        
        The JSON must have this structure:
        {{
            "items": [
                {{
                    "topic_name": "Topic Name",
                    "priority": 1, 
                    "difficulty": "beginner/intermediate/advanced",
                    "order_index": 1
                }},
                ...
            ]
        }}
        
        Keep the roadmap to a maximum of 15 key topics. 
        """

        try:
            response = await client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": system_prompt}]
            )
            text = response.choices[0].message.content
            
            if "<json>" in text:
                start = text.find("<json>") + 6
                end = text.find("</json>", start)
                if end != -1:
                    data = json.loads(text[start:end].strip(), strict=False)
                else:
                    data = json.loads(text[start:].strip(), strict=False)
            else:
                # Fallback parsing
                start = text.find("{")
                end = text.rfind("}")
                if start != -1 and end != -1:
                    data = json.loads(text[start:end+1], strict=False)
                else:
                    data = json.loads(text, strict=False)
                    
            items = data.get("items", [])
            
            # Save to database
            existing_roadmap = db.query(Roadmap).filter(Roadmap.user_id == user.id).first()
            if existing_roadmap:
                db.query(RoadmapItem).filter(RoadmapItem.roadmap_id == existing_roadmap.id).delete()
                db.delete(existing_roadmap)
                db.commit()

            roadmap = Roadmap(user_id=user.id, target_role=target_role)
            db.add(roadmap)
            db.commit()
            db.refresh(roadmap)

            for idx, item in enumerate(items):
                roadmap_item = RoadmapItem(
                    roadmap_id=roadmap.id,
                    topic_name=item.get("topic_name", f"Topic {idx+1}"),
                    priority=item.get("priority", 1),
                    difficulty=item.get("difficulty", "beginner"),
                    order_index=item.get("order_index", idx+1)
                )
                db.add(roadmap_item)
            
            db.commit()
            return {"status": "success", "roadmap_id": roadmap.id, "items": items}
            
        except Exception as e:
            print(f"Error generating roadmap: {e}")
            raise Exception(f"Error generating roadmap: {e}")
