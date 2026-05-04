# Smart-Task Academic Project Manager
A desktop application designed to help university students manage their academic tasks, deadlines and workload.

## Overview
Smart-Task is a task management application built in Python using Tkinter. It helps organise coursework, track deadlines and prioritise tasks in one place.

The aim of the project is to provide a more structured alternative to basic to-do lists by including features such as filtering, deadline tracking and a dashboard view.

## Features
- Add, update and delete tasks
- Store tasks using a CSV file (data persistence)
- Filter tasks by status, priority and module
- Search tasks by name
- Dashboard summary (total, completed, next deadline)
- Deadline urgency system (red / amber / green)
- Calendar view
- Timer feature

## Setup and Installation

### Prerequisities
- Python 3.10 or above

### Installation
1. Clone the repository:
git clone https://github.com/gabrielafdezk/Software-Engineering_Group-13.git

2. Open the project in VS Code (or any IDE)

## How to Run
Run the main file:
python main.py

## Project Structure
Software-Engineering_Group-13/
-controllers/
---app_controller.py   # Connects UI to data logic
-models/
---tasks_model.py  # Handles data storage and CSV logic
-data/
---tasks.csv   # Stores all task data
-tests/
---test_task_model.py  # Unit tests for model
---test_integration.py # Integration tests
-views/  # UI screens (Tkinter)
-main.py # Launches the application


## Architecture Overview
The project follows a simple Model-View-Controller (MVC) structure:
- Model: TaskModel handles all task data and file storage
- Controller: AppController manages logic between the UI and the model
- View: Tkinter screens built by different team members

This structure ensures that the UI is separated from the data logiv, making the code easier to maintain and extend.

## Testing
Tests are implemented using Python's unittest module.

To run all tests:
python -m unittest discover -s tests -p "test_*.py"

The tests cover:
- Adding, deleting and updating tasks
- Filtering and searching
- CSV saving and loading
- Dashboard summary logiv
- Integration between controller and model

## Known Issues and Limitations
- The UI is still under development and not fully integrated
- Error handling in the UI layer is not complete yet
- Calendar and timer features are not fully implemented

## Contributing
Each team member works on a separate feature branch.

Typical workflow:
- Create a feature branch
- Commit changes
- Push to GitHub
- Open a pull request
- Merge into main

## Team
- Gabriela: Data layer, controller, testing, README
- Rishith: Main task list screen
- Viv: Calendar screen
- Hashem: Add/edit task form and search bar
- Gérson: Sidebar, timer, main app file
