# Blogging Platform API

A robust and feature-rich REST API built with Django and Django REST Framework for managing blog posts, categories, tags, and users. This API provides a complete backend solution for a blogging platform with authentication, authorization, search capabilities, and comprehensive documentation.

## Features

### Core Functionality

- **User Management**: Registration, authentication, and profile management
- **Post Management**: Full CRUD operations for blog posts
- **Categorization**: Organize posts with categories and tags
- **Search & Filtering**: Advanced search and filtering capabilities
- **Authorization**: Role-based permissions (authors can only edit their own posts)
- **API Documentation**: Interactive API documentation with Swagger and Redoc

### Technical Features

- **Token-based Authentication**: Secure API access using Django REST Framework tokens
- **Auto-generated Documentation**: Interactive API docs using drf-spectacular
- **Database Optimization**: Efficient queries with proper relationships
- **Input Validation**: Comprehensive data validation and error handling
- **Testing**: Extensive test coverage with unit and integration tests

## Requirements

- Python 3.8+
- Django 4.2+
- Django REST Framework 3.14+
- MySQL 5.7+

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd blogging-platform-api
```

### 2. Create and activate virtual environment

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

Ensure you have MySQL installed and create a database:

```sql
CREATE DATABASE blogging_platform_api_db;
```

### 5. Configure environment

Update the database configuration in `blogging_platform_api/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'blogging_platform_api_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306'
    }
}
```

### 6. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create superuser (optional)

```bash
python manage.py createsuperuser
```

### 8. Run the development server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## API Documentation

### Interactive Documentation

- **Swagger UI**: `http://127.0.0.1:8000/api/docs/swagger/`
- **ReDoc**: `http://127.0.0.1:8000/api/docs/redoc/`
- **Schema**: `http://127.0.0.1:8000/api/schema/`

### API Endpoints

#### Authentication Endpoints

| Method | Endpoint     | Description       | Authentication |
| ------ | ------------ | ----------------- | -------------- |
| POST   | `/register/` | User registration | None           |
| POST   | `/login/`    | User login        | None           |
| GET    | `/profile/`  | Get user profile  | Token Required |

#### Post Management Endpoints

| Method | Endpoint | Description         | Authentication   |
| ------ | -------- | ------------------- | ---------------- |
| GET    | `/`      | List all posts      | None             |
| POST   | `/`      | Create new post     | Token Required   |
| GET    | `/<id>/` | Get post details    | None             |
| PUT    | `/<id>/` | Update post         | Token Required\* |
| PATCH  | `/<id>/` | Partial update post | Token Required\* |
| DELETE | `/<id>/` | Delete post         | Token Required\* |

\*Only the author of the post can modify or delete it.

## Search & Filtering

The API supports advanced search and filtering capabilities:

### Search Parameters

- `search`: Search in post titles, content, author username, and tag names
- `category`: Filter by category name
- `author`: Filter by author username
- `tags`: Filter by tag name
- `published_date`: Filter by specific publication date
- `published_after`: Filter posts published after date
- `published_before`: Filter posts published before date

### Example Requests

```bash
# Search posts
GET /?search=django

# Filter by category
GET /?category=Technology

# Filter by author
GET /?author=johndoe

# Filter by multiple criteria
GET /?category=Tech&author=johndoe&search=tutorial

# Date range filtering
GET /?published_after=2024-01-01&published_before=2024-12-31
```

## Authentication

The API uses token-based authentication. To access protected endpoints:

1. **Register or Login** to obtain a token
2. **Include the token** in request headers:
   ```
   Authorization: Token your_token_here
   ```

### Example Authentication Flow

#### 1. Register a new user

```bash
curl -X POST http://127.0.0.1:8000/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword"
  }'
```

#### 2. Login to get token

```bash
curl -X POST http://127.0.0.1:8000/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepassword"
  }'
```

#### 3. Use token for authenticated requests

```bash
curl -X POST http://127.0.0.1:8000/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your_token_here" \
  -d '{
    "title": "My First Blog Post",
    "content": "This is the content of my blog post.",
    "category_name": "Technology",
    "tags": ["python", "django", "tutorial"]
  }'
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
python manage.py test

# Run tests with coverage
coverage run --source='.' manage.py test
coverage report

# Run specific test file
python manage.py test posts.test.PostTests
```

### Test Coverage

The project includes extensive tests covering:

- User authentication and registration
- Post CRUD operations
- Permission enforcement
- Search and filtering functionality
- Input validation and error handling

## Project Structure

```
blogging_platform_api/
├── manage.py
├── requirements.txt
├── .gitignore
├── blogging_platform_api/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── posts/
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── permissions.py
│   ├── filters.py
│   ├── tests.py
│   └── migrations/
└── users/
    ├── __init__.py
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    └── migrations/
```

### Key Components

#### Models

- **User**: Django's built-in user model
- **Category**: Blog post categories
- **Tag**: Reusable tags for posts
- **Post**: Main blog post model with relationships to User, Category, and Tags

#### Views & Serializers

- **Generic Views**: Using Django REST Framework's class-based views
- **Custom Serializers**: Custom field handling for better API experience
- **Permission Classes**: Custom permission implementation for post ownership

#### Features

- **Filtering**: Django Filter integration for advanced querying
- **Search**: Full-text search across multiple fields
- **Documentation**: Automatic API documentation generation
- **Validation**: Comprehensive input validation and error handling

## 🚀 Deployment

### Production Settings

1. Set `DEBUG = False` in `settings.py`
2. Configure proper `SECRET_KEY`
3. Set appropriate `ALLOWED_HOSTS`
4. Use environment variables for sensitive data
5. Configure proper database settings
6. Set up static file serving

### Example Production Configuration

```python
import os
from pathlib import Path

DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    }
}
```

### Docker Deployment

Create a `Dockerfile` for containerized deployment:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Update documentation for API changes
- Use meaningful commit messages

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions:

1. Check the [API Documentation](http://127.0.0.1:8000/api/docs/swagger/)
2. Review the test files for usage examples
3. Create an issue on GitHub

## Future Enhancements

- [ ] Comment system for posts
- [ ] Like/unlike functionality
- [ ] User following system
- [ ] Post publishing workflow (draft/published)
- [ ] File upload for images
- [ ] Rate limiting
- [ ] Email notifications
- [ ] RSS feed generation
- [ ] Analytics and metrics
- [ ] Social media integration

---

**Built using Django and Django REST Framework**
