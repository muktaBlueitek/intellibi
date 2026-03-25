# IntelliBI User Guide

## Getting Started

### Prerequisites
- Web browser (Chrome, Firefox, Safari, Edge)
- User account (register or use admin-provided credentials)

### Logging In
1. Open the IntelliBI application in your browser
2. Enter your **username** and **password**
3. Click **Login**
4. You'll be redirected to the home dashboard

### First-Time Registration
1. Click **Register** on the login page
2. Fill in: Email, Username, Password, Full Name
3. Click **Register**
4. Log in with your new credentials

---

## Dashboards

### Viewing Dashboards
- Go to **Dashboards** in the navigation
- Click a dashboard to open it
- Widgets display charts, tables, and metrics

### Creating a Dashboard
1. Go to **Dashboards**
2. Click **Create Dashboard** (or **New Dashboard**)
3. Enter name and description
4. Add widgets and configure layout

### Editing Layout
- Click **Edit** to enable drag-and-drop
- Drag widgets to reposition
- Resize by dragging corners
- Changes save automatically

### Exporting to PDF
- Open a dashboard that has at least one widget
- Click **Export as PDF**
- Your browser downloads an A4 PDF; tall dashboards span multiple pages
- The PDF captures the widget layout area (charts and tables as shown on screen)

### Sharing
- Open dashboard → **Share**
- Add users with View or Edit permission
- Share link for public dashboards (if enabled)

---

## Data Sources

### Adding a File (CSV/Excel)
1. Go to **Data Sources**
2. Click **Upload File**
3. Select CSV or Excel file
4. Optionally enable data cleaning
5. Preview and confirm

### Connecting a Database
1. Go to **Data Sources** → **Add Database**
2. Select PostgreSQL or MySQL
3. Enter connection details (host, port, database, credentials)
4. Test connection and save

### Managing Data Sources
- View, edit, or delete from the Data Sources list
- Test database connections before saving
- Preview data after upload

---

## AI Chatbot

### Asking Questions
1. Go to **Chatbot**
2. (Optional) Select a data source for SQL queries
3. Type your question in natural language, e.g.:
   - "What are total sales by region?"
   - "Show top 10 products by revenue"
4. Press **Send** or use a suggested query

### Understanding Results
- The chatbot returns text, SQL (if applicable), and data tables
- Use **Suggested queries** for quick follow-ups
- Export conversations via **Export (TXT/JSON)**

### Tips
- Be specific about columns and filters
- For database queries, select the correct data source first

---

## Navigation

| Link        | Purpose                         |
|-------------|---------------------------------|
| Home        | Overview and quick links        |
| Dashboards  | View and manage dashboards      |
| Data Sources| Add and manage data connections |
| Chatbot     | AI-powered data queries         |
| Profile     | View and edit your profile      |

---

## Troubleshooting

**Can't log in?**
- Verify username and password
- Contact admin if account is locked

**Dashboard not loading?**
- Check data source connection
- Refresh the page

**Chatbot not responding?**
- Ensure a data source is selected for SQL queries
- Check OpenAI API key is configured (admin)
