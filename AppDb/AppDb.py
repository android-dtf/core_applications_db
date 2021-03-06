#!/usr/bin/env python
# Copyright 2013-2015 Jake Valletta (@jake_valletta)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# API for working with applications

import sqlite3
from os.path import isfile, isdir
import dtf.logging as log

import dtf.globals as globals
import dtf.properties as prop
import base64

_TAG = "AppDb"

APP_DB_NAME = "sysapps.db"

AOSP_PACKAGE_PREFIX = "aosp-data-"

PROTECTION_NORMAL = 0
PROTECTION_DANGEROUS = 1
PROTECTION_SIGNATURE = 2
PROTECTION_SIGNATURE_OR_SYSTEM = 3

PROTECTION_FLAG_SYSTEM = 0x10
PROTECTION_FLAG_DEVELOPMENT = 0x20

PROTECTION_MASK_BASE = 0x0f

# Check if we can the api data
def isAOSPDataInstalled():

    sdk = prop.get_prop("Info", "sdk")
    dtf_packages = globals.DTF_PACKAGES_DIR

    if isdir(dtf_packages + '/' + AOSP_PACKAGE_PREFIX + sdk):
        return True
    else:
        return False

# Check if made by Google.
def isGoogleApp(package_name):
    if package_name[0:11] == "com.google.":
        return True
    else:
        return False

# Exceptions
class AppDbException(Exception):

    def __init__(self, message):

        # Call the base class constructor with the parameters it needs
        Exception.__init__(self, message)


# Application Class
class Application(object):

    _id = 0
    package_name = ''
    project_name = ''
    decoded_path = ''
    has_native = 0
    min_sdk_version = 0
    target_sdk_version = 0
    version_name = ''
    version_code = ''
    permisison = None
    debuggable = None
    successfully_unpacked = None
    shared_user_id = ''
    shared_user_label = ''
    allow_backup = None

    def __init__(self, package_name, project_name, decoded_path, has_native,
                min_sdk_version, target_sdk_version, version_name,
                version_code, permission, debuggable, shared_user_id,
                shared_user_label, allow_backup, id=None):

        self.project_name = project_name
        self.package_name = package_name
        self.decoded_path = decoded_path

        self.has_native = has_native

        if debuggable == None:
            self.debuggable = None
        elif debuggable == True:
            self.debuggable = 1
        elif debuggable == False:
            self.debuggable = 0

        if allow_backup == None:
            self.allow_backup = None
        elif allow_backup == True:
            self.allow_backup = 1
        elif allow_backup == False:
            self.allow_backup = 0

        self.min_sdk_version = min_sdk_version
        self.target_sdk_version = target_sdk_version
        self.version_name = version_name
        self.version_code = version_code

        self.permission = permission

        self.shared_user_id = shared_user_id
        self.shared_user_label = shared_user_label

        if id is not None:
            self._id = id

    def setDebuggable(self, value):
        self.debuggable = value

    def getDebuggable(self):
        if self.debuggable == None:
            return None
        elif self.debuggable == 0:
            return False
        elif self.debuggable == 1:
            return True

    def setAllowBackup(self, value):

        """Set allow_backup value"""

        self.allow_backup = value

    def getAllowBackup(self):

        """Check if app allows backup"""

        if self.allow_backup == None:
            return None
        elif self.allow_backup == 0:
            return False
        elif self.allow_backup == 1:
            return True

# Component Object Classes
class PermissionGroup(object):

    _id = 0
    application_id = 0
    name = ""

    def __init__(self, name, application_id, id=None):

        self.name = name
        self.application_id = application_id

        if id is not None:
            self._id = id

class Permission(object):

    _id = 0
    application_id = 0
    name = ""
    permission_group = None
    protection_level = ""

    def __init__(self, name, protection_level, permission_group, application_id, id=None):
        self.name = name
        self.protection_level = protection_level
        self.permission_group = permission_group
        self.application_id = application_id

        if id is not None:
            self._id = id

    def __repr__(self):
        return "%s [%s]" % (self.name, self.protection_level)

class Activity(object):

    _id = 0
    application_id = 0
    name = ""
    permission = None
    enabled = None
    exported = None

    def __init__(self, name, enabled, exported, permission, application_id, id=None):

        # EDIT : Constructor expects True/False/NoneType as exported and enabled.
        self.name = name
        self.permission = permission

        self.exported = exported
        self.enabled = enabled

        self.application_id = application_id

        if id is not None:
            self._id = id

class Service(object):

    _id = 0
    application_id = 0
    name = ""
    permission = None
    enabled = None
    exported = None

    def __init__(self, name, enabled, exported, permission, application_id, id=None):

        # EDIT : Constructor expects True/False/NoneType as exported and enabled.
        self.name = name
        self.permission = permission

        self.exported = exported
        self.enabled = enabled

        self.application_id = application_id

        if id is not None:
            self._id = id

class Provider(object):

    _id = 0
    application_id = 0
    name = ""
    authorities = None
    enabled = None
    exported = None
    permission = None
    read_permission = None
    write_permission = None
    grant_uri_permissions = ""
    path_permission_data = ""
    grant_uri_permission_data = ""

    def __init__(self, name, authorities, enabled, exported, grant_uri_permissions,
                 grant_uri_permission_data, path_permission_data, permission, read_permission,
                 write_permission, application_id, id=None):

        # EDIT : Constructor expects True/False/NoneType as exported and enabled.
        # Note - Constructor expects 0/1/NoneType as grantUriPermissions
        # Note - Constrctor expects path_permission_data  as a string.
        self.name = name
        self.authorities = authorities

        self.exported = exported
        self.enabled = enabled

        if grant_uri_permissions == 0:
            self.grant_uri_permissions = False
        elif grant_uri_permissions == 1:
            self.grant_uri_permissions = True
        else:
            self.grant_uri_permissions = None

        self.permission = permission
        self.read_permission = read_permission
        self.write_permission = write_permission
        self.path_permission_data = path_permission_data
        self.grant_uri_permission_data = grant_uri_permission_data
        self.application_id = application_id

        if id is not None:
            self._id = id

class Receiver(object):

    _id = 0
    application_id = 0
    name = ""
    permission = None
    enabled = None
    exported = None

    def __init__(self, name, enabled, exported, permission, application_id, id=None):

        # EDIT : Constructor expects True/False/NoneType as exported and enabled.
        # Note - Construtor expects 0/1/NoneType as exported/enabled
        self.name = name
        self.permission = permission

        self.exported = exported
        self.enabled = enabled

        self.application_id = application_id

        if id is not None:
            self._id = id

class IntentFilter(object):

    _id = 0
    _actions = None
    _categories = None
    _datas = None
    _priority = 0

    def __init__(self, priority, actions, categories, datas, id=None):

        if len(actions) == 0:
            self._actions = None
        else:
            self._actions = actions

        if len(categories) == 0:
            self._categories = None
        else:
            self._categories = categories

        if len(datas) == 0:
            self._datas = None
        else:
            self._datas = datas

        self._priority = priority

        if id is not None:
            self._id = id

    def getActions(self):
        if self._actions == None:
            return []
        else:
            return self._actions

    def getCategories(self):
        if self._categories == None:
            return []
        else:
            return self._categories

    def getDatas(self):
        if self._datas == None:
            return []
        else:
            return self._datas

    def getPriority(self):
        return self._priority

