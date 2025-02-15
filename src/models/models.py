from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Project:
    name: str
    project_number: str
    location: Optional[str] = None
    sector: Optional[str] = None
    success: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    id: Optional[int] = None

    @staticmethod
    def database_schema() -> dict:
        return {
            
            "Project Name": {"title": {}},
            "Project Number": {"rich_text": {}},
            "Location": {"rich_text": {}},
            "Sector": {"select": {}},
            "RFP Status": {"checkbox": {}},
            "Start Date": {"date": {}},
            "End Date": {"date": {}}
        }
    
    

    def to_notion_properties(self) -> dict:
        """Convert to Notion API properties format"""
        properties = {
            "Project Name": {"title": [{"text": {"content": self.name}}]},
            "Project Number": {"rich_text": [{"text": {"content": self.project_number}}]},
            "Location": {"rich_text": [{"text": {"content": self.location or ""}}]},
            "Sector": {"select": {"name": self.sector} if self.sector else None},
            "RFP Status": {"checkbox": self.success if self.success is not None else False}
        }
        
        if self.start_date:
            properties["Start Date"] = {"date": {"start": self.start_date.isoformat()}}
        if self.end_date:
            properties["End Date"] = {"date": {"start": self.end_date.isoformat()}}
            
        return properties
    
    @staticmethod
    def database_schema() -> dict:
        return {
            "Project Name": {"title": {}},
            "Project Number": {"rich_text": {}},
            "Location": {"rich_text": {}},
            "Sector": {"select": {}},
            "RFP Status": {"checkbox": {}},
            "Start Date": {"date": {}},
            "End Date": {"date": {}}
        }
    
@dataclass
class TextChunk:
    content: str
    title: str
    project_number: str
    project_id: Optional[str] = None  # Optional with None default
    rating: Optional[int] = None
    date: Optional[datetime] = None
    author: Optional[str] = None
    revision_number: Optional[int] = None
    tags: Optional[List[str]] = None
    ai_tags: Optional[List[str]] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    @staticmethod
    def database_schema(project_db_id) -> dict:
        return {
            "Title": {"title": {}},
            "Content": {"rich_text": {}},
            "Project": {   # Now the key matches the one in to_notion_properties
                "relation": {
                    "database_id": project_db_id,
                    "type": "dual_property",
                    "dual_property": {}
                }
            },
            "Tags": {"multi_select": {}},
            "AI Tags": {"multi_select": {}},
            "Rating": {"number": {}},
            "Date Used": {"date": {}},
            "Author": {"rich_text": {}},
            "Revision": {"number": {}}
        }
    

    def to_notion_properties(self) -> dict:
        """
        Convert to Notion API properties format.
        Note: The "Title" field in the database was created as a rich_text field.
        """
        properties = {
            "Title": {"title": [{"text": {"content": self.title}}]},  # 
            "Content": {"rich_text": [{"text": {"content": self.content[:2000]}}]},
            "Tags": {"multi_select": [{"name": tag} for tag in (self.tags or [])]},
            "AI Tags": {"multi_select": [{"name": tag} for tag in (self.ai_tags or [])]},
            "Project": {"relation": [{"id": str(self.project_id)}]},
        }

        if self.rating:
            properties["Rating"] = {"number": self.rating}
        if self.date:
            properties["Date Used"] = {"date": {"start": self.date.isoformat()}}
        if self.author:
            properties["Author"] = {"rich_text": [{"text": {"content": self.author}}]}
        if self.revision_number:
            properties["Revision"] = {"number": self.revision_number}

        return properties
