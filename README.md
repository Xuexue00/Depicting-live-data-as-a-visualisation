# Project Overview
This project presents carbon emissions data through an interactive web interface. It includes a main page and four data visualization charts, depicting emissions over time, by region, by project, and by cloud status. All visualization charts are housed within a `templates` directory, while the main page is located at the project's root level.

## File Structure
```
/project
│
├── index.html             # Main page, provides navigation tabs for charts
├── /templates             # Contains all HTML files for the charts
│   ├── plot.html          # Chart showing emissions over time
│   ├── plot2.html         # Chart showing emissions by region
│   ├── plot3.html         # Chart showing emissions by project
│   └── plot4.html         # Chart showing emissions by cloud status
├── app.py                 # Python script for data generation or backend logic
├── synthetic_data.csv     # Synthetic data, possibly used for visualizations
├── emissions-1.csv        # Original carbon emissions data
├── Synthetic data.ipynb   # Jupyter notebook for synthetic data analysis and processing
└── Static visualisation.ipynb # Jupyter notebook for static data visualisation
```


## Tech Stack
- HTML/CSS
- JavaScript (using Plotly.js)
- Python

## Usage Instructions
1. Ensure your server is set up to parse Python scripts and correctly configured to serve HTML files.
2. Open `index.html` in a browser to access the main page.
3. Click the tabs at the top to switch between different carbon emissions data visualizations.

## Development and Deployment
- Make sure to test modifications to the Python script or HTML files in a local environment before deployment.
- Before deploying to production, double-check that all file paths are correctly set and all dependencies are properly loaded.

## Maintainer
- Information about the maintainer(s) (fill in based on project details)

## File Descriptions
- **index.html**: The main page of the project, containing tabs for navigation, allowing users to view different data visualizations.
- **/templates/plot.html, plot2.html, plot3.html, plot4.html**: HTML files containing various data visualizations.
- **app.py**: A Python script that may be used for backend data processing or generating data for the front-end charts.
- **synthetic_data.csv** and **emissions-1.csv**: These CSV files contain the original and synthetic data used for the visualizations.
- **Synthetic data.ipynb**: Jupyter notebook that includes analysis and processing of synthetic data for visualization.
- **Static visualisation.ipynb**: Jupyter notebook that includes static data visualisation.
