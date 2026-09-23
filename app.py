import os
import logging
from flask import Flask, jsonify
from config import Config
from models import db, User, Chat, Message, Progress, UserSkill
from routes import auth_bp, chat_bp, main_bp, career_bp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def create_app():
    """Application factory for SkillMap AI."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure required directories exist
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)
    os.makedirs(os.path.join(Config.BASE_DIR, 'database'), exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Register modular Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(career_bp)

    # Global Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Resource not found', 'status': 404}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error occurred', 'status': 500}), 500

    return app


app = create_app()


def get_or_create_default_user():
    """Retrieve or initialize default learner profile (SANJAY)."""
    user = User.query.filter_by(username='sanjay_learner').first()
    if not user:
        user = User(
            username='sanjay_learner',
            display_name='SANJAY',
            email='sanjay@skillmap.ai',
            target_career='Full Stack Developer',
            current_level='Beginner',
            study_hours_per_day=2.5
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        # Seed initial conversation
        chat = Chat(
            user_id=user.id,
            title='Welcome to SkillMap AI',
            career_context='Full Stack Developer'
        )
        db.session.add(chat)
        db.session.commit()

        welcome_msg = Message(
            chat_id=chat.id,
            role='assistant',
            content="Welcome to **SkillMap AI**! 🚀 I'm your Personal Career Mentor, engineered to help you analyze skill gaps, architect production portfolio projects, and navigate a realistic learning roadmap.\n\nWhat role do you want to break into today? You can select a quick prompt below or type your career aspirations!"
        )
        db.session.add(welcome_msg)

        # Seed default progress entry
        prog = Progress(
            user_id=user.id,
            study_hours=14.5,
            notes='Completed JavaScript fundamentals and Git version control modules.',
            skills_completed_count=6,
            projects_completed_count=2,
            streak_days=5,
            overall_progress_pct=68
        )
        db.session.add(prog)

        # Seed initial skills
        default_skills = [
            ("HTML5 & CSS3", "Frontend", "✓", "High", 1, 95),
            ("JavaScript (ES6+)", "Languages", "✓", "High", 2, 85),
            ("Git & GitHub", "DevOps", "✓", "High", 3, 90),
            ("React", "Frontend", "In Progress", "High", 4, 55),
            ("SQL & Relational DBs", "Databases", "In Progress", "High", 5, 50),
            ("Python Backend", "Backend", "✓", "Medium", 6, 80),
            ("Docker Containers", "DevOps", "Missing", "Medium", 7, 20),
            ("CI/CD & Cloud Deploy", "DevOps", "Missing", "High", 8, 15)
        ]
        for name, cat, stat, prio, order, prof in default_skills:
            us = UserSkill(
                user_id=user.id,
                skill_name=name,
                category=cat,
                status=stat,
                priority=prio,
                learning_order=order,
                proficiency=prof,
                target_career='Full Stack Developer'
            )
            db.session.add(us)

        db.session.commit()
    else:
        # Guarantee hashed password exists for default user
        if not user.password_hash:
            user.set_password('password123')
            db.session.commit()

    return user


def sync_db_columns():
    """Ensure newly introduced columns exist in SQLite without requiring manual migrations."""
    from sqlalchemy import text
    try:
        with db.engine.connect() as conn:
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))
                conn.commit()
            except Exception:
                pass
            try:
                conn.execute(text("ALTER TABLE messages ADD COLUMN chat_id INTEGER"))
                conn.execute(text("UPDATE messages SET chat_id = conversation_id WHERE chat_id IS NULL"))
                conn.commit()
            except Exception:
                pass
    except Exception as e:
        logger.warning(f"Schema sync notice: {e}")


# Ensure database schema is synchronized and default user is ready on startup
with app.app_context():
    db.create_all()
    sync_db_columns()
    try:
        get_or_create_default_user()
    except Exception as e:
        logger.error(f"Error seeding default user: {e}")
        db.session.rollback()


if __name__ == '__main__':
    logger.info(f"Starting SkillMap AI on http://{Config.HOST}:{Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
