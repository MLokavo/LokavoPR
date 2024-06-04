from google.cloud import bigquery
import json

class NearbyCompetitors:
    def __init__(self, project_id):
        self.client = bigquery.Client(project_id)
    
    def get_competitors(self, arglatitude, arglongitude):
        count_of_places = self.query_count_of_places(arglatitude, arglongitude)

        if count_of_places < 30:
            return self.not_enough_competitors_response(count_of_places)

        rows = self.query_competitors(arglatitude, arglongitude)

        return {
            "status": 200,
            "count": count_of_places,
            "places": rows
        }
        
    def get_competitor_details(self, argplace_id):
        # Define the query with parameter placeholders
        query = '''
          SELECT *
          FROM `gmapsapi-c4dca.gmapsdata90.PLACE v4`
          WHERE place_id = @argplace_id;
        '''

        # Configure the query with parameters
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("argplace_id", "STRING", argplace_id),
            ]
        )

        # Execute the query
        query_job = self.client.query(query, job_config=job_config)
        results = query_job.result()

        rows = []
        for row in results:
            row_dict = dict(row)
            
            # Correct the coordinates field
            row_dict['coordinates'] = json.loads(row_dict['coordinates'])

            # Correct the categories field
            row_dict['categories'] = json.loads(row_dict['categories'])

            # Correct the most_popular_times field
            if row_dict['most_popular_times'] is not None:
                row_dict['most_popular_times'] = json.loads(row_dict['most_popular_times'])
            
            # Correct the reviews_per_rating field
            row_dict['reviews_per_rating'] = json.loads(row_dict['reviews_per_rating'])

            rows.append(row_dict)

        # Construct the final response
        response = {
            "status": 200,
            "details": rows
        }

        return response

    def query_count_of_places(self, arglatitude, arglongitude):
        count_query = '''
        CREATE TEMP FUNCTION RADIANS(x FLOAT64) AS (
            ACOS(-1) * x / 180
        );

        WITH distances AS (
            SELECT place_id,
                (6371 * ACOS(COS(RADIANS(@arglatitude)) * COS(RADIANS(CAST(JSON_EXTRACT(coordinates, '$.latitude') AS FLOAT64))) * COS(RADIANS(CAST(JSON_EXTRACT(coordinates, '$.longitude') AS FLOAT64)) - RADIANS(@arglongitude)) + SIN(RADIANS(@arglatitude)) * SIN(RADIANS(CAST(JSON_EXTRACT(coordinates, '$.latitude') AS FLOAT64))))) AS distance
            FROM `gmapsapi-c4dca.gmapsdata90.PLACE v4`
        )
        SELECT COUNT(*) AS count_of_places_within_4km
        FROM distances
        WHERE distance <= 4;
        '''

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("arglatitude", "FLOAT64", arglatitude),
                bigquery.ScalarQueryParameter("arglongitude", "FLOAT64", arglongitude),
            ]
        )

        count_query_job = self.client.query(count_query, job_config=job_config)
        count_results = count_query_job.result()
        count_row = list(count_results)[0]
        count_of_places = count_row["count_of_places_within_4km"]

        return count_of_places

    def query_competitors(self, arglatitude, arglongitude):
        main_query = '''
        CREATE TEMP FUNCTION RADIANS(x FLOAT64) AS (
            ACOS(-1) * x / 180
        );

        WITH distances AS (
            SELECT place_id, coordinates, top_average_popularity, main_category,
                (6371 * ACOS(COS(RADIANS(@arglatitude)) * COS(RADIANS(CAST(JSON_EXTRACT(coordinates, '$.latitude') AS FLOAT64))) * COS(RADIANS(CAST(JSON_EXTRACT(coordinates, '$.longitude') AS FLOAT64)) - RADIANS(@arglongitude)) + SIN(RADIANS(@arglatitude)) * SIN(RADIANS(CAST(JSON_EXTRACT(coordinates, '$.latitude') AS FLOAT64))))) AS distance
            FROM `gmapsapi-c4dca.gmapsdata90.PLACE v4`
        )
        SELECT place_id, coordinates, top_average_popularity, main_category
        FROM distances
        WHERE distance <= 4
        ORDER BY top_average_popularity DESC 
        LIMIT 50;
        '''

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("arglatitude", "FLOAT64", arglatitude),
                bigquery.ScalarQueryParameter("arglongitude", "FLOAT64", arglongitude),
            ]
        )

        main_query_job = self.client.query(main_query, job_config=job_config)
        results = main_query_job.result()

        rows = []
        for row in results:
            row_dict = dict(row)
            row_dict['coordinates'] = json.loads(row_dict['coordinates'])
            rows.append(row_dict)

        return rows

    def not_enough_competitors_response(self, count_of_places):
        return {
            "status": 4001,
            "count": count_of_places,
            "places": None,
            "message": "Not enough competitors in the area to conduct the analysis"
        }


    def get_competitors_data(self, arglatitude, arglongitude):
        pass
