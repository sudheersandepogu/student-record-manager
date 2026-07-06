import json
import re
import os
from django.shortcuts import render
from django.http import JsonResponse
from django.db import models, IntegrityError
from django.conf import settings
from .models import Student

# Email regex pattern
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# Backup file path
BACKUP_FILE_PATH = os.path.join(settings.BASE_DIR, 'students.txt')

def index(request):
    """Renders the main page."""
    return render(request, 'student_app/index.html')

def get_backup_count():
    """Counts the number of records in students.txt backup."""
    if not os.path.exists(BACKUP_FILE_PATH):
        return 0
    try:
        with open(BACKUP_FILE_PATH, 'r', encoding='utf-8') as f:
            return sum(1 for line in f if line.strip())
    except IOError:
        return 0

def add_student_to_backup(student):
    """Appends student record to backup file."""
    try:
        # Write comma-separated values to backup file
        created_str = student.created_at.strftime('%Y-%m-%d %H:%M:%S') if student.created_at else ''
        record_line = f"{student.id},{student.name},{student.email},{student.age},{student.grade},{created_str}\n"
        with open(BACKUP_FILE_PATH, 'a', encoding='utf-8') as f:
            f.write(record_line)
        return True
    except IOError as e:
        # We can log or raise to views to handle
        raise IOError(f"Failed to write to backup file: {str(e)}")

def remove_student_from_backup(student_id):
    """Removes student record with specific ID from backup file."""
    if not os.path.exists(BACKUP_FILE_PATH):
        return
    try:
        temp_file_path = BACKUP_FILE_PATH + '.tmp'
        deleted = False
        with open(BACKUP_FILE_PATH, 'r', encoding='utf-8') as f_in:
            with open(temp_file_path, 'w', encoding='utf-8') as f_out:
                for line in f_in:
                    parts = line.strip().split(',')
                    if parts and parts[0] == str(student_id):
                        deleted = True
                        continue  # Skip writing this line (delete it)
                    f_out.write(line)
        
        # Replace original file with temp file
        if os.path.exists(BACKUP_FILE_PATH):
            os.remove(BACKUP_FILE_PATH)
        os.rename(temp_file_path, BACKUP_FILE_PATH)
        return deleted
    except IOError as e:
        raise IOError(f"Backup file operation failed during deletion: {str(e)}")

def get_stats():
    """Helper to calculate dashboard statistics."""
    total_students = Student.objects.count()
    
    # Average age
    avg_age_query = Student.objects.aggregate(models.Avg('age'))['age__avg']
    avg_age = round(avg_age_query, 1) if avg_age_query is not None else 0
    
    # Highest Grade Count
    grade_counts = Student.objects.values('grade').annotate(count=models.Count('id')).order_by('-count')
    if grade_counts.exists():
        highest_grade_count = grade_counts[0]['count']
        highest_grade_name = grade_counts[0]['grade']
    else:
        highest_grade_count = 0
        highest_grade_name = "N/A"
        
    # Total Records (Backup file size/lines)
    total_backup_records = get_backup_count()
    
    return {
        'total_students': total_students,
        'average_age': avg_age,
        'highest_grade_count': highest_grade_count,
        'highest_grade_name': highest_grade_name,
        'total_records': total_backup_records
    }

def get_students(request):
    """API endpoint to get list of all students and stats."""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        students = Student.objects.all().order_by('-id')
        student_list = []
        for s in students:
            student_list.append({
                'id': s.id,
                'name': s.name,
                'email': s.email,
                'age': s.age,
                'grade': s.grade,
                'created_at': s.created_at.strftime('%Y-%m-%d %H:%M:%S') if s.created_at else ''
            })
            
        stats = get_stats()
        return JsonResponse({
            'success': True,
            'students': student_list,
            'stats': stats
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': f"Database or unexpected error: {str(e)}"}, status=500)

def add_student(request):
    """API endpoint to add a new student."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        age_str = str(data.get('age', '')).strip()
        grade = data.get('grade', '').strip()
        
        # 1. Empty Fields Validation
        if not name or not email or not age_str or not grade:
            return JsonResponse({'success': False, 'error': 'All fields are required.'}, status=400)
            
        # 2. Email Validation using Regex
        if not re.match(EMAIL_REGEX, email):
            return JsonResponse({'success': False, 'error': 'Please provide a valid email address (e.g. user@domain.com).'}, status=400)
            
        # 3. Age Validation
        try:
            age = int(age_str)
            if age <= 0 or age > 120:
                return JsonResponse({'success': False, 'error': 'Age must be a positive integer between 1 and 120.'}, status=400)
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Age must be a valid integer.'}, status=400)
            
        # 4. Duplicate Email Validation
        if Student.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': 'A student with this email address already exists.'}, status=400)
            
        # Create and save Student model
        student = Student(name=name, email=email, age=age, grade=grade)
        student.save()
        
        # Save to backup file
        try:
            add_student_to_backup(student)
        except IOError as e:
            # File Not Found / File write exception handling
            # We still saved to database, but notify user about backup issue
            return JsonResponse({
                'success': True,
                'message': f"Student '{name}' added to database successfully, but backup failed: {str(e)}",
                'stats': get_stats()
            })
            
        return JsonResponse({
            'success': True,
            'message': f"Student '{name}' successfully registered and backed up!",
            'stats': get_stats()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON request data.'}, status=400)
    except IntegrityError:
        return JsonResponse({'success': False, 'error': 'Database integrity error. Email may already exist.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f"Database or system error: {str(e)}"}, status=500)

def delete_student(request, student_id):
    """API endpoint to delete a student."""
    if request.method != 'DELETE':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        
    try:
        try:
            student = Student.objects.get(pk=student_id)
        except Student.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Student record not found.'}, status=404)
            
        name = student.name
        
        # Delete from backup first (or after)
        try:
            remove_student_from_backup(student_id)
        except IOError as e:
            # Handle file read/write issues but proceed to database delete if database is primary
            pass
            
        # Delete from database
        student.delete()
        
        return JsonResponse({
            'success': True,
            'message': f"Student '{name}' successfully deleted.",
            'stats': get_stats()
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': f"Failed to delete student record: {str(e)}"}, status=500)

def search_student(request):
    """API endpoint to search students in real-time by name or email."""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        
    try:
        query = request.GET.get('query', '').strip()
        
        # If query is empty, return all students
        if not query:
            students = Student.objects.all().order_by('-id')
        else:
            students = Student.objects.filter(
                models.Q(name__icontains=query) | models.Q(email__icontains=query)
            ).order_by('-id')
            
        student_list = []
        for s in students:
            student_list.append({
                'id': s.id,
                'name': s.name,
                'email': s.email,
                'age': s.age,
                'grade': s.grade,
                'created_at': s.created_at.strftime('%Y-%m-%d %H:%M:%S') if s.created_at else ''
            })
            
        return JsonResponse({
            'success': True,
            'students': student_list
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': f"Search failed: {str(e)}"}, status=500)

