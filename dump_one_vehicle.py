#!/usr/bin/env python3
import sys
import json
from bson import json_util
sys.path.append('/home/ubuntu/EkerGallery')
from models.database import db

v = db.vehicles.find_one()
if v:
    print(json.dumps(dict(v, _id=str(v['_id'])), indent=2, ensure_ascii=False))
else:
    print("Veritabanı boş!")
