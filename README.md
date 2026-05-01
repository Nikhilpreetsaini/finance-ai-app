# AI‑Powered Personal Finance Manager

This project is a modern, responsive web application that helps individuals track their income and expenses while leveraging simple AI‑driven categorisation and personalised insights. Built entirely with HTML, CSS and vanilla JavaScript, the app is lightweight, deploys easily on any static hosting provider and stores data locally in the browser (so no external database is required).  
It uses **Bootstrap 5** for styling and **Chart.js** for dynamic charts.  

## Features

* **User registration and login** – Users can create an account and securely sign in. Credentials are stored in the browser’s `localStorage` (encoded) to keep the app server‑free.  
* **AI‑powered categorisation** – When a transaction is added, the description is analysed against a set of keywords to assign a spending category automatically (e.g. food, transport, utilities). Income transactions are categorised separately.  
* **Expense and income tracking** – Add transactions with date, description, amount and type (income or expense). Data is saved per user and loaded whenever the user logs back in.  
* **Dynamic charts and summaries** – The dashboard displays a doughnut chart visualising spending distribution across categories and shows total income, total expense and the highest expense category with its percentage share.  
* **Responsive design** – The UI adapts to different screen sizes and devices, making it usable on desktops, tablets and phones.  
* **Offline‑first experience** – All data is stored locally in the browser so the app works without an internet connection after the first load.  

## Getting Started

This project doesn’t require any server‑side installation. To run it locally during development:

1. Clone or download this repository.  
2. Open `index.html` in a modern web browser (Chrome, Firefox, Safari, Edge).  
3. Register a new account and start adding transactions.

### Deployment

Because the app is completely static, it can be deployed to any static hosting service such as GitHub Pages, Netlify or Render. Simply upload the contents of the `finance-ai-app` directory (all files) to your hosting provider.

To deploy on **Render**:

1. Create a new **Static Site** in Render and connect it to your GitHub repository containing this project.  
2. Set the **Build Command** to `npm install` (optional if you don’t have any build step) and the **Publish Directory** to `finance-ai-app`.  
3. Render will automatically serve `index.html` as the entry point.

## Project Structure

```
finance-ai-app/
├── index.html        # Main HTML file containing the page structure
├── style.css         # Custom CSS for fine‑tuned styling
├── app.js            # JavaScript logic (authentication, transactions, chart)
└── README.md         # This documentation file
```

## Limitations & Future Improvements

While this project demonstrates a functional personal finance tool, there are a few limitations worth noting:

* **Security** – Passwords are encoded using `btoa` and stored in `localStorage`. In a production system you would never store credentials client‑side. Implementing a proper backend with password hashing and secure session management would be required for real‑world use.  
* **AI categorisation** – The categorisation logic uses simple keyword matching. A more advanced version could integrate a lightweight machine‑learning model or call an AI service for smarter categorisation and personalised recommendations.  
* **Data portability** – All data is stored in the browser; there’s no way to export or sync across devices. Adding an export/import feature or cloud sync (e.g. via Firebase or a custom backend) would make the app more robust.  
* **Accessibility** – Additional work could be done to improve keyboard navigation and screen reader compatibility.  

Despite these limitations, the application serves as a strong foundation for a professional personal finance manager. Feel free to fork, extend and adapt it to suit your own needs!
