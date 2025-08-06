# Insurance Claim Management System

## Overview

This is a desktop-based Insurance Claim Management System built with Python and Tkinter for local insurance claim processing. The application provides a comprehensive solution for managing insurance claims with a focus on data privacy through local SQLite storage. The system features a user-friendly GUI for claim entry, editing, searching, and data export capabilities, designed specifically for daily use by insurance claims processors in healthcare-related insurance operations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **GUI Framework**: Tkinter with ttk for modern styling
- **Window Management**: Single main window with tabbed interface for different functionalities
- **Component Structure**: Modular design with separate classes for claim forms, search functionality, and reusable UI components
- **Layout Pattern**: Grid-based layout with responsive design and scrollable forms
- **Custom Components**: Date picker widgets, currency entry fields, and validation-enabled form controls

### Backend Architecture
- **Database Layer**: SQLite database with a dedicated DatabaseManager class for all data operations
- **Data Models**: Dataclass-based Claim model with type hints and validation support
- **Business Logic**: Separated validation logic in ClaimValidator class with comprehensive field validation
- **Export System**: Modular ExportManager supporting CSV and Excel formats with optional openpyxl dependency

### Data Storage Solutions
- **Primary Database**: SQLite for local, single-user data storage with foreign key constraints enabled
- **Schema Design**: Claims table with support for linked claims through parent_claim_id relationships
- **Data Privacy**: All data stored locally with no external transmission requirements
- **Backup Strategy**: File-based database allows for easy backup and portability

### Application Flow
- **Entry Point**: main.py orchestrates application startup and database initialization
- **Tab Management**: MainWindow coordinates between claim form and search tabs
- **Data Validation**: Multi-layer validation including real-time form validation and business rule enforcement
- **Error Handling**: Comprehensive error handling with user-friendly message dialogs

### Key Design Patterns
- **MVC Pattern**: Clear separation between models (Claim), views (GUI components), and controllers (database operations)
- **Factory Pattern**: Database connection management with connection reuse
- **Observer Pattern**: Form validation triggers and data refresh mechanisms
- **Strategy Pattern**: Multiple export formats handled through unified ExportManager interface

## External Dependencies

### Core Dependencies
- **Python Standard Library**: tkinter, sqlite3, datetime, csv, os, sys
- **Type Hinting**: typing module for enhanced code documentation and IDE support

### Optional Dependencies
- **openpyxl**: Excel file export functionality (gracefully degrades to CSV-only if unavailable)

### System Requirements
- **Python 3.6+**: Required for dataclass support and type hints
- **Operating System**: Cross-platform compatibility through Tkinter
- **Database**: No external database server required - uses embedded SQLite

### Predefined Data Sets
- **Company Options**: Fixed list of insurance companies (NIVA, HDFC, TATA, CARE, NEW INDIA, NATIONAL, UNITED, ORIENTAL, FUTURE GENERALI)
- **Claim Status Options**: Predefined workflow states (Intimation, Submitted, Approved, Declined, Reconsideration, Settled, Additional requirement, Ombudsman)
- **Claim Type Options**: Standard claim categories (Cashless, Reimbursement, Pre-post, Day care, Hospital cash, Health check-up)