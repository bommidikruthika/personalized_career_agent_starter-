
import os
import html
from urllib.parse import quote_plus

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Career Compass",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CUSTOM STYLING
# =========================================================

st.markdown(
    """
    <style>
    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: #f4f7fc;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg, #102c4b 0%, #071a31 100%
        );
    }

    [data-testid="stSidebar"] * {
        color: #edf5ff;
    }

    .brand {
        font-size: 25px;
        font-weight: 800;
        color: white;
        padding: 10px 0 4px;
    }

    .brand-subtitle {
        color: #a9c1df;
        font-size: 12px;
        margin-bottom: 25px;
    }

    .welcome-banner {
        background: linear-gradient(
            110deg, #e3f3ff, #f1fbff, #d9f1ff
        );
        border: 1px solid #d8ebf8;
        border-radius: 17px;
        padding: 24px 27px;
        margin-bottom: 19px;
    }

    .welcome-title {
        color: #17344f;
        font-size: 25px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .welcome-description {
        color: #5c7188;
        font-size: 13px;
    }

    .metric-card {
        border-radius: 16px;
        padding: 18px;
        min-height: 135px;
        border: 1px solid #e5edf5;
        margin-bottom: 10px;
    }

    .metric-blue { background: #eaf3ff; }
    .metric-green { background: #e9f7ef; }
    .metric-purple { background: #f0edff; }
    .metric-yellow { background: #fff6df; }

    .metric-icon {
        font-size: 22px;
        margin-bottom: 7px;
    }

    .metric-label {
        font-size: 13px;
        font-weight: 600;
        color: #52657c;
        line-height: 1.5;
    }

    .metric-number {
        font-size: 29px;
        font-weight: 800;
        color: #172f49;
        margin-top: 5px;
    }

    .metric-caption {
        color: #718096;
        font-size: 11px;
        margin-top: 5px;
    }

    .section-heading {
        color: #183650;
        font-size: 19px;
        font-weight: 800;
        margin-bottom: 12px;
    }

    .roadmap-item {
        border-left: 3px solid #dbe7f5;
        padding: 3px 0 18px 18px;
        margin-left: 10px;
    }

    .roadmap-title {
        color: #234568;
        font-size: 14px;
        font-weight: 750;
    }

    div.stButton > button {
        border-radius: 9px;
        font-weight: 600;
    }

    div[data-testid="stMetric"] {
        background: white;
        padding: 13px;
        border-radius: 12px;
        border: 1px solid #e6edf5;
    }

    hr {
        border-color: #e6edf5;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================

DEFAULTS = {
    "page": "Home",
    "profile_id": None,
    "saved_profile": None,
    "recommendations": [],
    "chat_history": [],
    "learning_progress": {},
    "selected_career": "Software Developer",
    "pending_question": None,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# NAVIGATION
# =========================================================

PAGE_MAPPING = {
    "🏠 Home": "Home",
    "👤 Profile": "Profile",
    "🎯 Recommendations": "Recommendations",
    "🗺️ Learning Roadmap": "Learning Roadmap",
    "📊 Skill Gap Analysis": "Skill Gap Analysis",
    "💼 Job Opportunities": "Job Opportunities",
    "🤖 Chat Assistant": "Chat Assistant",
}

REVERSE_MAPPING = {
    value: key for key, value in PAGE_MAPPING.items()
}


def navigate(page_name):
    st.session_state.page = page_name


def navigation_changed():
    """Handle sidebar selection changes."""
    selected = st.session_state.get(
        "navigation_radio", "🏠 Home"
    )
    st.session_state.page = PAGE_MAPPING.get(selected, "Home")


if "navigation_radio" not in st.session_state:
    st.session_state.navigation_radio = REVERSE_MAPPING.get(
        st.session_state.page, "🏠 Home"
    )


# =========================================================
# API HELPERS
# =========================================================

def api_get(path, params=None):
    try:
        response = requests.get(
            f"{API_BASE_URL}{path}",
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException as error:
        st.error(f"Backend GET request failed: {error}")
        return None

    except ValueError:
        st.error("The backend returned invalid JSON.")
        return None


def api_post(path, payload):
    try:
        response = requests.post(
            f"{API_BASE_URL}{path}",
            json=payload,
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException as error:
        st.error(f"Backend POST request failed: {error}")
        return None

    except ValueError:
        st.error("The backend returned invalid JSON.")
        return None


def api_put(path, payload):
    try:
        response = requests.put(
            f"{API_BASE_URL}{path}",
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException as error:
        st.error(f"Could not save the update: {error}")
        return None

    except ValueError:
        st.error("The backend returned invalid JSON.")
        return None


# =========================================================
# PROFILE HELPERS
# =========================================================

def get_profile_id():
    profile = st.session_state.saved_profile or {}
    return (
        st.session_state.profile_id
        or profile.get("id")
    )


def get_student_name():
    profile = st.session_state.saved_profile or {}
    return profile.get("name", "Student")


def parse_list(value):
    """Convert a comma-separated string or list into a list."""
    if isinstance(value, list):
        return value

    if isinstance(value, str):
        return [
            item.strip()
            for item in value.replace(";", ",").split(",")
            if item.strip()
        ]

    return []


def get_student_skills():
    profile = st.session_state.saved_profile or {}
    return parse_list(profile.get("skills", []))


def load_profile(profile_id):
    profile = api_get(f"/profiles/{profile_id}")

    if isinstance(profile, dict) and profile.get("id"):
        st.session_state.saved_profile = profile
        st.session_state.profile_id = profile["id"]
        return True

    return False


# =========================================================
# CAREER HELPERS
# =========================================================

def normalize_list(data):
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in (
            "recommendations",
            "careers",
            "results",
            "items",
            "data",
        ):
            value = data.get(key)

            if isinstance(value, list):
                return value

    return []


def get_career_title(career):
    if isinstance(career, str):
        return career

    if isinstance(career, dict):
        return (
            career.get("title")
            or career.get("career")
            or career.get("career_title")
            or career.get("name")
            or "Career Option"
        )

    return "Career Option"


def get_career_description(career):
    if not isinstance(career, dict):
        return (
            "Explore this career path and develop the required skills."
        )

    return (
        career.get("description")
        or career.get("overview")
        or career.get("summary")
        or "Explore this career path and develop the required skills."
    )


def get_career_skills(career):
    if not isinstance(career, dict):
        return []

    skills = (
        career.get("required_skills")
        or career.get("skills")
        or career.get("matched_skills")
        or []
    )

    return parse_list(skills)


def get_match_score(career):
    if not isinstance(career, dict):
        return None

    for field in (
        "match_percentage",
        "match_score",
        "score",
        "similarity",
    ):
        value = career.get(field)

        if value is None:
            continue

        try:
            score = float(value)

            if 0 <= score <= 1:
                score *= 100

            return max(0, min(100, round(score)))

        except (ValueError, TypeError):
            continue

    return None


# =========================================================
# DEFAULT CAREER OPTIONS
# =========================================================

DEFAULT_CAREERS = [
    {
        "title": "Software Developer",
        "description": (
            "Build and maintain software applications "
            "and solve real-world problems."
        ),
        "required_skills": [
            "Python",
            "Problem Solving",
            "Data Structures",
            "Algorithms",
            "Git",
        ],
    },
    {
        "title": "Data Analyst",
        "description": (
            "Analyze data, discover insights, and support "
            "data-driven business decisions."
        ),
        "required_skills": [
            "SQL",
            "Data Analysis",
            "Power BI",
            "Python",
        ],
    },
    {
        "title": "Machine Learning Engineer",
        "description": (
            "Develop and evaluate machine learning models "
            "to solve practical problems."
        ),
        "required_skills": [
            "Python",
            "Machine Learning",
            "Mathematics",
            "Data Analysis",
        ],
    },
    {
        "title": "Cybersecurity Analyst",
        "description": (
            "Help protect computer systems, networks, "
            "and information from security threats."
        ),
        "required_skills": [
            "Networking",
            "Security",
            "Linux",
            "Problem Solving",
        ],
    },
    {
        "title": "Cloud Engineer",
        "description": (
            "Deploy and maintain applications and "
            "infrastructure using cloud platforms."
        ),
        "required_skills": [
            "Linux",
            "Cloud Computing",
            "Networking",
            "Python",
        ],
    },
]


# =========================================================
# CAREER RECOMMENDATIONS API
# =========================================================

def load_recommendations():
    profile_id = get_profile_id()

    if not profile_id:
        st.session_state.recommendations = []
        return []

    profile = st.session_state.saved_profile

    if not isinstance(profile, dict) or not profile:
        if not load_profile(profile_id):
            st.warning(
                "Your profile could not be loaded. "
                "Please save your profile again."
            )
            return []

        profile = st.session_state.saved_profile

    payload = {
        "name": str(profile.get("name", "Student")),
        "education": str(profile.get("education", "")),
        "skills": parse_list(profile.get("skills", [])),
        "interests": str(profile.get("interests", "")),
        "goals": str(profile.get("goals", "")),
    }

    data = api_post("/recommendations", payload)

    if data is None:
        return st.session_state.recommendations

    recommendations = normalize_list(data)
    st.session_state.recommendations = recommendations

    return recommendations


# =========================================================
# LEARNING ROADMAP DATA
# =========================================================

ROADMAP_PHASES = [
    {
        "title": "Build Strong Fundamentals",
        "duration": "Weeks 1–4",
        "details": [
            "Python programming",
            "Data structures and algorithms",
        ],
        "items": [
            "Python programming",
            "Data structures and algorithms",
        ],
    },
    {
        "title": "Learn Core Technologies",
        "duration": "Weeks 5–8",
        "details": [
            "Web development and REST APIs",
            "Database fundamentals using SQL",
        ],
        "items": [
            "Web development and REST APIs",
            "Database fundamentals using SQL",
        ],
    },
    {
        "title": "Gain Practical Experience",
        "duration": "Weeks 9–10",
        "details": [
            "Build personal projects",
            "Participate in hackathons or internships",
        ],
        "items": [
            "Build a personal project",
            "Participate in a hackathon",
        ],
    },
    {
        "title": "Prepare for Your Career",
        "duration": "Weeks 11–12",
        "details": [
            "Git and GitHub fundamentals",
            "Resume and interview preparation",
        ],
        "items": [
            "Git and GitHub fundamentals",
            "Resume and interview preparation",
        ],
    },
]


# =========================================================
# LEARNING PROGRESS
# =========================================================

def progress_key(career_title, item_name):
    return f"{career_title}::{item_name}"


def load_learning_progress():
    profile_id = get_profile_id()

    if not profile_id:
        return

    data = api_get(
        f"/profiles/{profile_id}/learning-progress"
    )

    if data is None:
        return

    if isinstance(data, dict) and "progress" in data:
        records = data["progress"]
    else:
        records = normalize_list(data)

    if isinstance(records, dict):
        records = records.get("items", [])

    if not isinstance(records, list):
        return

    for item in records:
        if not isinstance(item, dict):
            continue

        key = progress_key(
            item.get("career_title", ""),
            item.get("item_name", ""),
        )

        st.session_state.learning_progress[key] = bool(
            item.get("completed", False)
        )


def save_progress(career_title, item_name, item_type, completed):
    profile_id = get_profile_id()

    key = progress_key(career_title, item_name)
    st.session_state.learning_progress[key] = completed

    if not profile_id:
        return

    api_put(
        f"/profiles/{profile_id}/learning-progress",
        {
            "career_title": career_title,
            "item_name": item_name,
            "item_type": item_type,
            "completed": completed,
        },
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown(
        """
        <div class="brand">🧭 Career Compass</div>
        <div class="brand-subtitle">
            Discover your path. Build your future.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.radio(
        "Navigation",
        options=list(PAGE_MAPPING.keys()),
        key="navigation_radio",
        on_change=navigation_changed,
        label_visibility="collapsed",
    )

    st.divider()

    if st.session_state.saved_profile:
        st.caption("CURRENT PROFILE")
        st.markdown(
            f"**👤 {html.escape(str(get_student_name()))}**"
        )
        st.caption(
            st.session_state.saved_profile.get(
                "education", "Student"
            )
        )
    else:
        st.info(
            "Create your student profile to get personalized results."
        )

    st.divider()
    st.caption("Career Compass")
    st.caption("Your journey to a brighter future ✨")


# =========================================================
# HOME DASHBOARD
# =========================================================

if st.session_state.page == "Home":

    name = html.escape(str(get_student_name()))
    profile_id = get_profile_id()

    st.markdown(
        f"""
        <div class="welcome-banner">
            <div class="welcome-title">👋 Hello, {name}!</div>
            <div class="welcome-description">
                Explore career paths, improve your skills,
                and plan your professional future.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    recommendations = st.session_state.recommendations

    if profile_id and not recommendations:
        recommendations = load_recommendations()

    skills = get_student_skills()

    if recommendations:
        required = get_career_skills(recommendations[0])
        current = {skill.lower() for skill in skills}
        skill_gap_count = sum(
            skill.lower() not in current for skill in required
        )
    else:
        skill_gap_count = 0

    career_count = len(recommendations)
    learning_count = sum(
        len(phase["items"]) for phase in ROADMAP_PHASES
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card metric-blue">
                <div class="metric-icon">💼</div>
                <div class="metric-label">Recommended Career Paths</div>
                <div class="metric-number">{career_count}</div>
                <div class="metric-caption">Career matches from your profile</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Explore Careers →",
            key="dashboard_careers",
            use_container_width=True,
        ):
            navigate("Recommendations")
            st.rerun()

    with col2:
        st.markdown(
            f"""
            <div class="metric-card metric-green">
                <div class="metric-icon">👤</div>
                <div class="metric-label">Recommended Job Roles</div>
                <div class="metric-number">{career_count}</div>
                <div class="metric-caption">Career paths to explore</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Explore Opportunities →",
            key="dashboard_job_roles",
            use_container_width=True,
        ):
            navigate("Job Opportunities")
            st.rerun()

    with col3:
        st.markdown(
            f"""
            <div class="metric-card metric-purple">
                <div class="metric-icon">📚</div>
                <div class="metric-label">Learning Activities</div>
                <div class="metric-number">{learning_count}</div>
                <div class="metric-caption">Planned learning activities</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "View Learning Plan →",
            key="dashboard_learning",
            use_container_width=True,
        ):
            navigate("Learning Roadmap")
            st.rerun()

    with col4:
        st.markdown(
            f"""
            <div class="metric-card metric-yellow">
                <div class="metric-icon">🎯</div>
                <div class="metric-label">Skills to Improve</div>
                <div class="metric-number">{skill_gap_count}</div>
                <div class="metric-caption">For your top career match</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Improve Skills →",
            key="dashboard_skill_gaps",
            use_container_width=True,
        ):
            navigate("Skill Gap Analysis")
            st.rerun()

    st.write("")

    left_column, right_column = st.columns([1.15, 0.85])

    with left_column:
        st.markdown(
            '<div class="section-heading">⭐ Career Recommendations</div>',
            unsafe_allow_html=True,
        )

        if not profile_id:
            st.info(
                "Save your student profile to generate personalized "
                "recommendations."
            )

            if st.button(
                "Create My Profile",
                key="home_create_profile",
                use_container_width=True,
            ):
                navigate("Profile")
                st.rerun()

        else:
            dashboard_careers = (
                recommendations if recommendations else DEFAULT_CAREERS
            )

            if not recommendations:
                st.info(
                    "Showing example career paths. "
                    "Personalized recommendations will appear when available."
                )

            for index, career in enumerate(dashboard_careers[:5]):
                title = get_career_title(career)

                with st.container(border=True):
                    st.subheader(title)
                    st.write(get_career_description(career))

                    score = get_match_score(career)
                    if score is not None:
                        st.caption(f"Match score: {score}%")

                    career_skills = get_career_skills(career)
                    if career_skills:
                        st.caption(
                            "Relevant skills: "
                            + ", ".join(career_skills[:5])
                        )

                    if st.button(
                        f"View Details: {title}",
                        key=f"home_career_{index}",
                        use_container_width=True,
                    ):
                        st.session_state.selected_career = title
                        navigate("Recommendations")
                        st.rerun()

        if st.button(
            "View All Recommendations →",
            key="home_all_recommendations",
            use_container_width=True,
        ):
            navigate("Recommendations")
            st.rerun()

    with right_column:
        st.markdown(
            '<div class="section-heading">📘 Your Learning Roadmap</div>',
            unsafe_allow_html=True,
        )

        for index, phase in enumerate(ROADMAP_PHASES):
            st.markdown(
                f"""
                <div class="roadmap-item">
                    <div class="roadmap-title">
                        Phase {index + 1}: {phase["title"]}
                    </div>
                    <div class="small-muted">
                        {phase["duration"]}
                    </div>
                    <div class="small-muted">
                        {" • ".join(phase["details"])}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if st.button(
            "Open Learning Roadmap →",
            key="home_open_roadmap",
            use_container_width=True,
        ):
            navigate("Learning Roadmap")
            st.rerun()

        st.markdown("### 🤖 Career Assistant")
        st.write(
            "Ask questions about technical skills, projects, "
            "courses, and career preparation."
        )

        if st.button(
            "Chat with Assistant →",
            key="home_chat_assistant",
            use_container_width=True,
        ):
            navigate("Chat Assistant")
            st.rerun()


# =========================================================
# STUDENT PROFILE
# =========================================================

elif st.session_state.page == "Profile":

    st.title("👤 Student Profile")
    st.write(
        "Enter your education, skills, interests, and goals "
        "to personalize career recommendations."
    )

    existing = st.session_state.saved_profile or {}
    existing_skills = parse_list(existing.get("skills", []))

    with st.form("profile_form"):
        name = st.text_input(
            "Full Name",
            value=existing.get("name", ""),
        )

        education = st.text_input(
            "Education",
            value=existing.get(
                "education", "B.Tech Computer Science"
            ),
        )

        skills_text = st.text_area(
            "Skills",
            value=", ".join(existing_skills),
            placeholder="Python, SQL, Problem Solving, Communication",
        )

        interests = st.text_area(
            "Interests",
            value=existing.get("interests", ""),
            placeholder="Technology, software development, data analysis",
        )

        goals = st.text_area(
            "Career Goals",
            value=existing.get("goals", ""),
            placeholder="Become a software engineer",
        )

        submitted = st.form_submit_button(
            "Save Profile",
            use_container_width=True,
            type="primary",
        )

    if submitted:
        if not name.strip() or not education.strip():
            st.error("Please enter your name and education.")
        else:
            payload = {
                "name": name.strip(),
                "education": education.strip(),
                "skills": parse_list(skills_text),
                "interests": interests.strip(),
                "goals": goals.strip(),
            }

            saved = api_post("/profiles", payload)

            if isinstance(saved, dict) and saved.get("id"):
                st.session_state.saved_profile = saved
                st.session_state.profile_id = saved["id"]
                st.session_state.recommendations = []
                st.session_state.learning_progress = {}

                load_learning_progress()

                st.success("Your profile has been saved successfully!")
                st.rerun()

            elif isinstance(saved, dict):
                st.error(
                    "The backend response did not contain a profile ID. "
                    "Check the POST /profiles response."
                )

    if existing:
        st.divider()
        st.subheader("Saved Profile")

        st.write("**Name:**", existing.get("name", ""))
        st.write("**Education:**", existing.get("education", ""))
        st.write("**Interests:**", existing.get("interests", ""))
        st.write("**Career Goals:**", existing.get("goals", ""))
        st.write("**Skills:**", ", ".join(get_student_skills()))


# =========================================================
# CAREER RECOMMENDATIONS
# =========================================================

elif st.session_state.page == "Recommendations":

    st.title("🎯 Career Recommendations")
    st.write(
        "Explore career paths that align with your profile, "
        "skills, interests, and goals."
    )

    profile_id = get_profile_id()

    if not profile_id:
        st.warning("Please create and save your student profile first.")

        if st.button("Go to Profile"):
            navigate("Profile")
            st.rerun()

    else:
        col1, col2 = st.columns([3, 1])

        with col1:
            st.caption(f"Recommendations for {get_student_name()}")

        with col2:
            if st.button(
                "Refresh Recommendations",
                use_container_width=True,
            ):
                st.session_state.recommendations = []
                st.rerun()

        recommendations = st.session_state.recommendations

        if not recommendations:
            recommendations = load_recommendations()

        if not recommendations:
            st.info(
                "No recommendations were returned by the backend. "
                "Check the response from POST /recommendations."
            )

        for index, career in enumerate(recommendations):
            title = get_career_title(career)

            with st.container(border=True):
                st.subheader(title)
                st.write(get_career_description(career))

                score = get_match_score(career)
                if score is not None:
                    st.progress(score / 100)
                    st.caption(f"Match score: {score}%")

                career_skills = get_career_skills(career)
                if career_skills:
                    st.write("**Relevant skills**")
                    st.write(", ".join(career_skills))

                if isinstance(career, dict):
                    matched = parse_list(
                        career.get("matched_skills", [])
                    )
                    missing = parse_list(
                        career.get("missing_skills", [])
                    )

                    if matched:
                        st.success(
                            "Matched skills: " + ", ".join(matched)
                        )

                    if missing:
                        st.warning(
                            "Skills to develop: " + ", ".join(missing)
                        )

                    for field in (
                        "courses",
                        "projects",
                        "certifications",
                    ):
                        items = career.get(field, [])

                        if isinstance(items, str):
                            items = [items]

                        if items:
                            with st.expander(
                                f"Suggested {field.title()}"
                            ):
                                for item in items:
                                    st.write(f"• {item}")

                if st.button(
                    f"View Learning Roadmap for {title}",
                    key=f"recommend_roadmap_{index}",
                    use_container_width=True,
                ):
                    st.session_state.selected_career = title
                    navigate("Learning Roadmap")
                    st.rerun()


# =========================================================
# LEARNING ROADMAP
# =========================================================

elif st.session_state.page == "Learning Roadmap":

    st.title("🗺️ Learning Roadmap")
    st.write(
        "Follow this 12-week roadmap to build technical skills "
        "and prepare for your target career."
    )

    profile_id = get_profile_id()

    if not profile_id:
        st.warning(
            "Save your profile first if you want to store "
            "learning progress in the backend."
        )
    elif not st.session_state.learning_progress:
        load_learning_progress()

    career_options = [
        "Software Developer",
        "Data Analyst",
        "Machine Learning Engineer",
        "Cybersecurity Analyst",
        "Cloud Engineer",
    ]

    selected_career = st.session_state.selected_career

    if selected_career not in career_options:
        career_options.insert(0, selected_career)

    selected_career = st.selectbox(
        "Choose your target career",
        career_options,
        index=career_options.index(selected_career),
        key="roadmap_career_selector",
    )

    st.session_state.selected_career = selected_career

    all_items = [
        item
        for phase in ROADMAP_PHASES
        for item in phase["items"]
    ]

    completed_count = sum(
        st.session_state.learning_progress.get(
            progress_key(selected_career, item),
            False,
        )
        for item in all_items
    )

    total_count = len(all_items)
    percentage = (
        round(completed_count / total_count * 100)
        if total_count
        else 0
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Activities", total_count)
    col2.metric("Completed", completed_count)
    col3.metric("Progress", f"{percentage}%")

    st.progress(percentage / 100)

    for phase_index, phase in enumerate(ROADMAP_PHASES):
        with st.container(border=True):
            st.subheader(
                f"Phase {phase_index + 1}: {phase['title']}"
            )
            st.caption(phase["duration"])

            for item_index, item in enumerate(phase["items"]):
                key = progress_key(selected_career, item)
                current_value = st.session_state.learning_progress.get(
                    key, False
                )

                checkbox_key = (
                    f"roadmap_{phase_index}_{item_index}_"
                    f"{quote_plus(selected_career)}"
                )

                checked = st.checkbox(
                    item,
                    value=current_value,
                    key=checkbox_key,
                )

                if checked != current_value:
                    save_progress(
                        selected_career,
                        item,
                        "skill",
                        checked,
                    )
                    st.rerun()

            st.markdown("**Learning topics**")

            for detail in phase["details"]:
                st.write(f"• {detail}")

    if percentage == 100:
        st.success(
            "Congratulations! You have completed all roadmap activities."
        )


# =========================================================
# SKILL GAP ANALYSIS
# =========================================================

elif st.session_state.page == "Skill Gap Analysis":

    st.title("📊 Skill Gap Analysis")
    st.write(
        "Compare your current skills with the skills suggested "
        "for your selected career."
    )

    profile_id = get_profile_id()

    if not profile_id:
        st.warning("Create your student profile to analyze skill gaps.")

        if st.button("Create Profile"):
            navigate("Profile")
            st.rerun()

    else:
        recommendations = st.session_state.recommendations

        if not recommendations:
            recommendations = load_recommendations()

        available_careers = [
            get_career_title(item)
            for item in recommendations
        ]

        if not available_careers:
            available_careers = [
                item["title"] for item in DEFAULT_CAREERS
            ]

        selected = st.selectbox(
            "Select a career",
            available_careers,
            key="skill_gap_career",
        )

        selected_data = next(
            (
                item for item in recommendations
                if get_career_title(item) == selected
            ),
            None,
        )

        if selected_data is None:
            selected_data = next(
                (
                    item for item in DEFAULT_CAREERS
                    if item["title"] == selected
                ),
                {},
            )

        current_skills = get_student_skills()
        required_skills = get_career_skills(selected_data)

        current_normalized = {
            skill.strip().lower()
            for skill in current_skills
        }

        matched_skills = [
            skill for skill in required_skills
            if skill.strip().lower() in current_normalized
        ]

        missing_skills = [
            skill for skill in required_skills
            if skill.strip().lower() not in current_normalized
        ]

        coverage = (
            round(
                len(matched_skills) / len(required_skills) * 100
            )
            if required_skills
            else 0
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("Required Skills", len(required_skills))
        col2.metric("Skills Matched", len(matched_skills))
        col3.metric("Skill Coverage", f"{coverage}%")

        st.progress(coverage / 100)

        st.subheader("✅ Skills You Have")

        if matched_skills:
            for skill in matched_skills:
                st.success(f"✓ {skill}")
        else:
            st.info("No matching skills identified yet.")

        st.subheader("🎯 Skills to Improve")

        if missing_skills:
            for skill in missing_skills:
                st.warning(f"○ {skill}")
        else:
            st.success("You match all listed required skills!")

        st.subheader("Recommended Next Steps")

        for skill in missing_skills:
            st.write(
                f"• Learn **{skill}** through tutorials, "
                "practice exercises, and a small project."
            )


# =========================================================
# JOB OPPORTUNITIES
# =========================================================

elif st.session_state.page == "Job Opportunities":

    st.title("💼 Job Opportunities")
    st.write(
        "Explore internships, entry-level roles, and fresher "
        "opportunities related to your career goal."
    )

    profile = st.session_state.saved_profile or {}

    default_role = (
        profile.get("goals", "").strip()
        or st.session_state.selected_career
        or "Software Developer"
    )

    search_role = st.text_input(
        "Job title or keyword",
        value=default_role,
        placeholder="Python Developer, Data Analyst, Intern",
        key="job_search_role",
    )

    location = st.text_input(
        "Preferred location",
        value="India",
        placeholder="Hyderabad, Bengaluru, Remote",
        key="job_search_location",
    )

    encoded_role = quote_plus(search_role.strip())
    encoded_location = quote_plus(location.strip())

    job_sites = [
        (
            "LinkedIn Jobs",
            "https://www.linkedin.com/jobs/search/?keywords="
            + encoded_role
            + "&location="
            + encoded_location,
        ),
        (
            "Naukri",
            "https://www.naukri.com/"
            + quote_plus(
                search_role.strip().replace(" ", "-")
            )
            + "-jobs",
        ),
        (
            "Indeed",
            "https://in.indeed.com/jobs?q="
            + encoded_role
            + "&l="
            + encoded_location,
        ),
        (
            "Internshala",
            "https://internshala.com/internships/"
            + quote_plus(
                search_role.strip().replace(" ", "-")
            )
            + "-internship/",
        ),
    ]

    st.subheader("Search Job Platforms")

    for site_name, url in job_sites:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.subheader(site_name)
                st.caption(
                    f"Search for {search_role or 'entry-level jobs'}"
                )

            with col2:
                st.link_button(
                    "Find Jobs ↗",
                    url,
                    use_container_width=True,
                )

    st.info(
        "These links open external job search websites. "
        "Check each listing for its eligibility and application details."
    )


# =========================================================
# CHAT ASSISTANT
# =========================================================

elif st.session_state.page == "Chat Assistant":

    st.title("🤖 Career Guidance Assistant")
    st.write(
        "Ask questions about career paths, technical skills, "
        "learning resources, projects, and interview preparation."
    )

    with st.container(border=True):
        st.markdown("### 👋 Welcome to Career Compass")

        st.write(
            "I can help you plan your learning journey and "
            "understand the skills needed for your target career."
        )

        st.markdown("**Try one of these questions:**")

        example_questions = [
            "How can I become a Python developer?",
            "What skills should I learn for a software engineering job?",
            "Suggest beginner-friendly projects for my resume.",
        ]

        example_cols = st.columns(3)

        for index, question_text in enumerate(example_questions):
            with example_cols[index]:
                if st.button(
                    question_text,
                    key=f"chat_example_{index}",
                    use_container_width=True,
                ):
                    st.session_state.pending_question = question_text
                    st.rerun()

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask your career question...")

    if st.session_state.pending_question:
        question = st.session_state.pending_question
        st.session_state.pending_question = None

    if question:
        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": question,
            }
        )

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Preparing your career guidance..."):
                answer_data = api_post(
                    "/chat",
                    {"question": question},
                )

                if isinstance(answer_data, dict):
                    answer = (
                        answer_data.get("answer")
                        or answer_data.get("response")
                        or answer_data.get("message")
                        or str(answer_data)
                    )

                elif answer_data is not None:
                    answer = str(answer_data)

                else:
                    answer = (
                        "I couldn't get a response from the career "
                        "assistant. Please check the backend and "
                        "the /chat endpoint."
                    )

                st.markdown(answer)

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

    if st.session_state.chat_history:
        if st.button(
            "Clear Chat History",
            key="clear_chat_history",
        ):
            st.session_state.chat_history = []
            st.rerun()
