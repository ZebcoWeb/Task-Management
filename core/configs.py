from datetime import timedelta

SECRET_ALGORITM = 'HS512'
REFRESH_TOKEN_UNLIMITED = True

ACCESS_TOKEN_EXPIRE_TIME = timedelta(minutes=15)
REFRESH_TOKEN_EXPIRE_TIME = timedelta(days=30)
DEACTIVE_COUNT = 5

DEFAULT_ROLES = [
    {
        'title': 'admin',
        'permissions': [
            {
                'state': 'user',
                'operates': ['read', 'create', 'update', 'delete', 'status', 'trash', 'recycle'] 
            },
            {
                'state': 'userrole',
                'operates': ['create', 'delete'] 
            },
            {
                'state': 'task',
                'operates': ['read', 'update', 'delete']
            },
            {
                'state': 'org',
                'operates': ['create', 'read', 'update', 'delete']
            },
            {
                'state': 'orguser',
                'operates': ['create', 'delete', 'update']
            },
            {
                'state': 'task',
                'operates': ['list', 'update']
            },
            {
                'state': 'request',
                'operates': ['list', 'update']
            },
        ]
    },
    {
        'title': 'org_manager',
        'permissions': [
            {
                'state': 'user',
                'operates': ['read', 'update']
            },
            {
                'state': 'userrole',
                'operates': ['delete']
            },
            {
                'state': 'task',
                'operates': ['create', 'read', 'update', 'delete']
            },
            {
                'state': 'org',
                'operates': ['read', 'update']
            },
            {
                'state': 'orguser',
                'operates': ['delete']
            },
            {
                'state': 'task',
                'operates': ['list', 'update']
            },
            {
                'state': 'request',
                'operates': ['list', 'update']
            },
        ]
    },
    {
        'title': 'org_employee',
        'permissions': [
            {
                'state': 'user',
                'operates': ['read', 'update']
            },
            {
                'state': 'task',
                'operates': ['create', 'update']
            },
            {
                'state': 'org',
                'operates': ['read']
            },
            {
                'state': 'task',
                'operates': ['create']
            },
            {
                'state': 'request',
                'operates': ['list', 'create']
            },
        ]
    },
    {
        'title': 'employee',
        'permissions': [
            {
                'state': 'user',
                'operates': ['read', 'update']
            },
            {
                'state': 'org',
                'operates': ['read']
            },
            {
                'state': 'task',
                'operates': ['create']
            },
            {
                'state': 'request',
                'operates': ['list', 'create']
            },
        ]
    },
]