try:
    db = DBManager()

    if not db.test_connection():
        st.error("Não foi possível conectar ao banco. Verifique secrets.")
        st.stop()

    users_from_db = db.get_users_for_auth()

    config["credentials"]["usernames"].update(users_from_db)

except Exception as e:
    st.error(f"❌ Falha ao carregar DB: {e}")
    st.stop()
