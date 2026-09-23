import json
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def utcnow():
    return datetime.now(timezone.utc)

class User(db.Model):
    """User account entity storing career profile."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, default='sanjay_learner')
    display_name = db.Column(db.String(100), default='Sanjay')
    email = db.Column(db.String(120), unique=True, nullable=True)
    target_career = db.Column(db.String(150), default='Full Stack Developer')
    current_level = db.Column(db.String(50), default='Beginner')
    study_hours_per_day = db.Column(db.Float, default=2.5)
    created_at = db.Column(db.DateTime, default=utcnow)

    # Relationships
    conversations = db.relationship('Conversation', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    roadmaps = db.relationship('Roadmap', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    user_skills = db.relationship('UserSkill', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    projects = db.relationship('Project', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    progress_entries = db.relationship('Progress', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    resume_analyses = db.relationship('ResumeAnalysis', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'display_name': self.display_name,
            'email': self.email,
            'target_career': self.target_career,
            'current_level': self.current_level,
            'study_hours_per_day': self.study_hours_per_day,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Conversation(db.Model):
    """Chat session with the AI Career Mentor."""
    __tablename__ = 'conversations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), default='Career Guidance Session')
    career_context = db.Column(db.String(150), default='General')
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    messages = db.relationship('Message', backref='conversation', lazy='dynamic', cascade='all, delete-orphan', order_by='Message.created_at')

    def to_dict(self, include_messages=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'career_context': self.career_context,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'message_count': self.messages.count()
        }
        if include_messages:
            data['messages'] = [m.to_dict() for m in self.messages.all()]
        return data


class Message(db.Model):
    """Individual chat bubble in a conversation."""
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'role': self.role,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Roadmap(db.Model):
    """Career roadmap generated for a user."""
    __tablename__ = 'roadmaps'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    career_goal = db.Column(db.String(150), nullable=False)
    current_level = db.Column(db.String(50), nullable=False)
    current_skills = db.Column(db.Text, default='')
    hours_per_day = db.Column(db.Float, default=2.0)
    target_duration = db.Column(db.String(50), default='6 months')
    overview = db.Column(db.Text, default='')
    prerequisites = db.Column(db.Text, default='')
    
    # JSON structured columns
    phases_json = db.Column(db.Text, default='[]')
    important_technologies = db.Column(db.Text, default='[]')
    projects_json = db.Column(db.Text, default='[]')
    certifications = db.Column(db.Text, default='[]')
    interview_prep = db.Column(db.Text, default='')
    portfolio_requirements = db.Column(db.Text, default='')
    job_prep = db.Column(db.Text, default='')
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        def parse_json(field, default):
            if not field:
                return default
            try:
                return json.loads(field)
            except Exception:
                return default

        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'career_goal': self.career_goal,
            'current_level': self.current_level,
            'current_skills': self.current_skills,
            'hours_per_day': self.hours_per_day,
            'target_duration': self.target_duration,
            'overview': self.overview,
            'prerequisites': self.prerequisites,
            'phases': parse_json(self.phases_json, []),
            'important_technologies': parse_json(self.important_technologies, []),
            'projects': parse_json(self.projects_json, []),
            'certifications': parse_json(self.certifications, []),
            'interview_prep': self.interview_prep,
            'portfolio_requirements': self.portfolio_requirements,
            'job_prep': self.job_prep,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Skill(db.Model):
    """Global catalogue of technological and professional skills."""
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(100), default='General')
    description = db.Column(db.Text, default='')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description
        }


class UserSkill(db.Model):
    """User-specific skill status and priority tracking."""
    __tablename__ = 'user_skills'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), default='Technical')
    status = db.Column(db.String(50), default='Missing')  # '✓' (Mastered), 'In Progress', 'Missing'
    priority = db.Column(db.String(20), default='High')    # 'High', 'Medium', 'Low'
    learning_order = db.Column(db.Integer, default=1)
    proficiency = db.Column(db.Integer, default=0)        # 0 to 100%
    target_career = db.Column(db.String(150), default='General')
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'skill_name': self.skill_name,
            'category': self.category,
            'status': self.status,
            'priority': self.priority,
            'learning_order': self.learning_order,
            'proficiency': self.proficiency,
            'target_career': self.target_career,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Project(db.Model):
    """Generated practice and portfolio projects."""
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    career_target = db.Column(db.String(150), default='Full Stack Developer')
    difficulty = db.Column(db.String(50), default='Intermediate')
    technology = db.Column(db.String(200), default='')
    problem_statement = db.Column(db.Text, default='')
    features_json = db.Column(db.Text, default='[]')
    technologies_json = db.Column(db.Text, default='[]')
    database_design = db.Column(db.Text, default='')
    folder_structure = db.Column(db.Text, default='')
    development_steps_json = db.Column(db.Text, default='[]')
    expected_output = db.Column(db.Text, default='')
    resume_description = db.Column(db.Text, default='')
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        def parse_json(field, default):
            if not field:
                return default
            try:
                return json.loads(field)
            except Exception:
                return default

        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'career_target': self.career_target,
            'difficulty': self.difficulty,
            'technology': self.technology,
            'problem_statement': self.problem_statement,
            'features': parse_json(self.features_json, []),
            'technologies': parse_json(self.technologies_json, []),
            'database_design': self.database_design,
            'folder_structure': self.folder_structure,
            'development_steps': parse_json(self.development_steps_json, []),
            'expected_output': self.expected_output,
            'resume_description': self.resume_description,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Progress(db.Model):
    """Daily study tracking, streaks, and milestone logs."""
    __tablename__ = 'progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_str = db.Column(db.String(20), default=lambda: datetime.now(timezone.utc).strftime('%Y-%m-%d'))
    study_hours = db.Column(db.Float, default=2.0)
    notes = db.Column(db.Text, default='')
    skills_completed_count = db.Column(db.Integer, default=0)
    projects_completed_count = db.Column(db.Integer, default=0)
    streak_days = db.Column(db.Integer, default=5)
    overall_progress_pct = db.Column(db.Integer, default=65)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date_str,
            'study_hours': self.study_hours,
            'notes': self.notes,
            'skills_completed_count': self.skills_completed_count,
            'projects_completed_count': self.projects_completed_count,
            'streak_days': self.streak_days,
            'overall_progress_pct': self.overall_progress_pct,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ResumeAnalysis(db.Model):
    """Resume ATS and career alignment analysis."""
    __tablename__ = 'resume_analyses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(200), default='Uploaded Resume')
    target_career = db.Column(db.String(150), default='Software Engineer')
    ats_score = db.Column(db.Integer, default=78)
    career_match_pct = db.Column(db.Integer, default=80)
    extracted_skills_json = db.Column(db.Text, default='[]')
    missing_keywords_json = db.Column(db.Text, default='[]')
    projects_critique = db.Column(db.Text, default='')
    education_critique = db.Column(db.Text, default='')
    experience_critique = db.Column(db.Text, default='')
    formatting_suggestions_json = db.Column(db.Text, default='[]')
    ats_improvements_json = db.Column(db.Text, default='[]')
    summary = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        def parse_json(field, default):
            if not field:
                return default
            try:
                return json.loads(field)
            except Exception:
                return default

        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'target_career': self.target_career,
            'ats_score': self.ats_score,
            'career_match_pct': self.career_match_pct,
            'extracted_skills': parse_json(self.extracted_skills_json, []),
            'missing_keywords': parse_json(self.missing_keywords_json, []),
            'projects_critique': self.projects_critique,
            'education_critique': self.education_critique,
            'experience_critique': self.experience_critique,
            'formatting_suggestions': parse_json(self.formatting_suggestions_json, []),
            'ats_improvements': parse_json(self.ats_improvements_json, []),
            'summary': self.summary,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
