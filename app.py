import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import uuid

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Gestionnaire de Projets Pro", page_icon="🚀", layout="wide")

# --- INITIALISATION DES DONNÉES ---
if "projects" not in st.session_state:
    st.session_state.projects = ["Projet Alpha"]
if "categories" not in st.session_state:
    st.session_state.categories = ["Développement", "Design", "Marketing", "Administratif"]
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "editing_task_id" not in st.session_state:
    st.session_state.editing_task_id = None

# --- FONCTIONS UTILITAIRES ---
def add_task(project, category, name, desc, tools, priority, start_date, deadline, people, color):
    st.session_state.tasks.append({
        "id": str(uuid.uuid4()),
        "project": project,
        "category": category,
        "name": name,
        "description": desc,
        "tools": tools,
        "priority": priority,
        "start_date": start_date,
        "deadline": deadline,
        "people": people,
        "color": color,
        "status": "En cours",
        "comment": "",
        "file_name": None,
        "file_data": None
    })

def delete_task(task_id):
    st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task_id]

def get_priority_badge(level):
    badges = {
        1: "🔴 **P1 (Critique)**",
        2: "🟠 **P2 (Haute)**",
        3: "🟡 **P3 (Moyenne)**",
        4: "🟢 **P4 (Basse)**"
    }
    return badges.get(level, "⚪")

# --- INTERFACE UTILISATEUR ---
st.title("🚀 Mon Espace Projets")

menu = st.sidebar.radio("Navigation", ["📋 Gestion des Tâches", "📊 Dashboard (Avancement)", "📅 Diagramme de Gantt"])

st.sidebar.markdown("---")
st.sidebar.subheader("Configuration")
new_project = st.sidebar.text_input("Nouveau Projet")
if st.sidebar.button("Ajouter Projet") and new_project:
    if new_project not in st.session_state.projects:
        st.session_state.projects.append(new_project)
        st.sidebar.success(f"Projet '{new_project}' ajouté !")

new_cat = st.sidebar.text_input("Nouvelle Catégorie")
if st.sidebar.button("Ajouter Catégorie") and new_cat:
    if new_cat not in st.session_state.categories:
        st.session_state.categories.append(new_cat)
        st.sidebar.success(f"Catégorie '{new_cat}' ajoutée !")

