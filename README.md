# Install required libraries

In the backend directory, run `pip install -r requirements.txt` to install required libraries.

# Start the server

In the backend directory, run `uvicorn api.main:app --reload`

# Accessing Swagger UI:

Open a web browser and visit:
- http://127.0.0.1:8000/docs
- Swagger UI will provide a user-friendly interface for testing API endpoints

# Create environment variable

- In the backend directory, create a .env file and insert these variables:
`OPENAI_API_KEY=sk-xxxx` (from OpenAI)
`GOOGLE_GEMINI_API_KEY=xxxx` (from Google Gemini API)
`SPELLTRAIN2_DATABASE_URL=sqlite:///./api/spelltrain2.db`

# API Testing

In the backend directory, run `pytest` to test the api endpoints

(Optional) helpful flags for debugging:

- `pytest -v` will print more descriptive information
- `pytest -s` will show all print statements in the program

# Sending HTTP Requests (Axios Example):

- await axios.get(`http://{your_ip}:8000/`).then((res) => {console.log(res.data);});

- Windows:
  - Open CMD and type `ipconfig`. (Mac: `ifconfig`)
  - Copy the IPv4 address of your machine.
  - Replace `{your_ip}` by the IP address of your machine
- Mac:
  - Replace `{your_ip}` by `localhost`
  - If it doesn't work, follow the same steps as Windows to find your IP address.

For example, await axios.get(`http://192.168.1.5:8000/`).then((res) => {console.log(res.data);});