class IntentData(object):

    scheme = ""
    host = ""
    port = ""
    path = ""
    path_pattern = ""
    path_prefix = ""
    mime_type = ""

    def __init__(self):
        return

    def __str__(self):

        tmp = ""

        # "If a scheme is not specified for the intent filter,
        # all the other URI attributes are ignored."
        if self.scheme == u"None":

            # MIME type has nothing to do with the URI
            if self.mime_type != u"None":
                return "(mime-type=%s)" % self.mime_type
        else:
            tmp += "%s://" % self.scheme

            # "If a host is not specified for the filter, the
            # port attribute and all the path attributes are ignored."
            if self.host != u"None":
                tmp += str(self.host)

                if self.port != u"None":
                    tmp += ":%s " % self.port
                else:
                    tmp += " "

                if self.path != u"None":
                    tmp += "[path=%s]" % self.path
                if self.path_pattern != u"None":
                    tmp += "[pathPattern=%s]" % self.path_pattern
                if self.path_prefix != u"None":
                    tmp += "[pathPrefix=%s]" % self.path_prefix

        # MIME type has nothing to do with the URI
        if self.mime_type != u"None":
            return  "%s (mime-type=%s)" % (tmp, self.mime_type)
        else:
            return tmp

# Signature class
class Signature(object):

    _id = 0
    issuer = ""
    subject = ""
    cert = ""

    def __init__(self):
        return

    def get_cert(self, print_format='base64'):

        """Get actual certifcate"""

        if print_format == 'base64':
            return self.cert
        elif print_format == 'base16':
            return base64.b64decode(self.cert).encode('hex')
        elif print_format == 'hex':
            return base64.b64decode(self.cert)
        else:
            return None
# End Component Class Declarations

#### Class AppDb ########################################
class AppDb(object):

    db_path = None
    app_db = None

    def __init__(self, db_path, safe=False):

        # Make sure the DB exists, don't create it.
        if safe and not isfile(db_path):
            raise AppDbException("Database file not found : %s!" % db_path)

        self.db_path = db_path
        self.app_db = sqlite3.connect(db_path)


    def commit(self):
        return self.app_db.commit()

