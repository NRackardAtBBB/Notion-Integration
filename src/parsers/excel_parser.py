import pandas as pd
import re
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ParsedMetadata:
    title: str
    date: str
    project_name: str 
    project_number: str

@dataclass
class TextChunk:
    content: str
    header: str
    section_title: str = ""
    metadata: Optional[ParsedMetadata] = None
    

class ExcelParser:
    def __init__(self, file_path: str):
        self.df = pd.read_excel(file_path)
        
        # Core patterns for header components
        self.header_indicators = {
            'project_number': r'[A-Z]{3}\s*\d{2}\s*\.\s*\d{2}',
            'bracketed_content': r'\[([^\]]+)\]',
            'date_patterns': [
                r'\[(\d{4},\s*\d{1,2}/\d{1,2})[^\]]*\]',  # [YYYY, M/D]
                r'(\d{4}/\d{1,2}/\d{1,2})',               # YYYY/MM/DD
                r'\[?(\d{1,2}/\d{1,2}/\d{4})\]?'          # [MM/DD/YYYY], with optional brackets
            ],
            'used_in': r'Used in\s*:?\s*'
        }

    def _is_section_title(self, line: str) -> bool:
        """
        Returns True if the line meets the heuristic for a 'section title':
        - Non-empty
        - Doesn't end with . : ! ?
        - Less than or equal to 70 characters (or <= 10 words)
        Adjust as needed for your use case.
        """
        line = line.strip()
        if not line:
            return False
        
        # If line ends with punctuation commonly used to end a sentence, skip it
        if line[-1] in ['.', ':', '!', '?']:
            return False

        # Check length or word count (tweak thresholds as desired)
        if len(line) > 70:
            return False
        if len(line.split()) > 10:
            return False
        
        return True

    def _normalize_date(self, date_str: str) -> str:
        """
        Normalize the date string to a standard format: YYYY-MM-DD.
        Tries several input formats.
        """
        # List of potential input formats
        date_formats = [
            "%Y, %m/%d",   # e.g., "2023, 7/31" (if that's ever used)
            "%Y/%m/%d",    # e.g., "2023/07/31" or "2023/7/31"
            "%m/%d/%Y",    # e.g., "07/31/2023" or "7/31/2023"
            "%Y-%m-%d"     # in case it's already normalized
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        # If parsing fails, return the original string
        return date_str



    def _is_standalone_line(self, text: str, lines: List[str], current_index: int) -> bool:
        """
        Check if line is standalone by verifying:
        1. It's either the first line OR has a blank line before it
        2. It's not an empty line itself
        """
        # First ensure the line itself has content
        if not text.strip():
            return False
            
        # Case 1: First line of the text
        if current_index == 0:
            return True
            
        # Case 2: Has blank line before it
        prev_line = lines[current_index - 1].strip()
        return not prev_line

    def _count_header_indicators(self, line: str) -> int:
        """
        Count how many header indicators are present in the line
        """
        count = 0
        
        # Check for project number
        if re.search(self.header_indicators['project_number'], line):
            count += 1
            
        # Check for bracketed content
        if re.search(self.header_indicators['bracketed_content'], line):
            count += 1
            
        # Check for dates
        for date_pattern in self.header_indicators['date_patterns']:
            if re.search(date_pattern, line):
                count += 1
                break
                
        # Check for "Used in"
        if re.search(self.header_indicators['used_in'], line):
            count += 1
            
        return count

    def _check_for_header(self, line: str, lines: List[str], current_index: int) -> bool:
        """
        Determine if a line is a header based on multiple criteria
        """
        # Must be a non-empty standalone line
        if not line.strip() or not self._is_standalone_line(line, lines, current_index):
            return False
            
        # Count header indicators
        indicator_count = self._count_header_indicators(line)
        
        # Line is a header if it has at least 2 indicators
        return indicator_count >= 2

    def parse_text_column(self, test_rows: Optional[int] = None) -> pd.DataFrame:
        """
        Parse and split text column into multiple rows based on headers.
        """
        working_df = self.df.copy()
        if test_rows:
            working_df = working_df.head(test_rows)
            
        result_rows = []
        for idx, row in working_df.iterrows():
            text_content = row['Text']
            
            # --- PREPROCESSING STEP: Remove bullet points and breaklines ---
            # Example 1: direct string replacements
            text_content = text_content.replace("●", "")
            text_content = text_content.replace("----------------------------------------------------------", "")
            
            # If you have multiple bullet chars or variations in the breaklines,
            # you can use a more general regex approach, for example:
            #
            # import re
            text_content = re.sub(r'[●•]', '', text_content)  # remove any bullet-like characters
            text_content = re.sub(r'-{2,}', '', text_content) # remove any sequence of 5+ dashes
            
            name = row['Name']
            description = row['Description']
            
            chunks = self._split_into_chunks(text_content)
            
            for chunk in chunks:
                new_row = {
                    'Name': name,
                    'Description': description,
                    'Text': chunk.content,
                    'Raw_Header': chunk.header,
                    # If you have a Section_Title or other fields, include them too:
                    'Section_Title': chunk.section_title if hasattr(chunk, 'section_title') else "",
                    'Title': chunk.metadata.title,
                    'Date': chunk.metadata.date,
                    'Project_Name': chunk.metadata.project_name,
                    'Project_Number': chunk.metadata.project_number
                }
                result_rows.append(new_row)
                
        return pd.DataFrame(result_rows)



    def _split_into_chunks(self, text: str) -> List[TextChunk]:
        """
        Split text into chunks based on headers and section titles.
        - A 'header' still starts a brand-new chunk with new metadata.
        - A 'section title' also starts a new chunk but retains the existing metadata.
        """
        chunks = []
        lines = text.split('\n')
        
        current_chunk_lines = []
        current_header = ""
        current_section_title = ""
        current_metadata = ParsedMetadata(title="", date="", project_name="", project_number="")

        for i, line in enumerate(lines):
            # 1) Check if line is a brand-new chunk header
            if self._check_for_header(line, lines, i):
                # Finalize the existing chunk
                if current_chunk_lines:
                    chunks.append(TextChunk(
                        header=current_header,
                        metadata=current_metadata,
                        section_title=current_section_title,
                        content='\n'.join(current_chunk_lines)
                    ))
                
                # Start a new chunk
                current_chunk_lines = []
                current_header = line
                current_section_title = ""
                current_metadata = self._extract_metadata(line)

            # 2) Else if it's recognized as a section title
            elif self._is_section_title(line):
                # Finalize the existing chunk
                if current_chunk_lines:
                    chunks.append(TextChunk(
                        header=current_header,
                        metadata=current_metadata,
                        section_title=current_section_title,
                        content='\n'.join(current_chunk_lines)
                    ))
                
                # Start a new chunk but keep existing header & metadata
                current_chunk_lines = []
                current_section_title = line

            # 3) Otherwise, it's just part of the current chunk content
            else:
                current_chunk_lines.append(line)

        # After the loop, finalize the last chunk if there's remaining text
        if current_chunk_lines:
            chunks.append(TextChunk(
                header=current_header,
                metadata=current_metadata,
                section_title=current_section_title,
                content='\n'.join(current_chunk_lines)
            ))
        
        return chunks

    def _extract_metadata(self, header_text: str) -> ParsedMetadata:
        """
        Extract metadata components from header text, and derive a 'title' from what's left.
        This method also normalizes the date and strips whitespace from the project number.
        """
        project_number = ""
        date = ""
        project_name = ""

        # 1. Match Project Number
        proj_num_match = re.search(self.header_indicators['project_number'], header_text)
        if proj_num_match:
            # Remove all whitespace from the project number (e.g., "ONY 32.12" becomes "ONY32.12")
            project_number = re.sub(r'\s+', '', proj_num_match.group(0).strip())

        # 2. Match Date using the various patterns
        date_match = None
        for date_pattern in self.header_indicators['date_patterns']:
            date_match_candidate = re.search(date_pattern, header_text)
            if date_match_candidate:
                date_match = date_match_candidate
                # Use the first captured group if available; otherwise, use the whole match.
                raw_date = date_match_candidate.group(1).strip() if date_match_candidate.groups() else date_match_candidate.group(0).strip()
                # Normalize the date format
                date = self._normalize_date(raw_date)
                break

        # 3. Extract Project Name (if both project number and date were found)
        if proj_num_match and date_match:
            start_idx = proj_num_match.end()
            end_idx = date_match.start()
            project_name = header_text[start_idx:end_idx].strip()
            # Remove trailing characters like underscores or left brackets (e.g., "Southwestern University_[" becomes "Southwestern University")
            project_name = re.sub(r'[_\[]+$', '', project_name).strip()

        # 4. Construct the "title" by removing matched substrings (project_number, date, project_name)
        original_text = header_text
        spans_to_remove = []
        if proj_num_match:
            spans_to_remove.append(proj_num_match.span())
        if date_match:
            spans_to_remove.append(date_match.span())
        if proj_num_match and date_match:
            spans_to_remove.append((start_idx, end_idx))
        
        # Remove the matched segments in reverse order to avoid index shifts
        spans_to_remove.sort(key=lambda x: x[0], reverse=True)
        for s, e in spans_to_remove:
            original_text = original_text[:s] + original_text[e:]
        
        # 5. Clean up the leftover text to form the title:
        #    a) Remove "Used in" (case-insensitive) and any following colon
        title = re.sub(r'(?i)\bUsed\s+in\s*:?', '', original_text)
        #    b) Remove any square brackets
        title = re.sub(r'[\[\]]+', '', title)
        #    c) Replace underscores with spaces
        title = title.replace('_', ' ')
        #    d) Trim leading/trailing whitespace
        title = title.strip()

        return ParsedMetadata(
            title=title,
            date=date,
            project_name=project_name,
            project_number=project_number
        )

    def save_parsed_data(self, output_path: str, df: Optional[pd.DataFrame] = None):
        """
        Save the parsed data to a new Excel file
        
        Args:
            output_path: Path to save the Excel file
            df: Optional DataFrame to save, uses parsed data if not provided
        """
        if df is None:
            df = self.parse_text_column()
        df.to_excel(output_path, index=False)
