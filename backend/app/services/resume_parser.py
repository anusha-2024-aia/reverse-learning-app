import os
import json
from app.ai_service.gemini_agent import client, model_name
from app.core.logging_config import logger

class ResumeParser:
    @staticmethod
    async def parse_resume(file_path: str):
        """
        Extracts text from PDF/DOCX and uses Gemini to extract skills, projects, and experience.
        Falls back to rule-based parser without fabricating data if AI service is unavailable.
        """
        text = ResumeParser._extract_text(file_path)
        if not text:
            return None
            
        from app.services.resume_intelligence_service import ResumeIntelligenceService

        if not client:
            return ResumeIntelligenceService.fallback_rule_based_parse(text)
            
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

            if isinstance(data, dict):
                data["skills"] = [s for s in data.get("skills", []) if isinstance(s, str)] if isinstance(data.get("skills"), list) else []
                data["projects"] = [p for p in data.get("projects", []) if isinstance(p, dict)] if isinstance(data.get("projects"), list) else []
                data["experience"] = [e for e in data.get("experience", []) if isinstance(e, dict)] if isinstance(data.get("experience"), list) else []
                data["education"] = [ed for ed in data.get("education", []) if isinstance(ed, dict)] if isinstance(data.get("education"), list) else []
                return data

            return ResumeIntelligenceService.fallback_rule_based_parse(text)
        except Exception as e:
            logger.warning(f"Error parsing resume with AI (using fallback): {e}")
            return ResumeIntelligenceService.fallback_rule_based_parse(text)

    @staticmethod
    def _extract_text(file_path: str) -> str:
        text = ""
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == '.pdf':
                import fitz # PyMuPDF
                with open(file_path, "rb") as f:
                    pdf_bytes = f.read()
                with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                    for page in doc:
                        text += page.get_text() + "\n"
            elif ext == '.docx':
                import docx
                import io
                with open(file_path, "rb") as f:
                    docx_bytes = f.read()
                doc = docx.Document(io.BytesIO(docx_bytes))
                for para in doc.paragraphs:
                    if para.text.strip():
                        text += para.text + "\n"
                for table in doc.tables:
                    for row in table.rows:
                        row_items = []
                        seen_cells = set()
                        for cell in row.cells:
                            ctext = cell.text.strip()
                            if ctext and ctext not in seen_cells:
                                seen_cells.add(ctext)
                                row_items.append(ctext)
                        if row_items:
                            text += " | ".join(row_items) + "\n"
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None
        return text.strip() if text else None
