# Customer Feedback Management System

A Django-based web application designed to simplify customer feedback collection and analysis for Accutech Middle East. The system allows customers to submit feedback through a shareable web link and helps the internal team manage and analyze responses efficiently.

## Features

- **Customer Feedback Form:** User-friendly form for collecting customer feedback.
- **Feedback Categories:** Collects ratings for service quality, timely delivery, communication, and overall satisfaction.
- **Email Integration:** Opens Outlook with a pre-filled email draft that users can customize before sending to customers.
- **Feedback Dashboard:** View and manage submitted customer responses through a centralized dashboard.
- **Excel Analysis:** Consolidates feedback responses into a shared Excel analysis sheet.
- **Responsive Interface:** Modern interface designed for a smooth user experience.

## Technology Stack

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, JavaScript
- **Data Analysis:** Excel (XLSX)
- **Email Integration:** Microsoft Outlook
- **Database:** Django-supported database

## Installation and Setup

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd <project-folder>
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

If a `requirements.txt` file is available:

```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations

```bash
python manage.py migrate
```

### 5. Run the Development Server

```bash
python manage.py runserver
```

Open the application in your browser at:

`http://127.0.0.1:8000/`

## How It Works

1. The internal team prepares a feedback email using the Outlook integration.
2. The email is customized and sent to the customer with the feedback form link.
3. The customer opens the link and submits their feedback.
4. The application stores the responses and updates the centralized Excel analysis sheet.
5. The internal team reviews the collected feedback through the dashboard.

## Project Purpose

The application helps streamline customer feedback collection, improve service evaluation, and maintain centralized feedback records to support continuous improvement.

## Future Enhancements

- Advanced feedback analytics and visualizations.
- Automated email reminders.
- Customer feedback trend analysis.
- Enhanced reporting and export options.

---

**Developed for:** Accutech Middle East  
**Project Type:** Customer Feedback Management System