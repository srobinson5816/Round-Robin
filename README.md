Here are the updated specs that match your new code:

### Models

1. **Tech Model**
    - **Fields:**
        - `id` (auto-generated)
        - `name` (CharField, max_length=100)
        - `active` (BooleanField, default=True)
    - **Methods:**
        - `get_next()`: Returns the next active tech in rotation.
        - `get_previous()`: Returns the previous active tech based on the assignment history.

2. **TechAssignment Model**
    - **Fields:**
        - `tech` (ForeignKey to Tech)
        - `assigned_at` (DateTimeField, default=timezone.now)
        - `is_current` (BooleanField, default=True)
    - **Meta:**
        - Ordering by `-assigned_at`

3. **Settings Model**
    - **Fields:**
        - `current_tech` (ForeignKey to Tech, null=True, on_delete=models.SET_NULL)
        - `previous_tech` (ForeignKey to Tech, null=True, on_delete=models.SET_NULL)
        - `database_location` (CharField, max_length=255, blank=True)
    - **Methods:**
        - `update_current_tech(new_tech, direction='forward')`: Updates `current_tech` and `previous_tech` based on the direction.
        - `load()`: Loads the settings object, creating it if necessary.

### Views

1. **Main View**
    - **Functions:**
        - Display the current tech
        - Display the previous tech
        - Determine the next tech based on the current tech and history
        - Handle "Next" button clicks
        - Show tech list and assignments
    - **Templates:**
        - `rotation/main.html`
    - **URLs:**
        - `'/'`

2. **Tech Management View**
    - **Functions:**
        - CRUD operations for techs (create, read, update, delete)
    - **Templates:**
        - `rotation/tech_list.html`
        - `rotation/tech_form.html`
        - `rotation/tech_confirm_delete.html`
    - **URLs:**
        - `/techs/`

3. **Settings View**
    - **Functions:**
        - Update database location
    - **Templates:**
        - `rotation/settings.html`
    - **URLs:**
        - `/settings/`

### URLs

1. **Main page:** `'/'`
2. **Tech management:** `'/techs/'`
3. **Settings:** `'/settings/'`

### Tests

1. **Model Tests:**
    - **Tech Model:**
        - Test `get_next()`
        - Test `get_previous()`
    - **TechAssignment Model:**
        - Test assignment creation
    - **Settings Model:**
        - Test `update_current_tech()` method (forward and backward)
        - Test assignment history limit

2. **View Tests:**
    - **Main View:**
        - Check if current and previous techs are displayed correctly
        - Verify "Next" button functionality
    - **Tech Management View:**
        - Verify CRUD operations for techs
    - **Settings View:**
        - Check database location update

### Development Process (TDD Approach)

1. Write failing tests for the **Tech** model.
2. Implement the **Tech** model to pass the tests.
3. Repeat for the **Settings** model.
4. Write failing view tests.
5. Implement views and templates to pass the tests.

### Additional Considerations

1. Use forms for tech management and settings.
2. Use Django's built-in authentication system to secure the app.
3. Utilize Django ORM for database operations, allowing easy switching between SQLite and other databases.

### Database

- **Default Database:** SQLite
- **Database Location Update:** Allow changing the database location through settings.

### User Interface

1. **Main Page:**
    - Display current and previous techs clearly.
    - Prominent "Next" button.
    - List of all techs with their active status.
    - CRUD buttons for techs.
    - Link to the settings page.

2. **Tech Management Page:**
    - Form for adding new techs.
    - List of existing techs with edit and delete options.
    - Option to toggle active status.

3. **Settings Page:**
    - Form to update database location.
    - Display current database location.
