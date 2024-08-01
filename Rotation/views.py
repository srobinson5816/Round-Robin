import sys
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import connections
from .models import Tech, TechAssignment, Settings
from .forms import TechForm, SettingsForm
from .utils import get_database_location, update_database_location
from .constants import ASSIGNMENT_HISTORY_LIMIT

def tech_list(request):
    techs = Tech.objects.all()
    return render(request, 'rotation/tech_list.html', {'techs': techs})

def tech_create(request):
    if request.method == 'POST':
        form = TechForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tech_list')
    else:
        form = TechForm()
    return render(request, 'rotation/tech_form.html', {'form': form})

def tech_update(request, pk):
    tech = get_object_or_404(Tech, pk=pk)
    if request.method == 'POST':
        form = TechForm(request.POST, instance=tech)
        if form.is_valid():
            form.save()
            return redirect('tech_list')
    else:
        form = TechForm(instance=tech)
    return render(request, 'rotation/tech_form.html', {'form': form})

def tech_delete(request, pk):
    tech = get_object_or_404(Tech, pk=pk)
    if request.method == 'POST':
        tech.delete()
        return redirect('tech_list')
    return render(request, 'rotation/tech_confirm_delete.html', {'tech': tech})

def main_view(request):
    settings = Settings.load()
    techs = Tech.objects.all()
    assignments = TechAssignment.objects.all()[:ASSIGNMENT_HISTORY_LIMIT]
    
    # Get the most recent assignment
    most_recent_assignment = TechAssignment.objects.order_by('-assigned_at').first()
    
    # Get the current assignment (which might be historical)
    current_assignment = TechAssignment.objects.filter(is_current=True).first()
    
    if current_assignment:
        # Find the previous assignment in history
        previous_assignment = TechAssignment.objects.filter(
            assigned_at__lt=current_assignment.assigned_at
        ).order_by('-assigned_at').first()
        
        previous_tech = previous_assignment.tech if previous_assignment else None
        current_tech = current_assignment.tech
        
        # Determine the next tech
        if current_assignment == most_recent_assignment:
            next_tech = current_tech.get_next()
        else:
            # If viewing history, next tech is the one after the current in history
            next_assignment = TechAssignment.objects.filter(
                assigned_at__gt=current_assignment.assigned_at
            ).order_by('assigned_at').first()
            next_tech = next_assignment.tech if next_assignment else most_recent_assignment.tech
    else:
        previous_tech = None
        current_tech = None
        next_tech = techs.filter(active=True).first()

    # Determine if we're viewing history
    viewing_history = current_assignment != most_recent_assignment if current_assignment and most_recent_assignment else False
    
    return render(request, 'rotation/main.html', {
        'settings': settings,
        'current_tech': current_tech,
        'previous_tech': previous_tech,
        'next_tech': next_tech,
        'techs': techs,
        'assignments': assignments,
        'viewing_history': viewing_history,
    })

def next_tech(request):
    settings = Settings.load()
    techs = Tech.objects.filter(active=True)
    
    # Get the most recent assignment
    most_recent_assignment = TechAssignment.objects.order_by('-assigned_at').first()
    
    # Get the current assignment (which might be historical)
    current_assignment = TechAssignment.objects.filter(is_current=True).first()

    if not current_assignment and techs.exists():
        # If no tech is currently assigned, assign the first active tech
        next_tech = techs.first()
    elif current_assignment != most_recent_assignment:
        # We're viewing history, so reset to the most recent assignment
        next_tech = most_recent_assignment.tech
    elif current_assignment:
        # We're at the most recent assignment, so get the next tech in rotation
        next_tech = current_assignment.tech.get_next()
    else:
        next_tech = None

    if next_tech:
        if current_assignment != most_recent_assignment:
            # If we were viewing history, update without creating a new assignment
            TechAssignment.objects.filter(is_current=True).update(is_current=False)
            most_recent_assignment.is_current = True
            most_recent_assignment.save()
            settings.current_tech = next_tech
            settings.previous_tech = TechAssignment.objects.filter(
                assigned_at__lt=most_recent_assignment.assigned_at
            ).order_by('-assigned_at').first().tech if TechAssignment.objects.filter(
                assigned_at__lt=most_recent_assignment.assigned_at
            ).exists() else None
            settings.save()
            messages.success(request, f"Returned to current tech: {next_tech.name}")
        else:
            # Normal forward progression
            settings.update_current_tech(next_tech, direction='forward')
            messages.success(request, f"{next_tech.name} has been assigned as the next tech.")
    else:
        messages.warning(request, "No active techs available to assign.")

    return redirect('main')

def previous_tech(request):
    settings = Settings.load()
    current_assignment = TechAssignment.objects.filter(is_current=True).first()
    if current_assignment:
        previous_assignment = TechAssignment.objects.filter(
            assigned_at__lt=current_assignment.assigned_at
        ).order_by('-assigned_at').first()
        if previous_assignment:
            settings.update_current_tech(None, direction='backward')
        else:
            messages.info(request, "You're at the beginning of the tech history.")
    else:
        messages.info(request, "No tech assignments found.")
    return redirect('main')

def settings_view(request):
    # Check if the code is running in a test environment
    is_testing = 'test' in sys.argv or 'test_coverage' in sys.argv
    
    current_location = get_database_location()

    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            new_location = form.cleaned_data['database_location']
            if new_location != current_location and not is_testing:
                # Only attempt to update database location if not in a test environment
                if update_database_location(new_location):
                    connections.close_all()
                    messages.success(request, 'Database location updated successfully. The change will take effect immediately.')
                    return redirect('settings')
                else:
                    messages.error(request, 'Failed to update database location.')
            elif is_testing:
                # Handle testing environment message if needed
                messages.info(request, 'Database location update skipped during testing.')
            else:
                messages.info(request, 'Database location remains unchanged.')
    else:
        form = SettingsForm(initial={'database_location': current_location})

    return render(request, 'rotation/settings.html', {'form': form, 'current_location': current_location})
