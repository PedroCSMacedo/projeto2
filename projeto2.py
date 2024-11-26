import streamlit as st
import sqlite3
import pandas as pd
import time

#Criar banco de dados
conn = sqlite3.connect("garcom2.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS itens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    descricao TEXT,
    fornecedor TEXT,
    valor REAL
)
""")

#barra laetral
barra_lateral = st.sidebar.selectbox("Página", ["Adicionar/Excluir Itens", "Criar Lista", "Visualizar Listas", "Visualizar Itens"])

#Página Inserir Item 
if barra_lateral == "Adicionar/Excluir Itens":

    st.title("Adiconar/Excluir Itens")

    adex = st.selectbox("Adicionar/excluir", ["Adicionar", "Excluir"])

    #adicionar
    if adex == "Adicionar":
        #Função que salva os dados
        def salvarDados():
            if nome and descricao and valor and fornecedor:
                try: 
                    cursor.execute(""" 
                    INSERT INTO itens (nome, descricao, fornecedor, valor) VALUES (?, ?, ?, ?)
                    """, (nome, descricao, fornecedor, valor))
                    conn.commit()
                    st.success("O item foi adiconado com sucesso")
                except ValueError:
                    st.error("Escreva um valor valido em todos os campos")
            else:
                st.erro("Todos os campos deve estar preenchido!")

        nome = st.text_input("Nome do item: ") 
        descricao = st.text_area("Descrição do Item: ")
        fornecedor = st.text_input("Nome do fornecedor")
        valor = st.number_input("Qual o Valor do Item: ")

        #botão para salvar
        if st.button("Salvar"):
            salvarDados()

    #excluir
    elif adex == "Excluir":

        #função que deleta os dados 
        def deletarDados():
            if idDelet and idDelet.isdigit:
                try:
                    idDelet_int = int(idDelet)
                    cursor.execute("SELECT 1 FROM itens WHERE id = ?", (idDelet_int,))
                    resultado = cursor.fetchone()

                    if resultado:
                        cursor.execute("DELETE FROM itens WHERE id = ?", (idDelet_int,))
                        conn.commit()
                        st.success("O item foi excluido com sucesso!")
                    else:
                        st.error("ID não encontrado")
                except sqlite3.Error as e:
                    st.error("Escreva um id valido")
            else:
                st.error("Todos os campos devem estar preenchidos")

        idDelet = st.text_input("Excluir Item (digite o id do item): ")       
        
        if 'confirm' not in st.session_state:
            st.session_state.confirm = False

        #botão de excluir
        if not st.session_state.confirm:  
            if st.button("Excluir"):
                st.session_state.confirm = True

        #botão de confirmar
        if st.session_state.confirm:    
            st.write("Você deseja excluir este item permanentemente? ")
            if st.button("Confirmar"):
                deletarDados()
                st.session_state.confirm = False
            if st.button("Cancelar"):
                st.error("Operação cancelada")
                st.session_state.confirm = False

#Página Criar Lista
elif barra_lateral == "Criar Lista":
    
    cursor.execute("SELECT id, nome FROM itens")
    itens = cursor.fetchall()

    # Criar um dicionário para facilitar acesso
    itens_dict = {f"{nome} (ID: {id_item})": (id_item, nome) for id_item, nome in itens}

    # Selecionar um item específico
    selecionado = st.selectbox("Selecione um item:", list(itens_dict.keys()))

    # Obter ID e Nome do item selecionado
    id_selecionado, nome_selecionado = itens_dict[selecionado]

    # Exibir no expander
    with st.expander(f"Detalhes do Item Selecionado"):
        st.write(f"**ID:** {id_selecionado}")
        st.write(f"**Nome:** {nome_selecionado}")

    # Adicionar um campo para a quantidade
    quantidade = st.number_input(f"Quantidade de {nome_selecionado}:", min_value=0, step=1)

    # Botão para salvar as informações
    if st.button("Salvar informações"):
        st.session_state["item_id"] = id_selecionado
        st.session_state["item_nome"] = nome_selecionado
        st.session_state["quantidade"] = quantidade
        st.success("Item e quantidade salvos com sucesso!")


#Página Visualizar Listas
elif barra_lateral == "Visualizar Listas":
    st.title("Visualizar Listas")
    

#Página Visualizar Itens
elif barra_lateral == "Visualizar Itens":
    st.title("Visualizar Itens")

    #puxa os dados
    cursor.execute("SELECT * FROM itens")
    itens = cursor.fetchall()

    #ver tabela
    if itens:
        tabela = pd.DataFrame(itens, columns=["ID", "Nome", "Descrição", "Valor", "Fornecedor"])
        st.write(tabela)
    else:
        st.write("Adicione algum item no banco de dados")
        

conn.close()