# Rotation/models.py

from django.db import models
from django.utils import timezone
from .constants import ASSIGNMENT_HISTORY_LIMIT

class Tech(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_next(self):
        next_tech = Tech.objects.filter(active=True, id__gt=self.id).order_by('id').first()
        if not next_tech:
            next_tech = Tech.objects.filter(active=True).exclude(id=self.id).order_by('id').first()
        return next_tech or self

    def get_previous(self):
        previous_assignments = TechAssignment.objects.filter(
            tech__active=True
        ).order_by('-assigned_at')
        
        if not previous_assignments.exists():
            return None
        
        current_assignment = previous_assignments.filter(tech=self).first()
        
        if not current_assignment:
            return previous_assignments.first().tech
        
        current_index = list(previous_assignments).index(current_assignment)
        previous_index = (current_index + 1) % len(previous_assignments)
        
        return previous_assignments[previous_index].tech

class TechAssignment(models.Model):
    tech = models.ForeignKey(Tech, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(default=timezone.now)
    is_current = models.BooleanField(default=True)

    class Meta:
        ordering = ['-assigned_at']

class Settings(models.Model):
    current_tech = models.ForeignKey(Tech, on_delete=models.SET_NULL, null=True, related_name='current_settings')
    previous_tech = models.ForeignKey(Tech, on_delete=models.SET_NULL, null=True, related_name='previous_settings')
    database_location = models.CharField(max_length=255, blank=True)

    def update_current_tech(self, new_tech, direction='forward'):
        current_time = timezone.now()

        if direction == 'forward':
            # Check if there's already a current assignment for today
            today_assignment = TechAssignment.objects.filter(
                is_current=True,
                assigned_at__date=current_time.date()
            ).first()

            if today_assignment and today_assignment.tech == new_tech:
                # If the same tech is already assigned for today, do nothing
                return
            
            # Set all current assignments to False
            TechAssignment.objects.filter(is_current=True).update(is_current=False)
            
            self.previous_tech = self.current_tech
            self.current_tech = new_tech
            
            # Create a new assignment for the new tech
            TechAssignment.objects.create(tech=new_tech, is_current=True, assigned_at=current_time)
            
            # Ensure we only keep the last ASSIGNMENT_HISTORY_LIMIT entries
            old_assignments = TechAssignment.objects.order_by('-assigned_at')[ASSIGNMENT_HISTORY_LIMIT:]
            TechAssignment.objects.filter(pk__in=old_assignments).delete()
        
        elif direction == 'backward':
            current_assignment = TechAssignment.objects.filter(is_current=True).order_by('-assigned_at').first()
            if current_assignment:
                previous_assignment = TechAssignment.objects.filter(
                    assigned_at__lt=current_assignment.assigned_at
                ).order_by('-assigned_at').first()
                
                if previous_assignment:
                    TechAssignment.objects.filter(is_current=True).update(is_current=False)
                    previous_assignment.is_current = True
                    previous_assignment.save()
                    self.previous_tech = self.current_tech
                    self.current_tech = previous_assignment.tech
                else:
                    # If there's no previous assignment, stay on the current one
                    return
        
        self.save()

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
