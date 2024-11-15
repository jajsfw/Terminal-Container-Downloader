def get_style_sheet(theme):
    """获取全局样式表"""
    return f"""
        QMainWindow {{
            background-color: {theme['window_background']};
            color: {theme['text_color']};
        }}
        
        QToolBar {{
            background-color: {theme['toolbar_background']};
            border: none;
            spacing: 5px;
            padding: 5px;
        }}
        
        QPushButton {{
            background-color: {theme['accent_color']};
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            font-weight: bold;
            min-width: 80px;
        }}
        
        QPushButton:hover {{
            background-color: {theme['accent_color']}CC;
        }}
        
        QPushButton:pressed {{
            background-color: {theme['accent_color']}99;
        }}
        
        QTableWidget {{
            background-color: {theme['window_background']};
            alternate-background-color: {theme['table_alternate_background']};
            gridline-color: {theme['table_gridline']};
            color: {theme['text_color']};
            border: 1px solid {theme['table_gridline']};
            border-radius: 4px;
        }}
        
        QTableWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {theme['table_gridline']};
        }}
        
        QTableWidget::item:selected {{
            background-color: {theme['accent_color']}33;
        }}
        
        QHeaderView::section {{
            background-color: {theme['toolbar_background']};
            color: {theme['text_color']};
            padding: 8px;
            border: none;
            border-right: 1px solid {theme['table_gridline']};
            font-weight: bold;
        }}
        
        QStatusBar {{
            background-color: {theme['toolbar_background']};
            color: {theme['text_color']};
            padding: 5px;
        }}
        
        QProgressBar {{
            border: 2px solid {theme['accent_color']};
            border-radius: 4px;
            text-align: center;
            background-color: {theme['progress_bar_background']};
            height: 20px;
        }}
        
        QProgressBar::chunk {{
            background-color: {theme['progress_bar_chunk']};
            border-radius: 2px;
        }}
        
        QScrollBar:vertical {{
            border: none;
            background-color: {theme['window_background']};
            width: 10px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {theme['accent_color']}66;
            border-radius: 5px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {theme['accent_color']}99;
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
    """ 