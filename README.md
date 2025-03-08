# PR_Logger
#### Video Demo:  <URL HERE>
#### Description:
PR Logger is a web application designed to manage purchase request (PR) forms. The application allows users to create, view, revise, and track revisions of PRs. It is built using Flask as the web framework and SQLite as the database. The application also supports session management and is configured to be deployed on Railway using a `nixpacks.toml` file.

## Motivation
At my previous workplace, purchase requests were handled using Excel, which was tedious and inefficient. For instance, assigning a PR number required manually checking the last number and adding one, often leading to mistakes where two requests shared the same number.

Formatting issues were another challenge—adding a new row would break the layout, requiring formulas to be manually reapplied. Additionally, there was no centralized system to track purchase requests; they were stored in folders, sometimes misplaced, renamed, or even accidentally deleted.

Revisions were even more frustrating. Since everything was done locally in Excel, updates weren’t automatically shared, leading to inconsistencies across the organization. When a request needed revision, we had to recreate it from scratch before converting it to PDF, resulting in unnecessary redundancy.

This project was created to eliminate these inefficiencies, streamline the process, and ensure accuracy and consistency.

## Features

### Home Page
- **Welcome Message**: Displays a welcome message to the user.
- **Create New PR Button**: A button that redirects the user to the form for creating a new PR.
- **PR Logs Table**: Displays a table of all PR logs with details such as PR number, title, currency, total cost, budget line, creation date, and action buttons for viewing or toggling the status of the PR.

### Create PR
- **Form for Creating PR**: A form that allows users to enter details for a new PR, including PR number, title, currency, budget line, creation date, and entries for description, cost, quantity, and total.
- **Add New Row Button**: A button that allows users to add new rows to the PR entries table.
- **Submit Button**: A button to submit the new PR to the database.
- **Cancel Button**: A button to cancel the creation of the PR and return to the home page.

### View PR
- **PR Details**: Displays the details of a selected PR, including PR number, title, currency, budget line, creation date, and entries for description, cost, quantity, and total.
- **Revise Button**: A button that allows users to revise the selected PR if it has not been deleted.
- **Current Version Button**: A button that allows users to view the current version of the PR if revisions exist.
- **Revisions Table**: Displays a table of all revisions made to the selected PR with timestamps.

### Revise PR
- **Form for Revising PR**: A form that resembles PR creation form, which allows users to revise the details of an existing PR, including PR number, title, currency, budget line, creation date, and entries for description, cost, quantity, and total.
- **Add New Row Button**: A button that allows users to add new rows to the PR entries table.
- **Update Button**: A button to submit the revised PR to the database.
- **Cancel Button**: A button to cancel the revision of the PR and return to the home page.

### Toggle PR Status
- **Delete/Restore PR**: Allows users to delete or restore a PR. Deleted PRs are marked in red and can be restored if the button is clicked again.

### View Revision
- **Revision Details**: Displays the details of a selected revision, including PR number, title, currency, budget line, creation date, and entries for description, cost, quantity, and total.
- **Current Version Button**: A button that allows users to view the current version of the PR.

## Files

### `app.py`
- **Flask Application**: Initializes the Flask application and configures session management and the SQLite database.
- **Routes**: Defines routes for the home page, creating PR, viewing PR, revising PR, updating PR, toggling PR status, viewing revision, and canceling actions.
- **Database Operations**: Handles database operations for inserting, updating, and retrieving PR logs and entries.

### `helpers.py`
- **Helper Functions**: Contains helper functions for interacting with the database, including functions to get PR logs, get PR details, get PR entries, get new PR number, get form data, and get PR revisions.

### `templates/index.html`
- **Home Page Template**: Defines the HTML structure for the home page, including the welcome message, create new PR button, and PR logs table.

### `templates/layout.html`
- **Layout Template**: Defines the base HTML layout for all pages, including the header, footer, and main content area.

### `templates/process_pr_form.html`
- **PR Form Template**: Defines the HTML structure for the form used to create or revise a PR, including input fields for PR details and entries, and buttons for adding rows, submitting, and canceling.

### `templates/view_pr.html`
- **View PR Template**: Defines the HTML structure for viewing the details of a PR, including the PR log, entries, and revisions.

### `static/script.js`
- **JavaScript Functions**: Contains JavaScript functions for handling dynamic behavior on the PR form, such as adding and deleting rows, calculating totals, and updating indexes.

### `static/styles.css`
- **CSS Styles**: Contains CSS styles for the application, including styles for buttons and tables.

### `requirements.txt`
- **Dependencies**: Lists the Python dependencies required for the application, including Flask, Flask-Session, CS50, and others.

### `nixpacks.toml`
- **Deployment Configuration**: Contains configuration for deploying the application on Railway using Nixpacks.

### `.gitignore`
- **Git Ignore File**: Specifies files and directories to be ignored by Git, including the PR logger, Flask session, and `__pycache__`.

## How to Operate Locally

1. **Clone the Repository**: Clone this repository to your local machine.
2. **Install Dependencies**: Install the required dependencies by running:
    ```sh
    pip install -r requirements.txt
    ```
3. **Run Flask**: Start the Flask application by running:
    ```sh
    python -m flask --app ./app.py run
    ```

## Deployment

To deploy the application on Railway, follow these steps:

1. **Visit Railway**: Go to [Railway](https://railway.com/).
2. **Deploy the Application**: Use the `nixpacks.toml` file to configure and deploy the application on Railway.

## Design Choices

1 - Revision Panel
The biggest obstacle in the entire project was the revisions panel.
Had to be written on paper and followed by step by step in order aquire the prefered user-friendly outcome.
One of the two design choices were to be used. Either that each time a revision timestamp was clicked, the differences would be compared and presented. Or the second, which was to log the differences at the time of revision submission into the database.
The first choice takes less storage but processes slower. The second choice would be vise versa. The second was chosen due to faster processing would be more optimal since storage isn't much of an issue for a small sized column.

2 - Delete / Restore button in homepage
Instead of deleting the PR from the database directly, it was chosen that it would instead be strikethrough to present it being deleted. And to be restored when toggled back. This is to show the project more clearly and it soleley depends on the client's preference.

-PRs cannot be revised while deleted.-

3 - PR. no
PR numbers are automatically assigned and cannot be edited in order to preserve unique identification.

## Conclusion

PR Logger fixes all the issues discussed in the project motivation. And in the future, we can enhance it by adding authentication, digital signatures, and integrating multiple apps like this into a unified ERP system. Additionally, we can optimize the design for mobile use.

This was CS50.