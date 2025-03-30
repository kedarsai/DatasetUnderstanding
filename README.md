# SQL Integration Tool

A Streamlit-based tool for creating and managing SQL views through natural language processing.

## Features

- Connect to various databases (SQL Server, PostgreSQL, MySQL, SQLite)
- Create views using natural language join conditions
- View management and data preview
- OpenAI integration for SQL query generation

## Prerequisites

- Python 3.8+
- SQL Server Native Client 11.0 (for SQL Server connections)
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd <repository-name>
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key in the application

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Connect to your database using the sidebar
3. Select tables and define join conditions
4. Generate and execute CREATE VIEW queries

## Project Structure

```
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── src/
│   ├── database/         # Database connection handling
│   ├── vector_store/     # Vector store management
│   └── utils/           # Utility functions
└── README.md            # Project documentation
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 