
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


CAREERS = [
    {
        "title": "Software Developer",
        "description": "Build software, web applications and APIs; solve programming problems.",
        "skills": ["python", "data structures", "algorithms", "sql", "git", "problem solving"],
        "courses": ["Python programming", "Data Structures and Algorithms", "REST API development"],
        "projects": ["Task management web app", "Student portal API"],
        "certifications": ["Python programming certificate", "Git and GitHub fundamentals"],
    },
    {
        "title": "Data Analyst",
        "description": "Analyze data, write SQL queries, build dashboards and communicate business insights.",
        "skills": ["sql", "excel", "power bi", "statistics", "python", "data visualization"],
        "courses": ["SQL for analytics", "Statistics fundamentals", "Power BI dashboards"],
        "projects": ["Sales dashboard", "Student performance analysis"],
        "certifications": ["Power BI learning path", "SQL certificate"],
    },
    {
        "title": "Machine Learning Engineer",
        "description": "Prepare datasets, train machine learning models, evaluate algorithms and deploy predictions.",
        "skills": ["python", "machine learning", "statistics", "scikit-learn", "sql", "data preprocessing"],
        "courses": ["Machine learning fundamentals", "Model evaluation", "Feature engineering"],
        "projects": ["Student score prediction", "Recommendation system"],
        "certifications": ["Machine learning course certificate", "Cloud fundamentals"],
    },
    {
        "title": "Frontend Developer",
        "description": "Create responsive user interfaces using HTML, CSS, JavaScript and frontend frameworks.",
        "skills": ["html", "css", "javascript", "responsive design", "git", "ui design"],
        "courses": ["HTML and CSS", "JavaScript fundamentals", "Responsive web design"],
        "projects": ["Portfolio website", "Interactive image gallery"],
        "certifications": ["Web development certificate", "JavaScript fundamentals"],
    },
    {
        "title": "Cybersecurity Analyst",
        "description": "Monitor security events, investigate threats, understand networks and protect systems.",
        "skills": ["networking", "linux", "security fundamentals", "python", "risk analysis", "problem solving"],
        "courses": ["Networking fundamentals", "Linux basics", "Security fundamentals"],
        "projects": ["Security log analyzer", "Network traffic report"],
        "certifications": ["Cybersecurity fundamentals", "Networking fundamentals"],
    },
    {
        "title": "Cloud Engineer",
        "description": "Deploy applications, manage cloud infrastructure, automate delivery and monitor services.",
        "skills": ["linux", "networking", "cloud", "docker", "git", "python"],
        "courses": ["Linux and networking", "Cloud fundamentals", "Docker and CI/CD"],
        "projects": ["Deploy a Python API", "CI/CD pipeline demo"],
        "certifications": ["Cloud learning path", "Docker fundamentals"],
    },
    {
        "title": "Business Intelligence Analyst",
        "description": "Transform business data into reports, metrics and dashboards for decision making.",
        "skills": ["sql", "power bi", "data modeling", "excel", "communication", "data visualization"],
        "courses": ["SQL reporting", "Power BI", "Data modeling"],
        "projects": ["Business KPI dashboard", "Customer trends report"],
        "certifications": ["Power BI learning path", "SQL certificate"],
    },
]


# Normalize common names and equivalent skill terms.
SKILL_ALIASES = {
    "py": "python",
    "python programming": "python",
    "dsa": "data structures",
    "data structures and algorithms": "data structures",
    "problem-solving": "problem solving",
    "communication skills": "communication",
    "structured query language": "sql",
    "powerbi": "power bi",
    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "js": "javascript",
    "html5": "html",
    "css3": "css",
    "git and github": "git",
}


def normalize_skill(skill):
    value = str(skill).strip().lower()
    value = " ".join(value.split())
    return SKILL_ALIASES.get(value, value)


def recommend_careers(skills, interests="", goals="", top_k=5):
    # Normalize all student skills consistently.
    normal = {
        normalize_skill(skill)
        for skill in skills
        if str(skill).strip()
    }

    # Use the original profile text for ranking.
    profile_text = " ".join(
        [*sorted(normal), str(interests or ""), str(goals or "")]
    ).strip()

    if not profile_text:
        profile_text = "student exploring technology careers"

    career_documents = [
        career["title"] + " " +
        career["description"] + " " +
        " ".join(career["skills"])
        for career in CAREERS
    ]

    documents = [profile_text] + career_documents

    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(documents)

    text_scores = cosine_similarity(
        matrix[0:1], matrix[1:]
    ).flatten()

    results = []

    for career, text_score in sorted(
        zip(CAREERS, text_scores),
        key=lambda item: item[1],
        reverse=True
    )[:top_k]:

        required = {
            normalize_skill(skill)
            for skill in career["skills"]
        }

        matched = sorted(normal & required)
        missing = sorted(required - normal)

        # Combine text similarity with direct skill coverage.
        skill_coverage = (
            len(matched) / len(required)
            if required else 0.0
        )

        combined_score = (
            0.6 * float(text_score) +
            0.4 * skill_coverage
        ) * 100

        results.append({
            "title": career["title"],
            "match_score": round(combined_score, 1),
            "description": career["description"],
            "matched_skills": matched,
            "missing_skills": missing,
            "courses": career["courses"],
            "projects": career["projects"],
            "certifications": career["certifications"],
        })

    return results


def career_chat(question):
    q = question.lower()

    if any(x in q for x in ["data analyst", "data analysis", "power bi", "sql"]):
        return (
            "For Data Analytics, learn Excel and SQL, practise statistics, "
            "then build Power BI dashboards. Create two portfolio projects "
            "and explain the insights."
        )

    if any(x in q for x in ["frontend", "web developer", "html", "javascript"]):
        return (
            "For Frontend Development, learn HTML, CSS, JavaScript, "
            "responsive design, Git and accessibility. Build a portfolio, "
            "image gallery and API-based project."
        )

    if any(x in q for x in ["machine learning", "ml engineer", "ai engineer"]):
        return (
            "For Machine Learning, strengthen Python, statistics, data cleaning, "
            "model evaluation and scikit-learn. Build an end-to-end prediction project."
        )

    if any(x in q for x in ["cybersecurity", "security analyst"]):
        return (
            "For Cybersecurity, learn networking, Linux, security fundamentals "
            "and risk analysis. Practise in legal training labs and build a "
            "security log analysis project."
        )

    if any(x in q for x in ["cloud engineer", "cloud computing", "docker"]):
        return (
            "For Cloud Engineering, learn Linux, networking, Git, cloud basics "
            "and Docker. Deploy a Python API and practise a simple CI/CD pipeline."
        )

    if any(x in q for x in ["software", "programmer", "developer", "coding"]):
        return (
            "For Software Development, practise Python, data structures, algorithms, "
            "Git, SQL, testing and REST APIs. Build projects that solve a clear user problem."
        )

    if any(x in q for x in ["skill gap", "missing skills", "improve skills"]):
        return (
            "Enter your current skills in Student Profile, then open Recommendations. "
            "Use the missing-skills list to choose your next learning goal."
        )

    return (
        "I can help with Software Development, Data Analytics, Machine Learning, "
        "Frontend Development, Cybersecurity and Cloud Engineering. Ask about a role, "
        "skills, roadmap or project."
    )