#### Table Creation Methods ############################
    def createTables(self):

        log.d(_TAG, "Creating tables!")

        if (not self.createPermissionsTable()):
            log.e(_TAG, "failed to create permissions table!")
            return -1

        if (not self.createPermissionGroupsTable()):
            log.e(_TAG, "failed to create permission Groups table!")
            return -1

        if (not self.createActivitiesTable()):
            log.e(_TAG, "failed to create activities table!")
            return -1

        if (not self.createServicesTable()):
            log.e(_TAG, "failed to create services table!")
            return -1

        if (not self.createProvidersTable()):
            log.e(_TAG, "failed to create providers table!")
            return -1

        if (not self.createReceiversTable()):
            log.e(_TAG, "failed to create receivers table!")
            return -1

        if (not self.createAppUsesPermissionsTable()):
            log.e(_TAG, "failed to create app uses permissions table!")
            return -1

        if (not self.createSharedLibrariesTable()):
            log.e(_TAG, "failed to create Shared libraries table!")
            return -1

        if (not self.createProtectedBroadcastsTable()):
            log.e(_TAG, "failed to create protected broadcasts table!")
            return -1

        if (not self.createIntentFiltersTable()):
            log.e(_TAG, "failed to create intent filters table!")
            return -1

        if (not self.createIntentFilterToActivityTable()):
            log.e(_TAG, "failed to create activity to intent filter table!")
            return -1

        if (not self.createIntentFilterToServiceTable()):
            log.e(_TAG, "failed to create service to intent filter table!")
            return -1

        if (not self.createIntentFilterToReceiverTable()):
            log.e(_TAG, "failed to create receiver to intent filter table!")
            return -1

        if (not self.createIntentCategorysTable()):
            log.e(_TAG, "failed to create intent categorys table!")
            return -1

        if (not self.createIntentActionsTable()):
            log.e(_TAG, "failed to create intent actions table!")
            return -1

        if (not self.createIntentDatasTable()):
            log.e(_TAG, "failed to create intent datas table!")
            return -1

        if (not self.createSignaturesTable()):
            log.e(_TAG, "failed to create signatures table!")
            return -1

        if (not self.createAppUsesSignaturesTable()):
            log.e(_TAG, "failed to create app uses signatures table!")
            return -1

        return 0

    def createAppsTable(self):

        """Create the 'apps' table"""

        sql = ('CREATE TABLE IF NOT EXISTS apps('
               'id INTEGER PRIMARY KEY AUTOINCREMENT, '
               'package_name TEXT, '
               'project_name TEXT UNIQUE NOT NULL, '
               'decoded_path TEXT, '
               'has_native INTEGER DEFAULT 0, '
               'min_sdk_version INTEGER DEFAULT 0, '
               'target_sdk_version INTEGER DEFAULT 0, '
               'version_name TEXT, '
               'version_code TEXT, '
               'permission INTEGER DEFAULT 0, '
               'debuggable INTEGER, '
               'successfully_pulled INTEGER DEFAULT 0, '
               'successfully_unpacked INTEGER DEFAULT 0, '
               'shared_user_id TEXT, '
               'shared_user_label TEXT, '
               'allow_backup INTEGER)')

        return self.app_db.execute(sql)

    def createPermissionGroupsTable(self):

        sql = ('CREATE TABLE IF NOT EXISTS permission_groups'
               '('
               'id INTEGER PRIMARY KEY AUTOINCREMENT,'
               'name TEXT NOT NULL,'
               'application_id INTEGER,'
               'FOREIGN KEY(application_id) REFERENCES apps(id)'
               ')')

        return self.app_db.execute(sql)

    def createPermissionsTable(self):

        sql = ('CREATE TABLE IF NOT EXISTS permissions'
               '('
               'id INTEGER PRIMARY KEY AUTOINCREMENT,'
               'name TEXT NOT NULL,'
               'permission_group INTEGER,'
               'protection_level TEXT,'
               'application_id INTEGER,'
               'FOREIGN KEY(application_id) REFERENCES apps(id),'
               'FOREIGN KEY(permission_group) REFERENCES permission_groups(id)'
               ')')

        rtn = self.app_db.execute(sql)
        if rtn != 0:
            return rtn

        # TODO: This is hacky.
        sql = ('INSERT INTO permissions(id, name, permission_group, protection_level, application_id) '
               "VALUES (0, 'None', 0, 'None',0)")

        return self.app_db.execute(sql)

    def createActivitiesTable(self):

        sql = ('CREATE TABLE IF NOT EXISTS activities'
               '('
               'id INTEGER PRIMARY KEY AUTOINCREMENT,'
               'name TEXT NOT NULL,'
               'permission INTEGER,'
               'exported TEXT,'
               'enabled TEXT,'
               'application_id INTEGER,'
               'FOREIGN KEY(application_id) REFERENCES apps(id),'
               'FOREIGN KEY(permission) REFERENCES permissions(id)'
               ')')

        return self.app_db.execute(sql)

    def createServicesTable(self):

        sql = ('CREATE TABLE IF NOT EXISTS services'
               '('
               'id INTEGER PRIMARY KEY AUTOINCREMENT,'
               'name TEXT NOT NULL,'
               'permission INTEGER,'
               'exported TEXT,'
               'enabled TEXT,'
               'application_id INTEGER,'
               'FOREIGN KEY(application_id) REFERENCES apps(id),'
               'FOREIGN KEY(permission) REFERENCES permissions(id)'
               ')')

        return self.app_db.execute(sql)

    def createProvidersTable(self):

        sql = ('CREATE TABLE IF NOT EXISTS providers'
               '('
               'id INTEGER PRIMARY KEY AUTOINCREMENT,'
               'authorities TEXT NOT NULL,'
               'name TEXT NOT NULL,'
               'permission INTEGER,'
               'read_permission INTEGER,'
               'write_permission INTEGER,'
               'exported TEXT,'
               'enabled TEXT,'
               'grant_uri_permissions INTEGER,'
               'path_permission_data TEXT,'
               'grant_uri_permission_data TEXT,'
               'application_id INTEGER,'
               'FOREIGN KEY(application_id) REFERENCES apps(id),'
               'FOREIGN KEY(permission) REFERENCES permissions(id),'
               'FOREIGN KEY(read_permission) REFERENCES permissions(id),'
               'FOREIGN KEY(write_permission) REFERENCES permissions(id)'
               ')')

        return self.app_db.execute(sql)

    def createReceiversTable(self):

        sql = ('CREATE TABLE IF NOT EXISTS receivers'
               '('
               'id INTEGER PRIMARY KEY AUTOINCREMENT,'
               'name TEXT NOT NULL,'
               'permission INTEGER,'
               'exported TEXT,'
               'enabled TEXT,'
               'application_id INTEGER,'
               'FOREIGN KEY(application_id) REFERENCES apps(id)'
               ')')

        return self.app_db.execute(sql)

    def createAppUsesPermissionsTable(self):

        sql = ('CREATE TABLE IF NOT EXISTS app_uses_permissions'
               '('
               'id INTEGER PRIMARY KEY AUTOINCREMENT,'
               'application_id INTEGER,'
               'permission_id INTEGER,'
               'FOREIGN KEY(application_id) REFERENCES apps(id),'
               'FOREIGN KEY(permission_id) REFERENCES permissions(id)'
               ')')

        return self.app_db.execute(sql)

    def createSharedLibrariesTable(self):

        sql = ('CREATE TABLE IF NOT EXISTS shared_libraries'
               '('
               'id INTEGER PRIMARY KEY AUTOINCREMENT,'
               'name TEXT NOT NULL,'
               'application_id INTEGER,'
               'FOREIGN KEY(application_id) REFERENCES apps(id)'
               ')')

        return self.app_db.execute(sql)

    def createProtectedBroadcastsTable(self):

        sql = ('CREATE TABLE IF NOT EXISTS protected_broadcasts'
               '('
               'id INTEGER PRIMARY KEY AUTOINCREMENT,'
               'name TEXT NOT NULL,'
               'application_id INTEGER,'
               'FOREIGN KEY(application_id) REFERENCES apps(id)'
               ')')

        return self.app_db.execute(sql)

    # Intent Tables
    def createIntentFiltersTable(self):

        sql = ('CREATE TABLE IF NOT EXISTS intent_filters'
               '('
               'id INTEGER PRIMARY KEY AUTOINCREMENT,'
               'priority INTEGER'
               ')')

        return self.app_db.execute(sql)

    def createIntentFilterToActivityTable(self):

        sql = ('CREATE TABLE IF NOT EXISTS intent_filter_to_activity'
               '('
               'id INTEGER PRIMARY KEY AUTOINCREMENT,'
               'intent_filter_id INTEGER,'
               'activity_id INTEGER,'
               'FOREIGN KEY(activity_id) REFERENCES activities(id),'
               'FOREIGN KEY(intent_filter_id) REFERENCES intent_filters(id)'
               ')')

        return self.app_db.execute(sql)

    def createIntentFilterToServiceTable(self):

        sql = ('CREATE TABLE IF NOT EXISTS intent_filter_to_service'
               '('
               'id INTEGER PRIMARY KEY AUTOINCREMENT,'
               'intent_filter_id INTEGER,'
               'service_id INTEGER,'
               'FOREIGN KEY(service_id) REFERENCES services(id),'
               'FOREIGN KEY(intent_filter_id) REFERENCES intent_filters(id)'
               ')')

        return self.app_db.execute(sql)

    def createIntentFilterToReceiverTable(self):

        sql = ('CREATE TABLE IF NOT EXISTS intent_filter_to_receiver'
               '('
               'id INTEGER PRIMARY KEY AUTOINCREMENT,'
               'intent_filter_id INTEGER,'
               'receiver_id INTEGER,'
               'FOREIGN KEY(receiver_id) REFERENCES receivers(id),'
               'FOREIGN KEY(intent_filter_id) REFERENCES intent_filters(id)'
               ')')

        return self.app_db.execute(sql)

    def createIntentCategorysTable(self):

        sql = ('CREATE TABLE IF NOT EXISTS intent_categories'
               '('
               'id INTEGER PRIMARY KEY AUTOINCREMENT,'
               'name STRING,'
               'intent_filter_id INTEGER,'
               'FOREIGN KEY(intent_filter_id) REFERENCES intent_filters(id)'
               ')')

        return self.app_db.execute(sql)

    def createIntentActionsTable(self):

        sql = ('CREATE TABLE IF NOT EXISTS intent_actions'
               '('
               'id INTEGER PRIMARY KEY AUTOINCREMENT,'
               'name STRING,'
               'intent_filter_id INTEGER,'
               'FOREIGN KEY(intent_filter_id) REFERENCES intent_filters(id)'
               ')')

        return self.app_db.execute(sql)

    def createIntentDatasTable(self):

        sql = ('CREATE TABLE IF NOT EXISTS intent_datas'
               '('
               'id INTEGER PRIMARY KEY AUTOINCREMENT,'
               'port STRING,'
               'host STRING,'
               'mime_type STRING,'
               'path STRING,'
               'path_pattern STRING,'
               'path_prefix STRING,'
               'scheme STRING,'
               'intent_filter_id INTEGER,'
               'FOREIGN KEY(intent_filter_id) REFERENCES intent_filters(id)'
               ')')

        return self.app_db.execute(sql)

    def createSignaturesTable(self):

        sql = ('CREATE TABLE IF NOT EXISTS signatures'
               '('
               'id INTEGER PRIMARY KEY AUTOINCREMENT,'
               'issuer STRING,'
               'subject STRING,'
               'certificate STRING NOT NULL'
               ')')

        return self.app_db.execute(sql)

    def createAppUsesSignaturesTable(self):

        sql = ('CREATE TABLE IF NOT EXISTS app_uses_signatures'
               '('
               'id INTEGER PRIMARY KEY AUTOINCREMENT,'
               'application_id INTEGER,'
               'signature_id INTEGER,'
               'FOREIGN KEY(application_id) REFERENCES apps(id),'
               'FOREIGN KEY(signature_id) REFERENCES signatures(id)'
               ')')

        return self.app_db.execute(sql)
    # End Table Creation

