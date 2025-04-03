# Run Club Application

This is a Flask web application for managing a run club, including user registration, event management, gallery features, and UPI payment integration.

## Project Structure

YourProject/
├── running_club/
│   ├── app.py          # Main application initialization
│   ├── models.py       # Database models
│   ├── routes.py       # Flask routes and view functions
│   ├── functions.py    # Helper functions
│   ├── templates/      # HTML templates
│   │   ├── home.html
│   │   ├── login.html
│   │   ├── register.html
│   │   └── ...
│   ├── static/         # Static files (CSS, JavaScript, images)
│   │   ├── style.css
│   │   ├── gallery/
│   │   │   ├── Runs/
│   │   │   ├── Events/
│   │   │   └── Sports/
│   │   ├── profile_photos/
│   │   └── qrcodes/
│   ├── init.py     # Makes running_club a package
├── venv/               # Virtual environment (recommended)
├── README.md           # Project documentation (this file)

## Setup and Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd <project-directory>
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**

    * On Windows:

        ```bash
        venv\Scripts\activate
        ```

    * On macOS/Linux:

        ```bash
        source venv/bin/activate
        ```

4.  **Install dependencies:**

    ```bash
    pip install Flask Flask-SQLAlchemy Flask-Login qrcode Pillow Werkzeug
    ```

5.  **Database Setup:**

    * The application uses SQLite as the database. The `runclub.db` file will be created automatically when the application runs.

6.  **Run the application:**

    ```bash
    python running_club/app.py
    ```

    * The application will be accessible at `http://127.0.0.1:5000/`.

## Features

* **User Registration and Login:**
    * Users can register and log in to the application.
    * Admin users have special privileges.
* **Profile Management:**
    * Users can create and update their profiles.
* **Run, Event, and Sport Management:**
    * Admins can add, view, and manage runs, events, and sports activities.
* **Gallery:**
    * Admins can upload and manage images in the gallery.
    * Images are categorized by Runs, Events, and Sports.
* **Tracker:**
    * Users can track their run participation.
* **UPI Payment Integration:**
    * QR codes for UPI payments are generated for events.
    * Admins can update the UPI ID.
* **Admin-Only Features:**
    * Admin users have access to add/manage content.
    * Admin users can update the UPI payment QR code.

## Database Models

* `User`: Stores user information (username, password, role).
* `Profile`: Stores user profile details (name, photo, DOB, Instagram, bio).
* `Run`: Stores run details (name, week, theme, time, place).
* `Event`: Stores event details (name, price, venue, date, theme).
* `Sport`: Stores sport details (name, venue, price).
* `Gallery`: Stores image paths and categories.
* `UPI`: Stores the UPI ID for payment QR codes.

## Important Notes

* **Virtual Environments:** Using virtual environments is highly recommended to manage project dependencies.
* **Folder Structure:** Ensure that the `running_club` folder and its contents are structured correctly.
* **Database:** The SQLite database file (`runclub.db`) will be created automatically.
* **Static Files:** Make sure static files (CSS, images) are in the `static` directory.
* **Admin Access:** The application uses role-based access control. Only admin users have access to admin features.
* **UPI ID:** Ensure a valid UPI ID is configured for payment QR code generation.

## Author
Bhavya Nallamilli