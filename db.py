import logging
import os

from peewee import Model, SqliteDatabase, CharField, IntegerField, DeleteQuery

import config

logger = logging.getLogger("DB")

# Init

# Get parsed command line arguments
cmd_args = config.parse_args()

# Init DB
db_path = config.get_setting(cmd_args, 'queuefile')
db = SqliteDatabase(db_path, threadlocals=True)


class BaseQueueModel(Model):
    class Meta:
        database = db


class QueueItemModel(BaseQueueModel):
    scan_path = CharField(max_length=256, unique=True, null=False)
    scan_for = CharField(max_length=64, null=False)
    scan_section = IntegerField(null=False)
    scan_type = CharField(max_length=64, null=False)


def create_database(db_path):
    if not os.path.exists(db_path):
        db.create_tables([QueueItemModel])
        logger.info("Created database tables")


def connect():
    if not db.is_closed():
        logger.error("Already connected to database...")
        return False
    return db.connect()


def get_next_item():
    item = None
    try:
        item = QueueItemModel.get()
    except:
        # logger.exception("Exception getting first item to scan: ")
        pass
    return item


def exists_file_root_path(file_path):
    items = get_all_items()
    if '.' in file_path:
        dir_path = os.path.dirname(file_path)
    else:
        dir_path = file_path

    for item in items:
        if dir_path.lower() in item['scan_path'].lower():
            return True, item['scan_path']
    return False, None


def get_all_items():
    items = []
    try:
        for item in QueueItemModel.select():
            items.append({'scan_path': item.scan_path,
                          'scan_for': item.scan_for,
                          'scan_type': item.scan_type,
                          'scan_section': item.scan_section})
    except:
        logger.exception("Exception getting all items from database: ")
        return None
    return items


def remove_item(scan_path):
    try:
        return DeleteQuery(QueueItemModel).where(QueueItemModel.scan_path == scan_path).execute()
    except:
        logger.exception("Exception deleting %r from database: ", scan_path)
        return False


def add_item(scan_path, scan_for, scan_section, scan_type):
    item = None
    try:
        return QueueItemModel.create(scan_path=scan_path, scan_for=scan_for, scan_section=scan_section,
                                     scan_type=scan_type)
    except AttributeError as ex:
        return item
    except:
        pass
        # logger.exception("Exception adding %r to database: ", scan_path)
    return item


# Create database
def init():
    if not os.path.exists(db_path):
        create_database(db_path)
    connect()
