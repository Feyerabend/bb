
## Mocking in Python testing

Mocking is a technique used in unit testing to simulate the behavior of
real objects or dependencies in a controlled way. It's commonly used when
the behavior of an external component (like a database, API, or file system)
is not relevant to the unit being tested, or when you want to isolate
the unit from these external components.

In Python, the 'unittest.mock' module is typically used to create mock
objects in unit tests. It allows you to replace parts of your system
under test and control their behavior, track interactions, and verify
that expected methods were called.

### Using the built-in mock framework in Python

Python's unittest.mock is a powerful framework for mocking. Let's walk
through how it works using a simple example.

#### Example: Mocking an external API call

Suppose we have a function that makes an HTTP request to an external API.

```python
import requests

def get_weather(city):
    response = requests.get(f"https://api.weather.com/v3/weather/{city}")
    return response.json()['temperature']
```

In the test, we want to mock the 'requests.get' method
because we don't want to actually hit the API while testing.

Using 'unittest.mock' to mock the 'requests.get' method

```python
import unittest
from unittest.mock import patch
from your_module import get_weather

class TestGetWeather(unittest.TestCase):
    
    @patch('your_module.requests.get')
    def test_get_weather(self, mock_get):
        # mock behavior
        mock_get.return_value.json.return_value = {'temperature': 72}
        
        # call function under test
        result = get_weather("London")
        
        # assert mock was called as expected
        mock_get.assert_called_once_with("https://api.weather.com/v3/weather/London")
        
        # assert correct result was returned
        self.assertEqual(result, 72)
        
if __name__ == '__main__':
    unittest.main()
```

Patch Decorator: The '@patch decorator' is used to replace 'requests.get' with a mock object
during the test. The argument 'your_module.requests.get' is the full path to the method being
mocked. This allows you to mock external functions that are imported within your code.

Mocking return value: The "mock_get.return_value.json.return_value = {'temperature': 72}" line specifies
that when 'mock_get().json()' is called, it will return a dictionary with the key 'temperature' set to 72.
This simulates the API response we want for testing.


Assertions:

* 'mock_get.assert_called_once_with(...)': This checks that the mock object was called exactly
  once with the specified URL.

* 'self.assertEqual(result, 72)': This asserts that the return value from the 'get_weather'
  function is 72, as expected from the mocked response.


#### Example: Simulating a Database Query

Imagine we have a function that queries a database to retrieve user details.
The function interacts with an external database, but for testing purposes,
we want to mock the database call to avoid making real queries.


```python
import sqlite3

def get_user_details(user_id):
    # simulate querying a database to get user details
    connection = sqlite3.connect('mydatabase.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    connection.close()
    return user
```

Now, let's test this function using `unittest.mock` to mock the database call
and simulate a response:

```python
import unittest
from unittest.mock import patch

class TestGetUserDetails(unittest.TestCase):

    @patch('sqlite3.connect')  # patch the sqlite3.connect method
    def test_get_user_details(self, mock_connect):
        # create a mock cursor
        mock_cursor = mock_connect.return_value.cursor.return_value
        
        # mock the return value of fetchone (simulating a database row)
        mock_cursor.fetchone.return_value = (1, 'John Doe', 'john.doe@example.com')

        # call the function we want to test
        user_details = get_user_details(1)

        # assert that the returned result is as expected
        self.assertEqual(user_details, (1, 'John Doe', 'john.doe@example.com'))
        
        # ensure that sqlite3.connect was called correctly
        mock_connect.assert_called_once_with('mydatabase.db')

        # ensure fetchone was called to get the user data
        mock_cursor.fetchone.assert_called_once()

if __name__ == '__main__':
    unittest.main()
```


* "@patch('sqlite3.connect')": We patch the 'sqlite3.connect' method, which is
responsible for creating a database connection. The decorator will replace the
actual method with a mock object for the duration of the test.

