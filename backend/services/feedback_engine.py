#what is specifically wrong in my resume?

import re
from typing import List, Dict, Any, Optional
from backend.models.schemas import IssueDetail

def analyze_issues(
        resume_text: str, 
        parsed_resume: Dict, 
        skills: List[str], 
        projects: List[Dict], 
        action_verbs: List[str], 
        skill_validation: Dict, 
        scores: Dict, 
        contact_info: Optional[Dict]=None, 
) -> List[IssueDetail]:
    
    detected: List[IssueDetail]=[]

    #Unpack frequently-used structured fields once at the top

    exp_entries  = [e for e in parsed_resume.get('experience', []) if isinstance(e, dict)]
    edu_entries  = [e for e in parsed_resume.get('education',  []) if isinstance(e, dict)]
    proj_entries = [p for p in parsed_resume.get('projects',   []) if isinstance(p, dict)]
    summary      = (parsed_resume.get('professional_summary') or '').strip()

    #Build a combined experience text for regex-based checks that still need text
    experience_text = '\n'.join(e.get('description', '') for e in exp_entries).strip()


    #1. missig project section
    resume_lower = resume_text.lower()
    has_projects_signal = any(kw in resume_lower for kw in [
        'project', 'github.com', 'deployed', 'built a', 'developed a',
        'created a', 'implemented a', 'live demo', 'tech stack',
    ])

    if not proj_entries and len(projects) == 0 and not has_projects_signal:
        detected.append(IssueDetail(
            issue_title="Missing Projects Section",
            severity_level="High",
            ats_impact="High",
            explanation=(
                "Your resume does not have a dedicated Projects section. "
                "ATS systems and recruiters look for concrete projects to validate "
                "that your listed skills have been applied in practice."
            ),
            where_it_appears="Resume structure — no 'Projects' header was detected",
            how_to_fix=(
                "Add a 'Projects' section with 2–3 significant projects. "
                "For each project, include the title, technologies used, "
                "what you built, and a measurable outcome."
            ),
            action_items=[
                "Add a 'PROJECTS' section heading after your Experience section",
                "Include 2–3 projects (personal, academic, or open-source)",
                "For each project: write the title, tech stack used, what you built, and a measurable result",
                "Example: 'E-Commerce Platform — React, Node.js, MongoDB. Handled 500+ transactions/month'",
                "Link to GitHub or a live demo if available (e.g., github.com/yourname/project)",
            ],
            example_improvement=(
                "Add:\n"
                "PROJECTS\n"
                "• E-Commerce Platform — Built a full-stack shopping site using "
                "React, Node.js, and MongoDB. Implemented payment processing with "
                "Stripe, handling 500+ transactions/month.\n"
                "• ML Sentiment Analyzer — Trained a BERT model on 10K reviews "
                "achieving 92% accuracy. Deployed as a REST API with FastAPI."
            ),
        ))

    #2. missing experience section
    has_experience_signal = any(kw in resume_lower for kw in [
        'intern', 'internship', 'employed', 'worked at', 'working at',
        'company', 'organization', 'job', 'role', 'position', 'designation',
        'manager', 'engineer', 'developer', 'analyst', 'consultant',
    ])

    if not exp_entries and not has_experience_signal:
        detected.append(IssueDetail(
            issue_title="Missing Work Experience Section",
            severity_level="High",
            ats_impact="High",
            explanation=(
                "No work experience section was detected. Even for freshers, "
                "internships, freelance work, or volunteer experience help "
                "demonstrate professional capability."
            ),
            where_it_appears="Resume structure — no 'Experience' or 'Work History' header found",
            how_to_fix=(
                "Add an 'Experience' section. If you lack formal employment, "
                "include internships, freelance projects, open-source contributions, "
                "or relevant volunteer work."
            ),
            action_items=[
                "Add an 'EXPERIENCE' or 'INTERNSHIPS' section to your resume",
                "List each role with: Job Title — Company Name (Month Year – Month Year)",
                "Add 2–4 bullet points per role describing what you did and its impact",
                "If no formal job: include internships, freelance work, open-source, or college clubs",
                "Start every bullet with a past-tense action verb (Developed, Built, Led, etc.)",
            ],
            example_improvement=(
                "Add:\n"
                "EXPERIENCE\n"
                "Software Engineering Intern — XYZ Corp (Jun 2025 – Aug 2025)\n"
                "• Developed REST APIs with FastAPI serving 10K requests/day\n"
                "• Reduced page load time by 40% through caching optimization"
            ),
        ))

    #3. Missing Education Section 
    has_education_signal = any(kw in resume_lower for kw in [
        'b.tech', 'btech', 'b.e.', 'b.sc', 'bsc', 'm.tech', 'mtech', 'm.sc',
        'bachelor', 'master', 'phd', 'university', 'college',
        'institute of technology', 'cgpa', 'gpa', 'graduated', 'diploma',
        'class of', '20', 'batch of',
    ])
    if not edu_entries and not has_education_signal:
        detected.append(IssueDetail(
            issue_title="Missing Education Section",
            severity_level="Moderate",
            ats_impact="Medium",
            explanation=(
                "No education section was found. Most ATS systems expect an "
                "Education section with at least your degree and institution."
            ),
            where_it_appears="Resume structure — no 'Education' header detected",
            how_to_fix=(
                "Add an 'Education' section listing your degree, university, "
                "graduation year, and optionally your GPA or relevant coursework."
            ),
            action_items=[
                "Add an 'EDUCATION' section (usually at the bottom for experienced candidates, top for freshers)",
                "Include: Degree name — Institution name (Start Year – End Year)",
                "Add your CGPA or percentage if it is 7.0+ or 70%+",
                "Optionally list 3–5 relevant courses (e.g., Data Structures, DBMS, ML)",
            ],
            example_improvement=(
                "Add:\n"
                "EDUCATION\n"
                "B.Tech in Computer Science — IIT Delhi (2021–2025)\n"
                "CGPA: 8.5 | Relevant Coursework: Data Structures, ML, DBMS"
            ),
        ))

    #4. Missing Skills Section 
    if not parsed_resume.get('skills') and len(skills) < 3:
        detected.append(IssueDetail(
            issue_title="Missing or Weak Skills Section",
            severity_level="High",
            ats_impact="High",
            explanation=(
                f"Only {len(skills)} skill(s) were detected. ATS systems "
                "rely heavily on keyword matching from a dedicated Skills section. "
                "Without clear skills listed, your resume may fail automated filters."
            ),
            where_it_appears="Skills section — either missing or contains very few items",
            how_to_fix=(
                "Add a clear 'Skills' section organized by category. "
                "Include programming languages, frameworks, tools, and soft skills "
                "that match your target role."
            ),
            action_items=[
                "Add a 'TECHNICAL SKILLS' or 'SKILLS' section",
                "Organize by category: Languages, Frameworks, Tools, Databases, Cloud",
                "List at least 10–15 skills relevant to your target role",
                "Use the exact names that appear in job descriptions (e.g., 'React.js' not just 'React')",
                "Include tools you use daily: Git, VS Code, Postman, Docker, etc.",
            ],
            example_improvement=(
                "Add:\n"
                "TECHNICAL SKILLS\n"
                "Languages: Python, JavaScript, TypeScript, SQL\n"
                "Frameworks: React, FastAPI, Django, Express.js\n"
                "Tools: Docker, Git, AWS, PostgreSQL, MongoDB"
            ),
        ))

    # 5. Skills Lack Supporting Evidence
    # FIX: previously only fired when unvalidated > validated (~effectively >50%).
    # That missed cases like 14/30 (47%) unvalidated, which is still worth flagging.
    # Now fires at >=30% unvalidated, with severity scaling by how bad it is.
    unvalidated = skill_validation.get('unvalidated_skills', [])
    validated   = skill_validation.get('validated_skills', [])
    total_skills = len(unvalidated) + len(validated)

    if total_skills > 0:
        pct_unsupported = round((len(unvalidated) / total_skills) * 100)
        EVIDENCE_THRESHOLD_PCT = 30  # was implicitly ~50% before

        if pct_unsupported >= EVIDENCE_THRESHOLD_PCT:
            severity = "High" if pct_unsupported >= 50 else "Moderate"
            unsupported_list = ', '.join(unvalidated[:8])
            action_items_skills = [
                f"Mention '{skill}' in a project or experience bullet point" for skill in unvalidated[:5]
            ]
            action_items_skills.append("Remove skills you cannot demonstrate with any project or experience")
            if len(unvalidated) > 5:
                action_items_skills.append(f"({len(unvalidated) - 5} more unvalidated skills — review each one)")

            title = (
                "Most Skills Lack Supporting Evidence"
                if severity == "High"
                else "Some Skills Lack Supporting Evidence"
            )

            detected.append(IssueDetail(
                issue_title=title,
                severity_level=severity,
                ats_impact="High" if severity == "High" else "Moderate",
                explanation=(
                    f"{pct_unsupported}% of your listed skills ({len(unvalidated)} out of "
                    f"{total_skills}) are not backed by any mention in your projects or "
                    "experience sections. Recruiters and ATS systems cross-reference "
                    "skills against actual work to verify credibility."
                ),
                where_it_appears=f"These skills have no supporting context: {unsupported_list}",
                how_to_fix=(
                    "For each skill in your Skills section, ensure it appears at least "
                    "once in a project description or experience bullet point. "
                    "Describe how and where you used that technology."
                ),
                action_items=action_items_skills,
                example_improvement=(
                    f"Your skill '{unvalidated[0]}' has no supporting evidence.\n\n"
                    f"Fix: Add to a project or experience bullet:\n"
                    f"'Built a data pipeline using {unvalidated[0]} that processed "
                    "10K records daily, reducing manual effort by 60%.'"
                ),
            ))

    #6. Weak Action Verbs 
    description_lines = [
        line.strip()
        for exp in exp_entries
        for line in exp.get('description', '').split('\n')
        if line.strip()
    ]

    if len(description_lines) > 3 and len(action_verbs) < 3:
        detected.append(IssueDetail(
            issue_title="Bullet Points Lack Strong Action Verbs",
            severity_level="Moderate",
            ats_impact="Medium",
            explanation=(
                f"Your experience section has {len(description_lines)} bullet points but "
                f"only {len(action_verbs)} start with strong action verbs. "
                "ATS systems and recruiters favor bullets that begin with verbs like "
                "'Developed', 'Implemented', 'Designed', 'Optimized'."
            ),
            where_it_appears="Experience section — bullet point openings",
            how_to_fix=(
                "Start every bullet point with a past-tense action verb. "
                "Avoid starting with 'Responsible for', 'Worked on', or 'Helped with'. "
                "Use verbs like: Developed, Built, Designed, Implemented, Led, Automated, Optimized."
            ),
            action_items=[
                "Rewrite every bullet that starts with 'Responsible for', 'Helped', 'Worked on', or 'Assisted'",
                "Use: Developed, Built, Designed, Implemented, Led, Automated, Optimized, Deployed, Reduced, Increased",
                "Make verbs past-tense for previous roles, present-tense for current role",
                f"Review all {len(description_lines)} bullet points — at least {len(description_lines)} should start with action verbs",
                "Avoid weak openers like 'Was responsible for...' or 'Involved in...'",
            ],
            example_improvement=(
                "Before:\n"
                "• Responsible for building the backend\n"
                "• Worked on the payment feature\n\n"
                "After:\n"
                "• Developed a REST API with FastAPI handling 5K daily requests\n"
                "• Implemented Stripe payment integration reducing checkout time by 30%"
            ),
        ))

    #7. No Quantifiable Achievements 
    number_pattern = r'\d+[%+]?|\$\d+'
    has_metrics = bool(re.findall(number_pattern, experience_text)) if experience_text else False

    if experience_text and not has_metrics:
        detected.append(IssueDetail(
            issue_title="No Quantifiable Achievements Found",
            severity_level="Moderate",
            ats_impact="Medium",
            explanation=(
                "Your experience section does not contain any measurable outcomes "
                "(numbers, percentages, or dollar amounts). Quantified achievements "
                "make your impact concrete and are strongly preferred by recruiters."
            ),
            where_it_appears="Experience section — bullet point content",
            how_to_fix=(
                "Add numbers to at least 50% of your bullet points. "
                "Include metrics like: users served, response time improved, "
                "revenue generated, lines of code, team size, etc."
            ),
            action_items=[
                "Go through each bullet point and ask: 'How much?', 'How many?', 'By what %?'",
                "Add metrics: users served, requests/day, % improvement, team size, time saved",
                "Examples: '500+ daily users', 'reduced load time by 40%', 'handled 10K API calls/day'",
                "If exact numbers aren't known, use reasonable estimates (e.g., '~200 users')",
                "Aim for numbers in at least 50% of your experience bullets",
            ],
            example_improvement=(
                "Before:\n"
                "• Improved application performance\n"
                "• Managed a team of developers\n\n"
                "After:\n"
                "• Improved API response time by 45% through Redis caching\n"
                "• Led a team of 5 developers delivering 3 features per sprint"
            ),
        ))

    #8. Missing Contact Information 
    if contact_info:
        missing_contacts = []
        if not contact_info.get('email'):
            missing_contacts.append('email')
        if not contact_info.get('phone'):
            missing_contacts.append('phone number')
        if not contact_info.get('linkedin'):
            missing_contacts.append('LinkedIn URL')

        if len(missing_contacts) >= 2:
            contact_action_items = [f"Add your {item} to the header section" for item in missing_contacts]
            contact_action_items += [
                "Format the contact line as: email | phone | linkedin | github",
                "Make sure your LinkedIn URL is a custom short URL (linkedin.com/in/yourname)",
                "Add a GitHub link if you have public projects (github.com/yourname)",
            ]
            detected.append(IssueDetail(
                issue_title="Incomplete Contact Information",
                severity_level="High",
                ats_impact="High",
                explanation=(
                    f"Your resume is missing: {', '.join(missing_contacts)}. "
                    "Recruiters need reliable ways to reach you. Missing contact "
                    "details can cause your application to be skipped entirely."
                ),
                where_it_appears="Header / Contact section at the top of the resume",
                how_to_fix=(
                    "Add your full name, email, phone number, LinkedIn profile, "
                    "and optionally a GitHub or portfolio link at the top of your resume."
                ),
                action_items=contact_action_items,
                example_improvement=(
                    "Add at top:\n"
                    "John Doe\n"
                    "john.doe@email.com | +91-9876543210\n"
                    "linkedin.com/in/johndoe | github.com/johndoe"
                ),
            ))

    # 9. Formatting Score
    # FIX: previously only fired below 10/20 ("High" severity only).
    # That missed a "Good but improvable" band like 10-15/20.
    # Now adds a Moderate tier so scores like 12/20 still produce feedback.
    formatting_score = scores.get('formatting_score', 20)

    if formatting_score < 10:
        f_severity, f_title = "High", "Poor Resume Formatting"
    elif formatting_score < 16:
        f_severity, f_title = "Moderate", "Formatting Could Be Improved"
    else:
        f_severity, f_title = None, None

    if f_severity:
        is_high = f_severity == "High"
        detected.append(IssueDetail(
            issue_title=f_title,
            severity_level=f_severity,
            ats_impact="High" if is_high else "Moderate",
            explanation=(
                f"Your formatting score is {formatting_score}/20. "
                + (
                    "This indicates problems like missing section headers, inconsistent "
                    "structure, or a non-standard layout that ATS parsers struggle with."
                    if is_high else
                    "Your structure is mostly solid, but a few formatting tweaks would "
                    "improve ATS parsing and recruiter readability further."
                )
            ),
            where_it_appears="Overall document structure and formatting",
            how_to_fix=(
                "Use a clean, single-column layout with standard section headers "
                "(Experience, Education, Skills, Projects). Use consistent bullet "
                "points, standard fonts, and avoid tables, columns, or graphics."
            ),
            action_items=[
                "Use standard section headers: EXPERIENCE, EDUCATION, SKILLS, PROJECTS",
                "Use bullet points (•) consistently — don't mix with dashes or asterisks",
                "Remove tables, text boxes, headers/footers, and images — ATS cannot parse them",
                "Use a standard font (Calibri, Arial, Times New Roman) at 10–12pt",
                "Order sections: Contact → Summary → Experience → Projects → Education → Skills",
            ],
            example_improvement=(
                "Use this structure:\n"
                "NAME & CONTACT\n"
                "SUMMARY (2-3 lines)\n"
                "EXPERIENCE (reverse chronological)\n"
                "PROJECTS (2-3 key projects)\n"
                "EDUCATION\n"
                "SKILLS (categorized)"
            ),
        ))

    #10. Missing Summary/Objective
    if not summary:
        detected.append(IssueDetail(
            issue_title="Missing Professional Summary",
            severity_level="Low",
            ats_impact="Low",
            explanation=(
                "Your resume does not include a Professional Summary or Objective "
                "section at the top. While not required, a 2-3 line summary helps "
                "recruiters quickly understand your profile and target role."
            ),
            where_it_appears="Top of resume — below contact info",
            how_to_fix=(
                "Add a 2-3 sentence summary highlighting your experience level, "
                "key skills, and career focus. Tailor it to the job you're applying for."
            ),
            action_items=[
                "Add a 'PROFESSIONAL SUMMARY' or 'OBJECTIVE' section at the top of your resume",
                "Write 2–3 sentences: who you are, your key skills, and what role you seek",
                "Mention your years of experience or education level upfront",
                "Tailor this section for each job application — reference the specific role",
                "Keep it under 60 words — recruiters spend only 6 seconds on first scan",
            ],
            example_improvement=(
                "Add:\n"
                "PROFESSIONAL SUMMARY\n"
                "Full-stack developer with 2+ years of experience building scalable "
                "web applications using React, Node.js, and AWS. Passionate about "
                "clean architecture and performance optimization."
            ),
        ))

    # 11. NEW: Empty-state fallback.
    # If every check above passed cleanly, `detected` would previously be []
    # and the API would silently return empty issues_summary/detailed_feedback,
    # which looks like a bug to the user even though it's a genuinely good resume.
    # This makes that state explicit instead of blank.
    if not detected:
        ats_score = scores.get('ats_score') or scores.get('total_score')
        score_note = f" (ATS score: {ats_score}/100)" if ats_score is not None else ""
        detected.append(IssueDetail(
            issue_title="No Critical Issues Detected",
            severity_level="Low",
            ats_impact="Low",
            explanation=(
                f"Your resume passed all automated checks{score_note} — sections, "
                "skills evidence, formatting, action verbs, and quantified achievements "
                "all meet the baseline bar. This doesn't mean it's unimprovable, just "
                "that nothing rose to a flagged issue."
            ),
            where_it_appears="N/A — this is a summary status, not a specific location",
            how_to_fix=(
                "Consider tailoring keyword density to a specific job description for "
                "an extra edge, or have a peer/mentor review tone and clarity, since "
                "those aren't fully capturable by automated checks."
            ),
            action_items=[
                "Run this resume against a specific job description for keyword-match scoring",
                "Ask a peer or mentor for a manual readability/tone review",
                "Re-check this analysis after any major resume update",
            ],
            example_improvement=(
                "No structural fix needed right now — focus on tailoring this resume "
                "to specific job descriptions for incremental gains."
            ),
        ))

    print("Projects:", len(proj_entries))
    print("Experience:", len(exp_entries))
    print("Education:", len(edu_entries))
    print("Skills:", len(skills))
    print("Validated:", len(validated))
    print("Unvalidated:", len(unvalidated))
    print("Action Verbs:", len(action_verbs))
    print("Formatting Score:", formatting_score)
    print("Summary:", bool(summary))
    print("Issues Detected:", len(detected))
    return detected


def generate_issues_summary(detected_issues: List[IssueDetail]) -> List[str]:
    """Extract issue titles to formulate the issues_summary list."""
    return [issue.issue_title for issue in detected_issues]