import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import uuid

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Gestionnaire de Projets Pro", page_icon="🚀", layout="wide")

# --- INITIALISATION DES DONNÉES (Session State) ---
if "projects" not in st.session_state:
    st.session_state.projects = ["Projet Alpha"]
if "categories" not in st.session_state:
    st.session_state.categories = ["Développement", "Design", "Marketing", "Administratif"]
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# --- FONCTIONS UTILITAIRES ---
def add_task(project, category, name, desc, tools, priority, start_date, deadline, people):
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
        "status": "En cours"
    })

def delete_task(task_id):
    st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task_id]

def mark_done(task_id):
    for t in st.session_state.tasks:
        if t["id"] == task_id:
            t["status"] = "Terminé"

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

# Sidebar pour la navigation
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
            
            t_desc = st.text_area("Description")
            
            submitted = st.form_submit_button("Enregistrer la tâche")
            if submitted:
                if t_name:
                    add_task(t_project, t_category, t_name, t_desc, t_tools, t_priority, t_start, t_deadline, t_people)
                    st.success("Tâche ajoutée avec succès !")
                else:
                    st.error("Le nom de la tâche est obligatoire.")

    st.markdown("---")
    
    # Filtres d'affichage
    f_project = st.selectbox("Filtrer par projet", ["Tous"] + st.session_state.projects)
    
    # Affichage des tâches
    tasks_to_display = [t for t in st.session_state.tasks if f_project == "Tous" or t["project"] == f_project]
    
    if not tasks_to_display:
        st.info("Aucune tâche à afficher pour le moment.")
    else:
        for t in tasks_to_display:
            # Calcul de l'urgence (< 4 jours)
            days_left = (t["deadline"] - datetime.date.today()).days
            is_urgent = (0 <= days_left < 4) and t["status"] != "Terminé"
            is_overdue = days_left < 0 and t["status"] != "Terminé"
            
            # Application de la couleur d'alerte rouge
            bg_color = "#ffe6e6" if is_urgent or is_overdue else "transparent"
            border_color = "red" if is_urgent or is_overdue else "#ddd"
            
            with st.container():
                st.markdown(
                    f"""
                    <div style="background-color: {bg_color}; border: 1px solid {border_color}; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                        <h4 style="margin:0;">{t['name']} <span style="font-size: 0.8em; font-weight: normal;">({t['status']})</span></h4>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
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
                        st.error(f"**Échéance:** {t['deadline']} (En retard!)")
                    elif is_urgent:
                        st.warning(f"**Échéance:** {t['deadline']} (J-{days_left})")
                    else:
                        st.write(f"**Échéance:** {t['deadline']}")
                with c4:
                    if t["status"] != "Terminé":
                        if st.button("✅ Terminer", key=f"done_{t['id']}"):
                            mark_done(t["id"])
                            st.rerun()
                    if st.button("🗑️ Supprimer", key=f"del_{t['id']}"):
                        delete_task(t["id"])
                        st.rerun()

# ==========================================
# VUE 2 : DASHBOARD (CAMEMBERT)
# ==========================================
elif menu == "📊 Dashboard (Avancement)":
    st.header("Tableau de bord Global")
    
    if not st.session_state.tasks:
        st.warning("Ajoutez des tâches pour voir les statistiques.")
    else:
        df = pd.DataFrame(st.session_state.tasks)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("État des tâches (Global)")
            status_counts = df['status'].value_counts().reset_index()
            status_counts.columns = ['Statut', 'Nombre']
            fig_pie = px.pie(status_counts, values='Nombre', names='Statut', hole=0.4, 
                             color='Statut', color_discrete_map={"Terminé": "#28a745", "En cours": "#ffc107"})
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col2:
            st.subheader("Répartition par Projet")
            proj_counts = df['project'].value_counts().reset_index()
            proj_counts.columns = ['Projet', 'Nombre']
            fig_bar = px.bar(proj_counts, x='Projet', y='Nombre', color='Projet')
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
        # Convertir en datetime pour Plotly
        df['start_date'] = pd.to_datetime(df['start_date'])
        df['deadline'] = pd.to_datetime(df['deadline'])
        
        # Sélection du projet pour le Gantt
        gantt_proj = st.selectbox("Sélectionnez le projet à visualiser", ["Tous"] + st.session_state.projects)
        
        if gantt_proj != "Tous":
            df = df[df['project'] == gantt_proj]
            
        if df.empty:
             st.info("Aucune tâche pour ce projet.")
        else:
            fig_gantt = px.timeline(
                df, 
                x_start="start_date", 
                x_end="deadline", 
                y="name", 
                color="status",
                hover_data=["priority", "people"],
                color_discrete_map={"Terminé": "#28a745", "En cours": "#007bff"}
            )
            fig_gantt.update_yaxes(autorange="reversed") # Tâches dans l'ordre de création de haut en bas
            fig_gantt.update_layout(xaxis_title="Date", yaxis_title="Tâches")
            st.plotly_chart(fig_gantt, use_container_width=True)
