import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from app.models import db, Settings

app = create_app()
app.testing = True
app.config['WTF_CSRF_ENABLED'] = False

with app.app_context():
    client = app.test_client()
    # Ensure we can GET settings page
    r = client.get('/admin/settings')
    print('GET /admin/settings ->', r.status_code)

    # Create admin session cookie by setting session via test_client (use login)
    # First get login page to get any session
    rv = client.get('/')

    # login as admin with default credentials (admin/change-me-please) if exists
    login_data = {'username':'admin','password':'change-me-please'}
    rv = client.post('/login', data=login_data, follow_redirects=True)
    print('POST /login ->', rv.status_code)

    # Check access to admin settings after login
    # Ensure admin session for testing (set session directly)
    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['username'] = 'admin'
        sess['role'] = 'admin'
    r = client.get('/admin/settings')
    print('GET /admin/settings after login ->', r.status_code)

    # Test site settings POST
    site_data = {'siteName':'Prueba Sitio','supportEmail':'prueba@ejemplo.com','defaultPage':'home','maxConcurrent':'3'}
    r = client.post('/admin/settings/site', data=site_data, follow_redirects=True)
    print('/admin/settings/site ->', r.status_code)
    print('response:', r.data.decode()[:400])
    s = Settings.query.first()
    print('system_name ->', s.system_name, 'support_email ->', s.support_email, 'max ->', s.max_concurrent)

    # Test maintenance POST
    maint_data = {'maintenance':'on','maintenanceMessage':'Mantenimiento de prueba'}
    r = client.post('/admin/settings/maintenance', data=maint_data, follow_redirects=True)
    print('/admin/settings/maintenance ->', r.status_code)
    print('response:', r.data.decode()[:400])
    s = Settings.query.first()
    print('maintenance ->', s.maintenance, 'message ->', s.maintenance_message)

    # Verify redirection for non-admin user to /maintenance
    # logout admin
    client.get('/logout')
    r = client.get('/home', follow_redirects=True)
    print('GET /home after maintenance (not logged) ->', r.status_code, r.request.path)

print('Test finished')
