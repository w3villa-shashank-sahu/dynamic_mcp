
import os

def get_weather_data():
    """
    Simulates an API request by reading and returning the contents of 'functionStore.txt'.
    """
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, 'functionStore.txt')
        
        with open(file_path, 'r') as file:
            data = file.read()
        return {
            "status": "success",
            "data": data
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "functionStore.txt not found"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

def get_tools_config():
    """
    Loads the tools configuration from 'toolsConfig.txt'.
    """
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, 'toolsConfig.txt')
        
        with open(file_path, 'r') as file:
            data = file.read()
        return {
            "status": "success",
            "data": data
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "toolsConfig.txt not found"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }