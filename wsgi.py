#!/usr/bin/python
# -*- coding: UTF-8 -*-
# ===========================================================
#      Author : yxu
#       Email :
#        Date : 
# Description : 
#        Args : 
# ===========================================================

from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from young import create_app
app = create_app('production')