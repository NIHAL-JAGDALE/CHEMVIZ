#!/bin/bash
echo "Creating Django superuser..."
echo ""
echo "Please enter the following credentials:"
echo "Username: admin"
echo "Email: admin@example.com"
echo "Password: admin123"
echo ""

# Attempt to use venv python, fallback to system python
if [ -f "./venv/bin/python" ]; then
    PYTHON_BIN="./venv/bin/python"
elif [ -f "./venv/Scripts/python" ]; then
    PYTHON_BIN="./venv/Scripts/python"
else
    PYTHON_BIN="python3"
fi

$PYTHON_BIN manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"

echo ""
echo "Superuser created successfully (if it didn't already exist)!"
echo "Username: admin"
echo "Password: admin123"
