# HabitBuilder - AI-Powered Habit Formation App

A modern web application that helps users build lasting habits using AI-powered goal decomposition, habit stacking, and progress tracking.

## Features

- 🎯 **Goal Decomposition**: Break down complex goals into manageable atomic habits
- 🔗 **Habit Stacking**: Link new habits to existing ones for maximum success
- 📊 **Progress Tracking**: Track daily habit completion with streaks and analytics
- 📈 **Progress Dashboard**: View detailed analytics and motivational insights
- 🧠 **AI-Powered**: Uses DeepSeek AI for intelligent habit formation guidance
- 🎨 **Modern UI**: Beautiful, responsive design with smooth animations

## Tech Stack

- **Frontend**: React 19, Modern CSS with custom design system
- **Backend**: Flask (Python)
- **AI**: DeepSeek API for natural language processing
- **Storage**: LocalStorage (frontend), optional Firestore integration

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd HabitBuilder
```

### 2. Backend Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install flask flask-cors openai python-dotenv

# Set up environment variables
echo "DEEPSEEK_API_KEY=your_api_key_here" > .env
```

### 3. Frontend Setup
```bash
cd frontend/habit-builder-react
npm install
npm run build
cd ../..
```

### 4. Run the Application
```bash
# Start the Flask server
python app.py
```

The app will be available at `http://localhost:5001`

## API Endpoints

### Goal Decomposition
- **POST** `/decompose_goal`
- Body: `{"goal": "Your goal here"}`
- Returns: Identity shift and atomic habits

### Habit Stacking
- **POST** `/stack_habits`
- Body: `{"current_habits": [...], "desired_habits": [...]}`
- Returns: Habit stack formulas

### Reduce Friction
- **POST** `/reduce_friction`
- Body: `{"habit": "Complex habit"}`
- Returns: 4-week progression plan

### Habit Tracking
- **POST** `/track_habit`
- Body: `{"habit_name": "...", "completed": true, "date": "2025-06-23"}`
- Returns: Success confirmation

### Habit Adjustment
- **POST** `/adjust_habit`
- Body: `{"habit": "...", "history": [true, false, true, ...]}`
- Returns: Personalized suggestions

## Usage

1. **Goal Decomposition**: Enter a big goal and get AI-powered breakdown into atomic habits
2. **Habit Stacking**: Link new habits to existing routines for better success rates
3. **Track Progress**: Use the tracking interface to log daily habit completion
4. **View Analytics**: Check your dashboard for insights, streaks, and motivation

## File Structure

```
HabitBuilder/
├── app.py                    # Flask backend server
├── habit_builder.py          # Goal decomposition logic
├── habit_stacker.py          # Habit stacking logic
├── reduce_friction.py        # Friction reduction features
├── agent.py                  # AI agent with memory
├── frontend/
│   └── habit-builder-react/  # React frontend
│       ├── src/
│       │   ├── App.js        # Main React component
│       │   ├── App.css       # Modern styling
│       │   └── components/   # React components
│       └── build/            # Production build
└── test_endpoints.py         # API testing script
```

## Development

### Running in Development Mode

1. **Backend**: 
   ```bash
   python app.py
   ```

2. **Frontend** (for development with hot reload):
   ```bash
   cd frontend/habit-builder-react
   npm start
   ```

### Testing
```bash
python test_endpoints.py
```

## Environment Variables

- `DEEPSEEK_API_KEY`: Your DeepSeek API key for AI functionality
- `DEEPSEEK_BASE_URL`: Optional, defaults to "https://api.deepseek.com"

## Future Enhancements

- [ ] User authentication and personal accounts
- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Mobile app (React Native)
- [ ] Social features and accountability partners
- [ ] Advanced analytics and insights
- [ ] Integration with fitness trackers and calendars
- [ ] Gamification elements (points, badges, achievements)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions, please open an issue on GitHub or contact the development team.

---

**Happy Habit Building! 🚀**
