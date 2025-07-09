# Graph Analysis AI

## Project Overview

This is a full-stack AI application that analyzes graph images and provides evidence-backed insights using Google's Gemini API. The application consists of:

- **Backend**: Python FastAPI server with PostgreSQL database
- **Frontend**: Next.js React application with modern UI
- **AI Integration**: Google Gemini Vision API for graph analysis
- **Database**: PostgreSQL for storing historical data and validation

## Architecture

The application follows the architecture described in `concept.md`:

1. User uploads or captures a graph image
2. Frontend sends image to FastAPI backend
3. Backend processes image with Gemini Vision API
4. System validates insights against historical data
5. Refined insights are returned to user

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 18+
- PostgreSQL 12+
- Google Gemini API key

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   copy .env.example .env
   ```
   
   Edit `.env` and add your configuration:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `DATABASE_URL`: PostgreSQL connection string

5. Initialize the database:
   ```bash
   psql -U your_username -d postgres -f ../database/init.sql
   ```

6. Run the server:
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create environment file:
   ```bash
   copy .env.local.example .env.local
   ```
   
   Add your configuration:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:3000`

### Database Setup

1. Create PostgreSQL database:
   ```sql
   CREATE DATABASE graph_analysis;
   ```

2. Run the initialization script:
   ```bash
   psql -U username -d graph_analysis -f database/init.sql
   ```

## API Endpoints

### Backend API

- `GET /`: Health check
- `POST /api/analyze/upload`: Analyze uploaded graph image
- `POST /api/analyze/screencap`: Analyze screen capture
- `GET /api/history`: Get historical data

### Example Usage

```bash
# Upload a graph image for analysis
curl -X POST "http://localhost:8000/api/analyze/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@graph.png"
```

## Features

### Image Analysis
- Upload graph images (PNG, JPG, JPEG, GIF, BMP)
- Screen capture functionality for live graphs
- Support for various chart types (line, bar, pie, etc.)

### AI-Powered Insights
- Chart type identification
- Trend analysis and pattern recognition
- Anomaly detection
- Evidence-backed recommendations
- Data extraction from visual elements

### Data Validation
- Historical data storage
- Cross-validation with previous analyses
- Insight refinement based on historical context

### Modern UI
- Drag-and-drop file upload
- Real-time screen capture
- Responsive design with Tailwind CSS
- Clear visualization of results

## Security Features

- API key management via environment variables
- HTTPS/TLS support (configure in production)
- Input validation and sanitization
- File type restrictions
- Error handling and logging

## Development

### Running Tests

Backend:
```bash
cd backend
python -m pytest tests/
```

Frontend:
```bash
cd frontend
npm run test
```

### Code Quality

- Backend uses Black for code formatting
- Frontend uses ESLint and Prettier
- Type checking with TypeScript

## Deployment

### Production Considerations

1. **Environment Variables**: Use secure secret management
2. **Database**: Use managed PostgreSQL service
3. **HTTPS**: Configure SSL/TLS certificates
4. **Monitoring**: Add logging and error tracking
5. **Scaling**: Consider load balancers and container orchestration

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the GitHub issues
- Review the concept.md for architectural details
- Consult the API documentation at `/docs` when server is running