We create a mock cursor object using 'mock_connect.return_value.cursor.return_value'.
We simulate that 'fetchone()' (which retrieves a row from the database) returns a
tuple with user details: "(1, 'John Doe', 'john.doe@example.com')".

Assertions:
* We check that the 'get_user_details' function returns the mocked data.
* We verify that 'sqlite3.connect' was called once with the expected argument 'mydatabase.db'.
* We ensure that the 'fetchone()' method was called to simulate retrieving the user.




### Can We Create Our Own Mocking Framework?

Create your own mock framework. Building your own mock framework can be a good learning exercise and
might be useful if you need more customized behavior.


#### Example: Simple mock framework

```python
class CustomMock:
    def __init__(self):
        self._calls = []
        self._return_value = None
    
    def return_value(self, value):
        self._return_value = value
    
    def __call__(self, *args, **kwargs):
        self._calls.append((args, kwargs))
        return self._return_value
    
    def assert_called_with(self, *args, **kwargs):
        assert (args, kwargs) in self._calls, f"Expected call with {args}, {kwargs}, but got {self._calls}"

# example
def fetch_data(url):
    # simulating a function that fetches data from a URL
    return "data from " + url

def process_data(fetch):
    data = fetch("http://example.com")
    return f"Processed {data}"

# create mock for the `fetch` function
mock_fetch = CustomMock()
mock_fetch.return_value("mocked data")

# use mock in the test
result = process_data(mock_fetch)

# test result
print(result)  # process mocked data

# verify mock was called with the expected arguments
mock_fetch.assert_called_with("http://example.com")
```

Using the Mock: In the example, 'fetch_data' is a function that simulates fetching
data from a URL, and 'process_data' processes the fetched data. Instead of calling
the real 'fetch_data', we use a mock object that simulates the return value
"mocked data". This allows us to test 'process_data' without actually making a network
request.


#### Example: Querying a database


```python
class CustomDatabaseMock:
    def __init__(self):
        self._calls = []
        self._return_value = None
    
    def return_value(self, value):
        self._return_value = value
    
    def cursor(self):
        return self  # in reality, this would return a cursor object
    
    def execute(self, query, params):
        self._calls.append(('execute', query, params))  # track query executed
    
    def fetchone(self):
        self._calls.append(('fetchone',))  # track fetchone call
        return self._return_value  # simulate behavior of fetchone
    
    def assert_called(self):
        assert len(self._calls) > 0, "No method was called"
    
    def assert_called_with(self, method, *args):
        assert any(call[0] == method and call[1:] == args for call in self._calls), f"Method {method} was not called with {args}"


# function that queries the database
def get_user_details(user_id, db_connection):
    # querying a database to get user details
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    return user


# test
mock_db = CustomDatabaseMock()
mock_db.return_value((1, 'John Doe', 'john.doe@example.com'))

# mock in the test
user_details = get_user_details(1, mock_db)

# test result
print(user_details)  # output: (1, 'John Doe', 'john.doe@example.com')

# verify mock methods were called with expected arguments
mock_db.assert_called_with('execute', "SELECT * FROM users WHERE id=?", (1,))
mock_db.assert_called_with('fetchone')
```

Using it: We instantiate 'CustomDatabaseMock and set it to return specific data using 'return_value'.
We call 'get_user_details' with our mock, and it behaves as if it's interacting with a real database.
After the function call, we assert that the correct SQL query was executed and that the 'fetchone'
method was called.


### Conclusion

Using 'unittest.mock' is the recommended approach for mocking in Python,
as it provides a robust and well-integrated solution for testing with mock objects.
Building your own mock framework can be an interesting exercise, but the built-in
library already provides a lot of functionality that would be difficult and
time-consuming to replicate, such as patching, method chaining, and assertions.

In practice, creating your own mock framework would only be necessary if you need
a highly specific, tailored mocking system for particular cases that the existing
frameworks don't cover.