#### Table Deletion Methods ############################
    def dropTables(self):

        self.app_db.execute('''DROP TABLE IF EXISTS shared_libraries''')
        self.app_db.execute('''DROP TABLE IF EXISTS app_uses_permissions''')
        self.app_db.execute('''DROP TABLE IF EXISTS receivers''')
        self.app_db.execute('''DROP TABLE IF EXISTS providers''')
        self.app_db.execute('''DROP TABLE IF EXISTS services''')
        self.app_db.execute('''DROP TABLE IF EXISTS activities''')
        self.app_db.execute('''DROP TABLE IF EXISTS permission_groups''')
        self.app_db.execute('''DROP TABLE IF EXISTS permissions''')
        self.app_db.execute('''DROP TABLE IF EXISTS protected_broadcasts''')
        self.app_db.execute('''DROP TABLE IF EXISTS intent_filters''')
        self.app_db.execute('''DROP TABLE IF EXISTS intent_filter_to_activity''')
        self.app_db.execute('''DROP TABLE IF EXISTS intent_filter_to_service''')
        self.app_db.execute('''DROP TABLE IF EXISTS intent_filter_to_receiver''')
        self.app_db.execute('''DROP TABLE IF EXISTS intent_categories''')
        self.app_db.execute('''DROP TABLE IF EXISTS intent_actions''')
        self.app_db.execute('''DROP TABLE IF EXISTS intent_datas''')
        self.app_db.execute('''DROP TABLE IF EXISTS signatures''')
        self.app_db.execute('''DROP TABLE IF EXISTS app_uses_signatures''')

    # End Table Deletion

#### Private Methods #####################################
    def _getLastId(self, table_name):

        sql = ("SELECT seq FROM SQLITE_SEQUENCE WHERE name='%s'" % table_name)
        cur = self.app_db.cursor()
        cur.execute(sql)

        try:
            return cur.fetchone()[0]
        except:
            return 0