# ==========================================
# VUE 1 : GESTION DES TÂCHES
# ==========================================
if menu == "📋 Gestion des Tâches":
    st.header("Gestion des Tâches")
    
    # Formulaire d'ajout
    with st.expander("➕ Créer une nouvelle tâche", expanded=False):
        with st.form("new_task_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                t_project = st.selectbox("Projet", st.session_state.projects)
                t_name = st.text_input("Nom de la tâche")
                t_tools = st.text_input("Outils nécessaires")
            with col2:
                t_category = st.selectbox("Catégorie", st.session_state.categories)
                t_priority = st.selectbox("Priorité (1 = max, 4 = min)", [1, 2, 3, 4])
                t_people = st.text_input("Personnes concernées")
            with col3:
                t_start = st.date_input("Date de début", datetime.date.today())
                t_deadline = st.date_input("Date butoir", datetime.date.today() + datetime.timedelta(days=7))
                t_color = st.color_picker("Couleur dans le Gantt", "#007bff")
            
            t_desc = st.text_area("Description")
            
            if st.form_submit_button("Enregistrer la tâche"):
                if t_name:
                    add_task(t_project, t_category, t_name, t_desc, t_tools, t_priority, t_start, t_deadline, t_people, t_color)
                    st.success("Tâche ajoutée avec succès !")
                    st.rerun()
                else:
                    st.error("Le nom de la tâche est obligatoire.")

    st.markdown("---")
    
    # Filtres
    f_project = st.selectbox("Filtrer par projet", ["Tous"] + st.session_state.projects)
    tasks_to_display = [t for t in st.session_state.tasks if f_project == "Tous" or t["project"] == f_project]
    
    if not tasks_to_display:
        st.info("Aucune tâche à afficher pour le moment.")
    else:
        for t in tasks_to_display:
            # Mode Édition
            if st.session_state.editing_task_id == t["id"]:
                st.markdown(f"### ✏️ Modification de : {t['name']}")
                with st.form(f"edit_form_{t['id']}"):
                    e_name = st.text_input("Nom", t['name'])
                    e_desc = st.text_area("Description", t['description'])
                    e_tools = st.text_input("Outils", t['tools'])
                    e_people = st.text_input("Personnes", t['people'])
                    e_color = st.color_picker("Couleur Gantt", t.get('color', '#007bff'))
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.form_submit_button("💾 Sauvegarder"):
                            t['name'], t['description'], t['tools'], t['people'], t['color'] = e_name, e_desc, e_tools, e_people, e_color
                            st.session_state.editing_task_id = None
                            st.rerun()
                    with c2:
                        if st.form_submit_button("❌ Annuler"):
                            st.session_state.editing_task_id = None
                            st.rerun()
                continue # Passe à la tâche suivante sans afficher la vue normale

            # Calcul des alertes
            days_left = (t["deadline"] - datetime.date.today()).days
            is_urgent = (0 <= days_left < 4) and t["status"] != "Terminé"
            is_overdue = days_left < 0 and t["status"] != "Terminé"
            
            bg_color = "#ffe6e6" if is_urgent or is_overdue else "transparent"
            border_color = "red" if is_urgent or is_overdue else "#ddd"
            
            with st.container():
                st.markdown(f"""
                    <div style="background-color: {bg_color}; border: 1px solid {border_color}; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                        <h4 style="margin:0;">{t['name']} <span style="font-size: 0.8em; font-weight: normal;">({t['status']})</span></h4>
                    </div>
                """, unsafe_allow_html=True)
                
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                with c1:
                    st.write(f"**Description:** {t['description']}")
                    st.write(f"**Outils:** {t['tools']} | **Équipe:** {t['people']}")
                with c2:
                    st.write(f"**Catégorie:** {t['category']}")
                    st.write(f"**Priorité:** {get_priority_badge(t['priority'])}")
                with c3:
                    st.write(f"**Début:** {t['start_date']}")
                    if is_overdue:
                        st.error(f"**Échéance:** {t['deadline']} (Retard!)")
                    elif is_urgent:
                        st.warning(f"**Échéance:** {t['deadline']} (J-{days_left})")
                    else:
                        st.write(f"**Échéance:** {t['deadline']}")
                with c4:
                    if st.button("✏️ Modifier", key=f"edit_{t['id']}"):
                        st.session_state.editing_task_id = t["id"]
                        st.rerun()
                    if st.button("🗑️ Supprimer", key=f"del_{t['id']}"):
                        delete_task(t["id"])
                        st.rerun()
                
                # Gestion de la clôture (Fichiers & Commentaires)
                if t["status"] != "Terminé":
                    with st.expander("✅ Clôturer la tâche (Rendu & Commentaire)"):
                        finish_comment = st.text_area("Commentaire de fin", key=f"fc_{t['id']}")
                        finish_file = st.file_uploader("Joindre le rendu final (Optionnel)", key=f"file_{t['id']}")
                        
                        if st.button("Valider la fin de tâche", key=f"done_{t['id']}"):
                            t["status"] = "Terminé"
                            t["comment"] = finish_comment
                            if finish_file:
                                t["file_name"] = finish_file.name
                                t["file_data"] = finish_file.getvalue()
                            st.rerun()
                else:
                    # Affichage du rendu si la tâche est terminée
                    st.success(f"**Commentaire de clôture :** {t['comment'] if t['comment'] else 'Aucun commentaire'}")
                    if t.get("file_name"):
                        st.download_button(
                            label=f"💾 Télécharger le rendu ({t['file_name']})",
                            data=t["file_data"],
                            file_name=t["file_name"],
                            mime="application/octet-stream",
                            key=f"dl_{t['id']}"
                        )

# ==========================================
# VUE 2 : DASHBOARD
# ==========================================
elif menu == "📊 Dashboard (Avancement)":
    st.header("Tableau de bord Global")
    if not st.session_state.tasks:
        st.warning("Ajoutez des tâches pour voir les statistiques.")
    else:
        df = pd.DataFrame(st.session_state.tasks)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("État des tâches")
            fig_pie = px.pie(df, names='status', hole=0.4, color='status', 
                             color_discrete_map={"Terminé": "#28a745", "En cours": "#ffc107"})
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            st.subheader("Répartition par Projet")
            fig_bar = px.bar(df, x='project', color='project')
            st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# VUE 3 : DIAGRAMME DE GANTT
# ==========================================
elif menu == "📅 Diagramme de Gantt":
    st.header("Diagramme de Gantt")
    
    if not st.session_state.tasks:
        st.warning("Ajoutez des tâches pour générer le diagramme de Gantt.")
    else:
        df = pd.DataFrame(st.session_state.tasks)
        df['start_date'] = pd.to_datetime(df['start_date'])
        df['deadline'] = pd.to_datetime(df['deadline'])
        
        gantt_proj = st.selectbox("Sélectionnez le projet à visualiser", ["Tous"] + st.session_state.projects)
        if gantt_proj != "Tous":
            df = df[df['project'] == gantt_proj]
            
        if df.empty:
             st.info("Aucune tâche pour ce projet.")
        else:
            # Création d'un dictionnaire de couleurs unique pour chaque tâche
            color_mapping = {row['name']: row['color'] for index, row in df.iterrows()}
            
            fig_gantt = px.timeline(
                df, 
                x_start="start_date", 
                x_end="deadline", 
                y="name", 
                color="name", # On colore par nom de tâche
                hover_data=["status", "priority", "people"],
                color_discrete_map=color_mapping # On applique les couleurs choisies par l'utilisateur
            )
            fig_gantt.update_yaxes(autorange="reversed")
            fig_gantt.update_layout(xaxis_title="Date", yaxis_title="Tâches", showlegend=False)
            st.plotly_chart(fig_gantt, use_container_width=True)
