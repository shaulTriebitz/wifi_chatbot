# Project Setup

Follow these steps to set up the project:

1. **Ensure Python 3.13.x is installed:**
    ```sh
    python -V
    ```

2. **Create a virtual environment:**
    ```sh
    python -m venv venv
    ```

3. **Activate the virtual environment:**
    - **Windows:**
        ```sh
        venv\Scripts\activate
        ```
    - **macOS/Linux:**
        ```sh
        source venv/bin/activate
        ```

4. **Install the required Python packages:**
    ```sh
    python -m pip install -r requirements.txt
    ```

5. **Add a `.env` file:**
    - Create a new file in the project root named `.env`.
    - Copy the contents from `.env_example` into the new `.env` file.
    - Update the variables in `.env` as needed.

6. **Run the project:**
    ```sh
    streamlit run langgraph_wifi_agent.py
    ```