#### Table Modification Methods ############################
    def addNewApp(self, app):

        """Add just the application name to our DB"""

        package_name, project_name = app
        sql = ('INSERT INTO apps(package_name, project_name) '
               'VALUES (?, ?)')

        self.app_db.execute(sql, (package_name, project_name))
        self.app_db.commit()
        return 0

    def addPermissionGroup(self, permission_group):

        name = permission_group.name
        application_id = permission_group.application_id

        sql = ('INSERT INTO permission_groups(name, application_id) '
               "VALUES ('%s', %i)" % (name, application_id))

        return self.app_db.execute(sql)


    def addPermission(self, permission):

        name = permission.name
        protection_level = permission.protection_level
        permission_group = permission.permission_group
        application_id = permission.application_id

        if permission_group is None:
            permission_group_id = 0
        else:
            permission_group_id = permission_group._id


        sql = ('INSERT INTO permissions(name, permission_group, protection_level, application_id) '
               "VALUES('%s',%i,'%s',%i)" % (name, permission_group_id, protection_level, application_id))

        return self.app_db.execute(sql)

    def addAppUsesPermission(self, application_id, permission_id):

        sql = ('INSERT INTO app_uses_permissions(application_id, permission_id) '
               "VALUES (%i,%i)" % (application_id, permission_id))

        return self.app_db.execute(sql)

    def addAppUsesSignature(self, application_id, signature_id):

        sql = ('INSERT INTO app_uses_signatures'
               '(application_id, signature_id) '
               "VALUES (%i, %i)" % (application_id, signature_id))

        return self.app_db.execute(sql)

    def addActivity(self, activity):

        name = activity.name
        enabled = activity.enabled
        exported = activity.exported
        application_id = activity.application_id

        permission = activity.permission

        if permission != None:
            permission_id = permission._id
        else:
            permission_id = 0

        sql = ('INSERT INTO activities(name, permission, exported, enabled, application_id) '
               "VALUES ('%s',%i,'%s','%s',%i)"  % (name, permission_id, exported, enabled,
                                                        application_id))

        return self.app_db.execute(sql)

    def addService(self, service):

        name = service.name
        enabled = service.enabled
        exported = service.exported
        application_id = service.application_id

        permission = service.permission

        if permission != None:
            permission_id = permission._id
        else:
            permission_id = 0

        sql = ('INSERT INTO services(name, permission, exported, enabled, application_id) '
               "VALUES ('%s',%i,'%s','%s',%i)"  % (name, permission_id, exported, enabled,
                                                        application_id))

        return self.app_db.execute(sql)


    def addProvider(self, provider):

        name = provider.name
        authorities = ';'.join(provider.authorities)
        enabled = provider.enabled
        exported = provider.exported
        grant_uri_permissions = provider.grant_uri_permissions
        grant_uri_permission_data = base64.b64encode(provider.grant_uri_permission_data)
        path_permission_data = base64.b64encode(provider.path_permission_data)

        if grant_uri_permissions == True:
            grant_uri_permissions = 1
        elif grant_uri_permissions == False:
            grant_uri_permissions = 0

        application_id = provider.application_id

        permission = provider.permission
        read_permission = provider.read_permission
        write_permission = provider.write_permission

        if permission != None:
            permission_id = permission._id
        else:
            permission_id = 0

        if read_permission != None:
            read_permission_id = read_permission._id
        else:
            read_permission_id = 0

        if write_permission != None:
            write_permission_id = write_permission._id
        else:
            write_permission_id = 0

        sql = ('INSERT INTO providers'
               '(name, authorities, permission, read_permission, write_permission, exported, enabled, '
               'grant_uri_permissions, grant_uri_permission_data, path_permission_data, application_id) '
               "VALUES ('%s','%s',%i,%i,%i,'%s','%s','%s','%s','%s',%i)"
                % (name, authorities, permission_id, read_permission_id, write_permission_id, exported, enabled,
                   grant_uri_permissions, grant_uri_permission_data, path_permission_data, application_id))

        return self.app_db.execute(sql)


    def addReceiver(self, receiver):

        name = receiver.name
        enabled = receiver.enabled
        exported = receiver.exported
        application_id = receiver.application_id

        permission = receiver.permission

        if permission != None:
            permission_id = permission._id
        else:
            permission_id = 0

        sql = ('INSERT INTO receivers(name, permission, exported, enabled, application_id) '
               "VALUES ('%s',%i,'%s','%s',%i)"  % (name, permission_id, exported, enabled,
                                                        application_id))

        return self.app_db.execute(sql)

    def addShared(self, application_id, name):

        sql = ('INSERT INTO shared_libraries(name, application_id)'
            "VALUES( '%s',%i)" % (name, application_id))

        return self.app_db.execute(sql)

    def addProtectedBroadcast(self, name, application_id):

        sql = ('INSERT INTO protected_broadcasts(name, application_id) '
               "VALUES ('%s', %i)"  % (name, application_id))

        return self.app_db.execute(sql)

    def addActivityIntentFilter(self, intent_filter, activity_id):

        priority = int(intent_filter.getPriority())

        # First we add to intent_filter table
        sql = ('INSERT INTO intent_filters(priority) '
               'VALUES (%i)' % (priority))

        if (not self.app_db.execute(sql)):
            log.e(_TAG, "Error adding intent filter!")
            return -3

        # Next we map intent --> activity
        _id = self._getLastId("intent_filters")

        sql = ('INSERT INTO intent_filter_to_activity'
               '(activity_id, intent_filter_id) '
               'VALUES(%i, %i)' % (activity_id, _id))

        if (not self.app_db.execute(sql)):
            log.e(_TAG, "Error adding intent filter mapping!")
            return -3

        # Last we add the action, category, and data.
        for action in intent_filter.getActions():
            self.addIntentAction(action, _id)

        for category in intent_filter.getCategories():
            self.addIntentCategory(category, _id)

        for data in intent_filter.getDatas():
            self.addIntentData(data, _id)

    def addServiceIntentFilter(self, intent_filter, service_id):

        priority = int(intent_filter.getPriority())

        # First we add to intent_filter table
        sql = ('INSERT INTO intent_filters(priority) '
               'VALUES (%i)' % (priority))

        if (not self.app_db.execute(sql)):
            log.e(_TAG, "Error adding intent filter!")
            return -3

        # Next we map intent --> service
        _id = self._getLastId("intent_filters")

        sql = ('INSERT INTO intent_filter_to_service'
               '(service_id, intent_filter_id) '
               'VALUES(%i, %i)' % (service_id, _id))

        if (not self.app_db.execute(sql)):
            log.e(_TAG, "Error adding intent filter mapping!")
            return -3

        # Last we add the action, category, and data.
        for action in intent_filter.getActions():
            self.addIntentAction(action, _id)

        for category in intent_filter.getCategories():
            self.addIntentCategory(category, _id)

        for data in intent_filter.getDatas():
            self.addIntentData(data, _id)

    def addReceiverIntentFilter(self, intent_filter, receiver_id):

        priority = int(intent_filter.getPriority())

        # First we add to intent_filter table
        sql = ('INSERT INTO intent_filters(priority) '
               'VALUES (%i)' % (priority))

        if (not self.app_db.execute(sql)):
            log.e(_TAG, "Error adding intent filter!")
            return -3

        # Next we map intent --> receiver
        _id = self._getLastId("intent_filters")

        sql = ('INSERT INTO intent_filter_to_receiver'
               '(receiver_id, intent_filter_id) '
               'VALUES(%i, %i)' % (receiver_id, _id))

        if (not self.app_db.execute(sql)):
            log.e(_TAG, "Error adding intent filter mapping!")
            return -3

        # Last we add the action, category, and data.
        for action in intent_filter.getActions():
            self.addIntentAction(action, _id)

        for category in intent_filter.getCategories():
            self.addIntentCategory(category, _id)

        for data in intent_filter.getDatas():
            self.addIntentData(data, _id)


    def addIntentAction(self, action_name, intent_filter_id):

        sql = ('INSERT INTO intent_actions'
               '(name, intent_filter_id) '
               "VALUES('%s', %i)" % (action_name, intent_filter_id))

        return self.app_db.execute(sql)

    def addIntentCategory(self, category_name, intent_filter_id):

        sql = ('INSERT INTO intent_categories'
               '(name, intent_filter_id) '
               "VALUES('%s', %i)" % (category_name, intent_filter_id))

        return self.app_db.execute(sql)


    def addIntentData(self, data, intent_filter_id):

        sql = ('INSERT INTO intent_datas'
               '(scheme, host, port, path, path_pattern, '
               ' path_prefix, mime_type, intent_filter_id) '
               "VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', %i)"
                 % (data.scheme, data.host, data.port, data.path,
                    data.path_pattern, data.path_prefix,
                    data.mime_type, intent_filter_id))

        return self.app_db.execute(sql)

    def addSignature(self, signature):

        sql = ('INSERT INTO signatures'
               '(issuer, subject, certificate) '
               "VALUES('%s', '%s', '%s')"
                 % (signature.issuer, signature.subject,
                    signature.cert))

        return self.app_db.execute(sql)
    # End Table Modification

