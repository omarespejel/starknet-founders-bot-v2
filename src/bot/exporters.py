"""Export conversations in various formats."""
import io
from datetime import datetime
from fpdf import FPDF
import markdown2

class ConversationExporter:
    """Export conversations to different formats."""
    
    @staticmethod
    async def export_to_markdown(messages: list, user_info: dict) -> str:
        """Export conversation to Markdown format."""
        md_content = f"""# Startup Advisory Session

**Date**: {datetime.now().strftime('%Y-%m-%d')}  
**User**: {user_info.get('first_name', 'Founder')}  
**Total Messages**: {len(messages)}

---

## Conversation

"""
        for msg in messages:
            role = "**Advisor**" if msg['role'] == 'assistant' else "**You**"
            timestamp = msg.get('created_at', '')[:10]
            
            # Clean HTML tags from message
            clean_msg = msg['message'].replace('<b>', '**').replace('</b>', '**')
            clean_msg = clean_msg.replace('<i>', '*').replace('</i>', '*')
            clean_msg = clean_msg.replace('<a href="', '[').replace('">', '](').replace('</a>', ')')
            
            md_content += f"\n### {role} ({timestamp})\n\n{clean_msg}\n\n---\n"
        
        return md_content
    
    @staticmethod
    async def export_to_pdf(messages: list, user_info: dict) -> bytes:
        """Export conversation to PDF."""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Startup Advisory Session", ln=True, align='C')
        
        # Metadata
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
        pdf.cell(0, 10, f"User: {user_info.get('first_name', 'Founder')}", ln=True)
        pdf.ln(10)
        
        # Messages
        pdf.set_font("Arial", size=11)
        for msg in messages:
            role = "Advisor" if msg['role'] == 'assistant' else "You"
            
            # Role header
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 8, f"{role}:", ln=True)
            
            # Message content (truncated for PDF)
            pdf.set_font("Arial", size=10)
            clean_msg = msg['message'][:500].replace('<b>', '').replace('</b>', '')
            clean_msg = clean_msg.replace('<i>', '').replace('</i>', '')
            clean_msg = clean_msg.replace('<a href="', '').replace('">', ': ').replace('</a>', '')
            
            pdf.multi_cell(0, 6, clean_msg)
            pdf.ln(5)
        
        return pdf.output(dest='S').encode('latin-1')
