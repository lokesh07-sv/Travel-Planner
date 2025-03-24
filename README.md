# AI Travel Planner

An interactive web application that generates personalized travel itineraries using Google's Gemini AI. The application provides detailed travel recommendations including daily itineraries, must-see attractions, accommodation suggestions, and budget estimates.

## Features

- 🌍 Personalized travel recommendations
- 📅 Day-by-day itinerary planning
- 💰 Smart budget calculation and tracking
- 🏨 Accommodation suggestions
- 🍴 Local food recommendations
- 🎯 Must-see attractions with Google Maps integration
- 📥 Downloadable travel plans
- ✨ Interactive UI with animations

## Technologies Used

- Backend: Python, Flask
- Frontend: Vue.js, Tailwind CSS
- AI: Google Gemini API

## Setup

1. Clone the repository:
```bash
git clone [your-repository-url]
cd [repository-name]
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory and add your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to `http://localhost:5000`

## Environment Variables

- `GOOGLE_API_KEY`: Your Google Gemini API key

## Usage

1. Enter your destination
2. Specify number of travelers and duration
3. Add optional trip description
4. Set your budget (manual or automatic)
5. Click "Generate Travel Plan"
6. View and download your personalized itinerary

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

You can test the API key by visiting:
```
http://127.0.0.1:5000/test
```

This will show you a simple test page where you can click the "Test API Key" button to check if your API key is working. The page will show:
1. If the API key is working (Success/Error)
2. The response message from the API
3. A preview of your API key (first 5 characters)

Would you like me to restart the Flask application so you can test it? 