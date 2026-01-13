# MASLD vs Healthy Ultrasound ML - Premium Results Viewer

A polished, interactive Streamlit dashboard for presenting model performance and explainability results from the MASLD vs Healthy ultrasound classification project.

## Purpose

This application is designed to **present results clearly and attractively** for dissertation review. It does NOT retrain models or modify any ML training logic—it is a results viewer only.

## Important Ethics & Privacy Rules

- **No Patient IDs**: The UI displays only Case IDs (Case-01, Case-02, etc.) and never shows patient_id
- **No Absolute Paths**: The app never displays absolute filesystem paths (no "C:\Users\..." or "/home/...")
- **Privacy First**: Only friendly labels like "Connected ✅" or sanitized folder names are shown
- **Research Disclaimer**: All pages include clear disclaimers that this is for research use only, not medical advice

## Quick Start

### Installation

```bash
cd streamlit_app
pip install -r requirements.txt
```

### Running the App

```bash
streamlit run app.py
```

The app will open in your default web browser at `http://localhost:8501`

## Expected Folder Structure

The app expects results in the following structure:

```
results/
├── explainability_reports/
│   ├── index.csv                    # Required: Case results with probabilities, uncertainty, risk bands
│   ├── case_mapping.csv             # Required: Case ID to patient ID mapping (not displayed)
│   └── Case-XX.png                  # Optional: Explainability visualization images
├── patient_metrics_summary.csv      # Optional: Model performance metrics
├── run_config.json                  # Optional: Experiment configuration
├── calibration_plots/               # Optional: Calibration plot images
├── roc_curves_patient_level.png     # Optional: ROC curve plots
├── pr_curves_patient_level.png      # Optional: PR curve plots
└── confusion_matrices_patient_level.png  # Optional: Confusion matrix plots
```

### Required Files

- `explainability_reports/index.csv`: Must contain columns:
  - `case_id`: Case identifier (e.g., "Case-01")
  - `patient_id`: Patient identifier (used internally, never displayed)
  - `fold`: Cross-validation fold (0, 1, 2)
  - `y_true`: True label (0=Healthy, 1=MASLD)
  - `p_calibrated`: Calibrated probability
  - `uncertainty_std`: Uncertainty standard deviation
  - `risk_band`: Risk classification (LOW, LOW-MOD, MODERATE, HIGH)

- `explainability_reports/case_mapping.csv`: Case to patient mapping (not displayed)

**Note**: The dashboard shows cases with explainability reports. If your full dataset has more patients than cases in `index.csv`, the app will display a note explaining this discrepancy.

## Features

### 1. Dashboard
- **Hero Banner**: Premium gradient banner with title and subtitle
- **Artifact Cards**: Visual cards showing available result files (index.csv, case images, metrics, etc.)
- **KPI Cards**: 
  - Cases with Reports (shows subset note if applicable)
  - High Risk percentage
  - Average Risk
  - Average Uncertainty
  - Images Available
- **Top N Cases**: Quick access tables for high-risk and most uncertain cases with "View in Case Explorer" buttons
- **Interactive Charts**: 
  - Risk distribution histogram (p_calibrated)
  - Risk band counts bar chart
  - Uncertainty vs Risk scatter plot (hover shows Case ID only)
- **Global Filters**: Collapsible filter bar with active filter chips displayed outside
  - Filter by risk band, class, fold, probability range, uncertainty range
  - Reset filters button

### 2. Case Explorer
- **Searchable Case Table**: Filter and search cases by Case ID
- **Case Selection**: Dropdown menu to select a case
- **Case Detail View**:
  - Large Case ID header with color-coded risk band badge
  - **Risk Level Gauge**: Interactive Plotly gauge showing calibrated risk (0-100%)
  - **Uncertainty Meter**: Horizontal progress bar with color coding
  - True Label and Fold information cards
  - Explainability image viewer with full-width toggle
  - Case Summary expander with all case details
  - Download buttons: Case summary (JSON) and image (if available)

### 3. Performance & Run Info
- **Tabs**: Organized into Metrics | Calibration | Artifacts
- **Metrics Tab**: 
  - Key performance indicators in cards (AUC, PR-AUC, Accuracy, F1)
  - Detailed metrics table with formatting
- **Calibration Tab**: 
  - ROC curves, PR curves, confusion matrices (if available)
- **Artifacts Tab**: 
  - Visual artifact cards with status indicators
  - Run Summary card with experiment configuration (no raw paths)

## Premium UI Features

- **Hero Banner**: Gradient banner at top of Dashboard
- **Branded Sidebar**: 
  - Premium header card with app name and icon
  - Navigation pills with active state highlighting
  - Status & Summary card showing key metrics
  - Clean Connect Results section
