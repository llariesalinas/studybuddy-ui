# Tutee Profile Redesign - Backend Task 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Include `profile_picture_url` in the tutee profile response and refactor to use a Serializer.

**Architecture:** Use Django Rest Framework Serializers to handle the data transformation, ensuring absolute URLs are generated for media files.

**Tech Stack:** Python, Django, DRF

---

### Task 1: Create UserProfileSerializer

**Files:**
- Modify: `backend/studybuddy/serializers.py`

- [ ] **Step 1: Add UserProfileSerializer to serializers.py**

```python
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['fname', 'mname', 'lname', 'course', 'year_level', 'bio']
```

- [ ] **Step 2: Commit**

```bash
git add backend/studybuddy/serializers.py
git commit -m "backend: add UserProfileSerializer"
```

### Task 2: Implement Failing Test for Avatar URL

**Files:**
- Modify: `backend/studybuddy/tests.py`

- [ ] **Step 1: Add TuteeProfileTests class to tests.py**

```python
class TuteeProfileTests(APITestCase):
    def setUp(self):
        self.tutee_user = User.objects.create_user(
            username="tutee-test",
            email="tutee@example.com",
            password="password",
        )
        self.tutee_profile = UserProfile.objects.create(
            user=self.tutee_user,
            fname="Tutee",
            mname="",
            lname="Test",
            role="Tutee",
            year_level=11,
        )

    def test_get_profile_includes_avatar_url(self):
        self.client.force_authenticate(user=self.tutee_user)
        response = self.client.get('/api/tutee/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('profile_picture_url', response.data)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/studybuddy/tests.py -k test_get_profile_includes_avatar_url`

- [ ] **Step 3: Commit**

```bash
git add backend/studybuddy/tests.py
git commit -m "test: add failing test for profile_picture_url"
```

### Task 3: Update View to include Avatar URL

**Files:**
- Modify: `backend/studybuddy/views.py`

- [ ] **Step 1: Update imports in views.py**

Ensure `UserProfileSerializer` is imported.

- [ ] **Step 2: Refactor get_tutee_profile to use Serializer and include avatar URL**

```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tutee_profile(request):
    profile = request.user.userprofile
    
    try:
        pref = Preference.objects.get(user=profile)
        subject_ids = list(pref.subjects.values_list("subject_code", flat=True))
    except Preference.DoesNotExist:
        subject_ids = []

    data = UserProfileSerializer(profile).data
    data['email'] = request.user.email
    data['subjects'] = subject_ids
    data['profile_picture_url'] = request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else None
    
    return Response(data)
```

- [ ] **Step 3: Run test to verify it passes**

Run: `pytest backend/studybuddy/tests.py -k test_get_profile_includes_avatar_url`

- [ ] **Step 4: Commit**

```bash
git add backend/studybuddy/views.py
git commit -m "backend: include profile_picture_url in tutee profile data"
```
