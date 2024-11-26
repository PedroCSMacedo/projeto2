 #Função para limpar os campos 
'''def lc():
        st.session_state["1"]=""
        st.session_state["2"]=""
        st.session_state["3"]=""  '''


'''st.title("Criar Lista")

    def validarID():
        if x and x.isdigit:
            try:
                x_int = int(x)
                cursor.execute("SELECT 1 FROM itens WHERE id = ?", (x_int,))
                resultado = cursor.fetchone()

                if resultado:
                    cursor.execute("DELETE FROM itens WHERE id = ?", (x_int,))
                    conn.commit()
                    st.success("O item adicionado a lista")
                else:
                    st.error("ID não encontrado")
            except sqlite3.Error as e:
                st.error("Escreva um id valido")
        else:
            st.error("Todos os campos devem estar preenchidos")
    
    idAdd = st.text_input("ID do item a ser adicionado")
    listaCriadas = selectbox("")'''
    # Recuperar os itens do banco de dados
