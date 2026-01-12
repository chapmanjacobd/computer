#!/usr/bin/python3
import argparse
import curses
import os
import sqlite3
import sys

KB = 1024
MB = KB * 1024
GB = MB * 1024


def format_size(size_bytes):
    if size_bytes >= GB:
        return f"{size_bytes / GB:.1f}G"
    if size_bytes >= MB:
        return f"{size_bytes / MB:.1f}M"
    if size_bytes >= KB:
        return f"{size_bytes / KB:.1f}K"
    return f"{size_bytes}B"


def format_row_count(count, width=10):
    if count is None:
        return "".rjust(width)
    return f"{count:,}".rjust(width)


class SQLiteAnalyzer:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def get_column_stats(self, table_name, column_name, row_count):
        if row_count == 0:
            return 0, 0, 0, 0

        sql = f"""
        SELECT
            SUM(CASE WHEN "{column_name}" IS NULL THEN 1 ELSE 0 END) AS null_count,
            SUM(CASE WHEN "{column_name}" = 0 AND "{column_name}" IS NOT NULL THEN 1 ELSE 0 END) AS zero_count,
            SUM(CASE WHEN "{column_name}" = '' AND "{column_name}" IS NOT NULL THEN 1 ELSE 0 END) AS empty_string_count
        FROM {table_name};
        """
        try:
            self.cursor.execute(sql)
            null, zero, empty = self.cursor.fetchone()
        except Exception:
            # If query fails (e.g., incompatible type comparison, or general error)
            null, zero, empty = row_count, 0, 0

        null = null or 0
        zero = zero or 0
        empty = empty or 0

        present = row_count - null

        return null, zero, empty, present

    def get_database_structure(self):
        try:
            total_db_size = os.path.getsize(self.db_path)
        except OSError:
            raise FileNotFoundError(f"Database file not found: {self.db_path}")

        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        table_names = [row[0] for row in self.cursor.fetchall()]

        tree = {
            'name': os.path.basename(self.db_path),
            'type': 'database',
            'size': total_db_size,
            'items': [],
            'row_count': None,
        }

        total_estimated_data_size = 0
        table_data = {}

        for table_name in table_names:
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = self.cursor.fetchone()[0]

                self.cursor.execute(f"PRAGMA table_info({table_name})")
                columns_info = self.cursor.fetchall()

                column_data_map = {}
                sample_limit = min(1000, row_count)

                for cid, name, type_str, notnull, dflt_value, pk in columns_info:
                    col_data_size = 0

                    if row_count > 0:
                        self.cursor.execute(f"SELECT AVG(LENGTH({name})) FROM {table_name} LIMIT {sample_limit}")
                        avg_len = self.cursor.fetchone()[0] or 0

                        if type_str.upper() in ['INTEGER', 'REAL', 'NUMERIC'] and avg_len == 0:
                            # Heuristic for numeric types with no string length data
                            col_data_size = row_count * 4
                        else:
                            # Estimate based on average string length
                            col_data_size = int(avg_len * row_count) + (row_count if avg_len > 0 else 0)

                    null, zero, empty, present = self.get_column_stats(table_name, name, row_count)

                    column_data_map[name] = {
                        'name': name,
                        'type': 'column',
                        'data_size': col_data_size,  # Data size only
                        'size': col_data_size,  # Total size (starts as data size)
                        'index_size': 0,  # Index size component
                        'info': f"Type: {type_str}, PK: {'Yes' if pk else 'No'}",
                        'row_count': row_count,
                        'table_name': table_name,
                        'null_count': null,
                        'zero_count': zero,
                        'empty_count': empty,
                        'present_count': present,
                        'single_index': None,  # Store single-column index info here
                    }

                # Step 2: Analyze and size Indexes
                self.cursor.execute(f"PRAGMA index_list({table_name})")
                indexes = self.cursor.fetchall()

                multi_index_items = []

                for idx_cid, idx_name, unique, origin, partial in indexes:
                    self.cursor.execute(f"PRAGMA index_info({idx_name})")
                    index_columns = self.cursor.fetchall()
                    index_col_names = [c[2] for c in index_columns]

                    # Calculate index size based on component column data sizes
                    index_key_size_estimate = sum(
                        column_data_map.get(col_name, {}).get('data_size', 0) for col_name in index_col_names
                    )
                    index_size = int((index_key_size_estimate / row_count) * row_count * 1.5) if row_count > 0 else 0

                    index_item = {
                        'name': idx_name,
                        'type': 'index',
                        'table_name': table_name,
                        'size': index_size,
                        'info': f"Unique: {unique}, Columns: {', '.join(index_col_names)}",
                        'row_count': None,
                    }

                    if len(index_col_names) == 1 and index_col_names[0] in column_data_map:
                        # Single-column index: Aggregate size into column node
                        col_name = index_col_names[0]
                        column_data_map[col_name]['size'] += index_size
                        column_data_map[col_name]['index_size'] += index_size
                        column_data_map[col_name]['single_index'] = index_item
                    else:
                        # Multi-column index: Direct child of table
                        multi_index_items.append(index_item)

                column_items = list(column_data_map.values())

                table_items = sorted(column_items + multi_index_items, key=lambda x: x['size'], reverse=True)

                total_table_size = sum(item['size'] for item in table_items)
                total_estimated_data_size += total_table_size

                table_data[table_name] = {
                    'name': table_name,
                    'type': 'table',
                    'size': total_table_size,
                    'row_count': row_count,
                    'table_name': table_name,
                    'items': table_items,
                }

            except Exception as e:
                table_data[table_name] = {
                    'name': f"{table_name} (ERROR: {e})",
                    'type': 'table',
                    'size': 0,
                    'row_count': 0,
                    'table_name': table_name,
                    'items': [],
                }

        sorted_tables = sorted(table_data.values(), key=lambda x: x['size'], reverse=True)
        tree['items'] = sorted_tables

        overhead_size = max(0, total_db_size - total_estimated_data_size)

        if overhead_size > 0 or total_db_size == 0:
            tree['items'].append(
                {
                    'name': 'Overhead / Unaccounted Space',
                    'type': 'overhead',
                    'size': overhead_size,
                    'info': 'Journal, Free List, Internal Pages, etc.',
                    'row_count': None,
                    'items': [],
                }
            )
            tree['items'].sort(key=lambda x: x['size'], reverse=True)

        return tree

    def get_table_warnings(self, table_name):
        """Checks for multi-column indexes and foreign keys on a table."""
        warnings = []

        # Check for Multi-column indexes
        self.cursor.execute(f"PRAGMA index_list({table_name})")
        indexes = self.cursor.fetchall()
        multi_index_names = []

        for idx_cid, idx_name, unique, origin, partial in indexes:
            self.cursor.execute(f"PRAGMA index_info({idx_name})")
            index_columns = self.cursor.fetchall()
            if len(index_columns) > 1:
                multi_index_names.append(idx_name)

        if multi_index_names:
            warnings.append(f"Multi-column indexes: {', '.join(multi_index_names)}")

        # Check for Outbound Foreign Keys
        self.cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        fks_outbound = [f"references {row[2]}({row[4]})" for row in self.cursor.fetchall()]

        if fks_outbound:
            warnings.append(f"Outbound Foreign Keys: {'; '.join(fks_outbound)}")

        return warnings

    def execute_drop(self, selected_item):
        entity_type = selected_item['type']
        entity_name = selected_item['name']
        table_name = selected_item.get('table_name')

        try:
            if entity_type == 'column':
                index_to_drop = selected_item.get('single_index')
                idx_name = None
                if index_to_drop:
                    idx_name = index_to_drop['name']
                    self.cursor.execute(f"DROP INDEX IF EXISTS {idx_name}")

                sql = f"ALTER TABLE {table_name} DROP COLUMN {entity_name}"
                self.cursor.execute(sql)
                self.conn.commit()

                index_msg = f" (and index '{idx_name}')" if idx_name else ""
                return True, f"Dropped column '{entity_name}'{index_msg}."

            elif entity_type == 'table':
                sql = f"DROP TABLE IF EXISTS {entity_name}"
                self.cursor.execute(sql)
                self.conn.commit()
                return True, f"Dropped table '{entity_name}'."

            elif entity_type == 'index':
                sql = f"DROP INDEX IF EXISTS {entity_name}"
                self.cursor.execute(sql)
                self.conn.commit()
                return True, f"Dropped index '{entity_name}'."

            else:
                return False, f"Cannot drop entity of type '{entity_type}'."

        except Exception as e:
            self.conn.rollback()
            return False, f"SQL Error: {e}"


