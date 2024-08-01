from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch
from .models import Tech, TechAssignment, Settings
from .constants import ASSIGNMENT_HISTORY_LIMIT

class MainViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tech1 = Tech.objects.create(name="Alice", active=True)
        cls.tech2 = Tech.objects.create(name="Bob", active=True)
        cls.settings = Settings.load()

    def test_main_view_with_no_assignments(self):
        response = self.client.get(reverse('main'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['current_tech'])
        self.assertIsNone(response.context['previous_tech'])
        self.assertEqual(response.context['next_tech'], self.tech1)

    def test_main_view_with_assignments(self):
        self.settings.update_current_tech(self.tech1, direction='forward')
        response = self.client.get(reverse('main'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['current_tech'], self.tech1)
        self.assertIsNone(response.context['previous_tech'])
        self.assertEqual(response.context['next_tech'], self.tech2)

class PreviousTechViewTests(TestCase):
    def setUp(self):
        self.tech1 = Tech.objects.create(name="Alice", active=True)
        self.tech2 = Tech.objects.create(name="Bob", active=True)
        self.settings = Settings.load()

    def test_previous_tech(self):
        TechAssignment.objects.create(tech=self.tech1, assigned_at=timezone.now() - timezone.timedelta(days=1))
        self.settings.update_current_tech(self.tech2, direction='forward')
        response = self.client.post(reverse('previous_tech'))
        self.assertRedirects(response, reverse('main'))
        self.settings.refresh_from_db()
        self.assertEqual(self.settings.current_tech, self.tech1)

class NextTechViewTests(TestCase):
    def setUp(self):
        self.tech1 = Tech.objects.create(name="Alice", active=True)
        self.tech2 = Tech.objects.create(name="Bob", active=True)
        self.settings = Settings.load()

    def test_next_tech_with_no_current(self):
        response = self.client.post(reverse('next_tech'))
        self.assertRedirects(response, reverse('main'))
        self.settings.refresh_from_db()
        self.assertEqual(self.settings.current_tech, self.tech1)

    def test_next_tech_with_current(self):
        self.settings.update_current_tech(self.tech1, direction='forward')
        response = self.client.post(reverse('next_tech'))
        self.assertRedirects(response, reverse('main'))
        self.settings.refresh_from_db()
        self.assertEqual(self.settings.current_tech, self.tech2)
        self.assertEqual(self.settings.previous_tech, self.tech1)


class TechModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tech1 = Tech.objects.create(name="Alice", active=True)
        cls.tech2 = Tech.objects.create(name="Bob", active=True)
        cls.tech3 = Tech.objects.create(name="Charlie", active=True)
        cls.inactive_tech = Tech.objects.create(name="David", active=False)

        now = timezone.now()
        TechAssignment.objects.create(tech=cls.tech1, assigned_at=now - timezone.timedelta(days=3))
        TechAssignment.objects.create(tech=cls.tech2, assigned_at=now - timezone.timedelta(days=2))
        TechAssignment.objects.create(tech=cls.tech3, assigned_at=now - timezone.timedelta(days=1))

    def test_get_previous(self):
        self.assertEqual(self.tech1.get_previous(), self.tech3)
        self.assertEqual(self.tech2.get_previous(), self.tech1)
        self.assertEqual(self.tech3.get_previous(), self.tech2)

    def test_get_next(self):
        self.assertEqual(self.tech1.get_next(), self.tech2)
        self.assertEqual(self.tech2.get_next(), self.tech3)
        self.assertEqual(self.tech3.get_next(), self.tech1)

    def test_get_next_with_inactive(self):
        self.tech3.active = False
        self.tech3.save()
        self.assertEqual(self.tech2.get_next(), self.tech1)

class TechManagementViewTests(TestCase):
    def setUp(self):
        self.tech1 = Tech.objects.create(name="Alice", active=True)

    def test_tech_list_view(self):
        response = self.client.get(reverse('tech_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.tech1.name)

    def test_tech_create_view(self):
        response = self.client.post(reverse('tech_create'), {'name': 'Bob', 'active': True})
        self.assertRedirects(response, reverse('tech_list'))
        self.assertTrue(Tech.objects.filter(name='Bob').exists())

    def test_tech_update_view(self):
        response = self.client.post(reverse('tech_update', args=[self.tech1.id]), {'name': 'Alice Updated', 'active': False})
        self.assertRedirects(response, reverse('tech_list'))
        self.tech1.refresh_from_db()
        self.assertEqual(self.tech1.name, 'Alice Updated')
        self.assertFalse(self.tech1.active)

    def test_tech_delete_view(self):
        response = self.client.post(reverse('tech_delete', args=[self.tech1.id]))
        self.assertRedirects(response, reverse('tech_list'))
        self.assertFalse(Tech.objects.filter(id=self.tech1.id).exists())

class TechAssignmentModelTests(TestCase):
    def setUp(self):
        self.tech = Tech.objects.create(name="Alice", active=True)

    def test_assignment_creation(self):
        assignment = TechAssignment.objects.create(tech=self.tech)
        self.assertIsNotNone(assignment.assigned_at)
        self.assertTrue(assignment.is_current)

        from django.test import TestCase

class SettingsModelTests(TestCase):
    def setUp(self):
        self.tech1 = Tech.objects.create(name="Alice", active=True)
        self.tech2 = Tech.objects.create(name="Bob", active=True)
        self.settings = Settings.load()

    def test_update_current_tech_forward(self):
        self.settings.update_current_tech(self.tech1, direction='forward')
        self.assertEqual(self.settings.current_tech, self.tech1)
        self.assertIsNone(self.settings.previous_tech)

        self.settings.update_current_tech(self.tech2, direction='forward')
        self.assertEqual(self.settings.current_tech, self.tech2)
        self.assertEqual(self.settings.previous_tech, self.tech1)

    def test_update_current_tech_backward(self):
        TechAssignment.objects.create(tech=self.tech1, assigned_at=timezone.now() - timezone.timedelta(days=1))
        self.settings.update_current_tech(self.tech2, direction='forward')
        self.settings.update_current_tech(None, direction='backward')
        
        self.assertEqual(self.settings.current_tech, self.tech1)

    def test_assignment_history_limit(self):
        current_time = timezone.now()
        for i in range(ASSIGNMENT_HISTORY_LIMIT + 5):
            test_time = current_time - timezone.timedelta(days=i)
            with patch('django.utils.timezone.now', return_value=test_time):
                self.settings.update_current_tech(self.tech1, direction='forward')
        
        self.assertEqual(TechAssignment.objects.count(), ASSIGNMENT_HISTORY_LIMIT)

