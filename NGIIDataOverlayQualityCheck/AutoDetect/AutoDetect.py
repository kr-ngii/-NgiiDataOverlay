# -*- coding: utf-8 -*-
import os
import ConfigParser
import psycopg2
from psycopg2.sql import SQL, Identifier
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import threading
import platform
import subprocess
import time
import glob
import io

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

from qgis.core import *

# class SelectInspectData(QDialog, Ui_SelectInspectData):
DbInfoDialog_FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'DbInfo.ui'))


class DbInfoDialog(QDialog, DbInfoDialog_FORM_CLASS):

    inspectWidget = None
    __oldDataDir = None

    def __init__(self, parent=None):
        super(DbInfoDialog, self).__init__(parent)
        self.setupUi(self)
        self.parent = parent


# CLASS for multitasking
class CmdThread(threading.Thread):
    def __init__(self, commandList):
        self.commandList = commandList
        threading.Thread.__init__(self)

    def run(self):
        if platform.system() == 'Windows':
            subprocess.check_call(self.commandList, creationflags=0x08000000)
        else:
            subprocess.check_call(self.commandList, stderr=subprocess.STDOUT)
        return


def threadExecuteCmd(commandList):
    trd = CmdThread(commandList)
    trd.start()

    while threading.activeCount() > 1:
        QgsApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
        time.sleep(0.1)


class DBThread(threading.Thread):
    def __init__(self, cursor, query, param):
        self.cursor = cursor
        self.query = query
        self.param = param
        threading.Thread.__init__(self)

    def run(self):
        if self.param is None:
            self.cursor.execute(self.query)
        else:
            self.cursor.execute(self.query, self.param)

        return


def threadExecuteSql(cursor, sql, param=None):
    dbt = DBThread(cursor, sql, param)
    dbt.start()

    while threading.activeCount() > 1:
        QgsApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
        time.sleep(0.1)


AutoDetect_FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'AutoDetect.ui'))


