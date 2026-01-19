from fpdf import FPDF
from datetime import datetime
import io

class SovereignReport(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(255, 75, 75) # Sovereign Red
        self.cell(0, 10, '🛡️ SOVEREIGN SIEVE: PHYSICS VERDICT', border=False, ln=True, align='C')
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'Falsification-as-a-Service (FaaS) Industrial Logic Engine', border=False, ln=True, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()} | Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M")}', align='C')

    @staticmethod
    def generate_verdict_pdf(job_data):
        pdf = SovereignReport()
        pdf.add_page()
        
        # Job Metadata
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 10, f"JOB ID: {job_data['job_id']}", ln=True)
        pdf.set_font('helvetica', '', 10)
        pdf.cell(0, 10, f"File Name: {job_data['file_name']}", ln=True)
        pdf.cell(0, 10, f"Target: Chain {job_data['target_chain']} | Binder: Chain {job_data['binder_chain']}", ln=True)
        pdf.ln(5)

        # Verdict Section
        verdict = job_data['verdict']
        pdf.set_fill_color(255, 200, 200) if "VETO" in verdict else pdf.set_fill_color(200, 255, 200)
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 15, f"OFFICIAL VERDICT: {verdict}", border=True, ln=True, align='C', fill=True)
        pdf.ln(10)

        # Physics Metrics Table
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 10, "Physics Audit Metrics:", ln=True)
        pdf.set_font('helvetica', '', 10)
        
        metrics = job_data['metrics']
        data = [
            ["Metric", "Value", "Industrial Status"],
            ["Contact Density (rho)", str(metrics.get('rho', 'N/A')), "PASS" if metrics.get('rho', 0) > 100 else "FAIL"],
            ["Heavy Atom Clashes", str(metrics.get('clashes', 'N/A')), "PASS" if metrics.get('clashes', 0) == 0 else "VETO"],
            ["Min Distance (A)", str(metrics.get('min_distance_A', 'N/A')), "SAFE" if metrics.get('min_distance_A', 0) > 2.5 else "CRITICAL"]
        ]

        # Draw Table
        for row in data:
            pdf.cell(60, 10, row[0], border=True)
            pdf.cell(60, 10, row[1], border=True)
            pdf.cell(60, 10, row[2], border=True, ln=True)
        
        pdf.ln(10)

        # Adversarial Benchmarking
        adv = metrics.get('adversarial', {})
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 10, "Adversarial Benchmark (vs Clinical Clinical Gold Standard):", ln=True)
        pdf.set_font('helvetica', '', 10)
        pdf.cell(0, 10, f"Sovereignty Score: {adv.get('sovereignty_score', 'N/A')}%", ln=True)
        pdf.cell(0, 10, f"RMSD vs WL12 (Clinical): {adv.get('rmsd_vs_clinical', 'N/A')} A", ln=True)
        
        pdf.ln(20)
        pdf.set_font('helvetica', 'I', 8)
        pdf.multi_cell(0, 5, "Disclaimer: This report is a computational falsification audit using industrial physics parameters. It is intended to veto impossible designs. Pass verdicts do not guarantee clinical efficacy but indicate physical plausibility.")

        return pdf.output()