class NCduTUI:
    def __init__(self, screen, analyzer):
        self.screen = screen
        self.analyzer = analyzer
        self.data_tree = analyzer.get_database_structure()
        self.history = []
        self.current_node = self.data_tree
        self.selected_index = 0
        self.message = None

        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, -1, -1)

        DEFAULT = curses.color_pair(1)

        self.color_map = {
            'database': curses.A_BOLD | DEFAULT,
            'table': curses.A_NORMAL | DEFAULT,
            'index': curses.A_NORMAL | DEFAULT,
            'column': curses.A_NORMAL | DEFAULT,
            'data': curses.A_DIM | DEFAULT,
            'overhead': curses.A_BOLD | DEFAULT,
        }

        self._current_view_mode = 'standard'
        curses.curs_set(0)

    def _get_path_breadcrumb(self):
        path = [self.data_tree['name']]
        for parent, _, _ in self.history:
            path.append(parent['name'])
        return " / ".join(path)

    def _draw_header(self):
        header_text = f" ncsu {self._get_path_breadcrumb()} "

        display_text = header_text.center(self.width)
        self.screen.attron(curses.A_REVERSE)
        try:
            self.screen.addstr(0, 0, display_text[: self.width - 1].ljust(self.width), curses.A_REVERSE)
        except curses.error:
            pass
        self.screen.attroff(curses.A_REVERSE)

    def _draw_footer(self):
        if self._current_view_mode == 'column_detail':
            footer_text = " LEFT: Back to Table | d: Drop Column | q: Exit "
        else:
            footer_text = " UP/DOWN: Navigate | RIGHT/ENTER: Drill Down | LEFT: Up | d: Drop | q: Exit "

        display_text = footer_text.ljust(self.width)

        self.screen.attron(curses.A_REVERSE)
        try:
            self.screen.addstr(self.height - 1, 0, display_text[: self.width - 1])
        except curses.error:
            pass
        self.screen.attroff(curses.A_REVERSE)

    def _draw_message(self):
        if self.message:
            msg_line = self.height - 2
            self.screen.addstr(msg_line, 0, " " * self.width)

            display_text = f" MESSAGE: {self.message} "
            padding = (self.width - len(display_text)) // 2

            self.screen.addstr(msg_line, padding, display_text, curses.A_REVERSE)

    def _draw_column_detail_view(self):
        column = self.current_node

        total_size_str = format_size(column['size'])
        header_text = f" Column Detail: {column['table_name']}.{column['name']} (Total Size: {total_size_str}) "

        self.screen.attron(curses.A_BOLD)
        try:
            self.screen.addstr(1, 0, header_text.ljust(self.width)[: self.width - 1])
        except curses.error:
            pass
        self.screen.attroff(curses.A_BOLD)

        components = []
        components.append(
            {
                'name': 'Column Data (Estimated)',
                'type': 'data',
                'size': column['data_size'],
                'row_count': column['row_count'],
                'info': f"Base type: {column['info']}",
            }
        )

        if column['single_index']:
            idx = column['single_index']
            components.append(
                {
                    'name': f"Index: {idx['name']}",
                    'type': 'index',
                    'size': idx['size'],
                    'row_count': None,
                    'info': idx['info'],
                }
            )

        start_line = 4
        list_header_line = "  Size Info"
        try:
            self.screen.addstr(
                start_line - 1, 0, list_header_line.ljust(self.width)[: self.width - 1], curses.A_REVERSE
            )
        except curses.error:
            pass

        for i, item in enumerate(components):
            line_num = start_line + i
            if line_num >= self.height - 2:
                break

            attr = self.color_map.get(item['type'], curses.A_NORMAL)

            size_str = format_size(item['size']).rjust(6)
            name_info = f"{item['name']} - {item['info']}"
            max_name_len = self.width - len(list_header_line)
            display_name_info = name_info[:max_name_len].ljust(max_name_len)

            line = f"{size_str} {display_name_info}"

            try:
                self.screen.addstr(line_num, 0, line[: self.width - 1], attr)
            except curses.error:
                pass

    def _draw_list(self):
        items = self.current_node.get('items', [])
        display_start_line = 1
        display_end_line = self.height - 2

        is_root_view = self.current_node.get('type') == 'database'

        # Width for Present, Null, Zero, Empty counts
        COUNT_WIDTH = 10

        if is_root_view:
            header_line = "  Size   Size%       Rows Name"
            total_db_size = self.data_tree['size']
        else:
            header_line = "  Size Values%     Values       Null       Zero      Empty Name"

        display_start_line += 1
        try:
            self.screen.addstr(1, 0, header_line.ljust(self.width)[: self.width - 1], curses.A_REVERSE)
        except curses.error:
            pass

        scroll_offset = max(0, self.selected_index - (display_end_line - 1))
        for i in range(display_start_line, display_end_line + 1):
            list_index = i - display_start_line + scroll_offset

            if list_index >= len(items):
                try:
                    self.screen.addstr(i, 0, " " * self.width)
                except curses.error:
                    pass
                continue

            item = items[list_index]
            is_selected = list_index == self.selected_index

            attr = self.color_map.get(item['type'], curses.A_NORMAL)
            if is_selected:
                attr = curses.A_REVERSE

            size_str = format_size(item['size']).rjust(6)
            row_count_str = format_row_count(item.get('row_count'))
            name_str = item['name']

            max_name_len = self.width - len(header_line)

            if is_root_view:
                percent_str = "    "
                if total_db_size > 0:
                    percent = (item['size'] / total_db_size) * 100.0
                    percent_str = f"{percent:.1f}%".rjust(7)

                display_name = name_str[:max_name_len].ljust(max_name_len)
                line = f"{size_str} {percent_str} {row_count_str} {display_name}"
            else:  # columns / multi-column indexes
                stats_spacer = ' ' * (4 * COUNT_WIDTH + 4)  # Default spacer for non-column types

                if item['type'] == 'column':
                    present_str = format_row_count(item.get('present_count'), COUNT_WIDTH)
                    null_str = format_row_count(item.get('null_count'), COUNT_WIDTH)
                    zero_str = format_row_count(item.get('zero_count'), COUNT_WIDTH)
                    empty_str = format_row_count(item.get('empty_count'), COUNT_WIDTH)

                    stats_block = f"{present_str} {null_str} {zero_str} {empty_str}"

                    # Simplify name string for the list view if it has an index
                    if item['single_index']:
                        display_name = (f"{name_str} (+ Index)").ljust(max_name_len)
                    else:
                        display_name = name_str[:max_name_len].ljust(max_name_len)

                    percent_str = "    "
                    row_count = item.get('row_count')
                    if row_count > 0:
                        percent = (item['present_count'] / row_count) * 100.0
                        percent_str = f"{percent:.1f}%".rjust(7)

                    line = f"{size_str} {percent_str} {stats_block} {display_name}"
                else:
                    # Index or other items: use spacer for stats columns
                    display_name = name_str[:max_name_len].ljust(max_name_len)
                    line = f"{size_str}        {stats_spacer} {display_name}"

            try:
                self.screen.addstr(i, 0, line[: self.width - 1], attr)
            except curses.error:
                pass

    def _draw_drop_confirmation(self, selected_item, warnings=None):
        entity_type = selected_item['type']
        entity_name = selected_item['name']

        # Construct message, including warnings if present
        prompt_lines = [f"Permanently drop {entity_type} '{entity_name}'? (y/N)"]

        if warnings:
            prompt_lines.insert(0, "------------------------------------------")
            prompt_lines.insert(0, "WARNING: Dependencies Exist. Proceed with caution.")
            prompt_lines.append("------------------------------------------")
            # Limit warning lines displayed in box for curses compatibility
            for w in warnings[:2]:
                prompt_lines.append(f" - {w[:self.width - 6]}...")
            if len(warnings) > 2:
                prompt_lines.append(f" - ...and {len(warnings) - 2} more. ")

        max_line_len = max(len(line) for line in prompt_lines)
        box_width = max_line_len + 4
        box_height = len(prompt_lines) + 2

        start_y = (self.height - box_height) // 2
        start_x = (self.width - box_width) // 2

        # Ensure box fits
        if start_y < 0 or start_x < 0 or box_width > self.width or box_height > self.height:
            self.message = "Confirmation box too large for screen. Please resize terminal."
            return None

        self.screen.refresh()

        confirm_win = curses.newwin(box_height, box_width, start_y, start_x)
        confirm_win.box()

        for i, line in enumerate(prompt_lines):
            try:
                confirm_win.addstr(i + 1, 2, line)
            except curses.error:
                pass

        confirm_win.refresh()

        return confirm_win.getch()

    def _prompt_and_execute_drop(self, selected_item):
        entity_type = selected_item['type']
        entity_name = selected_item['name']

        warnings = None
        if entity_type == 'table':
            warnings = self.analyzer.get_table_warnings(entity_name)

        response_char = self._draw_drop_confirmation(selected_item, warnings)

        if response_char is None or chr(response_char).lower() != 'y':
            self.message = "Drop cancelled."
            self.screen.clear()
            return

        success, msg = self.analyzer.execute_drop(selected_item)

        if success:
            self.data_tree = self.analyzer.get_database_structure()

        self.message = msg
        self.screen.clear()

    def _handle_input(self):
        key = self.screen.getch()

        self.message = None
        self._should_exit = False

        if self._current_view_mode == 'column_detail':
            if key == curses.KEY_LEFT:
                parent_node, index, _ = self.history.pop()
                self.current_node = parent_node
                self.selected_index = index
                self._current_view_mode = 'standard'
            elif key == ord('d') or key == ord('D'):
                self._prompt_and_execute_drop(self.current_node)
            elif key == ord('q'):
                self._should_exit = True
            return

        # Handle input for standard list views
        items = self.current_node.get('items', [])
        num_items = len(items)

        if key == curses.KEY_UP:
            self.selected_index = max(0, self.selected_index - 1)
        elif key == curses.KEY_DOWN:
            self.selected_index = min(num_items - 1, self.selected_index + 1)
        elif key in (curses.KEY_RIGHT, ord('\n'), ord('\r')):
            if num_items > 0:
                selected_item = items[self.selected_index]

                if selected_item.get('type') == 'column':
                    # Drill down into column to see size breakdown
                    self.history.append((self.current_node, self.selected_index, 'standard'))
                    self.current_node = selected_item
                    self._current_view_mode = 'column_detail'
                    self.selected_index = 0
                elif selected_item.get('items'):
                    # Normal drill down (Table, Index, etc.)
                    self.history.append((self.current_node, self.selected_index, 'standard'))
                    self.current_node = selected_item
                    self.selected_index = 0
        elif key == curses.KEY_LEFT:
            if self.history:
                parent_node, index, _ = self.history.pop()
                self.current_node = parent_node
                self.selected_index = index
        elif key == ord('q'):
            self._should_exit = True
        elif key == ord('d') or key == ord('D'):
            if num_items > 0:
                selected_item = items[self.selected_index]
                if selected_item['type'] in ['table', 'index', 'column']:
                    self._prompt_and_execute_drop(selected_item)
                else:
                    self.message = f"Cannot drop entity of type '{selected_item['type']}'."

    def run(self):
        while True:
            self.screen.clear()
            self.height, self.width = self.screen.getmaxyx()

            self._draw_header()

            if self._current_view_mode == 'column_detail':
                self._draw_column_detail_view()
            else:
                self._draw_list()

            self._draw_footer()
            self._draw_message()

            self.screen.refresh()
            self._handle_input()

            if self._should_exit:
                break


def main(stdscr):
    parser = argparse.ArgumentParser(
        description="SQLite NCdu-like Analyzer. Calculates and displays approximate table/index/column sizes in a TUI."
    )
    parser.add_argument('db_path', help='Path to the SQLite database file.')

    try:
        args = parser.parse_args(sys.argv[1:2] if len(sys.argv) > 1 else [])
    except SystemExit:
        return

    try:
        analyzer = SQLiteAnalyzer(args.db_path)
    except Exception as e:
        stdscr.addstr(f"Error processing database: {e}")
        stdscr.getch()
        return

    tui = NCduTUI(stdscr, analyzer)
    tui.run()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Error: Missing database path.")
        print("Usage: python sqlite_ncdu_analyzer.py <db_path>")
        sys.exit(1)

    db_path_check = sys.argv[1]
    if not os.path.exists(db_path_check):
        print(f"Error: Database file not found at '{db_path_check}'")
        sys.exit(1)

    try:
        curses.wrapper(main)
    except Exception:
        try:
            curses.endwin()
        except:
            pass
        raise
