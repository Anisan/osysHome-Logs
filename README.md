# Logs - Log Viewer Module

![Logs Icon](static/Logs.png)

A log viewing and monitoring system for viewing system logs, error tracking, and log file management.

## Description

The `Logs` module provides a log viewer interface for the osysHome platform. It enables you to view system logs, track errors, and monitor log files through a web interface.

## Main Features

- ✅ **Log File Viewer**: View any log file from the `logs` directory
- ✅ **Smart Loading**: Loads only the first or last N lines (configurable in the UI) for large files
- ✅ **Parsed Entries**: Splits raw log text into structured entries (time, level, module, message)
- ✅ **Filtering**:
  - by text (search within messages),
  - by log level (INFO/ERROR/etc.),
  - by module.
- ✅ **Sorting**: Sort entries by time (ascending/descending)
- ✅ **Multiline Support**: Collapsible/expandable multiline messages (stack traces, long payloads)
- ✅ **Line & Entry Counters**: Shows `loaded / total` lines and number of parsed entries per file
- ✅ **Widget Support**: Dashboard widget showing error count based on the same regex as the viewer
- ✅ **API Integration**: RESTful API for log access and partial loading

## Admin Panel

The module provides a Vue‑based admin interface:

### Main View
- **Log Files List** (left column)
  - Sorted by modification time (newest first)
  - Filename filter and sort options (name, size, modified)
  - Checkboxes for selecting multiple files
  - Scrollable list that fits the viewport
- **Content Area** (right column)
  - One card per selected file
  - Per‑file toolbar: reload, download, collapse/expand content
  - Counters: loaded lines / total lines, number of parsed entries

### Log Display
- Entries are parsed with the same regex on backend and frontend:

  ```text
  ^(\d{2}:\d{2}:\d{2}(?:\.\d{3})?)\[(INFO|ERROR|DEBUG|WARNING|CRITICAL)](?:\[([^\]]*)])*([^\n\r]*)
  ```

- Each entry shows:
  - timestamp,
  - level badge (with color),
  - optional module badge,
  - message (single‑line or collapsible multiline).
- Long "unbreakable" strings (for example base64 payloads) are wrapped so they do not break layout.

## Widget

The module provides a dashboard widget showing:
- **Error Count**: Number of error entries in `errors.log`  
  (counted with the same regex as the viewer, so the numbers match)
- **Error Status**: Visual indicator if errors are present
- **Link**: Direct link to the Logs module
  - Clicking the widget opens the Logs admin page
  - `errors.log` is automatically pre‑selected and loaded

## API

The module provides RESTful API endpoints for programmatic log access:

- **GET /api/logs/...**: Access log files via API

## Usage

### Viewing Logs

1. Navigate to the Logs module in the admin panel.
2. Select one or more log files from the list on the left.
3. Use the content filters on the right:
   - text filter,
   - sort by time (asc/desc),
   - filter by module and level.
4. For large files:
   - Only a subset of lines is loaded (first or last N lines),
   - The card shows how many lines were loaded vs total,
   - If the file is truncated, a warning is shown.
5. Click on multiline entries marked with `(click)` to expand/collapse details.

### Error Monitoring

The widget automatically tracks errors in `errors.log`:
- Error count displayed on dashboard (same logic as the viewer)
- Visual indicator when errors are present
- Click widget to open Logs with `errors.log` pre‑selected

## Technical Details

- **Log Directory**: `logs/` folder
- **Error Log**: `errors.log` file
- **Entry Pattern**: Regex pattern for log entry detection
- **Encoding**: UTF-8 with error handling

## Version

Current version: **1.0**

## Category

System

## Actions

The module provides the following actions:
- `widget` - Dashboard widget with error count

## Requirements

- Flask
- osysHome core system

## Author

osysHome Team

## License

See the main osysHome project license

