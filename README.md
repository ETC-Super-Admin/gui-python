# Project Overview

This is a PySide6 application template for creating modern desktop applications with a Jira-inspired layout and theming system. The application features a responsive UI with a collapsible sidebar, a top navigation bar, and a footer. It includes a theme manager for switching between light and dark modes.

**Key Technologies:**

*   **UI Framework:** PySide6
*   **Icons:** QtAwesome
*   **Programming Language:** Python

**Architecture:**

The application follows a component-based architecture. The main layout is defined in `src/app/layout.py`, which integrates the following components:

*   **Navbar:** `src/components/layout/navbar.py`
*   **Sidebar:** `src/components/layout/sidebar.py`
*   **Footer:** `src/components/layout/footer.py`
*   **ThemeManager:** `src/components/ui/theme_manager.py`

Pages are implemented as separate modules. For example, the profile page is located at `src/app/profile/profile.py`. Pages are managed by a `QStackedWidget` in the main layout. The application includes pre-built pages for a dashboard, profile, and settings.

# Building and Running

**1. Install Dependencies:**

The project requires Python 3.8+. You can install the dependencies using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

**2. Run the Application:**

The application can be started by running the `main.py` script:

```bash
python main.py
```

# Code Formatting and Linting

This project uses `black` for code formatting and `ruff` for linting.

**1. Install Tools:**

```bash
pip install black ruff
```

**2. Run Tools:**

To format the code, run `black` from the project root:

```bash
black .
```

To lint the code, run `ruff` from the project root:

```bash
ruff check .
```

# Development Conventions

*   **Styling:** Use the `setObjectName()` method on widgets to apply styles.
*   **Component-Based:** Create reusable UI components in the `src/components/ui` directory.
*   **Page Creation:** To add a new page, create a new module (e.g., a directory with `__init__.py` and `my_page.py`) in the `src/app` directory, and register it in the `page_map` dictionary in `src/app/layout.py`.
*   **Theming:** The application uses a template-based theming system.
    *   The color palettes are defined in `src/styles/themes.py`.
    *   The `main.py` script dynamically generates the stylesheet based on the selected theme.
*   **Icons:** Use `qtawesome` to add icons to the application.
*   **Navigation:** Use the `navigate_to_page()` method in `MainLayout` to switch between pages.

# Project Status

For a detailed list of completed and pending tasks, please see the [TASKS.md](TASKS.md) file.