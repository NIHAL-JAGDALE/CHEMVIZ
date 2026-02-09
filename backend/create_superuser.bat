@echo off
echo Creating Django superuser...
echo.
echo Please enter the following credentials:
echo Username: admin
echo Email: admin@example.com
echo Password: admin123
echo.
.\venv\Scripts\python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"
echo.
echo Superuser created successfully!
echo Username: admin
echo Password: admin123
pause
