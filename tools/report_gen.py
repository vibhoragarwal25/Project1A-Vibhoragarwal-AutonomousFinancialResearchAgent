# tools/report_gen.py
def generate_report(template: str, sections: dict, 
                    sources: list) -> dict:
    report = f"# Research Report\n\n"
    for section, content in sections.items():
        report += f"## {section}\n{content}\n\n"
    return {"report": report, "template": template, 
            "word_count": len(report.split())}