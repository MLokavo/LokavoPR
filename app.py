from flask import Flask, request, jsonify
import json
from method.nearbycompetitors import NearbyCompetitors

app = Flask(__name__)
service = NearbyCompetitors("gmapsapi-c4dca")

headers = {"Content-Type": "application/json",
               "Accept": "application/json"}

@app.route('/competitors_nearby', methods=['POST'])
def competitors_nearby():
    
    try:
        request_json = request.get_json()
        arglatitude = request_json.get("arglatitude")
        arglongitude = request_json.get("arglongitude")
        if arglatitude is None or arglongitude is None:
            response = {
                "status": 400,
                "places": None,
                "message": "Missing JSON parameters 'arglatitude' and/or 'arglongitude'"
            }
            return (json.dumps(response), 400, headers)

        # Add additional data type checks if needed
        if not isinstance(arglatitude, (float)) or not isinstance(arglongitude, (float)):
            response = {
                "status": 400,
                "places": None,
                "message": "'arglatitude' and 'arglongitude' must be float"
            }
            return (json.dumps(response), 400, headers)

        response = service.get_competitors(arglatitude, arglongitude)

        return (json.dumps(response), 200, headers)

    except Exception as e:
        response = {
            "status": 500,
            "places": None,
            "message": "The server encountered an internal error and was unable to complete your request."
        }
        return (json.dumps(response), 500, headers)


@app.route('/competitor_details', methods=['POST'])
def competitor_details():
    
    try:
        request_json = request.get_json()
        argplace_id = request_json.get("argplace_id")
        if argplace_id is None:
            response = {
                "status": 400,
                "details": None,
                "message": "Missing JSON parameters 'argplace_id'"
            }
            return (json.dumps(response), 400, headers)

        response = service.get_competitor_details(argplace_id)

        if response["details"]==[]:
            response = {
                "status": 404,
                "details": None,
                "message": "Not found"
            }
            return (json.dumps(response), 404, headers)

        return (json.dumps(response), 200, headers)

    except Exception as e:
        response = {
            "status": 500,
            "details": None,
            "message": "The server encountered an internal error and was unable to complete your request."
        }
        return (json.dumps(response), 500, headers)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
