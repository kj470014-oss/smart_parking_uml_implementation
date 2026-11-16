# Smart Parking Management System (UML-based)

A small Flask web application based on the classes and relationships in the supplied UML diagram.

## Included files
- `app.py` — Python classes, enums, parking logic, ticket generation and payment handling.
- `templates/index.html` — dashboard page.
- `static/style.css` — page styling and responsive layout.
- `static/script.js` — browser-side form validation and registration number formatting.
- `requirements.txt` — Flask dependency.

## Run in VS Code
1. Install Python 3.10 or later.
2. Extract this ZIP file.
3. Open the extracted `smart_parking_uml_implementation` folder in VS Code.
4. Open Terminal → New Terminal.
5. Create a virtual environment (recommended):
   - Windows: `py -m venv venv`
   - Activate: `venv\Scripts\activate`
6. Install Flask: `pip install -r requirements.txt`
7. Start the app: `python app.py`
8. Open `http://127.0.0.1:5000` in your browser.

## Try the demo
- Register a vehicle such as `KA01AB1234`.
- Select a vehicle type and click **Register vehicle & park**.
- A compatible free spot is assigned and a parking ticket is generated.
- In Active parking tickets, choose the number of hours and Cash/Card, then click **Pay & exit**.
- The ticket is marked paid and the spot becomes available again.

## Notes
- This is an educational prototype. Data is stored in memory and resets when the Python server restarts.
- Login authentication, production-grade payment processing, persistent database storage, and hardware sensors are not included.
- The UML has a separate `ParkingAttendant`, `Admin`, `Account`, panel, payment and display-board concepts. Core domain classes are represented in Python; the page focuses on the main parking workflow.