#### Table Querying Methods ############################
    def getApps(self, dont_resolve=False):

        app_list = list()

        sql = ('SELECT id, package_name, project_name, '
               'decoded_path, has_native, min_sdk_version, '
               'target_sdk_version, version_name, version_code, '
               'permission, debuggable, successfully_unpacked, '
               'shared_user_id, shared_user_label, allow_backup '
               'FROM apps '
               'ORDER BY id')

        for line in self.app_db.execute(sql):

            id = line[0]
            package_name = line[1]
            project_name = line[2]
            decoded_path = line[3]
            has_native = line[4]
            min_sdk_version = line[5]
            target_sdk_version = line[6]
            version_name = line[7]
            version_code = line[8]
            permission_id = line[9]
            debuggable = line[10]
            successfully_unpacked = line[11]
            shared_user_id = line[12]
            shared_user_label = line[13]
            allow_backup = line[14]

            if not dont_resolve:
                if permission_id != 0 and permission_id is not None:
                    permission = self.resolvePermissionById(permission_id)
                else:
                    permission = None
            else:
                permission = None

            app_list.append(
                    Application(package_name, project_name, decoded_path,
                                has_native, min_sdk_version, target_sdk_version,
                                version_name, version_code, permission,
                                debuggable, shared_user_id, shared_user_label,
                                allow_backup,
                                id=id))
        return app_list

    def getFailedToPullApps(self):

        """Return only the failed to pull applications"""

        app_list = list()

        sql = ('SELECT package_name, project_name '
               'FROM apps '
               'WHERE successfully_pulled=0 '
               'ORDER BY project_name')

        for line in self.app_db.execute(sql):

            package_name = line[0]
            project_name = line[1]

            app_list.append((package_name, project_name))
        return app_list

    def getFailedToUnpackApps(self):

        """Return only the failed to unpack applications"""

        app_list = list()

        sql = ('SELECT id, package_name, project_name, '
               'decoded_path, has_native, min_sdk_version, '
               'target_sdk_version, version_name, version_code, '
               'permission, debuggable, successfully_unpacked, '
               'shared_user_id, shared_user_label, allow_backup '
               'FROM apps '
               'WHERE successfully_unpacked=0 '
               'ORDER BY id')

        for line in self.app_db.execute(sql):

            id = line[0]
            package_name = line[1]
            project_name = line[2]
            decoded_path = line[3]
            has_native = line[4]
            min_sdk_version = line[5]
            target_sdk_version = line[6]
            version_name = line[7]
            version_code = line[8]
            permission_id = line[9]
            debuggable = line[10]
            successfully_unpacked = line[11]
            shared_user_id = line[12]
            shared_user_label = line[13]
            allow_backup = line[14]

            permission = None

            app_list.append(
                    Application(package_name, project_name, decoded_path,
                                has_native, min_sdk_version, target_sdk_version,
                                version_name, version_code, permission,
                                debuggable, shared_user_id, shared_user_label,
                                allow_backup, id=id))
        return app_list


    def getAppById(self, application_id):

        sql = ('SELECT id, package_name, project_name, '
               'decoded_path, has_native, min_sdk_version, '
               'target_sdk_version, version_name, version_code, '
               'permission, debuggable, successfully_unpacked, '
               'shared_user_id, shared_user_label, allow_backup '
               'FROM apps '
               "WHERE id=%d "
               'ORDER BY id '
               'LIMIT 1' % application_id)

        c = self.app_db.cursor()

        rtn = c.execute(sql)
        try:

            fetched = c.fetchone()
            if fetched == None:
                return None

            (id, package_name, project_name, decoded_path, has_native,
             min_sdk_version, target_sdk_version, version_name, version_code,
             permission_id, debuggable, successfully_unpacked, shared_user_id,
             shared_user_label, allow_backup) = fetched

            if permission_id != 0 and permission_id is not None:
                permission = self.resolvePermissionById(permission_id)
            else:
                permission = None

            return Application(package_name, project_name, decoded_path,
                               has_native, min_sdk_version, target_sdk_version,
                               version_name, version_code, permission,
                               debuggable, shared_user_id, shared_user_label,
                               allow_backup, id=id)
        except TypeError:
            log.e(_TAG, "Unable to resolve application ID %d!" % id)
            return 0

    def getAppByName(self, name):

        sql = ('SELECT id, package_name, project_name, '
               'decoded_path, has_native, min_sdk_version, '
               'target_sdk_version, version_name, version_code, '
               'permission, debuggable, successfully_unpacked, '
               'shared_user_id, shared_user_label, allow_backup '
               'FROM apps '
               "WHERE project_name='%s' "
               'ORDER BY id '
               'LIMIT 1' % name)

        c = self.app_db.cursor()

        rtn = c.execute(sql)
        try:

            fetched = c.fetchone()
            if fetched == None:
                return None

            (id, package_name, project_name, decoded_path, has_native,
             min_sdk_version, target_sdk_version, version_name, version_code,
             permission_id, debuggable, successfully_unpacked, shared_user_id,
             shared_user_label, allow_backup) = fetched

            if permission_id != 0 and permission_id is not None:
                permission = self.resolvePermissionById(permission_id)
            else:
                permission = None

            return Application(package_name, project_name, decoded_path,
                               has_native, min_sdk_version, target_sdk_version,
                               version_name, version_code, permission,
                               debuggable, shared_user_id, shared_user_label,
                               allow_backup, id=id)
        except TypeError:
            log.e(_TAG, "Unable to resolve application ID %d!" % id)
            return 0

    def getAppsBySignature(self, signature):

        c = self.app_db.cursor()

        app_list = list()

        certificate = signature.cert

        sql = ('SELECT a.id '
               'FROM apps a '
               'JOIN app_uses_signatures aus '
               'ON aus.application_id = a.id '
               'JOIN signatures s '
               'ON aus.signature_id = s.id '
               "WHERE s.certificate='%s'" % certificate)

        for line in c.execute(sql):
            _id = line[0]
            app_list.append(self.getAppById(_id))

        return app_list

    def getAppSignature(self, app):

        c = self.app_db.cursor()
        project_name = app.project_name
        signature = Signature()

        rtn = c.execute('SELECT s.id, s.issuer, s.subject, '
                        's.certificate '
                        'FROM signatures s '
                        'JOIN app_uses_signatures aus '
                        'ON aus.signature_id = s.id '
                        'JOIN apps a '
                        'ON aus.application_id = a.id '
                        "WHERE a.project_name='%s'" %
                                    (project_name))

        try:
            _id, issuer, subject, certificate = c.fetchone()

            signature._id = _id
            signature.issuer = issuer
            signature.subject = subject
            signature.cert = certificate

            return signature

        except TypeError:
            log.e(_TAG, "Unable to find app signature for '%s'" %
                                                        project_name)
            return None

    def getAppsBySharedUserId(self, shared_id_name):

        c = self.app_db.cursor()

        app_list = list()

        sql = ('SELECT id '
               'FROM apps '
               "WHERE shared_user_id='%s'" % shared_id_name)

        for line in c.execute(sql):
            _id = line[0]
            app_list.append(self.getAppById(_id))

        return app_list

    def resolveGroupByName(self, permission_group_name):
        c = self.app_db.cursor()

        rtn = c.execute('SELECT id, name, application_id '
                        'FROM permission_groups '
                        "WHERE name=\"%s\"" % permission_group_name)

        try:
            id, name, application_id = c.fetchone()
            return PermissionGroup(name, int(application_id), id=int(id))

        except TypeError:
            log.e(_TAG, "Unable to resolve group \"%s\"!" % permission_group_name)
            return None

    def resolveGroupById(self, permission_group_id):

        c = self.app_db.cursor()

        rtn = c.execute('SELECT id, name, application_id '
                        'FROM permission_groups '
                        "WHERE id=%i" % permission_group_id)

        try:
            id, name, application_id = c.fetchone()
            return PermissionGroup(name, int(application_id), id=int(id))

        except TypeError:
            log.e(_TAG, "Unable to resolve group ID %i!" % permission_group_id)
            return 0

    def resolvePermissionByName(self, permission_name):

        c = self.app_db.cursor()

        rtn = c.execute('SELECT id, name, permission_group, protection_level, '
                        'application_id '
                        'FROM permissions '
                        "WHERE name=\"%s\"" % permission_name)

        try:
            id, name, permission_group_id, protection_level, application_id = c.fetchone()

            if permission_group_id is not 0:
                permission_group = self.resolveGroupById(permission_group_id)
            else:
                permission_group = None

            return Permission(name, protection_level, permission_group, int(application_id), id=int(id))

        except TypeError:
            return None

    def resolvePermissionById(self, permission_id):

        c = self.app_db.cursor()

        rtn = c.execute('SELECT id, name, permission_group, protection_level, '
                        'application_id '
                        'FROM permissions '
                        "WHERE id=%d" % permission_id)

        try:
            id, name, permission_group_id, protection_level, application_id = c.fetchone()

            if permission_group_id is not 0:
                permission_group = self.resolveGroupById(permission_group_id)
            else:
                permission_group = None

            return Permission(name, protection_level, permission_group, int(application_id), id=int(id))

        except TypeError:
            log.e(_TAG, "Unable to resolve permission by id %d!" % permission_id)
            return None

    def resolveSignature(self, signature):

        c = self.app_db.cursor()

        cert = signature.cert

        c.execute('SELECT id '
               'FROM signatures '
               "WHERE certificate='%s'" % cert)

        # If we can fetch one, we already know about this signature.
        try:
            _id = c.fetchone()[0]
            signature._id = _id
            return signature

        # This means it doesnt exist, return None
        except TypeError:
            return None

    def getAppPermissions(self, application_id):

        perm_list = list()
        c = self.app_db.cursor()

        sql = ('SELECT id, name, permission_group, protection_level '
               'FROM permissions '
               'WHERE application_id=%d' % application_id)

        for line in c.execute(sql):
            _id = line[0]
            name = line[1]
            permission_group_id = line[2]
            protection_level = line[3]

            if permission_group_id != 0:
                permission_group = self.resolveGroupById(permission_group_id)
            else:
                permission_group = None

            perm_list.append(Permission(name, protection_level, permission_group,
                             application_id, id=_id))

        return perm_list

    def getAppUsesPermissions(self, application_id):

        uses_perm_list = list()
        c = self.app_db.cursor()

        sql = ('SELECT permission_id FROM app_uses_permissions '
               'WHERE application_id=%d' % application_id)

        for line in c.execute(sql):
            permission_id = line[0]

            permission = self.resolvePermissionById(permission_id)

            uses_perm_list.append(permission)

        return uses_perm_list

    def getAppActivities(self, app):

        activity_list = list()
        c = self.app_db.cursor()

        sql = ('SELECT id, name, permission, exported, '
               'enabled, application_id '
               'FROM activities '
               'WHERE application_id=%d' % app._id)

        for line in c.execute(sql):
            _id = line[0]
            name = line[1]
            permission_id = line[2]
            exported = line[3]
            enabled = line[4]
            application_id = line[5]

            if exported == "None":
                exported = None
            elif exported == "False":
                exported = False
            elif exported == "True":
                exported = True
            else:
                log.e(_TAG, "Unknown export value :  %s" % exported)

            if enabled == "None":
                enabled = None
            elif enabled == "False":
                enabled = False
            elif enabled == "True":
                enabled = True
            else:
                log.e(_TAG, "Unknown export value :  %s" % enabled)

            # The component perm takes precedence
            if permission_id != 0:
                permission = self.resolvePermissionById(permission_id)

            # Otherwise, check the app perm
            else:
                if app.permission is not None:
                    permission = app.permission
                else:
                    permission = None

            activity_list.append(Activity(name, enabled, exported, permission,
                                          application_id, id=_id))

        return activity_list


    def getAppServices(self, app):

        service_list = list()
        c = self.app_db.cursor()

        sql = ('SELECT id, name, permission, exported, '
               'enabled, application_id '
               'FROM services '
               'WHERE application_id=%d' % app._id)

        for line in c.execute(sql):

            _id = line[0]
            name = line[1]
            permission_id = line[2]
            exported = line[3]

            enabled = line[4]
            application_id = line[5]

            if exported == "None":
                exported = None
            elif exported == "False":
                exported = False
            elif exported == "True":
                exported = True
            else:
                log.e(_TAG, "Unknown export value :  %s" % exported)

            if enabled == "None":
                enabled = None
            elif enabled == "False":
                enabled = False
            elif enabled == "True":
                enabled = True
            else:
                log.e(_TAG, "Unknown export value :  %s" % enabled)

            # The component perm takes precedence
            if permission_id != 0:
                permission = self.resolvePermissionById(permission_id)

            # Otherwise, check the app perm
            else:
                if app.permission is not None:
                    permission = app.permission
                else:
                    permission = None

            service_list.append(Service(name, enabled, exported, permission,
                                        application_id, id=_id))
        return service_list

    def getAppProviders(self, app):

        provider_list = list()
        c = self.app_db.cursor()

        sql = ('SELECT id, authorities, name, permission, '
               'read_permission, write_permission, '
               'exported, enabled, grant_uri_permissions, '
               'path_permission_data, grant_uri_permission_data, '
               'application_id '
               'FROM providers '
               'WHERE application_id=%d' % app._id)

        for line in c.execute(sql):

            _id = line[0]
            authorities = line[1].split(';')
            name = line[2]
            permission_id = line[3]
            read_permission_id = line[4]
            write_permission_id = line[5]
            exported = line[6]
            enabled = line[7]
            grant_uri_permissions = line[8]
            path_permission_data = base64.b64decode(line[9])

            grant_uri_permission_data = base64.b64decode(line[10])
            application_id = line[11]

            if exported == "None":
                exported = None
            elif exported == "False":
                exported = False
            elif exported == "True":
                exported = True
            else:
                log.e(_TAG, "Unknown export value :  %s" % exported)

            if enabled == "None":
                enabled = None
            elif enabled == "False":
                enabled = False
            elif enabled == "True":
                enabled = True
            else:
                log.e(_TAG, "Unknown export value :  %s" % enabled)

            # The component perm takes precedence
            if permission_id != 0:
                permission = self.resolvePermissionById(permission_id)

            # Otherwise, check the app perm
            else:
                if app.permission is not None:
                    permission = app.permission
                else:
                    permission = None

            # Read Permission
            if read_permission_id != 0:
                read_permission = self.resolvePermissionById(read_permission_id)
            else:
                read_permission = None

            # Write Permission
            if write_permission_id != 0:
                write_permission = self.resolvePermissionById(write_permission_id)
            else:
                write_permission = None

            provider_list.append(Provider(name, authorities, enabled, exported,
                                          grant_uri_permissions, grant_uri_permission_data,
                                          path_permission_data, permission, read_permission,
                                          write_permission, application_id, id=_id))

        return provider_list

    def getAppReceivers(self, app):

        receiver_list = list()
        c = self.app_db.cursor()

        sql = ('SELECT id, name, permission, exported, '
               'enabled, application_id '
               'FROM receivers '
               'WHERE application_id=%d' % app._id)

        for line in c.execute(sql):

            _id = line[0]
            name = line[1]
            permission_id = line[2]
            exported = line[3]
            enabled = line[4]
            application_id = line[5]

            if exported == "None":
                exported = None
            elif exported == "False":
                exported = False
            elif exported == "True":
                exported = True
            else:
                log.e(_TAG, "Unknown export value :  %s" % exported)

            if enabled == "None":
                enabled = None
            elif enabled == "False":
                enabled = False
            elif enabled == "True":
                enabled = True
            else:
                log.e(_TAG, "Unknown export value :  %s" % enabled)

            # The component perm takes precedence
            if permission_id != 0:
                permission = self.resolvePermissionById(permission_id)

            # Otherwise, check the app perm
            else:
                if app.permission is not None:
                    permission = app.permission
                else:
                    permission = None

            receiver_list.append(Receiver(name, enabled, exported, permission,
                                          application_id, id=_id))

        return receiver_list

    def isProtectedAction(self, name):

        c = self.app_db.cursor()

        sql = ('SELECT id FROM protected_broadcasts '
               "WHERE name='%s'" % name)

        c.execute(sql)

        if c.fetchone() == None:
            return False
        else:
            return True

    def getProtectedActions(self):

        intent_list = list()
        c = self.app_db.cursor()

        sql = ('SELECT DISTINCT name '
               'FROM protected_broadcasts '
               'ORDER BY name')

        try:
            return map(lambda x: x[0], c.execute(sql))
        except:
            return None

    def getIntentFilters(self, component):

        intent_filters = list()

        # Determine the type
        if type(component) is Activity:
            component_table = "activities"
            id_name = "activity_id"
            join_table = "intent_filter_to_activity"

        elif type(component) is Service:
            component_table = "services"
            id_name = "service_id"
            join_table = "intent_filter_to_service"

        elif type(component) is Receiver:
            component_table = "receivers"
            id_name = "receiver_id"
            join_table = "intent_filter_to_receiver"

        else:
            log.e(_TAG, "Unknown component type, returning!")
            return None

        # Get a list of intent_filter references
        sql = ('SELECT if.id, if.priority FROM intent_filters if '
               'JOIN %s iftx ON if.id=iftx.intent_filter_id '
               'JOIN %s x ON iftx.%s=x.id '
               'WHERE x.id=%i' % (join_table, component_table, id_name, component._id))

        for row in self.app_db.execute(sql):

            tmp_actions = list()
            tmp_categories = list()
            tmp_datas = list()

            intent_filter_id = row[0]
            priority = row[1]

            # Actions first.
            sql = ('SELECT ia.name FROM intent_actions ia '
                   'JOIN intent_filters if ON if.id=ia.intent_filter_id '
                   'WHERE if.id=%i' % intent_filter_id)

            for action in self.app_db.execute(sql):
                tmp_actions.append(action[0])

            # Categories.
            sql = ('SELECT ic.name FROM intent_categories ic '
                   'JOIN intent_filters if ON if.id=ic.intent_filter_id '
                   'WHERE if.id=%i' % intent_filter_id)

            for category in self.app_db.execute(sql):
                tmp_categories.append(category[0])

            # Datas last.
            #sql = ('SELECT * '
            sql = ('SELECT port, host, mime_type, path, path_pattern, '
                   'path_prefix, scheme '
                   'FROM intent_datas id '
                   'JOIN intent_filters if ON if.id=id.intent_filter_id '
                   'WHERE if.id=%i' % intent_filter_id)

            for data in self.app_db.execute(sql):

                tmp_data = IntentData()

                tmp_data.port = data[0]
                tmp_data.host = data[1]
                tmp_data.mime_type = data[2]
                tmp_data.path = data[3]
                tmp_data.path_pattern = data[4]
                tmp_data.path_prefix = data[5]
                tmp_data.scheme = data[6]

                tmp_datas.append(tmp_data)

            # Now that we have a list of IDs, lets build the IF objects.
            intent_filters.append(IntentFilter(priority,
                        tmp_actions, tmp_categories, tmp_datas))

        return intent_filters

    def getPermissions(self):

        sql = ('SELECT id, name, permission_group, '
               'protection_level, application_id '
               'FROM permissions '
               'ORDER BY name')

        perm_list = list()
        c = self.app_db.cursor()

        for line in c.execute(sql):
            _id = line[0]
            name = line[1]
            permission_group_id = line[2]
            protection_level = line[3]
            application_id = line[4]

            if permission_group_id != 0:
                permission_group = self.resolveGroupById(permission_group_id)
            else:
                permission_group = None

            perm_list.append(Permission(name, protection_level, permission_group,
                               application_id, id=_id))

        return perm_list

