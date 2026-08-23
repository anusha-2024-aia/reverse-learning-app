import os
import json
from app.ai_service.gemini_agent import client, model_name

class ResumeParser:
    @staticmethod
    async def parse_resume(file_path: str):
        """
        Extracts text from PDF/DOCX and uses Gemini to extract skills, projects, and experience.
        """
        text = ResumeParser._extract_text(file_path)
        if not text:
            return None
            
        if not client:
            raise Exception("GEMINI_API_KEY is not configured.")
            
        system_prompt = f"""
        You are an expert technical recruiter and resume parser.
        Extract the following information from the provided resume text.

        STRICT ACCURACY & SAFETY INSTRUCTIONS:
        1. Base your response ONLY on the provided resume text.
        2. DO NOT invent, assume, or fabricate any skills, projects, experience, education, or technologies.
        3. If a section is not mentioned in the resume, use an empty list [].

        FORMATTING RULES:
        Output your response strictly as a JSON object inside <json>...</json> tags.
        
        <json>
        {{
            "skills": ["skill1", "skill2"],
            "projects": [
                {{"name": "Project Name", "description": "Brief description", "technologies": ["tech1"], "role": "Role/contribution if available"}}
            ],
            "experience": [
                {{"company": "Company", "role": "Role", "duration": "Duration", "description": "Responsibilities"}}
            ],
            "education": [
                {{"degree": "Degree", "institution": "Institution", "course": "Course/Branch", "year": "Graduation Year"}}
            ]
        }}
        </json>
        
        Resume Text:
        {text}
        """
        
        try:
            response = await client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": system_prompt}]
            )
            resp_text = response.choices[0].message.content
            
            if "<json>" in resp_text:
                start = resp_text.find("<json>") + 6
                end = resp_text.find("</json>", start)
                if end != -1:
                    data = json.loads(resp_text[start:end].strip(), strict=False)
                else:
                    data = json.loads(resp_text[start:].strip(), strict=False)
            else:
                start = resp_text.find("{")
                end = resp_text.rfind("}")
                if start != -1 and end != -1:
                    data = json.loads(resp_text[start:end+1], strict=False)
                else:
                    data = json.loads(resp_text, strict=False)
            return data
        except Exception as e:
            print(f"Error parsing resume with AI: {e}")
            return None

    @staticmethod
    def _extract_text(file_path: str) -> str:
        text = ""
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == '.pdf':
                import fitz # PyMuPDF
                doc = fitz.open(file_path)
                for page in doc:
                    text += page.get_text()
            elif ext == '.docx':
                import docx
                doc = docx.Document(file_path)
                for para in doc.paragraphs:
                    text += para.text + "\n"
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
        return text
