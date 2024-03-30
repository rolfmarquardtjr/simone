import streamlit as st
import sqlite3
import pandas as pd

# Inicialização do banco de dados e criação das tabelas
def inicializar_db():
    with sqlite3.connect('escola.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alunos (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                idade INTEGER NOT NULL,
                serie TEXT NOT NULL,
                numero INTEGER NOT NULL,
                eletiva TEXT,
                projeto_vida TEXT,
                tutor TEXT,
                clube TEXT,
                tarefa TEXT,
                khan TEXT,
                redacao TEXT,
                leia_sp TEXT,
                itinerario_formativo TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY,
                usuario TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL
            );
        """)
        # Tenta inserir o usuário padrão; ignora se já existe
        try:
            cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES ('admin', 'admin123')")
            conn.commit()
        except sqlite3.IntegrityError:
            pass

# Função para verificar login
def verificar_login(usuario, senha):
    with sqlite3.connect('escola.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha))
        if cursor.fetchone():
            return True
        else:
            return False

# Função para inserir um aluno no banco de dados
def inserir_aluno(nome, idade, serie, numero, eletiva, projeto_vida, tutor, clube, tarefa, khan, redacao, leia_sp, itinerario_formativo):
    with sqlite3.connect('escola.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alunos (nome, idade, serie, numero, eletiva, projeto_vida, tutor, clube, tarefa, khan, redacao, leia_sp, itinerario_formativo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (nome, idade, serie, numero, eletiva, projeto_vida, tutor, clube, tarefa, khan, redacao, leia_sp, itinerario_formativo))
        conn.commit()

# Função para buscar todos os alunos
def buscar_todos_alunos():
    with sqlite3.connect('escola.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, serie, tutor FROM alunos;")
        return cursor.fetchall()

# Função para buscar detalhes de um aluno específico
def buscar_detalhes_aluno(aluno_id):
    with sqlite3.connect('escola.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alunos WHERE id = ?", (aluno_id,))
        return cursor.fetchone()

# Função para excluir um aluno
def excluir_aluno(aluno_id):
    with sqlite3.connect('escola.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM alunos WHERE id = ?", (aluno_id,))
        conn.commit()

# Interface principal do Streamlit
def main():
    st.title("Escola Eduardo Soares")

    inicializar_db()

    if 'logado' not in st.session_state:
        st.session_state.logado = False

    if st.session_state.logado:
        st.sidebar.success("Você está logado.")
        
        # Cadastrar novos administradores (Omitido para focar nas funcionalidades principais)
        
        nome = st.text_input("Nome do aluno:")
        idade = st.number_input("Idade:", min_value=5, max_value=100, step=1)
        serie = st.text_input("Série:")
        numero = st.number_input("Número:", min_value=1, max_value=1000, step=1)
        eletiva = st.text_input("Eletiva:")
        projeto_vida = st.text_area("Projeto de Vida:")
        tutor = st.text_input("Tutor:")
        clube = st.text_input("Clube:")
        tarefa = st.text_input("Tarefa:")
        khan = st.text_input("Khan Academy:")
        redacao = st.text_input("Redação:")
        leia_sp = st.text_input("Leia São Paulo:")
        itinerario_formativo = st.text_input("Itinerário Formativo:")
        
        if st.button("Cadastrar Aluno"):
            inserir_aluno(nome, idade, serie, numero, eletiva, projeto_vida, tutor, clube, tarefa, khan, redacao, leia_sp, itinerario_formativo)
            st.success("Aluno cadastrado com sucesso!")
            
        # Listagem e exclusão de alunos
        st.subheader("Alunos Cadastrados")
        alunos = buscar_todos_alunos()
        df_alunos = pd.DataFrame(alunos, columns=['ID', 'Nome', 'Série', 'Tutor'])
        st.table(df_alunos)
        
        aluno_id_excluir = st.selectbox("Selecionar aluno para excluir:", df_alunos['ID'])
        if st.button("Excluir Aluno"):
            excluir_aluno(aluno_id_excluir)
            st.success("Aluno excluído com sucesso.")
            st.experimental_rerun()
        
        # Visualização de detalhes de alunos
        aluno_id_detalhes = st.selectbox("Selecionar aluno para ver detalhes:", df_alunos['ID'], key='detalhes')
        if st.button("Ver Detalhes"):
            detalhes = buscar_detalhes_aluno(aluno_id_detalhes)
            if detalhes:
                detalhes_df = pd.DataFrame([detalhes[1:]], columns=['Nome', 'Idade', 'Série', 'Número', 'Eletiva', 'Projeto Vida', 'Tutor', 'Clube', 'Tarefa', 'Khan', 'Redação', 'Leia SP', 'Itinerário Formativo'])
                st.table(detalhes_df)
                
        if st.sidebar.button("Logout"):
            st.session_state.logado = False
            st.experimental_rerun()

    else:
        with st.sidebar:
            st.subheader("Login")
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            if st.button("Login"):
                if verificar_login(usuario, senha):
                    st.session_state.logado = True
                    st.experimental_rerun()
                else:
                    st.error("Usuário ou senha inválidos.")

if __name__ == "__main__":
    main()
