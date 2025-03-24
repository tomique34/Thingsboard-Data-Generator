# Setup Instructions

## Unix/MacOS

1. Make the setup script executable:
   ```
   chmod +x setup.sh
   ```

2. Run the setup script:
   ```
   ./setup.sh
   ```

3. Activate the virtual environment:
   ```
   source venv/bin/activate
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Access the web interface at http://localhost:5000

## Windows

1. Run the setup script by double-clicking `setup.bat` or executing:
   ```
   setup.bat
   ```

2. Activate the virtual environment:
   ```
   venv\Scripts\activate
   ```

3. Run the application:
   ```
   python app.py
   ```

4. Access the web interface at http://localhost:5000

## Configuration

Edit the `.env` file to configure your Thingsboard connection details:

```
# Thingsboard connection details
TB_HOST=http://your-thingsboard-host
TB_PORT=8080
TB_USERNAME=your-username
TB_PASSWORD=your-password

# Flask settings 
FLASK_SECRET_KEY=your-secret-key-change-it
FLASK_DEBUG=True
```

Make sure to replace the default values with your actual Thingsboard server information.