########### Update Methods ########################
    def updateApplication(self, a):

        if a.permission is None:
            permission_id = 0
        else:
            permission_id = a.permission._id

        sql = ('UPDATE apps '
               'SET id=?, package_name=?, project_name=?, decoded_path=?, '
               'has_native=?, min_sdk_version=?, target_sdk_version=?, '
               'version_name=?, version_code=?, debuggable=?, permission=?, '
               'successfully_unpacked=?, shared_user_id=?, '
               'shared_user_label=?, allow_backup=? '
               'WHERE id=?')

        return self.app_db.execute(sql,
                    (a._id, a.package_name, a.project_name, a.decoded_path,
                     a.has_native, a.min_sdk_version, a.target_sdk_version,
                     a.version_name, a.version_code, a.debuggable,
                     permission_id, a.successfully_unpacked, a.shared_user_id,
                     a.shared_user_label, a.allow_backup, a._id))
# End class AppDb

# Helpers
def getAttrib(element, attrib, default="None"):

    try:
        return element.attrib['{http://schemas.android.com/apk/res/android}' + attrib]
    except KeyError:
        return default


def parseIntentFiltersFromXML(component_xml):

    intent_filters = list()

    for intent_filter in component_xml.findall(".//intent-filter"):

        tmp_actions = list()
        tmp_categories = list()
        tmp_data = list()
        tmp_priority = 0

        # Parse the actions
        for action in intent_filter.findall(".//action"):
            tmp_actions.append(getAttrib(action, 'name'))

        # Parse the categories
        for category in intent_filter.findall(".//category"):
            tmp_categories.append(getAttrib(category, 'name'))

        # Parse the datas
        for data in intent_filter.findall(".//data"):
            tmp_data.append(parseIntentDataFromXML(data))

        # Priority?
        tmp_priority = getAttrib(intent_filter, "priority", default=0)

        # Handle hex priorities
        if type(tmp_priority) is str and tmp_priority[0:2] == "0x":
            tmp_priority = int(tmp_priority, 16)

        # Add new IntentFilter
        intent_filters.append(IntentFilter(tmp_priority,
                            tmp_actions, tmp_categories, tmp_data))

    return intent_filters

