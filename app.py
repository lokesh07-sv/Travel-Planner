from flask import Flask, render_template, request, jsonify, send_file, make_response
import google.generativeai as genai
import os
from dotenv import load_dotenv
import traceback
from io import BytesIO
from datetime import datetime
import re

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

try:
    # Initial API configuration test
    genai.configure(api_key=GOOGLE_API_KEY)
    # List available models to verify API key works
    model_list = genai.list_models()
    print("Available models:", [m.name for m in model_list])
except Exception as e:
    print(f"Error configuring API: {str(e)}")
    raise

# Initialize Flask app with additional configuration
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Add error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal Server Error'}), 500

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response

def test_api_key():
    try:
        # Configure Gemini
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('models/gemini-1.5-pro')
        
        # Try a simple test prompt
        response = model.generate_content(
            "Respond with 'API test successful' if you can read this message.",
            generation_config={'temperature': 0.1}
        )
        
        if response and response.text:
            return True, response.text
        return False, "No response from API"
    except Exception as e:
        error_msg = f"API Test Error: {str(e)}"
        print(error_msg)
        print(f"Full traceback: {traceback.format_exc()}")
        return False, error_msg

def get_travel_recommendations(destination, num_people, num_days, description, start_date=None, end_date=None):
    try:
        # Configure Gemini
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('models/gemini-1.5-pro')
        
        # Add date information to the prompt if available
        date_info = ""
        if start_date and end_date:
            date_info = f"\nTravel dates: From {start_date} to {end_date}"
        
        prompt = f"""
        Create a detailed {num_days}-day travel guide for {destination} for {num_people} {'person' if num_people == 1 else 'people'}.{date_info}
        Trip details: {description}

        Format the response with the following sections, using exact headers:

        1. Daily Itinerary
        For each day, use this format:
        Day X (include actual date if provided)
        • Morning (9:00): Activity/Place
        • Afternoon (14:00): Activity/Place
        • Evening (19:00): Activity/Place
        Include [Location Name](maps) for each place mentioned.

        2. Must-See Attractions
        List key attractions with their exact Google Maps names:
        • [Attraction Name](maps) - Brief description
        • [Attraction Name](maps) - Brief description

        3. Where to Stay
        • Recommended areas: [District/Area Name](maps)
        • Specific hotel suggestions in each area
        • Price ranges per night

        4. Best Time to Visit
        • Seasonal recommendations
        • Weather considerations
        • Special events or festivals

        5. Local Food to Try
        • Must-try dishes
        • [Restaurant/Food District Name](maps) - Specialties
        • Price ranges for meals

        6. Cultural Tips
        • Local customs
        • Etiquette guidelines
        • Important phrases

        7. How to Get Around
        • Public transportation options
        • [Transportation Hub Names](maps)
        • Cost estimates for different modes

        8. Budget Estimate
        • Accommodation: Price range
        • Daily meals: Price range
        • Activities: Price range
        • Transportation: Price range
        • Total estimated budget

        Keep it practical and organized with bullet points.
        For each location mentioned, use the exact name as it would appear on Google Maps using the [Name](maps) format.
        Consider the specific dates when suggesting activities and making recommendations.
        """
        
        print(f"Requesting travel plan for: {destination}")
        response = model.generate_content(
            prompt,
            generation_config={'temperature': 0.7}
        )
        
        if not response or not response.text:
            raise Exception("No response received from API")
            
        # Process the response to add Google Maps links
        processed_text = response.text
        
        def add_maps_link(match):
            location = match.group(1)
            encoded_location = location.replace(' ', '+')
            return f'<a href="https://www.google.com/maps/search/?api=1&query={encoded_location}" target="_blank" class="text-blue-600 hover:text-blue-800 underline">{location}</a>'
        
        # Replace [Location](maps) format with actual links
        processed_text = re.sub(r'\[(.*?)\]\(maps\)', add_maps_link, processed_text)
            
        print("Successfully generated travel plan")
        return processed_text

    except Exception as e:
        error_msg = f"Error generating recommendations: {str(e)}"
        print(error_msg)
        print(f"Full traceback: {traceback.format_exc()}")
        raise Exception(error_msg)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/test')
def test_page():
    return render_template('test.html')

@app.route('/test_api')
def test_api():
    success, message = test_api_key()
    return jsonify({
        'success': success,
        'message': message,
        'api_key_preview': f"{GOOGLE_API_KEY[:5]}..." if GOOGLE_API_KEY else "No API key found"
    })

@app.route('/get_recommendations', methods=['POST'])
def recommendations():
    try:
        data = request.get_json()
        print(f"Received request data: {data}")
        
        destination = data.get('destination')
        num_people = int(data.get('numPeople', 1))
        num_days = int(data.get('numDays', 1))
        description = data.get('description', '')
        start_date = data.get('startDate')
        end_date = data.get('endDate')

        if not destination:
            return jsonify({'error': 'Please enter a destination'}), 400
        
        if num_people < 1:
            return jsonify({'error': 'Number of people must be at least 1'}), 400
            
        if num_days < 1:
            return jsonify({'error': 'Number of days must be at least 1'}), 400
        
        print(f"Planning trip: {destination}, {num_people} people, {num_days} days, from {start_date} to {end_date}")
        travel_info = get_travel_recommendations(
            destination, 
            num_people, 
            num_days, 
            description,
            start_date,
            end_date
        )
        
        if not travel_info:
            return jsonify({'error': 'Could not generate travel plan'}), 500
            
        return jsonify({
            'recommendations': travel_info
        })
    except Exception as e:
        error_msg = str(e)
        print(f"Error: {error_msg}")
        return jsonify({'error': error_msg}), 500

@app.route('/download_plan', methods=['POST'])
def download_plan():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        content = data.get('content', '')
        destination = data.get('destination', 'Travel')
        budget_info = data.get('budgetInfo', {})
        budget_mode = data.get('budgetMode', 'auto')
        
        # Format the content with additional details
        formatted_content = f"""
===========================================
Travel Plan for {destination}
===========================================

BUDGET OVERVIEW
-------------------------------------------
Budget Mode: {'Manual' if budget_mode == 'manual' else 'Automatic'} Calculation
Total Budget: ${budget_info.get('totalBudget', 0):,.2f}
Daily Average: ${budget_info.get('dailyAverage', 0):,.2f}
Per Person: ${budget_info.get('perPerson', 0):,.2f}

DAILY BREAKDOWN
-------------------------------------------
{content}

-------------------------------------------
Generated by AI Travel Planner
Date Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
===========================================
"""
        
        # Create a safe filename
        safe_filename = "".join(c for c in destination if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_filename}_travel_plan.txt"
        
        # Create response with the formatted content
        response = make_response(formatted_content)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
        
        return response
    
    except Exception as e:
        print(f"Download error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    try:
        print("Starting Flask server...")
        app.run(
            debug=False,
            host='0.0.0.0',  # Allow external connections
            port=int(os.environ.get('PORT', 5000)),
            use_reloader=False,
            threaded=True    # Enable threading
        )
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        print(traceback.format_exc()) 