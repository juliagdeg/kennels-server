# add this import to the top of the file
from urllib.parse import urlparse, parse_qs
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from views import get_all_animals, get_single_animal, create_animal, delete_animal, update_animal, get_animal_by_location, get_animal_by_status
from views import get_all_locations, get_single_location, create_location, delete_location, update_location
from views import get_all_employees, get_single_employee, create_employee, delete_employee, update_employee
from views import get_all_customers, get_single_customer, create_customer, delete_customer, update_customer, get_customers_by_email


method_mapper = {
    "animals": {
        "all": get_all_animals,
        "single": get_single_animal
    },
    "locations": {
        "all": get_all_locations,
        "single": get_single_location
    },
    "employees": {
        "all": get_all_employees,
        "single": get_single_employee
    },
    "customers": {
        "all": get_all_customers,
        "single": get_single_customer
    }
}

# Here's a class. It inherits from another class.
# For now, think of a class as a container for functions that
# work together for a common purpose. In this case, that
# common purpose is to respond to HTTP requests from a client.
class HandleRequests(BaseHTTPRequestHandler):
    # This is a Docstring it should be at the beginning of all classes and functions
    # It gives a description of the class or function
    """Controls the functionality of any GET, PUT, POST, DELETE requests to the server
    """
    def get_all_or_single(self, resource, id):
        if id is not None:
            response = method_mapper[resource]["single"](id)

            if response is not None:
                self._set_headers(200)
            else:
                self._set_headers(404)
                response = ''
        else:
            self._set_headers(200)
            response = method_mapper[resource]["all"]()

        return response
    # Here's a class function

    # Here's a method on the class that overrides the parent's method.
    # It handles any GET request.
    # def do_GET(self):
    #     response = None
    #     (resource, id) = self.parse_url(self.path)
    #     response = self.get_all_or_single(resource, id)
    #     self.wfile.write(json.dumps(response).encode())
    def do_GET(self):
        self._set_headers(200)

        response = {}

        # Parse URL and store entire tuple in a variable
        parsed = self.parse_url(self.path)

        # If the path does not include a query parameter, continue with the original if block
        if '?' not in self.path:
            ( resource, id ) = parsed

            if resource == "animals":
                if id is not None:
                    response = get_single_animal(id)
                else:
                    response = get_all_animals()
            elif resource == "customers":
                if id is not None:
                    response = get_single_customer(id)
                else:
                    response = get_all_customers()

        else: # There is a ? in the path, run the query param functions
            (resource, query) = parsed

            # see if the query dictionary has an email key
            if query.get('email') and resource == 'customers':
                response = get_customers_by_email(query['email'][0])

            if query.get('location_id') and resource == 'animals':
                response = get_animal_by_location(query['location_id'][0])

            if query.get('status') and resource == 'animals':
                response = get_animal_by_status(query['status']["Treatment"])

        self.wfile.write(json.dumps(response).encode())

    # Here's a method on the class that overrides the parent's method.
    # It handles any POST request.
    def do_POST(self):
        self._set_headers(201)
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)

        # Convert JSON string to a Python dictionary
        post_body = json.loads(post_body)

        # Parse the URL/ says "id" is unused but Postman still created object
        (resource, id) = self.parse_url(self.path)

        # Initialize new animal
        new_animal = None

        # Add a new animal to the list. Don't worry about
        # the orange squiggle, you'll define the create_animal
        # function next.
        if resource == "animals":
            new_animal = create_animal(post_body)

        # Encode the new animal and send in response
        self.wfile.write(json.dumps(new_animal).encode())

        # initialize the new location
        new_location = None

        # this adds the new location to the list (post to body)
        if resource == "locations":
            new_location = create_location(post_body)
            if "name" in post_body and "address" in post_body:
                self._set_headers(201)
                created_resource = create_location(post_body)
            else:
                self._set_headers(400)
                created_resource = {"message": f'{"name is required" if "name" not in post_body else ""} {"address is required" if "address" not in post_body else ""}'}

        self.wfile.write(json.dumps(new_location).encode())
        self.wfile.write(json.dumps(created_resource).encode())

        new_employee = None

        if resource == "employees":
            new_employee = create_employee(post_body)

        self.wfile.write(json.dumps(new_employee).encode())

        new_customer = None

        # don't forget the double equals for if statement
        if resource == "customers":
            new_customer = create_customer(post_body)

        self.wfile.write(json.dumps(new_customer).encode())

    def do_DELETE(self):
        # Set a 204 response code
        self._set_headers(204)

        # Parse the URL
        (resource, id) = self.parse_url(self.path)

        # Delete a single animal from the list
        if resource == "animals":
            delete_animal(id)

        # Encode the new animal and send in response
        self.wfile.write("".encode())

        if resource == "employees":
            delete_employee(id)

        self.wfile.write("".encode())

        if resource == "locations":
            delete_location(id)

        self.wfile.write("".encode())

        if resource == "customers":
            delete_customer(id)


        self.wfile.write("".encode())
        # A method that handles any PUT request.


    def do_PUT(self):
        self._set_headers(204)
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        post_body = json.loads(post_body)

    # Parse the URL
        (resource, id) = self.parse_url(self.path)

        success = False

    # Delete a single animal from the list
        if resource == "animals":
            success = update_animal(id, post_body)

        if success:
            self._set_headers(204)
        else:
            self._set_headers(404)

    # Encode the new animal and send in response
        self.wfile.write("".encode())

        # if resource == "locations":
        #     update_location(id, post_body)

        # self.wfile.write("".encode())

        # if resource == "employees":
        #     update_employee(id, post_body)

        # self.wfile.write("".encode())

        # if resource == "customers":
        #     update_customer(id, post_body)

        # self.wfile.write("".encode())

    def _set_headers(self, status):
        # Notice this Docstring also includes information about the arguments passed to the function
        """Sets the status code, Content-Type and Access-Control-Allow-Origin
        headers on the response

        Args:
            status (number): the status code to return to the front end
        """
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    # Another method! This supports requests with the OPTIONS verb.
    def do_OPTIONS(self):
        """Sets the options headers
        """
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type, Accept')
        self.end_headers()

    # replace the parse_url function in the class
    def parse_url(self, path):
        """Parse the url into the resource and id"""
        parsed_url = urlparse(path)
        path_params = parsed_url.path.split('/')  # ['', 'animals', 1]
        resource = path_params[1]

        if parsed_url.query:
            query = parse_qs(parsed_url.query)
            return (resource, query)

        pk = None
        try:
            pk = int(path_params[2])
        except (IndexError, ValueError):
            pass
        return (resource, pk)


# This function is not inside the class. It is the starting
# point of this application.
def main():
    """Starts the server on port 8088 using the HandleRequests class
    """
    host = ''
    port = 8088
    HTTPServer((host, port), HandleRequests).serve_forever()


if __name__ == "__main__": # double underscore file demarcation ?
    main() # this function basically tells python to run
    # this FIRST (kind of like querySelector maybe?)