- **Card-Based Layout**: All content in rounded cards with subtle shadows
- **Interactive Elements**: Hover effects, smooth transitions
- **Color-Coded Badges**: Risk bands use intuitive color coding
- **Custom CSS**: Premium styling via `styles.css`

## Configuration

### Results Folder Path

By default, the app looks for results in `../results` (relative to the `streamlit_app/` folder).

You can change this in the sidebar:
1. Open the sidebar
2. Enter your results folder path in "Results Folder" (use relative paths like `../results`)
3. The app will validate and show connection status (e.g., "Connected ✅ (results)")

**Important**: The app never displays absolute paths. Only sanitized folder names are shown.

### Demo Mode

If you want to preview the UI without real data:
1. Check "Demo Mode" in the sidebar
2. The app will generate synthetic demo data (clearly labeled as DEMO)
3. Demo data does not resemble real patient data

## Data Filtering

The Dashboard and Case Explorer support comprehensive filtering via Global Filters:

- **Risk Band**: Filter by LOW, LOW-MOD, MODERATE, HIGH
- **Class**: Filter by Healthy (0) or MASLD (1)
- **Fold**: Filter by cross-validation fold (0, 1, 2)
- **Probability Range**: Slider to filter by calibrated probability
- **Uncertainty Range**: Slider to filter by uncertainty standard deviation

Filters are synced across pages using session state. Active filters are shown as chips above the collapsible filter controls.

## Export Features

- **Download Case Summary**: Export selected case information as JSON (includes case_id, risk_band, probabilities, no patient_id)
- **Download Case Image**: Export explainability visualization image (if available)

## File Structure

```
streamlit_app/
├── app.py              # Main application router and page logic
├── data_loader.py      # Data loading, validation, and demo data generation
├── ui.py               # UI components (cards, badges, hero banner, filter bar)
├── styles.css          # Premium CSS styling
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Design Philosophy

- **Premium Dashboard**: Clean, card-based layout with consistent spacing and rounded corners
- **Interactive**: Click to explore rather than scrolling through long text
- **Privacy-Focused**: No absolute paths or personal information exposed anywhere
- **Professional**: Suitable for supervisor review and presentations
- **Modern Aesthetic**: Warm gradients, subtle shadows, premium typography

## Privacy & Ethics

- **No Patient Data Display**: Patient IDs are never shown in the UI
- **Case IDs Only**: Only anonymized Case IDs (Case-01, Case-02, etc.) are displayed
- **No Path Exposure**: 
  - Absolute filesystem paths are never displayed
  - Only sanitized folder names (checked for path separators) are shown
  - Connection status shows "Connected ✅" or "Connected ✅ (folder_name)" only
- **Local Data Only**: All data stays on your local machine
- **Research Disclaimer**: Clear disclaimers on every page

## Troubleshooting

### "Missing required files" Error

1. Check that your results folder path is correct (try `../results`)
2. Verify that `explainability_reports/index.csv` and `explainability_reports/case_mapping.csv` exist
3. Check file permissions

### "8 cases" when you have 55 patients

This is expected if your `index.csv` only contains 8 explainability reports. The dashboard will show a note explaining that explainability reports were generated for a subset of cases. To see all patients, generate explainability reports for all cases in your pipeline.

### Images Not Showing

- This is expected if images are not included in your results folder
- The app will show a placeholder instead
- Images are optional and not required for the app to function

### Demo Mode Not Working

- Make sure the checkbox is checked in the sidebar
- Refresh the page after enabling demo mode

### ModuleNotFoundError for plotly

- Make sure you've installed dependencies: `pip install -r requirements.txt`
- Run the app with `streamlit run app.py` (not `python app.py`)

## Notes for Supervisors

This application is designed to be:
- **Easy to Run**: Single command (`streamlit run app.py`)
- **Self-Contained**: All dependencies in `requirements.txt`
- **Well-Documented**: Clear README and inline code comments
- **Robust**: Handles missing files gracefully with helpful error messages
- **Professional**: Modern UI suitable for presentations
- **Privacy-Safe**: No personal information or absolute paths exposed
- **Modular**: Clean separation of concerns (data loading, UI components, styling)

The app does not modify any training data or models—it is a read-only results viewer.

## License

This is a research prototype for dissertation purposes. All code is provided as-is for research use only.

---

**Remember**: This is a research prototype—NOT for clinical use. Always include appropriate disclaimers when presenting results.
**Researcher name: Shivangi Kamleshbhai Parmar**
**Supervisor: Dr Olamilekan Shobayo**
**Sheffield Hallam University**
