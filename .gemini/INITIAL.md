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
*   **ThemeManager:** `src/styles/theme_manager.py`

Pages are implemented as separate modules. For example, the profile page is located at `src/app/profile/profile.py`. Pages are managed by a `QStackedWidget` in the main layout. The application includes pre-built pages for a dashboard, profile, and settings.