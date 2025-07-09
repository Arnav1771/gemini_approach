import asyncio
import os
from pathlib import Path
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_gemini_connection():
    """Test the Gemini API connection and basic functionality."""
    
    # Check if API key is set
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("Please set your Gemini API key in the .env file")
        return False
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Test text-only model first
        print("Testing text-only model...")
        text_model = genai.GenerativeModel('gemini-pro')
        response = await text_model.generate_content_async("Hello, can you respond with 'API connection successful'?")
        print(f"✅ Text model response: {response.text}")
        
        # Test vision model
        print("\nTesting vision model...")
        vision_model = genai.GenerativeModel('gemini-pro-vision')
        
        # Create a simple test image (colored square)
        test_image = Image.new('RGB', (100, 100), color='red')
        
        vision_response = await vision_model.generate_content_async([
            "What color is this image?", 
            test_image
        ])
        print(f"✅ Vision model response: {vision_response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Gemini API: {str(e)}")
        return False

async def test_graph_analysis():
    """Test the graph analysis functionality with a sample prompt."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return False
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro-vision')
        
        # Create a simple bar chart-like image for testing
        from PIL import Image, ImageDraw
        
        # Create a simple bar chart
        img = Image.new('RGB', (400, 300), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw simple bars
        draw.rectangle([50, 200, 100, 250], fill='blue')   # Jan
        draw.rectangle([120, 180, 170, 250], fill='blue')  # Feb
        draw.rectangle([190, 160, 240, 250], fill='blue')  # Mar
        draw.rectangle([260, 140, 310, 250], fill='blue')  # Apr
        
        # Add simple labels
        draw.text((65, 260), "Jan", fill='black')
        draw.text((135, 260), "Feb", fill='black')
        draw.text((205, 260), "Mar", fill='black')
        draw.text((275, 260), "Apr", fill='black')
        
        prompt = """
        You are an expert data analyst. Analyze the provided chart image.
        Respond in a valid JSON format with the following keys:
        - "chart_type": (e.g., "Line Chart", "Bar Chart", "Pie Chart")
        - "summary": A brief, one-sentence summary of the chart's main point.
        - "trends": A list of key trends or patterns observed.
        - "anomalies": A list of any outliers or unexpected data points.
        - "recommendations": A list of 2-3 actionable business recommendations.
        - "extracted_data": An array of JSON objects representing the data points.
        """
        
        response = await model.generate_content_async([prompt, img])
        print("✅ Graph analysis test completed")
        print("Response:", response.text[:200] + "..." if len(response.text) > 200 else response.text)
        
        return True
        
    except Exception as e:
        print(f"❌ Error in graph analysis test: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Gemini API Integration")
    print("=" * 40)
    
    # Run tests
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Test basic connection
        connection_ok = loop.run_until_complete(test_gemini_connection())
        
        if connection_ok:
            print("\n" + "=" * 40)
            print("🧪 Testing Graph Analysis Functionality")
            analysis_ok = loop.run_until_complete(test_graph_analysis())
            
            if analysis_ok:
                print("\n🎉 All tests passed! The Gemini integration is working correctly.")
            else:
                print("\n⚠️ Graph analysis test failed, but basic connection works.")
        else:
            print("\n❌ Basic connection test failed. Please check your API key.")
    
    finally:
        loop.close()
