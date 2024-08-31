import streamlit as st
import sqlite3
import google.generativeai as genai
import os
import ast

# Configurer l'API Google Generative AI avec la clé API
genai.configure(api_key=os.getenv("API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# Initialiser les variables de session avec des valeurs par défaut
default_values = {
    'current_index': 0,
    'score': 0,
    'selected_option': None,
    'answer_submitted': False,
    'quiz_data': [],
    'category': None,
    'level': 'easy',  # Définir le niveau initial à 'facile'
    'username': '',
    'logged_in': False,
    'streak': 0,  # Initialiser la séquence à 0
    'prev_question_correct': False  # Initialiser l'état de la question précédente comme incorrect
}

# Parcourir les valeurs par défaut et les ajouter à l'état de session si elles n'existent pas
for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value

def run():
    # Configurer la page de l'application Streamlit
    st.set_page_config(
        page_title="Streamlit Quiz App",
        page_icon="❓",
    )

# Exécuter la fonction run si le script est exécuté directement
if __name__ == "__main__":
    run()

# CSS personnalisé pour centrer les boutons
st.markdown("""
<style>
div.stButton > button:first-child {
    display: block;
    margin: 0 auto;
}
</style>
""", unsafe_allow_html=True)

# Configuration de la base de données SQLite
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        score INTEGER DEFAULT 0
    )
''')
conn.commit()

# Ajouter un nouvel utilisateur à la base de données
def add_user(username, password):
    c.execute('INSERT INTO users (username, password) VALUES (?, ?, ?)', (username, password, 0))
    conn.commit()

# Authentifier un utilisateur en vérifiant son nom d'utilisateur et son mot de passe
def authenticate_user(username, password):
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()
    return user

# Mettre à jour le score d'un utilisateur
def update_score(username, score):
    c.execute('UPDATE users SET score = score + ? WHERE username = ?', (score, username))
    conn.commit()

# Récupérer le classement des utilisateurs
def get_leaderboard():
    c.execute('SELECT username, score FROM users ORDER BY score DESC LIMIT 10')
    return c.fetchall()

# Barre latérale pour la sélection de la catégorie et du niveau
with st.sidebar:
    if st.session_state.logged_in:
        page = st.selectbox("Select Page", ["Game", "Leaderboard"])
    else:
        page = st.selectbox("Select Page", ["Login", "Sign Up"])

# Gestion de la connexion et de l'inscription
if not st.session_state.logged_in:
    if page == "Login":
        st.header("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = authenticate_user(username, password)
            if user:
                st.session_state.username = username
                st.session_state.logged_in = True
                st.success("Login successful!")
            else:
                st.error("Invalid username or password")
    
    elif page == "Sign Up":
        st.header("Sign Up")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        if st.button("Sign Up"):
            try:
                add_user(new_username, new_password)
                st.success("User created successfully!")
            except sqlite3.IntegrityError:
                st.error("Username already exists")

else:
    # Interface principale du jeu
    if page == "Game":
        with st.sidebar:
            st.session_state.category = st.selectbox("Select Category", ["Science", "Literature", "Religion", "Geography", "History"])
        
        # Générer une question à choix multiples (QCM) en arabe en utilisant Google Generative AI
        def generate_mcq():
            prompt = f"""
            In Arabic, generate an MCQ in {st.session_state.category} with a {st.session_state.level} difficulty level.
            The format of the MCQ should be a Python dictionary:
            {{'question':'ما هو شكل الارض','options':['كروي','مسطح','مربع','دائري'],'answer':0}}
            PS: the example is not to be generated, it's just for the format.
            'answer' is the index of the correct answer.
            don't repeat any question !  
            make sure there is 4 options always.
            for easy level try to give question that any middle school kid can solve
            for medium level focus on questions of high schoolers level 
            for hard level give questions that are to specific in the field, that people out of that field can't answer 
            """
            response = model.generate_content(prompt)
            generated_text = response.candidates[0].content.parts[0].text.strip()
            
            # S'assurer que le texte généré est au format dictionnaire attendu
            if generated_text.startswith("{") and generated_text.endswith("}"):
                try:
                    mcq_dict = ast.literal_eval(generated_text)
                    # Valider la structure du dictionnaire généré
                    if all(key in mcq_dict for key in ['question', 'options', 'answer']):
                        if isinstance(mcq_dict['options'], list) and len(mcq_dict['options']) == 4:
                            return mcq_dict
                except (ValueError, SyntaxError):
                    pass
            # Retourner None si le contenu généré n'est pas valide
            return None

        # Récupérer la question suivante
        def fetch_next_question():
            gen_mcq = generate_mcq()
            if gen_mcq:
                st.session_state.quiz_data.append(gen_mcq)

        # Redémarrer le quiz
        def restart_quiz():
            st.session_state.current_index = 0
            st.session_state.score = 0
            st.session_state.selected_option = None
            st.session_state.answer_submitted = False
            st.session_state.quiz_data = []
            st.session_state.streak = 0  # Réinitialiser la séquence
            st.session_state.prev_question_correct = False  # Réinitialiser l'état de la question précédente
            fetch_next_question()

        # Soumettre la réponse sélectionnée
        def submit_answer():
            if st.session_state.selected_option is not None:
                st.session_state.answer_submitted = True
                current_question = st.session_state.quiz_data[st.session_state.current_index]
                correct_answer_index = current_question['answer']
                
                explanation = current_question.get('explanation', 'Explanation not provided.')

                if st.session_state.selected_option == correct_answer_index:
                    st.success(f"صحيح!")
                    st.session_state.score += 1  # Augmenter le score de 1 pour une réponse correcte
                    if st.session_state.prev_question_correct:
                        st.session_state.streak += 1
                    else:
                        st.session_state.streak = 1
                    st.session_state.prev_question_correct = True
                else:
                    correct_answer_text = current_question['options'][correct_answer_index]
                    st.error(f"خطأ! الإجابة الصحيحة هي {correct_answer_text}. {explanation}")
                    st.session_state.score -= 1  # Diminuer le score de 1 pour une réponse incorrecte
                    if st.session_state.streak > 0:
                        st.session_state.streak = 0
                    else:
                        st.session_state.streak -= 1
                    st.session_state.prev_question_correct = False
                    
                # Ajuster le niveau de difficulté en fonction de la séquence
                if st.session_state.level == "easy" and st.session_state.streak >= 1:
                    st.session_state.level = "medium"
                elif st.session_state.level == "hard" and st.session_state.streak <= 0:
                    st.session_state.level = "medium"
                elif st.session_state.level == "medium" and st.session_state.streak >= 2:
                    st.session_state.level = "hard"
                elif st.session_state.level == "medium" and st.session_state.streak <= -1:
                    st.session_state.level = "easy"
            else:
                st.warning("Please select an option before submitting.")

        # Passer à la question suivante
        def next_question():
            st.session_state.current_index += 1
            st.session_state.selected_option = None
            st.session_state.answer_submitted = False
            fetch_next_question()

        # Titre et description
        st.title("AraQuiz App")

        if st.button("Start Quiz"):
            fetch_next_question()

        # Barre de progression
        total_questions = '10'  # Définir le nombre total de questions
        progress_bar_value = st.session_state.current_index / total_questions

        st.metric(label="Score", value=f"{st.session_state.score}")
        st.metric(label="Streak", value=st.session_state.streak)
        st.metric(label="Level", value=st.session_state.level.capitalize())
        st.progress(progress_bar_value)

        # Afficher la question et les options de réponse
        if len(st.session_state.quiz_data) > st.session_state.current_index:
            question_item = st.session_state.quiz_data[st.session_state.current_index]
            st.subheader(f"Question {st.session_state.current_index + 1}")
            st.title(f"{question_item['question']}")
            st.write("")

            st.markdown(""" ___""")

            # Sélection de la réponse
            options = question_item['options']
            correct_answer = question_item['answer']

            if st.session_state.answer_submitted:
                for i, option in enumerate(options):
                    if i == correct_answer:
                        st.success(f"{option} (Correct answer)")
                    elif i == st.session_state.selected_option:
                        st.error(f"{option} (Incorrect answer)")
                    else:
                        st.write(option)
            else:
                for i, option in enumerate(options):
                    if st.button(option):
                        st.session_state.selected_option = i
                        submit_answer()

            st.markdown(""" ___""")

            # Bouton de soumission et logique de réponse
            if st.session_state.answer_submitted:
                if st.session_state.current_index < total_questions - 1:  # Passer à la question suivante jusqu'à ce que 10 questions soient répondues
                    if st.button('Next'):
                        next_question()
                else:
                    st.write(f"Quiz completed! Your score is: {st.session_state.score} / 10")
                    update_score(st.session_state.username, st.session_state.score)
                    if st.button('Restart'):
                        restart_quiz()
            else:
                st.button('Submit', on_click=submit_answer)

    # Afficher le classement
    elif page == "Leaderboard":
        st.title("Leaderboard")
        leaderboard = get_leaderboard()
        for i, (username, score) in enumerate(leaderboard):
            st.write(f"{i+1}. {username} - {score} points")
