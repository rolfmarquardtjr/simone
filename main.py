import streamlit as st
import sqlite3
import pandas as pd
import io

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

# Função para buscar os nomes de todos os alunos
def buscar_nomes_alunos():
    with sqlite3.connect('escola.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM alunos;")
        nomes = cursor.fetchall()
        # Extrai os nomes de alunos de tuplas para uma lista
        return [nome[0] for nome in nomes]

# Função para buscar detalhes de um aluno específico pelo nome
def buscar_detalhes_aluno(nome_aluno):
    with sqlite3.connect('escola.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alunos WHERE nome = ?", (nome_aluno,))
        return cursor.fetchone()

# Função para excluir um aluno pelo nome
def excluir_aluno(nome_aluno):
    with sqlite3.connect('escola.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM alunos WHERE nome = ?", (nome_aluno,))
        conn.commit()

# Função modificada para exportar alunos para Excel e retornar como objeto de bytes
def exportar_alunos_para_excel():
    with sqlite3.connect('escola.db') as conn:
        # Consulta para buscar todos os alunos
        df_alunos = pd.read_sql_query("SELECT * FROM alunos", conn)

    # Usando um objeto BytesIO como um arquivo na memória
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_alunos.to_excel(writer, index=False)
    output.seek(0)  # Volta ao início do objeto BytesIO

    return output

# Interface principal do Streamlit
def main():
    st.title("Escola Eduardo Soares")

    inicializar_db()

    if 'logado' not in st.session_state:
        st.session_state.logado = False

    if st.session_state.logado:
        st.sidebar.success("Você está logado.")
        
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
            
        # Listagem e exclusão de alunos por nome
        st.subheader("Alunos Cadastrados")
        alunos = buscar_todos_alunos()
        df_alunos = pd.DataFrame(alunos, columns=['ID', 'Nome', 'Série', 'Tutor'])
        st.table(df_alunos)
        
        nomes_alunos = buscar_nomes_alunos()  # Obtem os nomes dos alunos
        nome_aluno_excluir = st.selectbox("Digite ou selecione o nome do aluno para excluir:", [''] + nomes_alunos)
        if nome_aluno_excluir and st.button("Excluir Aluno"):
            excluir_aluno(nome_aluno_excluir)
            st.success("Aluno excluído com sucesso.")
            st.experimental_rerun()
        
        # Visualização de detalhes de alunos por nome
        nome_aluno_detalhes = st.selectbox("Digite ou selecione o nome do aluno para ver detalhes:", [''] + nomes_alunos, key='detalhes')
        if nome_aluno_detalhes and st.button("Ver Detalhes"):
            detalhes = buscar_detalhes_aluno(nome_aluno_detalhes)
            if detalhes:
                detalhes_df = pd.DataFrame([detalhes[1:]], columns=['Nome', 'Idade', 'Série', 'Número', 'Eletiva', 'Projeto Vida', 'Tutor', 'Clube', 'Tarefa', 'Khan', 'Redação', 'Leia SP', 'Itinerário Formativo'])
                st.table(detalhes_df)
            else:
                st.error("Aluno não encontrado.")
                
        if st.button("Exportar Alunos para Excel"):
            dados_excel = exportar_alunos_para_excel()
            st.download_button(
                label="Baixar Excel",
                data=dados_excel,
                file_name="alunos_exportados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
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
