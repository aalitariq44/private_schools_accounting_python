#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database.connection import db_manager

if __name__ == "__main__":
    try:
        info = db_manager.get_table_info('installments')
        print("Installments table structure:")
        for column in info:
            print(f"  {column['name']}: {column['type']} {'NOT NULL' if column['notnull'] else ''} {'PRIMARY KEY' if column['pk'] else ''}")
    except Exception as e:
        print(f"Error: {e}")