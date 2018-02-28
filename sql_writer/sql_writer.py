# -*- coding: utf-8 -*-
import pymysql


class sqlEngine:
    def __init__(self):
        try:
            self.db = pymysql.connect("localhost", "root", "root2018", "Digital Marketing-test") # "Coach Merchandising-NO"
            self.cur = self.db.cursor()
        except pymysql.Error, e:
            print "connection failed, error%d: %s" % (e.args[0],e.args[1])

    def insert_data(self, table, my_dict, user_id=0, info_id=0):
        print "insert:%s" % table
        try:
            #sql = "SELECT"
            '''
            if True:
                sql_1 = "ALTER TABLE " + table
                self.cur.execute(sql_1)
                self.db.commit()
            '''
            self.db.set_charset("utf8")

            cols = ', '.join(["`"+x+"`" for x in my_dict.keys()])
            values = '","'.join([x.replace('"', "\'") if isinstance(x, basestring) else str(x) for x in my_dict.values()])

            if user_id == 0 and info_id == 0:
                sql_2 = "INSERT INTO %s (%s) VALUES (%s)" % (table, cols, '"'+values+'"')
            else:
                sql_2 = "INSERT INTO %s (info_id, user_id, %s ) VALUES (%d, %d, %s)" % (table, cols, info_id, user_id, '"'+values+'"')
            try:
                self.cur.execute(sql_2)
                self.db.commit()
            except pymysql.Error, e:
                print e
                self.db.rollback()

        except pymysql.Error, e:
            print e

    def index(self, sql):
        try:
            self.cur.execute(sql)
            r = self.cur.fetchall()
            return r
        except pymysql.Error, e:
            print e
            print 'Index Failed!'
        #for i in r:
        #    print r


    def create_table(self, table, key, attName, attType={}):
        values = key + ' INT UNSIGNED AUTO_INCREMENT, ' + ', '.join([("`"+x+"`" + " ") + (attType[x] if x in attType else "INT") for x in attName])
        sql = "CREATE TABLE IF NOT EXISTS %s (%s, PRIMARY KEY (%s))" % (table, values, key)
        print sql
        try:
            self.cur.execute(sql)
            self.db.commit()
        except pymysql.Error,e:
            print e
            self.db.rollback()

    def __del__(self):
        self.db.close()


sql = sqlEngine()