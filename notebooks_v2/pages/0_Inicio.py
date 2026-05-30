streamlit.errors.StreamlitAPIException: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).

Traceback:
File "/mount/src/vermont-alerta-temprana/notebooks_v2/app.py", line 8, in <module>
    st.Page("pages/0_Inicio.py",         title="🏫 Inicio",        default=True),
    ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.14/site-packages/streamlit/runtime/metrics_util.py", line 698, in wrapped_func
    result = non_optional_func(*args, **kwargs)
File "/home/adminuser/venv/lib/python3.14/site-packages/streamlit/navigation/page.py", line 201, in Page
    return StreamlitPage(
        page,
    ...<4 lines>...
        visibility=visibility,
    )
File "/home/adminuser/venv/lib/python3.14/site-packages/streamlit/navigation/page.py", line 337, in __init__
    raise StreamlitAPIException(
        f"Unable to create Page. The file `{page.name}` could not be found."
    )
