import json
import unittest
from app import app, db, get_or_create_default_user
from models import User, Chat, Conversation, Message, Roadmap, Skill, UserSkill, Project, Progress, ResumeAnalysis


class SkillMapTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            get_or_create_default_user()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_pages_render(self):
        """Test index, dashboard, login, and register routes."""
        res_index = self.client.get('/')
        self.assertEqual(res_index.status_code, 200)
        self.assertIn(b'SkillMap', res_index.data)
        self.assertIn(b'SANJAY', res_index.data)

        res_dash = self.client.get('/dashboard')
        self.assertEqual(res_dash.status_code, 200)
        self.assertIn(b'Dashboard', res_dash.data)
        self.assertIn(b'SANJAY', res_dash.data)

        res_login = self.client.get('/login')
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b'Sign In', res_login.data)

        res_register = self.client.get('/register')
        self.assertEqual(res_register.status_code, 200)
        self.assertIn(b'Create Account', res_register.data)

    def test_auth_flow(self):
        """Test user registration, duplicate prevention, login, me, and logout."""
        # 1. Register new user
        reg_res = self.client.post('/api/auth/register', json={
            'username': 'alex_coder',
            'email': 'alex@example.com',
            'password': 'password123',
            'display_name': 'Alex'
        })
        self.assertEqual(reg_res.status_code, 201)
        reg_data = reg_res.get_json()
        self.assertTrue(reg_data['success'])
        self.assertEqual(reg_data['user']['username'], 'alex_coder')

        # 2. Prevent duplicate username
        dup_res = self.client.post('/api/auth/register', json={
            'username': 'alex_coder',
            'email': 'different@example.com',
            'password': 'password123'
        })
        self.assertEqual(dup_res.status_code, 409)

        # 3. Check current user session
        me_res = self.client.get('/api/auth/me')
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.get_json()['user']['username'], 'alex_coder')

        # 4. Logout
        logout_res = self.client.post('/api/auth/logout')
        self.assertEqual(logout_res.status_code, 200)

        # 5. Invalid login attempt
        bad_login = self.client.post('/api/auth/login', json={
            'username': 'alex_coder',
            'password': 'wrongpassword'
        })
        self.assertEqual(bad_login.status_code, 401)

        # 6. Valid login
        good_login = self.client.post('/api/auth/login', json={
            'username': 'alex_coder',
            'password': 'password123'
        })
        self.assertEqual(good_login.status_code, 200)
        self.assertTrue(good_login.get_json()['success'])

    def test_chat_api(self):
        """Test sending chat message and retrieving chat history."""
        # Send message
        res = self.client.post('/api/chat', json={
            'message': 'I want to become a Data Analyst. What should I learn?'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('conversation_id', data)
        self.assertIn('message', data)
        self.assertEqual(data['message']['role'], 'assistant')

        # List chats
        res_list = self.client.get('/api/chats')
        self.assertEqual(res_list.status_code, 200)
        chats = res_list.get_json()
        self.assertGreaterEqual(len(chats), 1)

    def test_chat_lifecycle_and_user_isolation(self):
        """Test chat creation, messaging, renaming, searching, clearing, deletion, and cross-user isolation."""
        # Create User A
        self.client.post('/api/auth/register', json={
            'username': 'user_a',
            'password': 'password123',
            'display_name': 'User A'
        })
        # User A creates a chat
        create_res = self.client.post('/api/chats', json={'title': 'Python Backend Roadmap'})
        self.assertEqual(create_res.status_code, 201)
        chat_a = create_res.get_json()
        chat_a_id = chat_a['id']

        # User A sends a message
        msg_res = self.client.post(f'/api/chats/{chat_a_id}/messages', json={
            'content': 'Explain Flask application factory pattern'
        })
        self.assertEqual(msg_res.status_code, 200)
        msg_data = msg_res.get_json()
        self.assertIn('message', msg_data)

        # User A renames the chat
        rename_res = self.client.post(f'/api/chats/{chat_a_id}/rename', json={'title': 'Flask Mastery'})
        self.assertEqual(rename_res.status_code, 200)
        self.assertEqual(rename_res.get_json()['title'], 'Flask Mastery')

        # User A searches for chat
        search_res = self.client.get('/api/chats/search?q=Flask')
        self.assertEqual(search_res.status_code, 200)
        self.assertGreaterEqual(len(search_res.get_json()), 1)

        # Now Register User B and verify isolation
        self.client.post('/api/auth/register', json={
            'username': 'user_b',
            'password': 'password123',
            'display_name': 'User B'
        })

        # User B cannot access User A's chat
        denied_res = self.client.get(f'/api/chats/{chat_a_id}')
        self.assertEqual(denied_res.status_code, 404)

        # User B's search yields nothing from User A's data
        search_b = self.client.get('/api/chats/search?q=Flask')
        self.assertEqual(search_b.status_code, 200)
        self.assertEqual(len(search_b.get_json()), 0)

        # Switch back to User A
        self.client.post('/api/auth/login', json={'username': 'user_a', 'password': 'password123'})

        # Clear chat
        clear_res = self.client.post(f'/api/chats/{chat_a_id}/clear')
        self.assertEqual(clear_res.status_code, 200)
        chat_after_clear = self.client.get(f'/api/chats/{chat_a_id}').get_json()
        self.assertEqual(len(chat_after_clear['messages']), 0)

        # Delete chat
        del_res = self.client.delete(f'/api/chats/{chat_a_id}')
        self.assertEqual(del_res.status_code, 200)
        del_check = self.client.get(f'/api/chats/{chat_a_id}')
        self.assertEqual(del_check.status_code, 404)

    def test_roadmap_api(self):
        """Test generating career roadmap."""
        res = self.client.post('/api/roadmap', json={
            'career_goal': 'Full Stack Developer',
            'current_level': 'Beginner',
            'current_skills': 'HTML, CSS, Basic JS',
            'hours_per_day': 3.0,
            'target_duration': '6 months'
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertEqual(data['career_goal'], 'Full Stack Developer')
        self.assertIn('phases', data)
        self.assertGreater(len(data['phases']), 0)

        # Get roadmaps list
        res_list = self.client.get('/api/roadmaps')
        self.assertEqual(res_list.status_code, 200)
        roadmaps = res_list.get_json()
        self.assertGreaterEqual(len(roadmaps), 1)

    def test_skill_gap_api(self):
        """Test skill gap analysis and skill toggling."""
        res = self.client.post('/api/skill-gap', json={
            'target_career': 'Data Analyst',
            'current_skills': 'Python, SQL, Excel'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('match_percentage', data)
        self.assertIn('skills', data)
        self.assertGreater(len(data['skills']), 0)

        # Retrieve user skills
        res_skills = self.client.get('/api/skills')
        self.assertEqual(res_skills.status_code, 200)
        skills = res_skills.get_json()
        self.assertGreater(len(skills), 0)

        # Toggle first skill
        first_id = skills[0]['id']
        res_toggle = self.client.post('/api/skills/toggle', json={'skill_id': first_id})
        self.assertEqual(res_toggle.status_code, 200)

    def test_project_generator_api(self):
        """Test project blueprint generation."""
        res = self.client.post('/api/project', json={
            'career': 'Full Stack Developer',
            'skill_level': 'Intermediate',
            'technology': 'Python, Flask, SQLite',
            'project_difficulty': 'Intermediate'
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertIn('title', data)
        self.assertIn('features', data)
        self.assertIn('database_design', data)
        self.assertIn('folder_structure', data)

    def test_progress_api(self):
        """Test telemetry progress retrieval and logging."""
        res = self.client.get('/api/progress')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('overall_progress_pct', data)
        self.assertIn('chart_data', data)

        # Log new study hours
        res_log = self.client.post('/api/progress', json={
            'study_hours': 3.5,
            'notes': 'Learned React hooks'
        })
        self.assertEqual(res_log.status_code, 201)

    def test_interview_api(self):
        """Test interview question generation and answer evaluation."""
        res_q = self.client.post('/api/interview', json={
            'career': 'Full Stack Developer',
            'difficulty': 'Intermediate',
            'question_number': 1
        })
        self.assertEqual(res_q.status_code, 200)
        q_data = res_q.get_json()
        self.assertIn('question', q_data)

        # Submit answer
        res_ans = self.client.post('/api/interview/answer', json={
            'career': 'Full Stack Developer',
            'difficulty': 'Intermediate',
            'question': q_data['question'],
            'answer': 'PostgreSQL is relational with ACID guarantees while MongoDB is document-oriented.'
        })
        self.assertEqual(res_ans.status_code, 200)
        ans_data = res_ans.get_json()
        self.assertIn('score', ans_data)
        self.assertIn('feedback', ans_data)
        self.assertIn('suggested_answer', ans_data)

    def test_resume_analyze_api(self):
        """Test resume ATS audit with text payload."""
        sample_resume = """
        John Doe - Full Stack Developer
        Skills: Python, JavaScript, React, SQL, Git, Docker, HTML, CSS
        Experience: Built scalable REST API with Flask and PostgreSQL handling 2000 users.
        Education: B.S. in Computer Science 2024
        Projects: E-Commerce Store with Stripe and Redis caching.
        """
        res = self.client.post('/api/resume/analyze', json={
            'target_career': 'Full Stack Developer',
            'resume_text': sample_resume
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('ats_score', data)
        self.assertIn('extracted_skills', data)
        self.assertIn('missing_keywords', data)


if __name__ == '__main__':
    unittest.main()
