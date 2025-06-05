# My Spring Application

This project is a Spring Boot application that interacts with a Python server to provide text-to-speech functionality. The application is structured to handle HTTP requests and communicate with the Python API.

## Project Structure

```
my-spring-app
├── src
│   └── main
│       ├── java
│       │   └── com
│       │       └── example
│       │           └── myapp
│       │               ├── MyAppApplication.java
│       │               ├── controller
│       │               │   └── ApiController.java
│       │               └── service
│       │                   └── TtsService.java
│       └── resources
│           └── application.properties
├── pom.xml
└── README.md
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd my-spring-app
   ```

2. **Build the project:**
   Ensure you have Maven installed, then run:
   ```
   mvn clean install
   ```

3. **Run the application:**
   You can start the Spring Boot application using:
   ```
   mvn spring-boot:run
   ```

4. **Configure the Python server:**
   Make sure your Python server is running and accessible. The Spring application will make HTTP requests to this server for text-to-speech functionality.

## Usage

- The application exposes RESTful endpoints through the `ApiController` class. You can interact with these endpoints to send text to the Python server and receive audio responses.

- The `TtsService` class handles the communication with the Python API, ensuring that requests are properly formatted and responses are handled.

## Dependencies

This project uses Maven for dependency management. The `pom.xml` file includes all necessary dependencies for running a Spring Boot application.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.