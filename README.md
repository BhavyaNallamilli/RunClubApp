# Run Club Web Application

This is a Flask-based web application designed for a local running club. It provides features for managing member profiles, displaying upcoming events, showcasing sports activities, and presenting a dynamic image gallery.

## Features

* **Member Profiles:** View member information, including photos, bios, and social media links.
* **Upcoming Events:** List upcoming running events with details like price, venue, date, and theme.
* **Sports Activities:** Display information about various sports activities offered by the club.
* **Dynamic Image Gallery:** Showcase weekly runs, events, and sports activities through an organized image gallery.
* **SQLite Database:** Uses SQLite for data storage, making it easy to set up and deploy.
* **Responsive Design:** The website is designed to be responsive and work on various screen sizes.

## Technologies Used

* **Python:** The core programming language.
* **Flask:** A micro web framework for building the web application.
* **Flask-SQLAlchemy:** A library for interacting with the database.
* **SQLite:** A lightweight, file-based database.
* **HTML, CSS, JavaScript:** For building the front-end interface.
* **Font Awesome:** For icons.

## Setup Instructions

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/BhavyaNallamilli/RunClubApp.git
    cd RunClubApp
    ```

2.  **Create a Virtual Environment:**

    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment:**

    * **Windows:**

        ```bash
        venv\Scripts\activate
        ```

    * **macOS/Linux:**

        ```bash
        source venv/bin/activate
        ```

4.  **Install Dependencies:**

    ```bash
    pip install Flask Flask-SQLAlchemy
    ```

5.  **Run the Application:**

    ```bash
    python app.py
    ```

6.  **Open in Browser:**

    * Open your web browser and go to `http://127.0.0.1:5000/`.

## Database Setup

* The application uses SQLite as its database. The database file (`runclub.db`) will be created automatically in your project directory when you run the application for the first time.
* Gallery images need to be placed into static/gallery/runs, static/gallery/events, or static/gallery/sports. The application will automatically find and display the images.

## Contributing

Contributions are welcome! If you find a bug or have an idea for a new feature, please open an issue or submit a pull request.


## Author

Bhavya Nallamilli