def parseIntentDataFromXML(data_xml):

    tmp_data = IntentData()

    tmp_data.scheme = getAttrib(data_xml, "scheme")
    tmp_data.host = getAttrib(data_xml, "host")
    tmp_data.port = getAttrib(data_xml, "port")
    tmp_data.path = getAttrib(data_xml, "path")
    tmp_data.path_pattern = getAttrib(data_xml, "pathPattern")
    tmp_data.path_prefix = getAttrib(data_xml, "pathPrefix")
    tmp_data.mime_type = getAttrib(data_xml, "mimeType")

    return tmp_data

# Fix Permission, if a numerical is present
# Shamelessly rewritten from AOSP
def protectionToString(level):

    prot_level = "????"

    level_based = level & PROTECTION_MASK_BASE

    if level_based == PROTECTION_DANGEROUS:
        prot_level = "dangerous"
    elif level_based == PROTECTION_NORMAL:
        prot_level = "normal"
    elif level_based == PROTECTION_SIGNATURE:
        prot_level = "signature"
    elif level_based == PROTECTION_SIGNATURE_OR_SYSTEM:
        prot_level = "signatureOrSystem"

    if (level & PROTECTION_FLAG_SYSTEM) != 0:
        prot_level += "|system"
    if (level & PROTECTION_FLAG_DEVELOPMENT) != 0:
        prot_level += "|development"

    return prot_level
