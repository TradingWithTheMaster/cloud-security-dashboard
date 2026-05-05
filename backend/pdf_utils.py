from fpdf import FPDF
import os

class SimpleGraduationPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 8)
            self.cell(0, 10, 'Cloud Security Monitoring & Alerting Dashboard - Technical Report', 0, 1, 'C')
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf(input_md, output_pdf):
    if not os.path.exists(input_md):
        return False
        
    pdf = SimpleGraduationPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    
    # Standard margins
    eff_width = 160 # 210 - 25 - 25 approx
    
    with open(input_md, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        text = line.strip()
        
        # Skip empty lines
        if not text:
            pdf.ln(5)
            continue
            
        # Clean text
        text = text.replace("**", "").replace("`", "").replace("–", "-").replace("—", "-")
        text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
        text = text.replace("μ", "mu").replace("σ", "sigma")
        
        # Remove any remaining non-latin1 characters to avoid fpdf errors
        text = text.encode('latin-1', 'ignore').decode('latin-1')

        if not text.strip():
            continue

        if line.startswith("# "):
            pdf.ln(10)
            pdf.set_font("Helvetica", 'B', 18)
            pdf.multi_cell(eff_width, 10, text, align='C')
            pdf.ln(5)
        elif line.startswith("## "):
            pdf.ln(5)
            pdf.set_font("Helvetica", 'B', 14)
            pdf.multi_cell(eff_width, 10, text)
            pdf.set_font("Helvetica", size=11)
        elif line.startswith("### "):
            pdf.set_font("Helvetica", 'B', 12)
            pdf.multi_cell(eff_width, 8, text)
            pdf.set_font("Helvetica", size=11)
        elif line.startswith("- "):
            pdf.set_font("Helvetica", size=11)
            # Use a slightly indented bullet point
            pdf.set_x(30)
            pdf.multi_cell(eff_width - 10, 7, f"* {text[2:]}")
        else:
            pdf.set_font("Helvetica", size=11)
            pdf.multi_cell(eff_width, 7, text)

    pdf.output(output_pdf)
    return True

if __name__ == "__main__":
    report_md = "/Users/mohamedabshir/.gemini/antigravity/brain/ab7916cf-ee2e-4a97-bbab-f36db7905645/technical_report.md"
    report_pdf = "/Users/mohamedabshir/cloud project/cloud_security_dashboard/graduation_report.pdf"
    generate_pdf(report_md, report_pdf)
    
    walk_md = "/Users/mohamedabshir/.gemini/antigravity/brain/ab7916cf-ee2e-4a97-bbab-f36db7905645/walkthrough.md"
    walk_pdf = "/Users/mohamedabshir/cloud project/cloud_security_dashboard/project_walkthrough.pdf"
    generate_pdf(walk_md, walk_pdf)
