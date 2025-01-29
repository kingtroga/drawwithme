# DrawWithMe - Technical Specification

## Overview

DrawWithMe is a collaborative drawing platform that combines creative expression with social interaction and gamification. Users can create art individually or participate in real-time collaborative drawing games with other users.

## Core Features

### Authentication System

- User registration and login
- Social authentication integration (optional)
- Session management for real-time collaboration

### Dashboard

- Personal artwork gallery
  - Completed artworks
  - Work in progress
  - Collaborative pieces
- CRUD operations for artwork management
- Sorting and filtering capabilities

### Drawing Interface

#### Individual Mode

- Canvas implementation using Fabric.js
- Standard drawing tools:
  - Brush, eraser, shapes, text
  - Color picker, brush size
  - Undo/redo functionality
- Auto-save functionality
- Export options (PNG, JSON)

#### Collaborative Mode

- Real-time canvas synchronization
- Cursor position sharing
- Chat interface for communication
- Player status indicators

### Game System

#### Matchmaking

- Random matching algorithm
- Friend-based matching
- Waiting room implementation

#### Game Flow

1. Match two players
2. Generate unique word pairs for each player
3. Start timed drawing session
4. Process completion:
   - Save artwork as PNG
   - Generate vector embeddings for:
     - Created artwork
     - Given word pairs
   - Calculate similarity score
   - Determine win/lose status

### Social Features

- Friend requests system
- Post-game connection options
- Basic profile system
- Activity feed

## Technical Architecture

### Backend (Django)

```python
# Core Models
class User(AbstractUser):
    # Standard Django user fields
    profile_picture = models.ImageField()
    friends = models.ManyToManyField('self')

class Artwork(models.Model):
    title = models.CharField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    creator = models.ForeignKey(User)
    collaborators = models.ManyToManyField(User, related_name='collaborations')
    canvas_data = models.JSONField()  # Fabric.js canvas state
    image = models.ImageField()  # PNG export
    vector_embedding = models.BinaryField()  # Stored as binary
    is_game_artwork = models.BooleanField()
    game_words = ArrayField(models.CharField())

class GameSession(models.Model):
    players = models.ManyToManyField(User)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    word_pairs = models.JSONField()
    artwork = models.OneToOneField(Artwork)
    similarity_score = models.FloatField()
    status = models.CharField()  # WAITING, ACTIVE, COMPLETED
```

### WebSocket Implementation

```python
# consumers.py
class DrawingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'drawing_{self.room_name}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Handle different types of messages:
        # - Canvas updates
        # - Cursor positions
        # - Chat messages
        # - Game state changes

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
```

### Vector Embedding System

```python
from sentence_transformers import SentenceTransformer
import numpy as np

class VectorEmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
      
    def generate_text_embedding(self, text):
        return self.model.encode(text)
      
    def generate_image_embedding(self, image):
        # Implement image embedding logic
        pass
      
    def calculate_similarity(self, embedding1, embedding2):
        return np.dot(embedding1, embedding2)
```

## API Endpoints

### Authentication

```
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/logout/
```

### Artwork Management

```
GET /api/artworks/
POST /api/artworks/
GET /api/artworks/<id>/
PUT /api/artworks/<id>/
DELETE /api/artworks/<id>/
```

### Game System

```
POST /api/games/matchmake/
GET /api/games/<id>/status/
POST /api/games/<id>/submit/
```

### Social

```
POST /api/friends/request/
PUT /api/friends/accept/
GET /api/friends/list/
```

## Frontend Structure

### Pages

1. Landing Page (`/`)
2. Authentication Pages (`/login`, `/register`)
3. Dashboard (`/dashboard`)
4. Drawing Interface (`/draw/<artwork_id>`)
5. Game Interface (`/game/<session_id>`)
6. Profile Page (`/profile/<user_id>`)

### Component Hierarchy

```
App
├── Navigation
├── LandingPage
├── Dashboard
│   ├── ArtworkGrid
│   │   └── ArtworkCard
│   └── GameHistory
├── DrawingInterface
│   ├── ToolBar
│   ├── Canvas
│   └── ChatPanel
└── GameInterface
    ├── PlayerInfo
    ├── Timer
    ├── Canvas
    └── GameStatus
```

## Deployment Considerations

### Infrastructure

- Django backend with PostgreSQL
- Redis for WebSocket support
- S3 or similar for image storage
- Vector database for embeddings

### Performance

- Canvas state optimization
- WebSocket connection management
- Image processing queue
- Caching strategy

### Security

- CSRF protection
- WebSocket authentication
- Rate limiting
- Content moderation

## Future Enhancements

1. Team-based games
2. Custom room creation
3. Advanced drawing tools
4. Achievement system
5. Public artwork gallery
6. Community challenges
