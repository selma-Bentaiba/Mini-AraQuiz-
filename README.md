# AraQuiz App

AraQuiz is an Arabic adaptive quiz application built using Streamlit and Google Generative AI GEMINI, designed to generate multiple-choice questions (MCQs) in Arabic across various categories. The app includes user authentication, a leaderboard, and adaptive difficulty levels based on user performance.

## Features

- **User Authentication**: Users can sign up and log in to save their progress and compete on the leaderboard.
- **Category Selection**: Users can choose from categories like Science, Literature, Religion, Geography, and History.
- **Adaptive Difficulty**: The difficulty level adjusts based on the user's performance (streak of correct answers).
- **Leaderboard**: Displays the top users based on their scores.
- **Arabic MCQs**: Generates multiple-choice questions in Arabic using Google Generative AI.

## Technologies Used

- **Streamlit**: For the front-end interface.
- **SQLite**: To store user information and scores.
- **Google Generative AI**: For generating Arabic multiple-choice questions.

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/araquiz-app.git
    cd araquiz-app
    ```

2. **Install the required packages:**

    Ensure you have Python installed, then run:

    ```bash
    pip install -r requirements.txt
    ```

3. **Set up the API Key:**

    Create a `.env` file in the root directory of your project and add your Google Generative AI API key:

    ```bash
    export API_KEY= your_google_api_key_here
    ```

4. **Run the application:**

    ```bash
    streamlit run app.py
    ```

## Usage

1. **Sign Up/Login**: New users can sign up, and returning users can log in to start or continue a quiz.
2. **Select a Category**: Choose a quiz category from the sidebar.
3. **Answer Questions**: Questions will be displayed one by one. Choose the correct answer to score points.
4. **Leaderboard**: Check the top scores on the leaderboard page.

>>>>>>> master
