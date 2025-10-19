from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from accounts.models import CustomUser
from .models import Class, Subject


class TeacherScopingTests(TestCase):
	def setUp(self):
		# Create users
		self.admin = CustomUser.objects.create_user(username='1001', full_name='Admin User', password='pass', role='admin')
		self.teacher_a = CustomUser.objects.create_user(username='2001', full_name='Teacher A', password='pass', role='teacher')
		self.teacher_b = CustomUser.objects.create_user(username='2002', full_name='Teacher B', password='pass', role='teacher')
		self.pupil = CustomUser.objects.create_user(username='3001', full_name='Pupil One', password='pass', role='pupil')

		# Create classes
		self.class_a = Class.objects.create(name='GRADE 1A', level='GRADE 1', assigned_teacher=self.teacher_a)
		self.class_b = Class.objects.create(name='GRADE 1B', level='GRADE 1', assigned_teacher=self.teacher_b)

		# Create API clients
		self.client = APIClient()

	def test_teacher_sees_only_assigned_classes(self):
		self.client.force_authenticate(self.teacher_a)
		url = reverse('class-list')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		data = resp.json()
		# Ensure only class_a is listed
		names = [c['name'] for c in data.get('results', data) ]
		self.assertIn(self.class_a.name, names)
		self.assertNotIn(self.class_b.name, names)

	def test_teacher_cannot_create_subject_for_unassigned_class(self):
		self.client.force_authenticate(self.teacher_a)
		url = reverse('subject-list')
		payload = {
			'name': 'Mathematics',
			'assigned_class': self.class_b.id,
			'assigned_teacher': self.teacher_a.id
		}
		resp = self.client.post(url, payload, format='json')
		self.assertIn(resp.status_code, (400, 403))

	def test_teacher_creates_subject_for_assigned_class_and_assigned_teacher_ignored(self):
		self.client.force_authenticate(self.teacher_a)
		url = reverse('subject-list')
		payload = {
			'name': 'English',
			'assigned_class': self.class_a.id,
			'assigned_teacher': self.teacher_b.id  # attempt to assign another teacher
		}
		resp = self.client.post(url, payload, format='json')
		self.assertEqual(resp.status_code, 201)
		data = resp.json()
		# assigned_teacher should be set to teacher_a regardless of provided value
		self.assertEqual(data['assigned_teacher'], self.teacher_a.id)
