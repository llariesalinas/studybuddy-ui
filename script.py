import os
import re

target_dir = r'C:\Users\Reginald\Documents\ThesisApp\studybuddy-ui'

def replace_in_file(rel_path, pattern, replacement):
    path = os.path.join(target_dir, rel_path)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = re.sub(pattern, replacement, content)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'Updated {rel_path}')

# 1. backend/studybuddy/views.py
replace_in_file(r'backend\studybuddy\views.py', r'SESSION_SLOT_MINUTES = 30', r'SESSION_SLOT_MINUTES = 60')

# 2. backend/studybuddy/chat/services.py
replace_in_file(r'backend\studybuddy\chat\services.py', r'SESSION_SLOT_MINUTES = 30', r'SESSION_SLOT_MINUTES = 60')

# 3. src/components/BookingTimePicker.vue
replace_in_file(r'src\components\BookingTimePicker.vue', r'minute \+= 30', r'minute += 60')

# 4. src/views/TutorSchedule.vue
replace_in_file(r'src\views\TutorSchedule.vue', r'minute \+= 30', r'minute += 60')
replace_in_file(r'src\views\TutorSchedule.vue', r'addThirtyMinutes', r'addOneHour')
replace_in_file(r'src\views\TutorSchedule.vue', r'getMinutes\(\) \+ 30', r'getMinutes() + 60')

# 5. src/views/TutorDetails.vue
replace_in_file(r'src\views\TutorDetails.vue', r'SESSION_SLOT_HOURS = 0.5', r'SESSION_SLOT_HOURS = 1.0')
replace_in_file(r'src\views\TutorDetails.vue', r'addThirtyMinutes', r'addOneHour')
replace_in_file(r'src\views\TutorDetails.vue', r'\+ 30', r'+ 60')

# 6. src/views/FindTutors.vue
replace_in_file(r'src\views\FindTutors.vue', r'timeToMinutes\(value\) \+ 30', r'timeToMinutes(value) + 60')

# 7. src/views/InitialBooking.vue
replace_in_file(r'src\views\InitialBooking.vue', r'timeToMinutes\(value\) \+ 30', r'timeToMinutes(value) + 60')