class AutoDetect(QDialog, AutoDetect_FORM_CLASS):

    PROPERTIES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pgInfo", "connection.ini")
    SQL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pgInfo", "sql.ini")

    ORIGIN_SCHEMA = 'qi_origin'
    EDIT_SCHEMA = 'qi_edit'

    conn = None
    sqlStatement = None

    def __init__(self, iface, parent=None):
        super(AutoDetect, self).__init__(parent)
        self.setupUi(self)

        self.iface = iface
        self.parent = parent

        self.progressMain = parent.prgMain
        self.progressSub = parent.prgSub
        self.lblStatus = parent.lblStatus

        self.__connectFn()

    def __connectFn(self):
        self.btnFindOriginData.clicked.connect(self.findOriginData)
        self.btnFindEditData.clicked.connect(self.findEditData)
        self.btnFindDiff.clicked.connect(self.findDiff)

    def connectPg(self):
        self.__loadProperties()
        self.__loadSql()

        try:
            if self.conn:
                self.conn.close()

            self.conn = psycopg2.connect(host=self.__dbHost, port=int(self.__dbPort), database=self.__dbNm,
                                         user=self.__dbUser, password=self.__dbPassword)

        except Exception as e:
            return False

        return True

    def __loadProperties(self):
        self.properties = ConfigParser.RawConfigParser()
        self.properties.read(self.PROPERTIES_FILE)

        # Database
        self.__dbHost = self.properties.get("database", "host")
        self.__dbPort = self.properties.get("database", "port")
        self.__dbNm = self.properties.get("database", "dbname")
        self.__dbUser = self.properties.get("database", "user")
        self.__dbPassword = self.properties.get("database", "password")

    def __loadSql(self):
        self.sqlStatement = ConfigParser.RawConfigParser()
        self.sqlStatement.read(self.SQL_FILE)

    def checkEnv(self):
        if platform.system() == 'Windows':
            from _winreg import *

            conReg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
            # check PostgreSQL
            try:
                postgresqlKey = "SOFTWARE\PostgreSQL"
                OpenKey(conReg, postgresqlKey)

            except:
                QMessageBox.warning(self.iface.mainWindow(), u"경고",
                                    u"PostgreSQL이 설치되어 있지 않습니다.<br>"
                                    u"아래 링크에서 9.6.x 버전 설치 파일을 받아 설치해주시기 바랍니다.<br><br>"
                                    u"<a href='https://www.enterprisedb.com/downloads/postgres-postgresql-downloads'>"
                                    u"PostgreSQL 다운로드</a>")
                return False

            # check PostGIS
            try:
                postgisKey = "SOFTWARE\PostGIS"
                OpenKey(conReg, postgisKey)

            except:
                QMessageBox.warning(self.iface.mainWindow(), u"경고",
                                    u"PostGIS가 설치되어 있지 않습니다.<br>"
                                    u"아래 링크에서 2.4.x 버전 설치 파일을 받아 설치해주시기 바랍니다.<br><br>"
                                    u"<a href='https://winnie.postgis.net/download/windows/pg96/buildbot/'>"
                                    u"PostGIS 다운로드</a>")
                return False

        if not os.path.exists(self.PROPERTIES_FILE):
            dlg = DbInfoDialog(self.iface.mainWindow())
            rc = dlg.exec_()
            if rc != QDialog.Accepted:
                QMessageBox.warning(self.iface.mainWindow(), u"경고", u"DB 접속정보가 입력되지 않아 프로그램을 계속할 수 없습니다.")
                os.remove(self.PROPERTIES_FILE)
                return False
            else:
                self.createIniFile(dlg)

        if not self.initDatabase():
            return False

        return True

    def createIniFile(self, dlg):
        iniExample = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pgInfo", "connection.ini.example")
        config = ConfigParser.RawConfigParser()
        try:
            config.read(iniExample)
            config.set("database", "host", dlg.edtHost.text())
            config.set("database", "port", dlg.edtPort.text())
            config.set("database", "dbname", dlg.edtDatabase.text())
            config.set("database", "user", dlg.edtUser.text())
            config.set("database", "password", dlg.edtPassword.text())
            with open(self.PROPERTIES_FILE, 'w') as fout:
                config.write(fout)
        except Exception as e:
            print(e)

    def initDatabase(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            properties = ConfigParser.RawConfigParser()
            properties.read(self.PROPERTIES_FILE)

            # Database
            host = properties.get("database", "host")
            port = properties.get("database", "port")
            dbname = properties.get("database", "dbname")
            user = properties.get("database", "user")
            password = properties.get("database", "password")

            rc = self.initDatbase(host, port, dbname, user, password)
            if rc:
                QApplication.restoreOverrideCursor()
                QMessageBox.about(self.iface.mainWindow(), u"오류", u"DB에 접속할 수 없어 중단됩니다.\n{}".format(rc))
                os.remove(self.PROPERTIES_FILE)
                return False
        except Exception as e:
            print(e)
        finally:
            QApplication.restoreOverrideCursor()

        return True

    def initDatbase(self, host, port, dbname, user, password):
        postgres_postgres_conn_str = u"host='{}' port='{}' dbname ='postgres' user='{}' password='{}'".format(host,
                                                                                                              port,
                                                                                                              user,
                                                                                                              password)
        sql_espg_file = os.path.join(os.path.dirname(__file__), "..", "pgInfo", "postgis_korea_epsg_towgs84.sql")

        # Read SQL files
        try:
            with io.open(sql_espg_file, 'r', encoding='utf8') as f:
                sql_espg = f.read()
        except:
            return "SQL File read error"

        try:
            # Make the ngii login role and database
            try:
                conn = psycopg2.connect(postgres_postgres_conn_str)
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            except:
                return u"error database connection: {}".format(postgres_postgres_conn_str)

            curs = conn.cursor()
            curs.execute(u"SELECT datname FROM pg_database WHERE datname = '{}'".format(dbname))
            results = curs.fetchall()
            if len(results) != 1:
                sql = u"CREATE DATABASE {} WITH ENCODING='UTF8' TEMPLATE=template0 LC_COLLATE='C' LC_CTYPE='C' CONNECTION LIMIT=-1".format(
                    dbname)
                curs.execute(sql)
            conn.close()

            tmp_postgres_conn_str = u"host='{}' port='{}' dbname ='{}' user='{}' password='{}'".format(host,
                                                                                                              port,
                                                                                                              dbname,
                                                                                                              user,
                                                                                                              password)

            # Setup extension and EPSG
            try:
                print tmp_postgres_conn_str
                conn = psycopg2.connect(tmp_postgres_conn_str)
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            except:
                return u"error database connection: {}".format(tmp_postgres_conn_str)

            curs = conn.cursor()
            curs.execute("SELECT extname FROM pg_extension WHERE extname = 'postgis'")
            results = curs.fetchall()
            if len(results) != 1:
                sql = u"CREATE EXTENSION postgis"
                threadExecuteSql(curs, sql)
                curs.execute(sql_espg)

            conn.close()
        except Exception as e:
            return e

        return None

    def findOriginData(self):
        # if self.radioShp.isChecked():
        #     dataPath = QFileDialog.getExistingDirectory(self.iface.mainWindow(), u'검사 대상 폴더 선택',
        #                                                 self.__oldDataDir)
        #     self.__oldDataDir = os.path.dirname(dataPath)
        #
        #     self.logger.info("Set inspect data : " + dataPath)
        #     self.txtInspectData.setText(dataPath)
        # else:
        #     fileFilter = "GeoPackage (*.gpkg)"
        #
        #     dataPath = QFileDialog.getOpenFileName(self.iface.mainWindow(), u'검사 대상 GeoPackage 선택',
        #                                            self.__oldDataDir, filter=fileFilter)
        #     self.__oldDataDir = os.path.dirname(dataPath)
        #
        #     self.logger.info("Set inspect data : " + dataPath)
        #     self.txtInspectData.setText(dataPath)

        dataPath = QFileDialog.getExistingDirectory(self.iface.mainWindow(), u'검사 대상 폴더 선택')
        self.txtOriginData.setText(dataPath)

        try:
            # 한글검사
            str(dataPath)

        except:
            QMessageBox.warning(self.parent, u'검사 대상 경로 오류',
                                u'검사 대상의 경로에 한글이 포함되어 있습니다.\n'
                                u'검사 대상의 위치를 이동해주시기 바랍니다.\n\n'
                                u'선택한 경로 : ' + dataPath)
            self.txtOriginData.setText('')

    def findEditData(self):
        # if self.radioShp.isChecked():
        #     dataPath = QFileDialog.getExistingDirectory(self.iface.mainWindow(), u'검사 대상 폴더 선택',
        #                                                 self.__oldDataDir)
        #     self.__oldDataDir = os.path.dirname(dataPath)
        #
        #     self.logger.info("Set inspect data : " + dataPath)
        #     self.txtInspectData.setText(dataPath)
        # else:
        #     fileFilter = "GeoPackage (*.gpkg)"
        #
        #     dataPath = QFileDialog.getOpenFileName(self.iface.mainWindow(), u'검사 대상 GeoPackage 선택',
        #                                            self.__oldDataDir, filter=fileFilter)
        #     self.__oldDataDir = os.path.dirname(dataPath)
        #
        #     self.logger.info("Set inspect data : " + dataPath)
        #     self.txtInspectData.setText(dataPath)

        dataPath = QFileDialog.getExistingDirectory(self.iface.mainWindow(), u'검사 대상 폴더 선택')
        self.txtEditData.setText(dataPath)

        try:
            # 한글검사
            str(dataPath)

        except:
            QMessageBox.warning(self.parent, u'검사 대상 경로 오류',
                                u'검사 대상의 경로에 한글이 포함되어 있습니다.\n'
                                u'검사 대상의 위치를 이동해주시기 바랍니다.\n\n'
                                u'선택한 경로 : ' + dataPath)
            self.txtEditData.setText('')

    def findDiff(self):
        self.close()

        self.progressMain.setMinimum(0)
        self.progressMain.setMaximum(0)

        self.lblStatus.setText(u"자료 확인 중 ... ")

        if self.ORIGIN_SCHEMA in self.selectSchemaList():
            self.dropSchema(self.ORIGIN_SCHEMA)

        if self.EDIT_SCHEMA in self.selectSchemaList():
            self.dropSchema(self.EDIT_SCHEMA)

        # 기성과 insert
        res = self.insertData(self.ORIGIN_SCHEMA, 'shp', self.txtOriginData.text())
        if not res:
            self.parent.error(u"오류가 발생하여 변화내용 자동탐지 탐지가 중단되었습니다.")
            return

        # 남품성과 insert
        res = self.insertData(self.EDIT_SCHEMA, 'shp', self.txtEditData.text())
        if not res:
            self.parent.error(u"오류가 발생하여 변화내용 자동탐지 탐지가 중단되었습니다.")
            return

        res = self.createInpsectObj(self.EDIT_SCHEMA)
        if not res:
            self.parent.error(u"오류가 발생하여 변화내용 자동탐지 탐지가 중단되었습니다.")
            return

        originTableList = self.selectTableList(self.ORIGIN_SCHEMA)
        editTableList = self.selectTableList(self.EDIT_SCHEMA)

        editTableList.remove("inspect_obj")

        for editTable in editTableList:
            # 비교할 테이블이 없으면 넘어감
            if editTable not in originTableList:
                self.parent.error(u'{table}가 매칭되는 기준 데이터가 없습니다.'.format(table=editTable))
                continue

            originGeomType = self.selectGeometryType(self.ORIGIN_SCHEMA, editTable)
            editGeomType = self.selectGeometryType(self.EDIT_SCHEMA, editTable)

            if originGeomType != editGeomType:
                self.parent.error(u'{table}의 도형타입이 기준 데이터와 일치하지 않습니다.'.format(table=editTable))
                continue

            self.selectColList(self.EDIT_SCHEMA, editTable)

            if editGeomType == 'MULTIPOLYGON':  # 폴리곤 일때는 GeoHash 와 면적 생성
                self.geohash_sql = u'st_geohash(ST_Transform(st_centroid(st_envelope(wkb_geometry)), 4326), ' \
                                   u'12) as mbr_hash_12, round( CAST(st_area(wkb_geometry) as numeric), 1) as geom_area'
            elif editGeomType == 'MULTILINESTRING':  # 선 일때는 GeoHash 와 길이 생성
                self.geohash_sql = u'st_geohash(ST_Transform(st_centroid(st_envelope(wkb_geometry)), 4326), 12) ' \
                                   u'as mbr_hash_12, round( CAST(st_length(wkb_geometry) as numeric), 1) as geom_length'
            else:  # 점 일때는 GeoHash 만 생성
                self.geohash_sql = u'st_geohash(ST_Transform(wkb_geometry, 4326), 12) as mbr_hash_12'

            self.lblStatus.setText(u"{} : 동일 객체 탐지".format(editTable))
            self.findSame(editTable, editGeomType)
            self.lblStatus.setText(u"{} : 형상 수정 탐지".format(editTable))
            self.findEditOnlyGeomety(editTable)
            self.lblStatus.setText(u"{} : 속성 수정 탐지".format(editTable))
            self.findEditAttr(editTable, editGeomType)
            self.lblStatus.setText(u"{} : 삭제 객체 탐지".format(editTable))
            self.findDel(editTable)
            self.lblStatus.setText(u"{} : 추가 객체 탐지".format(editTable))
            self.findAdd(editTable)

        self.lblStatus.setText(u"결과 불러오는 중 ... ")
        self.addLayers()

        self.lblStatus.setText(u"변화내용 자동탐지 완료 ")
        self.parent.info(u"변화내용 자동탐지 완료 ")

    def insertData(self, schema, dataType, data):
        if dataType == 'shp':
            return self.__insertShp(schema, data)

        else:
            return self.__insertGpkg(schema, data)

    def __insertShp(self, schema, inspectData):
        self.parent.info(u"{} 폴더를 읽고 있습니다.".format(inspectData))

        createResult = self.createSchema(schema)
        if not createResult:
            return False

        pgConnectInfo = 'PG:host={host} port={port} dbname={dbname} user={user} password={password}' \
            .format(host=self.__dbHost, port=self.__dbPort, dbname=self.__dbNm,
                    user=self.__dbUser, password=self.__dbPassword)

        for shp in glob.glob(os.path.join(inspectData, "*.shp")):
            self.parent.debug(u"{} 넣는중".format(shp))
            commandList = ['ogr2ogr', '-a_srs', 'EPSG:5179', '--config', 'SHAPE_ENCODING', 'CP949',
                           '--config', 'GDAL_FILENAME_IS_UTF8', 'NO', '-f', 'PostgreSQL',
                           pgConnectInfo, shp, '-nlt', 'PROMOTE_TO_MULTI', '-lco', 'PRECISION=NO',
                           '-lco', 'SCHEMA={schema}'.format(schema=schema)]

            try:
                self.parent.debug("Command : " + ' '.join(commandList))
                threadExecuteCmd(commandList)

                self.parent.debug("Insert completely.")

            except Exception as e:
                self.parent.error(u"SHP을 읽는 도중 문제가 발생하였습니다.")
                return False

        return True

    def __insertGpkg(self, schema, inspectData):
        self.parent.info(u"{} 파일을 읽고 있습니다.".format(inspectData))

        createResult = self.createSchema(schema)
        if not createResult:
            return

        pgConnectInfo = 'PG:host={host} port={port} dbname={dbname} user={user} password={password}' \
            .format(host=self.__dbHost, port=self.__dbPort, dbname=self.__dbNm,
                    user=self.__dbUser, password=self.__dbPassword)

        commandList = ['ogr2ogr', '-a_srs', 'EPSG:5179', '--config', 'SHAPE_ENCODING', 'UTF-8', '-f', 'PostgreSQL',
                       pgConnectInfo, inspectData, '-nlt', 'PROMOTE_TO_MULTI',
                       '-lco', 'SCHEMA={schema}'.format(schema=schema)]

        try:
            self.parent.debug("Command : " + ' '.join(commandList))
            threadExecuteCmd(commandList)

        except Exception as e:
            self.parent.error(u'GPKG를 DB에 넣는 도중 문제가 발생하였습니다.')
            return

    # 기본 SQL
    def selectSchemaList(self):
        schemaList = list()

        cur = self.conn.cursor()

        try:
            selectSql = self.sqlStatement.get("SQL", "selectSchemaList")
            cur.execute(SQL(selectSql), {"user": self.__dbUser})

            sqlResults = cur.fetchall()

            for sqlResult in sqlResults:
                schemaList.append(sqlResult[0])

        except Exception as e:
            self.parent.error(u"스키마 리스트를 조회하는 도중 문제가 발생하였습니다.")
            self.parent.error(e)

        if cur:
            cur.close()

        return schemaList

    def createSchema(self, schema):
        result = False

        cur = self.conn.cursor()

        try:
            createSql = self.sqlStatement.get("SQL", "createSchema")
            self.parent.debug(cur.mogrify(SQL(createSql).format(schema=Identifier(schema))))
            cur.execute(SQL(createSql).format(schema=Identifier(schema)))

            self.conn.commit()

            result = True

        except Exception as e:
            self.parent.error(u"스키마를 생성하는 도중 문제가 발생하였습니다.")
            self.parent.error(e)

            self.conn.rollback()

        if cur:
            cur.close()

        return result

    def dropSchema(self, schema):
        result = False
        errMsg = None

        cur = self.conn.cursor()

        try:
            dropSql = self.sqlStatement.get("SQL", "dropSchema")
            cur.execute(SQL(dropSql).format(schema=Identifier(schema)))

            self.conn.commit()

            result = True

        except Exception as e:
            self.parent.error(u"스키마를 삭제하는 도중 문제가 발생하였습니다.")
            self.parent.error(e)

            self.conn.rollback()

        if cur:
            cur.close()

        return result, errMsg

    def selectTableList(self, schema):
        tableList = list()

        cur = self.conn.cursor()

        try:
            selectSql = self.sqlStatement.get("SQL", "selectTableList")
            cur.execute(selectSql, {"schema": schema})
            sqlResults = cur.fetchall()

            for sqlResult in sqlResults:
                tableList.append(sqlResult[0])

        except Exception as e:
            self.parent.error(u"테이블 리스트를 조회하는 도중 문제가 발생하였습니다.")
            self.parent.error(e)

        if cur:
            cur.close()

        return tableList

    def selectGeometryType(self, schema, table):
        geomType = str()

        cur = self.conn.cursor()

        try:
            selectSql = """
                SELECT GeometryType(wkb_geometry) FROM {schema}.{table} limit 1;
            """

            cur.execute(SQL(selectSql).format(schema=Identifier(schema),
                                              table=Identifier(table)))
            sqlResult = cur.fetchone()

            geomType = sqlResult[0]

        except Exception as e:
            self.parent.error(u"지오메트리 타입을 조회하는 도중 문제가 발생하였습니다.")
            self.parent.error(e)

        if cur:
            cur.close()

        return geomType

    def selectColList(self, schema, table, checkNum=True):
        all_column_nm = []
        num_column_nm = []

        cur = self.conn.cursor()

        sql = """
                select column_name from information_schema.columns
                where table_schema = '{schema}' and table_name = '{table}' order by ordinal_position asc
            """.format(schema=schema, table=table)
        cur.execute(sql)
        all_results = cur.fetchall()

        if checkNum:
            sql = """
                    select column_name from information_schema.columns 
                    where table_schema = '{schema}' and table_name = '{table}' and data_type = 'numeric';
                """.format(schema=schema, table=table)

            cur.execute(sql)
            num_results = cur.fetchall()

            for list in num_results:
                num_column_nm.append(list[0])

            for list in all_results:
                if list[0] in num_column_nm:
                    all_column_nm.append(u"round({0}, 2) as {0}".format(list[0]))
                else:
                    all_column_nm.append(list[0])
        else:
            for list in all_results:
                all_column_nm.append(list[0])

        removeColList = ['ogc_fid', 'fid', 'wkb_geometry', 'obchg_dt', 'rsreg_de', 'obchg_se', 'mnent_nm',
                         'inins_se', 'lcins_se', 'loins_se', 'tiins_se', 'thins_se', 'dbreg_dt']

        for removeCol in removeColList:
            if removeCol in all_column_nm:
                all_column_nm.remove(removeCol)

        self.column_sql = ','.join(all_column_nm)

        self.id_column = all_column_nm[0]

    # 변화 탐지 SQL
    # 변화 정보 테이블
    def createInpsectObj(self, schema):
        result = False

        cur = self.conn.cursor()

        try:
            createSql = """
                    CREATE TABLE {schema}.inspect_obj (
                        seq_no serial primary key,
                        layer_nm character varying(50),
                        origin_ogc_fid integer,
                        receive_ogc_fid integer,
                        mod_type character varying(3)
                    );
                """

            cur.execute(SQL(createSql).format(schema=Identifier(schema)))

            self.conn.commit()

            result = True

        except Exception as e:
            self.parent.error(u"지오메트리 타입을 조회하는 도중 문제가 발생하였습니다.")
            self.parent.error(e)

            self.conn.rollback()

        if cur:
            cur.close()

        return result

    # 동일 파일 검사
    def findSame(self, table, geom_type):
        self.parent.info(u"{}의 동일 객체를 탐지하고 있습니다.".format(table))
        cur = self.conn.cursor()

        if geom_type == 'MULTIPOLYGON':  # 폴리곤 일때는 면적 비교 추가
            add_sql = u'and e.geom_area between o.geom_area*0.95 and o.geom_area*1.05'
        elif geom_type == 'MULTILINESTRING':  # 선 일때는 길이 비교 추가
            add_sql = u'and e.geom_length between o.geom_length*0.95 and o.geom_length*1.05'
        else:  # 점 일때는 PK 비교 추가
            add_sql = u'and o.{0} = e.{0}'.format(self.id_column)

        try:

            insertSql = """
                    WITH geom_same_data AS (
                        SELECT o.* FROM (
                            SELECT {column_sql}, {geohash_sql}
                            FROM {origin_schema}.{table} 
                        ) AS o
                        INNER JOIN (
                            SELECT {column_sql}, {geohash_sql}
                            FROM {edit_schema}.{table}
                        ) AS e
                        ON o.mbr_hash_12 = e.mbr_hash_12 
                        {add_sql}
                        AND o.{id_col} = e.{id_col}
                    )
                    , same_data AS (
                        SELECT o.* FROM (
                            SELECT {column_sql}, mbr_hash_12 FROM geom_same_data
                        ) AS o
                        INNER JOIN (
                            SELECT {column_sql}, 
                            ST_Geohash(ST_Transform(ST_Centroid(ST_Envelope(wkb_geometry)), 4326), 12) AS mbr_hash_12
                            FROM {edit_schema}.{table}
                        ) AS e
                        ON (o.*) = (e.*)
                    )
                    , origin AS (
                        SELECT o.ogc_fid AS origin_ogc_fid, a.{id_col}, a.mbr_hash_12
                        FROM same_data AS a
                        INNER JOIN (
                            SELECT ogc_fid, {id_col}, 
                            ST_Geohash(ST_Transform(ST_Centroid(ST_Envelope(wkb_geometry)), 4326), 12) AS mbr_hash_12
                            FROM {origin_schema}.{table}
                        ) AS o
                        ON a.{id_col} = o.{id_col}
                        AND a.mbr_hash_12 = o.mbr_hash_12
                    )
                    , recevie AS (
                        SELECT o.ogc_fid AS receive_ogc_fid, a.{id_col}, a.mbr_hash_12
                        FROM same_data AS a
                        INNER JOIN (
                            SELECT ogc_fid, {id_col}, 
                            ST_Geohash(ST_Transform(ST_Centroid(ST_Envelope(wkb_geometry)), 4326), 12) AS mbr_hash_12
                            FROM {edit_schema}.{table}
                        ) AS o
                        ON a.{id_col} = o.{id_col}
                        AND a.mbr_hash_12 = o.mbr_hash_12
                    )
                    INSERT INTO {edit_schema}.inspect_obj(
                        layer_nm, origin_ogc_fid, receive_ogc_fid, mod_type
                    )
                    SELECT %(layer_nm)s, origin_ogc_fid, receive_ogc_fid, 's'
                    FROM origin, recevie
                    WHERE origin.{id_col} = recevie.{id_col}
                    AND origin.mbr_hash_12 = recevie.mbr_hash_12;
                """
            threadExecuteSql(cur, SQL(insertSql).format(column_sql=SQL(self.column_sql),
                                                        geohash_sql=SQL(self.geohash_sql),
                                                        origin_schema=Identifier(self.ORIGIN_SCHEMA),
                                                        edit_schema=Identifier(self.EDIT_SCHEMA),
                                                        table=Identifier(table),
                                                        add_sql=SQL(add_sql),
                                                        id_col=Identifier(self.id_column)),
                             {"layer_nm": table})

        except Exception as e:
            self.parent.error(u"스키마 리스트를 조회하는 도중 문제가 발생하였습니다.")
            self.parent.error(e)

            self.conn.rollback()

        else:
            self.conn.commit()

    # 형상 수정
    def findEditOnlyGeomety(self, table):
        self.parent.info(u"{}의 형상 수정 객체를 탐지하고 있습니다.".format(table))
        cur = self.conn.cursor()

        try:

            insertSql = """
                    WITH attr_same_data AS (
                        SELECT o.* 
                        FROM (
                            SELECT {column_sql} FROM {origin_schema}.{table}
                        ) AS o, 
                        (
                            SELECT {column_sql} FROM {edit_schema}.{table}
                        ) AS e
                        WHERE (o.*) = (e.*)
                    )
                    , same_data AS (
                        SELECT wkb_geometry, {column_sql} 
                        FROM {origin_schema}.{table} 
                        WHERE ogc_fid IN (
                            SELECT origin_ogc_fid FROM {edit_schema}.inspect_obj
                            WHERE mod_type = 's'
                            AND layer_nm = %(layer_nm)s
                        )
                    )
                    , join_geom AS (
                        SELECT o.wkb_geometry, a.* 
                        FROM attr_same_data AS a, {origin_schema}.{table} AS o
                        WHERE o.{id_col} = a.{id_col}
                    )
                    , geo_edit AS (
                        SELECT * FROM join_geom
                        EXCEPT
                        SELECT * FROM same_data
                    )
                    INSERT INTO {edit_schema}.inspect_obj(layer_nm, origin_ogc_fid, receive_ogc_fid, mod_type)
                    SELECT %(layer_nm)s, origin_ogc_fid, receive_ogc_fid, 'eg'
                    FROM (
                        SELECT ogc_fid AS origin_ogc_fid, e.{id_col} 
                        FROM geo_edit AS e
                        INNER JOIN {origin_schema}.{table} AS o
                        ON e.{id_col} = o.{id_col}
                    ) AS origin
                    , (
                        SELECT ogc_fid AS receive_ogc_fid, e.{id_col} 
                        FROM geo_edit AS e
                        INNER JOIN {edit_schema}.{table} AS o
                        ON e.{id_col} = o.{id_col}
                    ) AS edit
                    WHERE origin.{id_col} = edit.{id_col};
                """

            threadExecuteSql(cur, SQL(insertSql).format(column_sql=SQL(self.column_sql),
                                                        origin_schema=Identifier(self.ORIGIN_SCHEMA),
                                                        edit_schema=Identifier(self.EDIT_SCHEMA),
                                                        table=Identifier(table),
                                                        id_col=Identifier(self.id_column)),
                             {"layer_nm": table})

        except Exception as e:
            self.parent.error(u"스키마 리스트를 조회하는 도중 문제가 발생하였습니다.")
            self.parent.error(e)

            self.conn.rollback()

        else:
            self.conn.commit()

    def findEditAttr(self, table, geom_type):
        self.parent.info(u"{}의 속성 수정 객체를 탐지하고 있습니다.".format(table))
        cur = self.conn.cursor()

        try:

            if geom_type == 'MULTIPOLYGON':
                insertSql = """
                        WITH same AS (
                            SELECT {column_sql}, {geohash_sql} 
                            FROM {origin_schema}.{table}
                            WHERE ogc_fid IN (
                                SELECT origin_ogc_fid 
                                FROM {edit_schema}.inspect_obj
                                where mod_type = 's'
                                AND layer_nm = %(layer_nm)s
                            )
                        )
                        , om AS (
                            SELECT {column_sql}, {geohash_sql} 
                            FROM {origin_schema}.{table} 
                            EXCEPT
                            SELECT * FROM same 
                        )
                        , em AS (
                            SELECT {column_sql}, {geohash_sql} 
                            FROM {edit_schema}.{table} 
                            EXCEPT
                            SELECT * FROM same 
                        )
                        , geometry AS ( 
                            SELECT mbr_hash_12, geom_area 
                            FROM ( 
                                SELECT om.* FROM om 
                                INNER join em 
                                ON em.mbr_hash_12 = om.mbr_hash_12 
                                AND em.geom_area BETWEEN om.geom_area*0.95 
                                AND om.geom_area*1.05 
                            ) AS t
                        ) 
                        INSERT INTO {edit_schema}.inspect_obj(layer_nm, origin_ogc_fid,receive_ogc_fid,mod_type)
                        SELECT %(layer_nm)s, origin_ogc_fid, receive_ogc_fid, 'ef' as mod_type 
                        FROM (
                            SELECT ogc_fid AS origin_ogc_fid, o.mbr_hash_12, o.geom_area 
                            FROM geometry 
                            INNER JOIN (
                                SELECT ogc_fid, {geohash_sql} 
                                FROM {origin_schema}.{table} 
                            ) as o 
                            ON geometry.mbr_hash_12=o.mbr_hash_12 
                            AND geometry.geom_area BETWEEN o.geom_area*0.95 AND o.geom_area*1.05
                        ) AS origin, 
                        (
                            SELECT ogc_fid AS receive_ogc_fid, o.mbr_hash_12, o.geom_area 
                            FROM geometry 
                            INNER JOIN (
                                SELECT ogc_fid, {geohash_sql} 
                                FROM {edit_schema}.{table} 
                            ) as o 
                            ON geometry.mbr_hash_12=o.mbr_hash_12 
                            AND geometry.geom_area BETWEEN o.geom_area*0.95 AND o.geom_area*1.05
                        ) as receive 
                        WHERE receive.mbr_hash_12=origin.mbr_hash_12 
                        AND receive.geom_area BETWEEN origin.geom_area*0.95 AND origin.geom_area*1.05
                    """
            elif geom_type == 'MULTILINESTRING':
                insertSql = """
                        WITH same AS (
                            SELECT {column_sql}, {geohash_sql} 
                            FROM {origin_schema}.{table}
                            WHERE ogc_fid IN (
                                SELECT origin_ogc_fid 
                                FROM {edit_schema}.inspect_obj
                                where mod_type = 's'
                                AND layer_nm = %(layer_nm)s
                            )
                        )
                        , om AS (
                            SELECT {column_sql}, {geohash_sql} 
                            FROM {origin_schema}.{table} 
                            EXCEPT
                            SELECT * FROM same 
                        )
                        , em AS (
                            SELECT {column_sql}, {geohash_sql} 
                            FROM {edit_schema}.{table} 
                            EXCEPT
                            SELECT * FROM same 
                        )
                        , geometry AS ( 
                            SELECT mbr_hash_12, geom_length 
                            FROM ( 
                                SELECT om.* FROM om 
                                INNER join em 
                                ON em.mbr_hash_12 = om.mbr_hash_12 
                                AND em.geom_length BETWEEN om.geom_length*0.95 
                                AND om.geom_length*1.05 
                            ) AS t
                        ) 
                        INSERT INTO {edit_schema}.inspect_obj(layer_nm, origin_ogc_fid,receive_ogc_fid,mod_type)
                        SELECT %(layer_nm)s, origin_ogc_fid, receive_ogc_fid, 'ef' as mod_type 
                        FROM (
                            SELECT ogc_fid AS origin_ogc_fid, o.mbr_hash_12, o.geom_length 
                            FROM geometry 
                            INNER JOIN (
                                SELECT ogc_fid, {geohash_sql} 
                                FROM {origin_schema}.{table} 
                            ) as o 
                            ON geometry.mbr_hash_12=o.mbr_hash_12 
                            AND geometry.geom_length BETWEEN o.geom_length*0.95 AND o.geom_length*1.05
                        ) AS origin, 
                        (
                            SELECT ogc_fid AS receive_ogc_fid, o.mbr_hash_12, o.geom_length 
                            FROM geometry 
                            INNER JOIN (
                                SELECT ogc_fid, {geohash_sql} 
                                FROM {edit_schema}.{table} 
                            ) as o 
                            ON geometry.mbr_hash_12=o.mbr_hash_12 
                            AND geometry.geom_length BETWEEN o.geom_length*0.95 AND o.geom_length*1.05
                        ) as receive 
                        WHERE receive.mbr_hash_12=origin.mbr_hash_12 
                        AND receive.geom_length BETWEEN origin.geom_length*0.95 AND origin.geom_length*1.05
                    """
            else:
                insertSql = """
                        WITH same AS (
                            SELECT {column_sql}, {geohash_sql} 
                            FROM {origin_schema}.{table}
                            WHERE ogc_fid IN (
                                SELECT origin_ogc_fid 
                                FROM {edit_schema}.inspect_obj
                                where mod_type = 's'
                                AND layer_nm = %(layer_nm)s
                            )
                        )
                        , om AS (
                            SELECT {column_sql}, {geohash_sql} 
                            FROM {origin_schema}.{table} 
                            EXCEPT 
                            SELECT * FROM same 
                        )
                        , em AS (
                            SELECT {column_sql}, {geohash_sql} 
                            FROM {edit_schema}.{table} 
                            EXCEPT 
                            SELECT * FROM same 
                        )
                        , geometry AS ( 
                            SELECT mbr_hash_12 
                            FROM ( 
                                SELECT om.* FROM om 
                                INNER JOIN em 
                                ON em.mbr_hash_12 = om.mbr_hash_12 
                            ) AS t
                        ) 
                        INSERT INTO {edit_schema}.inspect_obj(layer_nm, origin_ogc_fid,receive_ogc_fid,mod_type)
                        SELECT %(layer_nm)s, origin_ogc_fid, receive_ogc_fid, 'ef' AS mod_type 
                        FROM (
                            SELECT ogc_fid AS origin_ogc_fid, o.mbr_hash_12 
                            FROM geometry 
                            INNER JOIN (
                                SELECT ogc_fid, {geohash_sql} 
                                FROM {origin_schema}.{table} 
                            ) AS o 
                            ON geometry.mbr_hash_12= o.mbr_hash_12) AS origin
                            , (
                                SELECT ogc_fid AS receive_ogc_fid, o.mbr_hash_12 
                                FROM geometry 
                                INNER JOIN (
                                    SELECT ogc_fid, {geohash_sql} 
                                    FROM {edit_schema}.{table} 
                                ) AS o 
                                ON geometry.mbr_hash_12 = o.mbr_hash_12
                            ) AS receive 
                            WHERE origin.mbr_hash_12 = receive.mbr_hash_12
                    """
            threadExecuteSql(cur, SQL(insertSql).format(column_sql=SQL(self.column_sql),
                                                        geohash_sql=SQL(self.geohash_sql),
                                                        origin_schema=Identifier(self.ORIGIN_SCHEMA),
                                                        edit_schema=Identifier(self.EDIT_SCHEMA),
                                                        table=Identifier(table),
                                                        id_col=Identifier(self.id_column)),
                             {"layer_nm": table})

        except Exception as e:
            self.parent.error(u"스키마 리스트를 조회하는 도중 문제가 발생하였습니다.")
            self.parent.error(e)

            self.conn.rollback()

        else:
            self.conn.commit()

    def findDel(self, table):
        self.parent.info(u"{}의 삭제 객체를 탐지하고 있습니다.".format(table))
        cur = self.conn.cursor()

        try:

            insertSql = """
                    INSERT INTO {edit_schema}.inspect_obj(layer_nm, origin_ogc_fid, receive_ogc_fid, mod_type) 
                    SELECT %(layer_nm)s, origin_ogc_fid, 0 AS receive_ogc_fid, 'r' AS mod_type 
                    FROM (
                        SELECT ogc_fid AS origin_ogc_fid 
                        FROM {origin_schema}.{table} 
                        EXCEPT 
                        SELECT origin_ogc_fid 
                        FROM {edit_schema}.inspect_obj
                        WHERE layer_nm = %(layer_nm)s
                    ) AS rm
                """
            threadExecuteSql(cur, SQL(insertSql).format(column_sql=SQL(self.column_sql),
                                                        origin_schema=Identifier(self.ORIGIN_SCHEMA),
                                                        edit_schema=Identifier(self.EDIT_SCHEMA),
                                                        table=Identifier(table)),
                             {"layer_nm": table})

        except Exception as e:
            self.parent.error(u"스키마 리스트를 조회하는 도중 문제가 발생하였습니다.")
            self.parent.error(e)

            self.conn.rollback()

        else:
            self.conn.commit()

    def findAdd(self, table):
        self.parent.info(u"{}의 추가 객체를 탐지하고 있습니다.".format(table))
        cur = self.conn.cursor()

        try:

            insertSql = """
                    INSERT INTO {edit_schema}.inspect_obj(layer_nm, origin_ogc_fid, receive_ogc_fid, mod_type )
                    SELECT %(layer_nm)s, 0 as origin_ogc_fid, receive_ogc_fid, 'a' as mod_type 
                    FROM (
                        SELECT ogc_fid AS receive_ogc_fid
                        FROM {edit_schema}.{table}
                        EXCEPT
                        SELECT receive_ogc_fid
                        FROM {edit_schema}.inspect_obj
                        WHERE layer_nm = %(layer_nm)s
                    ) AS add
                """
            threadExecuteSql(cur, SQL(insertSql).format(column_sql=SQL(self.column_sql),
                                                        origin_schema=Identifier(self.ORIGIN_SCHEMA),
                                                        edit_schema=Identifier(self.EDIT_SCHEMA),
                                                        table=Identifier(table),
                                                        id_col=Identifier(self.id_column)),
                             {"layer_nm": table})

        except Exception as e:
            self.parent.error(u"스키마 리스트를 조회하는 도중 문제가 발생하였습니다.")
            self.parent.error(e)

            self.conn.rollback()

        else:
            self.conn.commit()

    def addLayers(self):
        self.parent.info(u"탐지 결과를 불러오고 있습니다.")
        QgsMapLayerRegistry.instance().removeAllMapLayers()

        canvas = self.iface.mapCanvas()
        canvas.mapRenderer().setProjectionsEnabled(True)
        canvas.mapRenderer().setDestinationCrs(QgsCoordinateReferenceSystem(5179))

        tableList = self.selectTableList(self.EDIT_SCHEMA)
        tableList.remove('inspect_obj')

        for table in tableList:

            self.selectColList(self.EDIT_SCHEMA, table, False)

            uri = QgsDataSourceURI()

            # 기존의 데이터 ( 변화없는 정보 )
            sql = "(SELECT row_number() over (order by mod_type asc) as id, wkb_geometry, {column_sql}, b.mod_type " \
                  "FROM {origin_schema}.{table} AS a, {edit_schema}.inspect_obj AS b " \
                  "WHERE a.ogc_fid = b.origin_ogc_fid " \
                  "AND layer_nm = '{table}' " \
                  "AND mod_type != 'r')".format(column_sql=self.column_sql,
                                                origin_schema=self.ORIGIN_SCHEMA,
                                                edit_schema=self.EDIT_SCHEMA,
                                                table=table)

            uri.setConnection(self.__dbHost, self.__dbPort, self.__dbNm, self.__dbUser, self.__dbPassword)
            uri.setDataSource("", sql, "wkb_geometry", "", "id")
            self.maintain_data = QgsVectorLayer(uri.uri(), u'변화없음_' + table, "postgres")

            symbol = None
            if self.maintain_data.wkbType() == QGis.WKBMultiPolygon:
                symbol = QgsFillSymbolV2().createSimple({'color_border': '#a7a7a7', 'width_border': '0.5',
                                                         'style': 'no', 'style_border': 'solid',
                                                         "outline_width_unit": "pixel"})
            elif self.maintain_data.wkbType() == QGis.WKBMultiLineString:
                symbol = QgsLineSymbolV2().createSimple({'color': '#a7a7a7', 'width': '0.5',
                                                         'style': 'solid',
                                                         "outline_width_unit": "pixel"})
            else:
                symbol = QgsMarkerSymbolV2.createSimple({'name': 'circle', 'color': '#a7a7a7', 'size': '1',
                                                         'outline_style': 'no',
                                                         "size_unit": "pixel"})

            self.maintain_data.rendererV2().setSymbol(symbol)
            QgsMapLayerRegistry.instance().addMapLayer(self.maintain_data)

            # 변화가 있는 정보
            sql = "(SELECT row_number() over (order by mod_type asc) as id, * " \
                  "FROM ( SELECT wkb_geometry, {column_sql}, b.mod_type " \
                  "FROM {origin_schema}.{table} AS a, {edit_schema}.inspect_obj AS b " \
                  "WHERE a.ogc_fid = b.origin_ogc_fid " \
                  "AND layer_nm = '{table}' " \
                  "AND mod_type = 'r' " \
                  "UNION SELECT wkb_geometry, {column_sql}, b.mod_type " \
                  "FROM {edit_schema}.{table} AS a, {edit_schema}.inspect_obj AS b " \
                  "WHERE a.ogc_fid = b.receive_ogc_fid " \
                  "AND layer_nm = '{table}' " \
                  "AND mod_type != 's') AS foo)".format(column_sql=self.column_sql,
                                                        origin_schema=self.ORIGIN_SCHEMA,
                                                        edit_schema=self.EDIT_SCHEMA,
                                                        table=table)

            uri.setDataSource("", sql, "wkb_geometry", "", "id")
            self.diff_data = QgsVectorLayer(uri.uri(), u'변화정보_' + table, "postgres")

            mod_type_symbol = {
                'a': ('green', u'추가'),
                'r': ('red', u'삭제'),
                'eg': ('orange', u'도형변경'),
                'ef': ('blue', u'속성변경')
            }

            diff_data_type = self.diff_data.wkbType()
            categories = []
            for mod_type, (color, label) in mod_type_symbol.items():
                if diff_data_type == QGis.WKBMultiPolygon:
                    symbol = QgsFillSymbolV2().createSimple({'color_border': color, 'width_border': '1.5',
                                                             'style': 'no', 'style_border': 'solid',
                                                             "outline_width_unit": "pixel"})
                elif diff_data_type == QGis.WKBMultiLineString:
                    symbol = QgsLineSymbolV2().createSimple({'color': color, 'width': '1.5',
                                                             'style': 'solid',
                                                             "outline_width_unit": "pixel"})
                else:
                    symbol = QgsMarkerSymbolV2.createSimple({'name': 'circle', 'color': color, 'size': '3',
                                                             'outline_style': 'no',
                                                             "size_unit": "pixel"})
                category = QgsRendererCategoryV2(mod_type, symbol, label)
                categories.append(category)

            expression = 'mod_type'  # field name
            renderer = QgsCategorizedSymbolRendererV2(expression, categories)
            self.diff_data.setRendererV2(renderer)

            QgsMapLayerRegistry.instance().addMapLayer(self.diff_data)

            self.inspectList = []
            self.crrIndex = -1
            iter = self.diff_data.getFeatures()
            for feature in iter:
                self.inspectList.append(feature)

            self.numTotal = len(self.inspectList)

            # 변경된 데이터가 없을 경우
            if self.numTotal <= 0:
                canvas.setExtent(self.maintain_data.extent())
                canvas.refresh()
                self.insertInspectRes()
                return
